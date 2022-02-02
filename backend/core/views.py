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
from core.serializers import CompanySerializer, ContractingSerializer, EstablishmentSerializer, UserSerializer, SwaggerLoginSerializer, SwaggerProfilePasswordSerializer
#  from rest_framework.authtoken.models import Token
from core.models import Company, Contracting, Establishment, User
from rolepermissions.checkers import has_permission, has_role
from rolepermissions.mixins import HasRoleMixin, HasPermissionsMixin
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from core.validators import has_any_permission_to_create_user

from orders.models import PriceTable

from django.db.models import Q, Value, Prefetch
#  from drf_yasg import openapi

#  @api_view(['POST', 'GET', 'DELETE', 'PATCH', 'PUT'])
#  @permission_classes([AllowAny])
#  def apiNotFound(request):
    #  return Response({"status":"api not found"}, status=status.HTTP_404_NOT_FOUND)

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
                serializer = ContractingSerializer(data=data, context={"request_user":request.user})
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
            serializer = ContractingSerializer(contracting, data=request.data)
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
            data = CompanySerializer(companies, many=True).data
            return Response(data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    @swagger_auto_schema(request_body=CompanySerializer) 
    @transaction.atomic
    def post(self, request):
            if has_permission(request.user, 'create_company'):
                data = request.data
                serializer = CompanySerializer(data=data, context={"request_user":request.user})
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
    def put(self, request, company_id):
        if has_permission(request.user, 'update_company'):
            try:
                company = Company.objects.get(company_id=company_id)
            except Company.DoesNotExist:
                return Response({"error": "'company_id' doesn't match with any company."},status=status.HTTP_400_BAD_REQUEST)
            serializer = CompanySerializer(company, data=request.data)
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
    def delete(self, request, company_id):
        if has_permission(request.user, 'delete_company'):
            try:
                company = Company.objects.get(company_id=company_id)
            except Company.DoesNotExist:
                return Response({"error": "'company_id' doesn't match with any company."},status=status.HTTP_400_BAD_REQUEST)
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
            serializer = EstablishmentSerializer(data=data, context={"request_user":request.user})
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
    def put(self, request, establishment_id):
        if has_permission(request.user, 'update_establishment'):
            try:
                establishment = Establishment.objects.get(establishment_id=establishment_id)
            except Establishment.DoesNotExist:
                return Response({"error": "'establishment_id' doesn't match with any establishment."},
                        status=status.HTTP_400_BAD_REQUEST)
            serializer = EstablishmentSerializer(establishment, data=request.data)
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
    def delete(self, request, establishment_id):
        if has_permission(request.user, 'delete_establishment'):
            try:
                establishment = Establishment.objects.get(establishment_id=establishment_id)
            except Establishment.DoesNotExist:
                return Response({"error": "'establishment_id' doesn't match with any establishment."},
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

class ClientView(APIView):
    def get(self, request):
        user = request.user
        #  if user.is_superuser:
        establishments = Establishment.objects.filter(company__contracting=user.contracting)
        data = EstablishmentSerializer(establishments, many=True).data
        return Response(data)
        #  return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)
    #  @swagger_auto_schema(request_body=ClientSerializer) 
    #  @transaction.atomic
    #  def post(self, request):
        #  try:
            #  user = request.user
            #  if user.is_superuser:
                #  data = request.data
                #  serializer = ClientSerializer(data=data, context={"request_user":request.user})
                #  if serializer.is_valid():
                    #  serializer.save()
                    #  return Response(serializer.data)
                #  return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            #  return Response(status=status.HTTP_401_UNAUTHORIZED)
        #  except Exception as error:
            #  transaction.rollback()
            #  print(error)
            #  return Response({"error": "Something went wrong when trying to create contracting."}, status=status.HTTP_400_BAD_REQUEST)

class SpecificClient(APIView):
    def put(self, request, company_id):
        price_table = request.data.get("price_table")
        if not company_code:
            return Response({"status": "Company_code is missing"},status=status.HTTP_400_BAD_REQUEST)
        if not has_role(request.user, 'admin') and not has_role(request.user, 'admin_agent'):
            return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)
        if price_table != "None":
            try:
                price_table = PriceTable.objects.get(table_code=price_table)
                company = Company.objects.get(company_code=company_code)
                if has_role(request.user, 'admin') or (has_role(request.user, 'admin_agent') and 
                        request.user.company == company.contracting_company):
                    if price_table.contracting_company == request.user.company:
                        company.price_table = price_table
                        company.save()
                        return Response("Company updated.")
                    return Response({"error": "Invalid price_table."},status=status.HTTP_400_BAD_REQUEST)
                return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)
            except PriceTable.DoesNotExist:
                return Response({"error": "'price_table' doesn't match with any price table."},status=status.HTTP_400_BAD_REQUEST)
            except Company.DoesNotExist:
                return Response({"error": "'company_code' doesn't match with any company."},status=status.HTTP_400_BAD_REQUEST)
        #OBS: this is if i want to update more info besides table_code
        #  company = Company.objects.get(company_code=company_code)
        #  serializer = CompanySerializer(company, data=request.data, partial=True) # (partial=True)we dont want to update every field
        #  if serializer.is_valid(raise_exception=True):  # ????????????????
            #  serializer.save()
            #  return Response(serializer.data)
        #  else:
            #  return Response({"status": "Bad request."},status=status.HTTP_400_BAD_REQUEST)

class UserView(APIView, HasRoleMixin, HasPermissionsMixin):
    allowed_roles = ['erp', 'agent', 'admin_agent']
    def get(self, request):
        user = request.user
        if has_permission(user, 'get_all_users'):
            users = User.objects.all().filter(is_superuser=False)
            data = UserSerializer(users, many=True).data
            return Response(data)
        if has_permission(user, 'get_agents') and has_permission(user, 'get_clients'):
            users = User.objects.all().filter(Q(is_superuser=False), ~Q(username=user.username), \
                    Q(company__contracting_company=request.user.company) | Q(company=request.user.company))
            data = UserSerializer(users, many=True).data
            return Response(data)
        if has_permission(user, 'get_clients'):
            users = User.objects.all().filter(is_superuser=False, company__contracting_company=request.user.company)
            data = UserSerializer(users, many=True).data
            return Response(data)
        return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)
    @swagger_auto_schema(request_body=UserSerializer) 
    @transaction.atomic
    def post(self, request):
        if has_any_permission_to_create_user(request.user):
            try:
                data = request.data
                serializer = UserSerializer(data=data, context={"request_user":request.user, "method": "post"})
                #  if serializer.is_valid(raise_exception=True):
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Exception as error:
                transaction.rollback()
                print(error)
                return Response({"error": "Something went wrong when trying to create user."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    @swagger_auto_schema(request_body=UserSerializer) 
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True, context={"method": "put"})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            #  return Response({"status": "Bad request."},status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SpecificUser(APIView):
    @transaction.atomic  
    def delete(self, request, username, company_code):
        if has_role(request.user, "admin") or has_role(request.user, "admin_agent") \
        or has_permission(request.user, 'delete_client'):
            try: 
                user_code = username + "#" + company_code
                user = User.objects.get(user_code=user_code)
                if has_role(request.user, 'admin') or (has_role(request.user, 'admin_agent') and \
                (request.user.company == user.company.contracting_company or request.user.company == user.company)) or \
                (has_permission(request.user, 'delete_client') and (request.user.company == user.company.contracting_company) and \
                (has_role(user, "client"))):
                    # agent and admin_agent can't delete user from another contracting_company
                    if user.is_superuser or has_role(user, 'admin'):
                        return Response({'error': "You don't have permission to delete this user."},status=status.HTTP_401_UNAUTHORIZED)
                    user.delete()
                    return Response({"success": "User deleted successfully."})
                return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
              return Response(status=status.HTTP_404_NOT_FOUND) 
            except Exception as error:
                print(error)
                transaction.rollback()
        return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)
    #  @swagger_auto_schema(request_body=UserSerializer) 
    #  def put(self, request, username, company_code):
        #  user = request.user
        #  serializer = UserSerializer(user, data=request.data, partial=True) # (partial=True)we dont want to update every field
        #  if serializer.is_valid(raise_exception=True):  # ????????????????
            #  serializer.save()
            #  return Response(serializer.data)
        #  else:
            #  return Response({"status": "Bad request."},status=status.HTTP_400_BAD_REQUEST)

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
