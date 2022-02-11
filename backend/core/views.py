from django.db.models.deletion import ProtectedError
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie, requires_csrf_token
from rest_framework import status, viewsets, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.views import APIView
from core.facade import get_all_client_users_by_agent, get_all_users_by_admin_agent, get_all_users_by_erp, get_clients_by_agent
from core.serializers import ClientSerializer, ClientTableSerializer, CompanySerializer, ContractingSerializer, EstablishmentSerializer, UserSerializer, SwaggerLoginSerializer, SwaggerProfilePasswordSerializer
#  from rest_framework.authtoken.models import Token
from core.models import Client, ClientTable, Company, Contracting, Establishment, User
from rolepermissions.checkers import has_permission, has_role
from rolepermissions.mixins import HasRoleMixin, HasPermissionsMixin
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from core.validators import agent_has_access_to_this_client, has_any_permission_to_create_user, has_any_permission_to_delete_user, has_any_permission_to_update_user, has_permission_to_delete_user

from orders.models import PriceTable

from django.db.models import Q, Value, Prefetch
#  from drf_yasg import openapi

#  @api_view(['POST', 'GET', 'DELETE', 'PATCH', 'PUT'])
#  @permission_classes([AllowAny])
#  def apiNotFound(request):
    #  return Response({"status":"api not found"}, status=status.HTTP_404_NOT_FOUND)

#------------------------/ Auth Views

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = (permissions.AllowAny,)
    def get(self, request, format=None):
        return Response({"sucess": "csrf cookie set"})

class Login(APIView):
    permission_classes = (permissions.AllowAny,)
    @swagger_auto_schema(request_body=SwaggerLoginSerializer) 
    def post(self, request, format=None):
        if request.user.is_authenticated:
            return Response({"status": "already_authenticated."})
        serializer = SwaggerLoginSerializer(data=request.data)
        if serializer.is_valid():
            user_code = serializer.validated_data["username" ] + "#" + serializer.validated_data["contracting_code"]
            user = authenticate(username=user_code, password=serializer.validated_data["password"], request=request)
            if user is not None:
                login(request, user)
                return Response(UserSerializer(user).data)
            else:
                return Response({"status": "login_failed"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#  @method_decorator(csrf_protect, name='dispatch')
class Logout(APIView):
    def post(self, request, format=None):
        try:
            logout(request)
            return Response({'success': 'Loggout out'})
        except Exception as error:
            print(error)
            return Response({'error': 'Something went wrong when logging out.'})

@method_decorator( ensure_csrf_cookie, name='dispatch')
class CheckAuthenticated(APIView):
    def get(self, request, format=None):
        try:
            data = UserSerializer(request.user).data
            return Response(data)
        except Exception as error:
            print(error)
            return Response({'status': 'error', 'description': 'Something went wrong when checking authentication status.'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#------------------------/ Organizations Views

class ContractingView(APIView):
    def get(self, request):
        user = request.user
        if user.is_superuser:
            contractings = Contracting.objects.all()
            data = ContractingSerializer(contractings, many=True).data
            return Response(data)
        return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)
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
                        return Response({"error": "Something went wrong when trying to create contracting."},
                                status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class SpecificContracting(APIView):
    #  def patch(self, request):
        #  return Response({'success': "ahdflasjdflajdf"})
    @swagger_auto_schema(request_body=ContractingSerializer) 
    @transaction.atomic
    def put(self, request, contracting_code):
        if request.user.is_superuser:
            try:
                contracting = Contracting.objects.get(contracting_code=contracting_code)
            except Contracting.DoesNotExist:
                return Response({"error": "'contracting_code' doesn't match with any Contracting."},
                        status=status.HTTP_400_BAD_REQUEST)
            serializer = ContractingSerializer(contracting, data=request.data, partial=True)
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return Response({"error": "Something went wrong when trying to update contracting."},
                            status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)
    @transaction.atomic
    def delete(self, request, contracting_code):
        if request.user.is_superuser:
            try:
                contracting = Contracting.objects.get(contracting_code=contracting_code)
            except Company.DoesNotExist:
                return Response({"error": "'contracting_code' doesn't match with any contracting."},
                        status=status.HTTP_400_BAD_REQUEST)
            try:
                contracting.delete()
                return Response("Contracting deleted.")
            except ProtectedError:
                return Response({"error": "you cannot delete this contracting because it has records linked to it."}, 
                        status=status.HTTP_400_BAD_REQUEST)
            except Exception as error:
                transaction.rollback()
                print(error)
                return Response({"error": "Something went wrong when trying to delete contracting."},
                        status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)

class CompanyView(APIView):
    def get(self, request):
        user = request.user
        if has_permission(user, 'get_companies'):
            companies = Company.objects.filter(contracting=user.contracting)
            data = CompanySerializer(companies, many=True, context={"request": request}).data
            return Response(data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
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
                        return Response({"error": "Something went wrong when trying to create company."},
                                status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)

class SpecificCompany(APIView):
    @transaction.atomic
    @swagger_auto_schema(request_body=CompanySerializer) 
    def put(self, request, company_compound_id):
        if has_permission(request.user, 'update_company'):
            if company_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return Response(status=status.HTTP_404_NOT_FOUND) 
            try:
                company = Company.objects.get(company_compound_id=company_compound_id)
            except Company.DoesNotExist:
                return Response({"error": "'company_compound_id' doesn't match with any company."},status=status.HTTP_400_BAD_REQUEST)
            serializer = CompanySerializer(company, data=request.data, partial=True, context={"request": request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return Response({"error": "Something went wrong when trying to update company."},
                            status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)
    @transaction.atomic
    def delete(self, request, company_compound_id):
        if has_permission(request.user, 'delete_company'):
            if company_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return Response(status=status.HTTP_404_NOT_FOUND) 
            try:
                company = Company.objects.get(company_compound_id=company_compound_id)
            except Company.DoesNotExist:
                return Response({"error": "'company_compound_id' doesn't match with any company."},status=status.HTTP_400_BAD_REQUEST)
            try:
                company.delete()
            except ProtectedError:
                return Response({"error": "you cannot delete this company because it has records linked to it."}, 
                        status=status.HTTP_400_BAD_REQUEST)
            except Exception as error:
                transaction.rollback()
                print(error)
                return Response({"error": "Something went wrong when trying to delete company."},
                        status=status.HTTP_400_BAD_REQUEST)
            return Response("Company deleted.")
        return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)

class EstablishmentView(APIView):
    def get(self, request):
        user = request.user
        if has_permission(request.user, 'get_establishments'):
            establishments = Establishment.objects.filter(company__contracting=user.contracting)
            data = EstablishmentSerializer(establishments, many=True).data
            return Response(data)
        return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)
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
                    return Response({"error": "Something went wrong when trying to create establishment."},
                            status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

class SpecificEstablishment(APIView):
    @swagger_auto_schema(request_body=EstablishmentSerializer) 
    def put(self, request, establishment_compound_id):
        if has_permission(request.user, 'update_establishment'):
            if establishment_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return Response(status=status.HTTP_404_NOT_FOUND) 
            try:
                establishment = Establishment.objects.get(establishment_compound_id=establishment_compound_id)
            except Establishment.DoesNotExist:
                return Response({"error": "'establishment_compound_id' doesn't match with any establishment."},
                        status=status.HTTP_400_BAD_REQUEST)
            serializer = EstablishmentSerializer(establishment, data=request.data, partial=True, context={"request":request} )
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return Response({"error": "Something went wrong when trying to update establishment."},
                            status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)
    def delete(self, request, establishment_compound_id):
        if has_permission(request.user, 'delete_establishment'):
            if establishment_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return Response(status=status.HTTP_404_NOT_FOUND) 
            try:
                establishment = Establishment.objects.get(establishment_compound_id=establishment_compound_id)
            except Establishment.DoesNotExist:
                return Response({"error": "'establishment_compound_id' doesn't match with any establishment."},
                        status=status.HTTP_400_BAD_REQUEST)
            try:
                establishment.delete()
            except ProtectedError:
                return Response({"error": "you cannot delete this establishment because it has records linked to it."}, 
                        status=status.HTTP_400_BAD_REQUEST)
            except Exception as error:
                transaction.rollback()
                print(error)
                return Response({"error": "Something went wrong when trying to delete establishment."},
                        status=status.HTTP_400_BAD_REQUEST)
            return Response("Establishment deleted.")
        return Response({'error': "You don't have permission to access this resource."},
                status=status.HTTP_401_UNAUTHORIZED)

class ClientTableView(APIView):
    def get(self, request):
        user = request.user
        if has_permission(user, 'get_client_tables'):
            client_table = ClientTable.objects.filter(contracting=user.contracting)
            data = ClientTableSerializer(client_table, many=True).data
            return Response(data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
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
                        return Response({"error": "Something went wrong when trying to create client table."},
                                status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)

class SpecificClientTable(APIView):
    @transaction.atomic
    @swagger_auto_schema(request_body=ClientTableSerializer) 
    def put(self, request, client_table_compound_id):
        if has_permission(request.user, 'update_client_table'):
            if client_table_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return Response(status=status.HTTP_404_NOT_FOUND) 
            try:
                client_table = ClientTable.objects.get(client_table_compound_id=client_table_compound_id)
            except ClientTable.DoesNotExist:
                return Response({"error": "'client_table_compound_id' doesn't match with any client table."},
                        status=status.HTTP_400_BAD_REQUEST)
            serializer = ClientTableSerializer(client_table, data=request.data, partial=True)
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return Response({"error": "Something went wrong when trying to update client table."},
                            status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)
    @transaction.atomic
    def delete(self, request, client_table_compound_id):
        if has_permission(request.user, 'delete_client_table'):
            if client_table_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return Response(status=status.HTTP_404_NOT_FOUND) 
            try:
                client_table = ClientTable.objects.get(client_table_compound_id=client_table_compound_id)
            except ClientTable.DoesNotExist:
                return Response({"error": "'client_table_compound_id' doesn't match with any client table."},
                        status=status.HTTP_400_BAD_REQUEST)
            try:
                client_table.delete()
                return Response("Client table deleted.")
            except ProtectedError:
                return Response({"error": "you cannot delete this client table because it has records linked to it."}, 
                        status=status.HTTP_400_BAD_REQUEST)
            except Exception as error:
                transaction.rollback()
                print(error)
                return Response({"error": "Something went wrong when trying to delete client table."},
                        status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)

class ClientView(APIView):
    def get(self, request):
        user = request.user
        if has_role(request.user, ["erp", "admin_agent"]) or has_permission(user, 'access_all_establishments'):
            clients = Client.objects.filter(client_table__contracting=user.contracting)
            data = ClientSerializer(clients, many=True).data
            return Response(data)
        if has_permission(user, 'get_clients'):
            clients = get_clients_by_agent(user)
            data = ClientSerializer(clients, many=True).data
            return Response(data)
        return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)
    @swagger_auto_schema(request_body=ClientSerializer) 
    @transaction.atomic
    def post(self, request):
            user = request.user
            if has_permission(user, 'create_client'):
                serializer = ClientSerializer(data=request.data, context={"request":request, "method": "post"})
                if serializer.is_valid():
                    try:
                        serializer.save()
                        return Response(serializer.data)
                    except Exception as error:
                        transaction.rollback()
                        print(error)
                        return Response({"error": "Something went wrong when trying to create contracting."},
                                status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class SpecificClient(APIView):
    @swagger_auto_schema(request_body=ClientSerializer) 
    @transaction.atomic
    def put(self, request, client_compound_id):
        user = request.user
        if has_permission(user, 'update_client'):
            # Is from the same Contracting
            if client_compound_id.split("#")[0] != user.contracting.contracting_code:
                return Response(status=status.HTTP_404_NOT_FOUND) 
            try:
                client = Client.objects.get(client_compound_id=client_compound_id)
            except Client.DoesNotExist:
                return Response({"error": "'client_compound_id' doesn't match with any client."},
                        status=status.HTTP_400_BAD_REQUEST)
            serializer = ClientSerializer(client, data=request.data, partial=True, context={"request":request, "method": "put"})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return Response({"error": "Something went wrong when trying to update client."},
                            status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    @transaction.atomic
    def delete(self, request, client_compound_id):
        if has_permission(request.user, 'delete_client'):
            # Is from the same Contracting
            if client_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return Response(status=status.HTTP_404_NOT_FOUND) 
            try:
                client = Client.objects.get(client_compound_id=client_compound_id)
            except Client.DoesNotExist:
                return Response({"error": "'client_compound_id' doesn't match with any client."},
                        status=status.HTTP_400_BAD_REQUEST)
            if has_role(request.user, 'agent') and not has_permission(request.user, 'access_all_establishments') and \
                    not agent_has_access_to_this_client(request.user, client):
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            try:
                client.delete()
                return Response("Client deleted.")
            except ProtectedError as er:
                print('>>>>>>>>>>>>>>>>:', er)
                return Response({"error": "you cannot delete this client because it has records linked to it."}, 
                        status=status.HTTP_400_BAD_REQUEST)
            except Exception as error:
                transaction.rollback()
                print(error)
                return Response({"error": "Something went wrong when trying to delete client."},
                        status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': "You don't have permission to access this resource."}, status=status.HTTP_401_UNAUTHORIZED)


#------------------------/ Users Views

class UserView(APIView, HasRoleMixin, HasPermissionsMixin):
    allowed_roles = ['erp', 'agent', 'admin_agent']
    def get(self, request):
        user = request.user
        if user.is_superuser:
            users = User.objects.all()
            data = UserSerializer(users, many=True).data
            return Response(data)
        if has_role(request.user, "erp"):
            users = get_all_users_by_erp(user)
            data = UserSerializer(users, many=True).data
            return Response(data)
        if has_role(request.user, "admin_agent"):
            users = get_all_users_by_admin_agent(user)
            data = UserSerializer(users, many=True).data
            return Response(data)
        if has_permission(user, 'get_client_users'):
            users = get_all_client_users_by_agent(user)
            data = UserSerializer(users, many=True).data
            return Response(data)
        return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)
    @swagger_auto_schema(request_body=UserSerializer) 
    @transaction.atomic
    def post(self, request):
        if has_any_permission_to_create_user(request.user):
                data = request.data
                serializer = UserSerializer(data=data, context={"request":request, "method": "post"})
                #  if serializer.is_valid(raise_exception=True):
                if serializer.is_valid():
                    try:
                        serializer.save()
                        return Response(serializer.data)
                    except Exception as error:
                        transaction.rollback()
                        print(error)
                        return Response({"error": "Something went wrong when trying to create user."},
                                status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    @swagger_auto_schema(request_body=UserSerializer) 
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True, context={"request": request,
            "method": "put", "view": "update own profile"})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SpecificUser(APIView):
    @swagger_auto_schema(request_body=UserSerializer) 
    def put(self, request, username, contracting_code):
        if has_any_permission_to_update_user(request.user):
            if contracting_code != request.user.contracting.contracting_code:
                return Response(status=status.HTTP_404_NOT_FOUND) 
            try: 
                user = User.objects.get(username=username,contracting__contracting_code=contracting_code)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)
            serializer = UserSerializer(user, data=request.data, partial=True,
                    context={"request": request,"method": "put", "view": "update user"})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    #  raise error
                    return Response({"error": "Something went wrong when trying to update user."},
                            status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    @transaction.atomic  
    def delete(self, request, username, contracting_code):
        #  if has_any_permission_to_delete_user(request.user):
            if contracting_code != request.user.contracting.contracting_code:
                return Response(status=status.HTTP_404_NOT_FOUND) 
            user_code = username + "#" + contracting_code
            try:
                user = User.objects.get(user_code=user_code)
            except User.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND) 
            if has_permission_to_delete_user(request.user, user):
                try:
                    user.delete()
                    return Response({"success": "User deleted successfully."})
                except ProtectedError as er:
                    print('>>>>: ', er)
                    return Response({"error": "you cannot delete this user because it has records linked to it."}, 
                            status=status.HTTP_400_BAD_REQUEST)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return Response({"error": "Something went wrong when trying to delete user."},
                            status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': "You don't have permission to delete this user."},
                        status=status.HTTP_401_UNAUTHORIZED)
        #  return Response(status=status.HTTP_401_UNAUTHORIZED)

class UpdateUserPassword(APIView):
    @swagger_auto_schema(request_body=SwaggerProfilePasswordSerializer) 
    def put(self, request):
        user = request.user
        data = request.data
        if not data.get('password'):
            return Response({"status": "Password field not sent."}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get('current_password'):
            return Response({"status": "Current Password field not sent."},status=status.HTTP_400_BAD_REQUEST)
        if user.check_password(data.get('current_password')):
            user.set_password(data['password'])
            user.save()
            return Response({"status": "Password updated"})
        return Response({"status": "passwords don't match"},status=status.HTTP_400_BAD_REQUEST)
