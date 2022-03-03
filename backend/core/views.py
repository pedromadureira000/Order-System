from django.db.models.deletion import ProtectedError
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status, permissions
#  from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from core.facade import get_all_client_users_by_agent, get_clients_by_agent
from core.serializers import AdminAgentSerializer, AgentSerializer, ClientSerializer, ClientTableSerializer, ClientUserSerializer, CompanySerializer, ContractingSerializer, ERPUserSerializer, EstablishmentSerializer, OwnProfileSerializer, UserSerializer, SwaggerLoginSerializer, SwaggerProfilePasswordSerializer
from core.models import Client, ClientTable, Company, Contracting, Establishment, User
from rolepermissions.checkers import has_permission, has_role
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from core.validators import agent_has_access_to_this_client, agent_has_access_to_this_client_user, req_user_is_agent_without_all_estabs
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

unauthorized_response = Response({'error': [_( "You don't have permission to access this resource.")]},status=status.HTTP_401_UNAUTHORIZED)

def success_response(detail, status=status.HTTP_200_OK):
    return Response(data={"success": [detail]}, status=status)

#This is to format error responses in drf format to have a pattern for error responses.
def error_response(detail, status):
    return Response(data={"error": [detail]}, status=status)

def not_found_response(object_name): 
    return Response({"error":[_( "{object_name} was not found.").format(object_name=object_name)]}, status=status.HTTP_404_NOT_FOUND)

def serializer_invalid_response(errors):
    return Response(errors, status=status.HTTP_400_BAD_REQUEST)

def protected_error_response(object_name): 
    return Response({"error":[_("You cannot delete this {object_name} because it has records linked to it.").format(object_name=object_name)]}, 
                        status=status.HTTP_400_BAD_REQUEST)
def unknown_exception_response(action): 
    return Response({"error":[_("Something went wrong when trying to {action}.").format(action=action)]}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#------------------------/ Organizations Views

class ContractingView(APIView):
    def get(self, request):
        user = request.user
        if user.is_superuser:
            contractings = Contracting.objects.all()
            data = ContractingSerializer(contractings, many=True).data
            return Response(data)
        return unauthorized_response
    @swagger_auto_schema(request_body=ContractingSerializer) 
    @transaction.atomic
    def post(self, request):
            user = request.user
            if user.is_superuser:
                data = request.data
                serializer = ContractingSerializer(data=data)
                if serializer.is_valid():
                    try:
                        serializer.save()
                        return Response(serializer.data)
                    except Exception as error:
                        transaction.rollback()
                        print(error)
                        return unknown_exception_response(action=_("create contracting"))
                return serializer_invalid_response(serializer.errors)
            return unauthorized_response

class SpecificContracting(APIView):
    @swagger_auto_schema(request_body=ContractingSerializer) 
    @transaction.atomic
    def put(self, request, contracting_code):
        if request.user.is_superuser:
            try:
                contracting = Contracting.objects.get(contracting_code=contracting_code)
            except Contracting.DoesNotExist:
                # I write 'The contracting' becouse in portuguese it need to be translated according to the noun gender. 
                # Ex: "A contratante", "O estabelecimento"
                return not_found_response(object_name=_('The contracting'))
            serializer = ContractingSerializer(contracting, data=request.data, partial=True)
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return unknown_exception_response(action=_('update contracting'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic
    def delete(self, request, contracting_code):
        if request.user.is_superuser:
            try:
                contracting = Contracting.objects.get(contracting_code=contracting_code)
            except Company.DoesNotExist:
                return not_found_response(object_name=_('The contracting'))
            try:
                contracting.delete()
                return success_response(detail=_("Contracting deleted."))
            except ProtectedError:
                return protected_error_response(object_name=_('contracting'))
            except Exception as error:
                transaction.rollback()
                print(error)
                return unknown_exception_response(action=_('delete contracting'))
        return unauthorized_response

class CompanyView(APIView):
    def get(self, request):
        user = request.user
        if has_permission(user, 'get_companies'):
            companies = Company.objects.filter(contracting=user.contracting)
            data = CompanySerializer(companies, many=True, context={"request": request}).data
            return Response(data)
        return unauthorized_response
    @swagger_auto_schema(request_body=CompanySerializer) 
    @transaction.atomic
    def post(self, request):
        if has_permission(request.user, 'create_company'):
            data = request.data
            serializer = CompanySerializer(data=data, context={"request": request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                return unknown_exception_response(action=_('create company'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response

class SpecificCompany(APIView):
    @transaction.atomic
    @swagger_auto_schema(request_body=CompanySerializer) 
    def put(self, request, company_compound_id):
        if has_permission(request.user, 'update_company'):
            if company_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The company'))
            try:
                company = Company.objects.get(company_compound_id=company_compound_id)
            except Company.DoesNotExist:
                return not_found_response(object_name=_('The company'))
            serializer = CompanySerializer(company, data=request.data, partial=True, context={"request": request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return unknown_exception_response(action=_('update company'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic
    def delete(self, request, company_compound_id):
        if has_permission(request.user, 'delete_company'):
            if company_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The company'))
            try:
                company = Company.objects.get(company_compound_id=company_compound_id)
            except Company.DoesNotExist:
                return not_found_response(object_name=_('The company'))
            try:
                company.delete()
                return success_response(detail=_("Company deleted"))
            except ProtectedError:
                return protected_error_response(object_name=_('company'))
            except Exception as error:
                transaction.rollback()
                print(error)
                return unknown_exception_response(action=_('delete company'))
        return unauthorized_response

class EstablishmentView(APIView):
    def get(self, request):
        user = request.user
        if has_permission(request.user, 'get_establishments'):
            establishments = Establishment.objects.filter(company__contracting=user.contracting)
            data = EstablishmentSerializer(establishments, many=True).data
            return Response(data)
        return unauthorized_response
    @swagger_auto_schema(request_body=EstablishmentSerializer) 
    @transaction.atomic
    def post(self, request):
        if has_permission(request.user, 'create_establishment'):
            data = request.data
            serializer = EstablishmentSerializer(data=data, context={"request":request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return unknown_exception_response(action=_('create establishment'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response

class SpecificEstablishment(APIView):
    @swagger_auto_schema(request_body=EstablishmentSerializer) 
    @transaction.atomic
    def put(self, request, establishment_compound_id):
        if has_permission(request.user, 'update_establishment'):
            if establishment_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The establishment'))
            try:
                establishment = Establishment.objects.get(establishment_compound_id=establishment_compound_id)
            except Establishment.DoesNotExist:
                return not_found_response(object_name=_('The establishment'))
            serializer = EstablishmentSerializer(establishment, data=request.data, partial=True, context={"request":request} )
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return unknown_exception_response(action=_('update establishment'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic
    def delete(self, request, establishment_compound_id):
        if has_permission(request.user, 'delete_establishment'):
            if establishment_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The establishment'))
            try:
                establishment = Establishment.objects.get(establishment_compound_id=establishment_compound_id)
            except Establishment.DoesNotExist:
                return not_found_response(object_name=_('The establishment'))
            try:
                establishment.delete()
                return success_response(detail=_("Establishment deleted"))
            except ProtectedError:
                return protected_error_response(object_name=_('establishment'))
            except Exception as error:
                transaction.rollback()
                print(error)
                return unknown_exception_response(action=_('delete establishment'))
        return unauthorized_response

class ClientTableView(APIView):
    def get(self, request):
        user = request.user
        if has_permission(user, 'get_client_tables'):
            client_table = ClientTable.objects.filter(contracting=user.contracting)
            data = ClientTableSerializer(client_table, many=True).data
            return Response(data)
        return unauthorized_response
    @swagger_auto_schema(request_body=ClientTableSerializer) 
    @transaction.atomic
    def post(self, request):
            if has_permission(request.user, 'create_company'):
                data = request.data
                serializer = ClientTableSerializer(data=data, context={"request":request})
                if serializer.is_valid():
                    try:
                        serializer.save()
                        return Response(serializer.data)
                    except Exception as error:
                        transaction.rollback()
                        print(error)
                        return unknown_exception_response(action=_('create client table'))
                return serializer_invalid_response(serializer.errors)
            return unauthorized_response

class SpecificClientTable(APIView):
    @transaction.atomic
    @swagger_auto_schema(request_body=ClientTableSerializer) 
    def put(self, request, client_table_compound_id):
        if has_permission(request.user, 'update_client_table'):
            if client_table_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The client table'))
            try:
                client_table = ClientTable.objects.get(client_table_compound_id=client_table_compound_id)
            except ClientTable.DoesNotExist:
                return not_found_response(object_name=_('The client table'))
            serializer = ClientTableSerializer(client_table, data=request.data, partial=True)
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return unknown_exception_response(action=_('update client table'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic
    def delete(self, request, client_table_compound_id):
        if has_permission(request.user, 'delete_client_table'):
            if client_table_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The client table'))
            try:
                client_table = ClientTable.objects.get(client_table_compound_id=client_table_compound_id)
            except ClientTable.DoesNotExist:
                return not_found_response(object_name=_('The client table'))
            try:
                client_table.delete()
                return success_response(detail=_("Client table deleted"))
            except ProtectedError:
                return protected_error_response(object_name=_('client table'))
            except Exception as error:
                transaction.rollback()
                print(error)
                return unknown_exception_response(action=_('delete client table'))
        return unauthorized_response

class ClientView(APIView):
    def get(self, request):
        user = request.user
        if has_permission(user, 'get_clients'):
            if has_role(user, 'agent'):
                clients = get_clients_by_agent(user)
                data = ClientSerializer(clients, many=True).data
                return Response(data)
            clients = Client.objects.filter(client_table__contracting=user.contracting)
            data = ClientSerializer(clients, many=True).data
            return Response(data)
        return unauthorized_response
    @swagger_auto_schema(request_body=ClientSerializer) 
    @transaction.atomic
    def post(self, request):
            user = request.user
            if has_permission(user, 'create_client'):
                request_user_is_agent_without_all_estabs = req_user_is_agent_without_all_estabs(request.user)
                serializer = ClientSerializer(data=request.data, context={"request":request,
                    "request_user_is_agent_without_all_estabs": request_user_is_agent_without_all_estabs})
                if serializer.is_valid():
                    try:
                        serializer.save()
                        return Response(serializer.data)
                    except Exception as error:
                        transaction.rollback()
                        print(error)
                        return unknown_exception_response(action=_('create client'))
                return serializer_invalid_response(serializer.errors)
            return unauthorized_response

class SpecificClient(APIView):
    @swagger_auto_schema(request_body=ClientSerializer) 
    @transaction.atomic
    def put(self, request, client_compound_id):
        user = request.user
        if has_permission(user, 'update_client'):
            # Is from the same Contracting
            if client_compound_id.split("#")[0] != user.contracting.contracting_code:
                return not_found_response(object_name=_('The client'))
            try:
                client = Client.objects.get(client_compound_id=client_compound_id)
            except Client.DoesNotExist:
                return not_found_response(object_name=_('The client'))
            # Check if agent without all estabs have access to this client
            request_user_is_agent_without_all_estabs = req_user_is_agent_without_all_estabs(request.user)
            if request_user_is_agent_without_all_estabs and not agent_has_access_to_this_client(request.user, client):
                return not_found_response(object_name=_('The client'))
            serializer = ClientSerializer(client, data=request.data, context={"request":request, 
                "request_user_is_agent_without_all_estabs": request_user_is_agent_without_all_estabs})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return unknown_exception_response(action=_('update client'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic
    def delete(self, request, client_compound_id):
        if has_permission(request.user, 'delete_client'):
            # Is from the same Contracting
            if client_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The client'))
            try:
                client = Client.objects.get(client_compound_id=client_compound_id)
            except Client.DoesNotExist:
                return not_found_response(object_name=_('The client')) 
            if req_user_is_agent_without_all_estabs(request.user) and \
                    not agent_has_access_to_this_client(request.user, client):
                return unauthorized_response
            try:
                client.delete()
                return success_response(detail=_("Client deleted"))
            except ProtectedError as er:
                return protected_error_response(object_name=_('client'))
            except Exception as error:
                transaction.rollback()
                print(error)
                return unknown_exception_response(action=_('delete client'))
        return unauthorized_response

#------------------------/ Auth Views

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request):
        return success_response(detail=_( "csrf cookie set"))
# If the user has status != 1, it will be considered disabled and the user can't log in.
class Login(APIView):
    permission_classes = (permissions.AllowAny,)
    @swagger_auto_schema(request_body=SwaggerLoginSerializer) 
    def post(self, request):
        if request.user.is_authenticated:
            return success_response(detail=_("User is already authenticated"))
        serializer = SwaggerLoginSerializer(data=request.data)
        if serializer.is_valid():
            user_code = serializer.validated_data["contracting_code"] + "#" + serializer.validated_data["username" ]
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
            return success_response(detail=_( 'Logged out'))
        except Exception as error:
            print(error)
            unknown_exception_response(action=_('log out'))

#-------------------------------------------/ Users Views / -------------------------------------

class OwnProfileView(APIView):
    @transaction.atomic
    def get(self, request):
        try:
            data = OwnProfileSerializer(request.user).data
            return Response(data)
        except Exception as error:
            print(error)
            return unknown_exception_response(action=_('get request user profile'))
    @swagger_auto_schema(request_body=OwnProfileSerializer) 
    @transaction.atomic
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True, context={"request": request, "view": "update own profile"})
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data)
            except Exception as error:
                print(error)
                return unknown_exception_response(action=_('update request user profile'))
        return serializer_invalid_response(serializer.errors)

class ERPUserView(APIView):
    def get(self, request):
        if request.user.is_superuser:
            erp_users = User.objects.filter(Q(groups__name='erp'))
            return Response(ERPUserSerializer(erp_users, many=True).data)
        return unauthorized_response
    @swagger_auto_schema(request_body=ERPUserSerializer) 
    @transaction.atomic
    def post(self, request):
        if request.user.is_superuser:
            serializer = ERPUserSerializer(data=request.data, context={"request":request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return unknown_exception_response(action=_('create erp user'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response

class SpecificERPUser(APIView):
    @swagger_auto_schema(request_body=ERPUserSerializer) 
    @transaction.atomic
    def put(self, request, contracting_code, username):
        if request.user.is_superuser:
            user_code = contracting_code + "#" + username
            try: 
                user = User.objects.get(user_code=user_code, groups__name='erp')
            except User.DoesNotExist:
                return not_found_response(object_name='The erp user')
            serializer = ERPUserSerializer(user, data=request.data, partial=True,
                    context={"request": request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    #  raise error
                    return unknown_exception_response(action=_('update erp user'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic  
    def delete(self, request, contracting_code, username):
        if request.user.is_superuser:
            user_code = contracting_code + "#" + username
            try:
                user = User.objects.get(user_code=user_code, groups__name='erp')
            except User.DoesNotExist:
                return not_found_response(object_name=_('The erp user'))
            try:
                user.delete()
                return success_response(detail=_("ERP user deleted successfully."))
            except ProtectedError as er:
                return protected_error_response(object_name=_('erp user'))
            except Exception as error:
                transaction.rollback()
                print(error)
                return unknown_exception_response(action=_('delete erp user'))
        return unauthorized_response

class AdminAgentView(APIView):
    def get(self, request):
        if has_permission(request.user, 'get_admin_agents'):
            user = request.user
            agents = User.objects.filter(Q(contracting=user.contracting), Q(groups__name='admin_agent'))
            return Response(AdminAgentSerializer(agents, many=True).data)
        return unauthorized_response
    @swagger_auto_schema(request_body=AdminAgentSerializer) 
    @transaction.atomic
    def post(self, request):
        if has_permission(request.user, 'create_admin_agent'):
            serializer = AdminAgentSerializer(data=request.data, context={"request":request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return unknown_exception_response(action=_('create admin agent'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response

class SpecificAdminAgent(APIView):
    @swagger_auto_schema(request_body=AdminAgentSerializer) 
    @transaction.atomic
    def put(self, request, contracting_code, username):
        if has_permission(request.user, 'update_admin_agent'):
            if contracting_code != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The admin agent'))
            user_code = contracting_code + "#" + username
            try: 
                user = User.objects.get(user_code=user_code, groups__name='admin_agent')
            except User.DoesNotExist:
                return not_found_response(object_name=_('The admin agent'))
            serializer = AdminAgentSerializer(user, data=request.data, partial=True,
                    context={"request": request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    #  raise error
                    return unknown_exception_response(action=_('update admin agent'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic  
    def delete(self, request, contracting_code, username):
        if has_permission(request.user, 'delete_admin_agent'):
            # Contracting Ownership
            if contracting_code != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The admin agent'))
            user_code = contracting_code + "#" + username
            try:
                user = User.objects.get(user_code=user_code, groups__name='admin_agent')
            except User.DoesNotExist:
                return not_found_response(object_name=_('The admin agent'))
            try:
                user.delete()
                return success_response(detail=_("Admin agent deleted successfully"))
            except ProtectedError as er:
                return protected_error_response(object_name=_('admin agent'))
            except Exception as error:
                transaction.rollback()
                print(error)
                return unknown_exception_response(action=_('delete admin agent'))
        return unauthorized_response

class AgentView(APIView):
    def get(self, request):
        if has_permission(request.user, 'get_agents'):
            user = request.user
            agents = User.objects.filter(Q(contracting=user.contracting), Q(groups__name='agent'))
            return Response(AgentSerializer(agents, many=True).data)
        return unauthorized_response
    @swagger_auto_schema(request_body=AgentSerializer) 
    @transaction.atomic
    def post(self, request):
        if has_permission(request.user, 'create_agent'):
            serializer = AgentSerializer(data=request.data, context={"request":request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return unknown_exception_response(action=_('create agent'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response

class SpecificAgent(APIView):
    @swagger_auto_schema(request_body=AgentSerializer) 
    @transaction.atomic
    def put(self, request, contracting_code, username):
        if has_permission(request.user, 'update_agent'):
            if contracting_code != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The agent'))
            user_code = contracting_code + "#" + username
            try: 
                user = User.objects.get(user_code=user_code, groups__name='agent')
            except User.DoesNotExist:
                return not_found_response(object_name=_('The agent'))
            serializer = AgentSerializer(user, data=request.data, partial=True,
                    context={"request": request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    #  raise error
                    return unknown_exception_response(action=_('update agent'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic  
    def delete(self, request, contracting_code, username):
        if has_permission(request.user, 'delete_agent'):
            # Contracting Ownership
            if contracting_code != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The agent'))
            user_code = contracting_code + "#" + username
            try:
                user = User.objects.get(user_code=user_code, groups__name='agent')
            except User.DoesNotExist:
                return not_found_response(object_name=_('The agent'))
            try:
                user.delete()
                return success_response(detail=_( "Agent deleted successfully"))
            except ProtectedError as er:
                return protected_error_response(object_name=_('agent'))
            except Exception as error:
                transaction.rollback()
                print(error)
                return unknown_exception_response(action=_('delete agent'))
        return unauthorized_response

class ClientUserView(APIView):
    def get(self, request):
        if has_permission(request.user, 'get_client_users'):
            user = request.user
            if has_role(user, 'agent'):
                client_users = get_all_client_users_by_agent(user)
                return Response(ClientUserSerializer(client_users, many=True).data)
            client_users = User.objects.filter(Q(contracting=user.contracting), Q(groups__name='client_user'))
            return Response(ClientUserSerializer(client_users, many=True).data)
        return unauthorized_response
    @swagger_auto_schema(request_body=ClientUserSerializer) 
    @transaction.atomic
    def post(self, request):
        if has_permission(request.user, 'create_client_user'):
                request_user_is_agent_without_all_estabs = req_user_is_agent_without_all_estabs(request.user)
                serializer = ClientUserSerializer(data=request.data, context={"request":request,
                    "request_user_is_agent_without_all_estabs": request_user_is_agent_without_all_estabs})
                #  if serializer.is_valid(raise_exception=True):
                if serializer.is_valid():
                    try:
                        serializer.save()
                        return Response(serializer.data)
                    except Exception as error:
                        transaction.rollback()
                        print(error)
                        return unknown_exception_response(action=_('create client user'))
                return serializer_invalid_response(serializer.errors)
        return unauthorized_response

class SpecificClientUser(APIView):
    @swagger_auto_schema(request_body=ClientUserSerializer) 
    @transaction.atomic
    def put(self, request, contracting_code, username):
        if has_permission(request.user, 'update_client_user'):
            if contracting_code != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The client user'))
            user_code = contracting_code + "#" + username
            try:
                user = User.objects.get(user_code=user_code, groups__name='client_user')
            except User.DoesNotExist:
                return not_found_response(object_name=_('The client user'))
            request_user_is_agent_without_all_estabs = req_user_is_agent_without_all_estabs(request.user)
            if request_user_is_agent_without_all_estabs and not agent_has_access_to_this_client_user(request.user, user):
                return not_found_response(object_name=_('The client user'))
            serializer = ClientUserSerializer(user, data=request.data, partial=True, context={"request": request,
                "request_user_is_agent_without_all_estabs": request_user_is_agent_without_all_estabs})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    #  raise error
                    return unknown_exception_response(action=_('update client user'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic  
    def delete(self, request, contracting_code, username):
        if has_permission(request.user, 'delete_client_user'):
            if contracting_code != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The client user'))
            user_code = contracting_code + "#" + username
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
                return success_response(detail=_("Client user deleted successfully"))
            except ProtectedError as er:
                return protected_error_response(object_name=_('client user'))
            except Exception as error:
                transaction.rollback()
                print(error)
                return unknown_exception_response(action=_('delete client user'))
        return unauthorized_response

class UpdateUserPassword(APIView):
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
            return success_response(detail=_( "Password updated"))
        return error_response(detail=_("passwords don't match"), status=status.HTTP_400_BAD_REQUEST )
