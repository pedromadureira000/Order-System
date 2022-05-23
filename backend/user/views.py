from django.db.models.deletion import ProtectedError
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, permissions
#  from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from organization.facade import get_clients_by_agent

from organization.models import Client, Contracting, Establishment
from organization.serializers import ClientSerializerPOST, ContractingPOSTSerializer, EstablishmentPOSTSerializer
from .facade import get_all_client_users_by_agent, get_update_permission
from .serializers import AdminAgentPOSTSerializer, AdminAgentPUTSerializer, AgentPOSTSerializer, AgentPUTSerializer, ClientUserPOSTSerializer, ClientUserPUTSerializer, ERPUserPOSTSerializer, ERPUserPUTSerializer, OwnProfileSerializer, SwaggerLoginSerializer, SwaggerProfilePasswordSerializer, UpdateUserPasswordSerializer
from .models import User
from settings.utils import has_permission, has_role
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from .validators import agent_has_access_to_this_client_user, req_user_is_agent_without_all_estabs
from organization.validators import agent_has_access_to_this_client
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from settings.response_templates import error_response, not_found_response, serializer_invalid_response, protected_error_response, unknown_exception_response, unauthorized_response


#------------------------/ Auth Views

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request):
        return Response(_("The CSRF cookie was sent"))
# If the user has status != 1, it will be considered disabled and the user can't log in.
class Login(APIView):
    permission_classes = (permissions.AllowAny,)
    @swagger_auto_schema(request_body=SwaggerLoginSerializer) 
    def post(self, request):
        if request.user.is_authenticated:
            return Response(_("User is already authenticated"))
        serializer = SwaggerLoginSerializer(data=request.data)
        if serializer.is_valid():
            user_code = serializer.validated_data["contracting_code"] + "*" + serializer.validated_data["username" ]
            user = authenticate(username=user_code, password=serializer.validated_data["password"], request=request)
            if user is not None:
                if user.status != 1:
                    return error_response(detail=_("Your account is disabled."), status=status.HTTP_401_UNAUTHORIZED)
                # If the contracting is disabled of if the user is client user with a client company disabled, then raise a error
                if user.contracting.status != 1 or (user.client != None and user.client.status != 1) :
                    return error_response(detail=_("The login is disabled"), status=status.HTTP_401_UNAUTHORIZED)
                login(request, user)
                return Response(OwnProfileSerializer(user).data)
            else:
                return error_response(detail=_("The login failed"), status=status.HTTP_401_UNAUTHORIZED)
        return serializer_invalid_response(serializer.errors)

class Logout(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            logout(request)
            return Response(_('Logged out'))
        except Exception as error:
            #  print(error)
            unknown_exception_response(action=_('log out'))

#-------------------------------------------/ Users Views / -------------------------------------
class OwnProfileView(APIView):
    def get(self, request):
        try:
            data = OwnProfileSerializer(request.user).data
            return Response(data)
        except Exception as error:
            #  print(error)
            return unknown_exception_response(action=_('get request user profile'))
    @swagger_auto_schema(request_body=OwnProfileSerializer) 
    @transaction.atomic
    def put(self, request):
        serializer = OwnProfileSerializer(request.user, data=request.data, partial=True, context={"request": request,
            "view": "update own profile"})
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data)
            except Exception as error:
                #  print(error)
                return unknown_exception_response(action=_('update request user profile'))
        return serializer_invalid_response(serializer.errors)


class fetchContractingCompaniesToCreateERPuser(APIView):
    def get(self, request):
        if has_permission(request.user, 'create_erp_user'):
            erp_users = Contracting.objects.filter(status=1)
            return Response(ContractingPOSTSerializer(erp_users, many=True).data)
        return unauthorized_response

class ERPUserView(APIView):
    def get(self, request):
        if has_permission(request.user, 'get_erp_user'):
            erp_users = User.objects.filter(Q(groups__name='erp_user'))
            return Response(ERPUserPOSTSerializer(erp_users, many=True).data)
        return unauthorized_response
    @swagger_auto_schema(request_body=ERPUserPOSTSerializer) 
    @transaction.atomic
    def post(self, request):
        if has_permission(request.user, 'create_erp_user'):
            serializer = ERPUserPOSTSerializer(data=request.data, context={"request":request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    #  print(error)
                    return unknown_exception_response(action=_('create erp user'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response

class SpecificERPUser(APIView):
    @swagger_auto_schema(request_body=ERPUserPUTSerializer) 
    @transaction.atomic
    def put(self, request, contracting_code, username):
        if has_permission(request.user, 'update_erp_user'):
            user_code = contracting_code + "*" + username
            try: 
                user = User.objects.get(user_code=user_code, groups__name='erp_user')
            except User.DoesNotExist:
                return not_found_response(object_name='The erp user')
            serializer = ERPUserPUTSerializer(user, data=request.data, partial=True,
                    context={"request": request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    #  print(error)
                    #  raise error
                    return unknown_exception_response(action=_('update erp user'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic  
    def delete(self, request, contracting_code, username):
        if has_permission(request.user, 'delete_erp_user'):
            user_code = contracting_code + "*" + username
            try:
                user = User.objects.get(user_code=user_code, groups__name='erp_user')
            except User.DoesNotExist:
                return not_found_response(object_name=_('The erp user'))
            try:
                user.delete()
                return Response(_("ERP user deleted successfully."))
            except ProtectedError as er:
                return protected_error_response(object_name=_('erp user'))
            except Exception as error:
                transaction.rollback()
                #  print(error)
                return unknown_exception_response(action=_('delete erp user'))
        return unauthorized_response

class AdminAgentView(APIView):
    def get(self, request):
        if has_permission(request.user, 'get_admin_agents'):
            user = request.user
            agents = User.objects.filter(Q(contracting_id=user.contracting_id), Q(groups__name='admin_agent'))
            return Response(AdminAgentPOSTSerializer(agents, many=True).data)
        return unauthorized_response
    @swagger_auto_schema(request_body=AdminAgentPOSTSerializer) 
    @transaction.atomic
    def post(self, request):
        if has_permission(request.user, 'create_admin_agent'):
            serializer = AdminAgentPOSTSerializer(data=request.data, context={"request":request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    #  print(error)
                    return unknown_exception_response(action=_('create admin agent'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response

class SpecificAdminAgent(APIView):
    @swagger_auto_schema(request_body=AdminAgentPUTSerializer) 
    @transaction.atomic
    def put(self, request, contracting_code, username):
        if has_permission(request.user, 'update_admin_agent'):
            if contracting_code != request.user.contracting_id:
                return not_found_response(object_name=_('The admin agent'))
            user_code = contracting_code + "*" + username
            try: 
                user = User.objects.get(user_code=user_code, groups__name='admin_agent')
            except User.DoesNotExist:
                return not_found_response(object_name=_('The admin agent'))
            serializer = AdminAgentPUTSerializer(user, data=request.data, partial=True,
                    context={"request": request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    #  print(error)
                    #  raise error
                    return unknown_exception_response(action=_('update admin agent'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic  
    def delete(self, request, contracting_code, username):
        if has_permission(request.user, 'delete_admin_agent'):
            # Contracting Ownership
            if contracting_code != request.user.contracting_id:
                return not_found_response(object_name=_('The admin agent'))
            user_code = contracting_code + "*" + username
            try:
                user = User.objects.get(user_code=user_code, groups__name='admin_agent')
            except User.DoesNotExist:
                return not_found_response(object_name=_('The admin agent'))
            try:
                user.delete()
                return Response(_("Admin agent deleted successfully"))
            except ProtectedError as er:
                return protected_error_response(object_name=_('admin agent'))
            except Exception as error:
                transaction.rollback()
                #  print(error)
                return unknown_exception_response(action=_('delete admin agent'))
        return unauthorized_response

class fetchEstablishmentsToCreateAgent(APIView):
    def get(self, request):
        if has_permission(request.user, 'create_agent'):
            estabs = Establishment.objects.filter(company__contracting_id=request.user.contracting_id,status=1)
            return Response(EstablishmentPOSTSerializer(estabs, many=True).data)
        return unauthorized_response

class AgentView(APIView):
    def get(self, request):
        if has_permission(request.user, 'get_agents'):
            user = request.user
            agents = User.objects.filter(Q(contracting_id=user.contracting_id), Q(groups__name='agent'))
            return Response(AgentPOSTSerializer(agents, many=True).data)
        return unauthorized_response
    @swagger_auto_schema(request_body=AgentPOSTSerializer) 
    @transaction.atomic
    def post(self, request):
        if has_permission(request.user, 'create_agent'):
            serializer = AgentPOSTSerializer(data=request.data, context={"request":request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    #  print(error)
                    return unknown_exception_response(action=_('create agent'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response

class SpecificAgent(APIView):
    @swagger_auto_schema(request_body=AgentPUTSerializer) 
    @transaction.atomic
    def put(self, request, contracting_code, username):
        if has_permission(request.user, 'update_agent'):
            if contracting_code != request.user.contracting_id:
                return not_found_response(object_name=_('The agent'))
            user_code = contracting_code + "*" + username
            try: 
                user = User.objects.get(user_code=user_code, groups__name='agent')
            except User.DoesNotExist:
                return not_found_response(object_name=_('The agent'))
            serializer = AgentPUTSerializer(user, data=request.data,
                    context={"request": request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    #  print(error)
                    #  raise error
                    return unknown_exception_response(action=_('update agent'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic  
    def delete(self, request, contracting_code, username):
        if has_permission(request.user, 'delete_agent'):
            # Contracting Ownership
            if contracting_code != request.user.contracting_id:
                return not_found_response(object_name=_('The agent'))
            user_code = contracting_code + "*" + username
            try:
                user = User.objects.get(user_code=user_code, groups__name='agent')
            except User.DoesNotExist:
                return not_found_response(object_name=_('The agent'))
            try:
                user.delete()
                return Response(_("Agent deleted successfully"))
            except ProtectedError as er:
                return protected_error_response(object_name=_('agent'))
            except Exception as error:
                transaction.rollback()
                #  print(error)
                return unknown_exception_response(action=_('delete agent'))
        return unauthorized_response

class fetchClientsToCreateClientUser(APIView):
    def get(self, request):
        user = request.user
        if has_permission(user, 'create_client_user'):
            if req_user_is_agent_without_all_estabs(user):
                clients = get_clients_by_agent(user).filter(status=1) #TODO TEST
                data = ClientSerializerPOST(clients, many=True).data
                return Response(data)
            clients = Client.objects.filter(client_table__contracting_id=user.contracting_id, status=1)
            data = ClientSerializerPOST(clients, many=True).data
            return Response(data)
        return unauthorized_response


class ClientUserView(APIView):
    def get(self, request):
        if has_permission(request.user, 'get_client_users'):
            user = request.user
            #  if req_user_is_agent_without_all_estabs(user):  <- This is not used because get_all_client_users_by_agent does it.
            if has_role(user, 'agent'):
                client_users = get_all_client_users_by_agent(user)
                return Response(ClientUserPOSTSerializer(client_users, many=True).data)
            client_users = User.objects.filter(Q(contracting_id=user.contracting_id), Q(groups__name='client_user'))
            return Response(ClientUserPOSTSerializer(client_users, many=True).data)
        return unauthorized_response
    @swagger_auto_schema(request_body=ClientUserPOSTSerializer) 
    @transaction.atomic
    def post(self, request):
        if has_permission(request.user, 'create_client_user'):
                request_user_is_agent_without_all_estabs = req_user_is_agent_without_all_estabs(request.user)
                serializer = ClientUserPOSTSerializer(data=request.data, context={"request":request,
                    "request_user_is_agent_without_all_estabs": request_user_is_agent_without_all_estabs})
                #  if serializer.is_valid(raise_exception=True):
                if serializer.is_valid():
                    try:
                        serializer.save()
                        return Response(serializer.data)
                    except Exception as error:
                        transaction.rollback()
                        #  print(error)
                        return unknown_exception_response(action=_('create client user'))
                return serializer_invalid_response(serializer.errors)
        return unauthorized_response

class SpecificClientUser(APIView):
    @swagger_auto_schema(request_body=ClientUserPUTSerializer) 
    @transaction.atomic
    def put(self, request, contracting_code, username):
        if has_permission(request.user, 'update_client_user'):
            if contracting_code != request.user.contracting_id:
                return not_found_response(object_name=_('The client user'))
            user_code = contracting_code + "*" + username
            try:
                user = User.objects.get(user_code=user_code, groups__name='client_user')
            except User.DoesNotExist:
                return not_found_response(object_name=_('The client user'))
            request_user_is_agent_without_all_estabs = req_user_is_agent_without_all_estabs(request.user)
            if request_user_is_agent_without_all_estabs and not agent_has_access_to_this_client_user(request.user, user):
                return not_found_response(object_name=_('The client user'))
            serializer = ClientUserPUTSerializer(user, data=request.data, partial=True, context={"request": request,
                "request_user_is_agent_without_all_estabs": request_user_is_agent_without_all_estabs})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    #  print(error)
                    #  raise error
                    return unknown_exception_response(action=_('update client user'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic  
    def delete(self, request, contracting_code, username):
        if has_permission(request.user, 'delete_client_user'):
            if contracting_code != request.user.contracting_id:
                return not_found_response(object_name=_('The client user'))
            user_code = contracting_code + "*" + username
            try:
                client_user = User.objects.get(user_code=user_code, groups__name='client_user')
            except User.DoesNotExist:
                return not_found_response(object_name=_('The client user'))
            # If request user is agent without all estabs and not has access to this client
            if req_user_is_agent_without_all_estabs(request.user) and not agent_has_access_to_this_client(request.user, 
                    client_user.client):
                return unauthorized_response
            try:
                client_user.delete()
                return Response(_("Client user deleted successfully"))
            except ProtectedError as er:
                return protected_error_response(object_name=_('client user'))
            except Exception as error:
                transaction.rollback()
                #  print(error)
                return unknown_exception_response(action=_('delete client user'))
        return unauthorized_response

class UpdateOwnPassword(APIView):
    @swagger_auto_schema(request_body=SwaggerProfilePasswordSerializer) 
    @transaction.atomic
    def put(self, request):
        user = request.user
        data = request.data
        if not data.get('password'):
            return error_response(detail=_("Password field not sent"), status=status.HTTP_400_BAD_REQUEST )
        if not data.get('current_password'):
            return error_response(detail=_("Current Password field not sent"), status=status.HTTP_400_BAD_REQUEST )
        if user.check_password(data.get('current_password')):
            user.set_password(data['password'])
            user.save()
            return Response(_("Password updated"))
        return error_response(detail=_("passwords don't match"), status=status.HTTP_400_BAD_REQUEST )

class UpdateUserPassword(APIView):
    @swagger_auto_schema(request_body=UpdateUserPasswordSerializer) 
    @transaction.atomic
    def put(self, request, contracting_code, username):
        if contracting_code != request.user.contracting_id:
            return not_found_response(object_name=_('The user'))
        user_code = contracting_code + "*" + username
        try:
            user = User.objects.get(user_code=user_code)
        except User.DoesNotExist:
            return not_found_response(object_name=_('The user'))
        try:
            permission = get_update_permission(user)
        except Exception as error:
            #  print(error)  #TODO send log. (user probably don't have role)
            return unknown_exception_response(action=_("update user's password"))

        if has_permission(request.user, permission):
            serializer = UpdateUserPasswordSerializer(user, data=request.data, context={"request": request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(_('Password updated'))
                except Exception as error:
                    transaction.rollback()
                    #  print(error)
                    #  raise error
                    return unknown_exception_response(action=_("update user's password"))
        return unauthorized_response
