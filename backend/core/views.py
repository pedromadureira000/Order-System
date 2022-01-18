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
from core.serializers import CompanySerializer, UserSerializer, SwaggerLoginSerializer, SwaggerProfilePasswordSerializer
#  from rest_framework.authtoken.models import Token
from core.models import Company, User
from rolepermissions.checkers import has_permission, has_role
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema

from orders.models import PriceTable

from django.db.models import Q, Value, Prefetch
#  from drf_yasg import openapi

#  @api_view(['POST', 'GET', 'DELETE', 'HEAD', 'PUT', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH', 'COPY', 'LINK', 'UNLINK', 'PURGE', 'LOCK','UNLOCK','PROPFIND', 'VIEW'])
#  @permission_classes([AllowAny])
#  def apiNotFound(request):
    #  return Response({"status":"api not found"}, status=status.HTTP_404_NOT_FOUND)


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
            user_code = serializer.validated_data["username" ] + "#" + serializer.validated_data["company_code"]
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


class UserView(APIView):
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
        try:
            if  has_permission(request.user, 'create_admin_agent') or has_permission(request.user, 'create_agent') \
            or has_permission(request.user, 'create_client'):
                data = request.data
                serializer = UserSerializer(data=data, context={"request_user":request.user, "method": "post"})
                #  if serializer.is_valid(raise_exception=True):
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Exception as error:
            transaction.rollback()
            print(error)
            return Response({"error": "Something get wrong when trying to create user."}, status=status.HTTP_400_BAD_REQUEST)

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
        if has_role(request.user, "admin") or has_role(request.user, "admin_agent") or has_permission(request.user, 'delete_client'):
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


class CompanyView(APIView):
    def get(self, request):
        user = request.user
        if has_permission(user, 'get_companies'):
            companies = Company.objects.all()
            data = CompanySerializer(companies, many=True).data
            return Response(data)

        if has_permission(user, "get_client_companies"):
            companies = Company.objects.filter(~Q(company_type="C"), contracting_company=request.user.company).all()
            data = CompanySerializer(companies, many=True).data
            return Response(data)


        return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(request_body=CompanySerializer) 
    @transaction.atomic
    def post(self, request):
        try:
            if has_role(request.user, 'admin') or has_role(request.user, 'admin_agent'):
                data = request.data
                serializer = CompanySerializer(data=data, context={"request_user":request.user})
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Exception as error:
            transaction.rollback()
            print(error)
            return Response({"error": "Something get wrong when trying to create company."}, status=status.HTTP_400_BAD_REQUEST)


class SpecificCompany(APIView):
    @swagger_auto_schema(request_body=CompanySerializer) 
    def put(self, request, company_code):
        price_table = request.data.get("price_table")
        if not company_code:
            return Response({"status": "Company_code is missing"},status=status.HTTP_400_BAD_REQUEST)
        if not has_role(request.user, 'admin') or not has_role(request.user, 'admin_agent'):
            return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)
        if price_table != "None":
            try:
                price_table = PriceTable.objects.get(table_code=price_table)
                company = Company.objects.get(company_code=company_code)
                if has_role(request.user, 'admin') or (has_role(request.user, 'admin_agent') and 
                        request.user.company == company.contracting_company):
                    if price_table.contracting_company != request.user.company:
                        company.price_table = price_table
                        company.save()
                        return Response("Company updated.")
                    return Response({"error": "Invalid price_table."},status=status.HTTP_400_BAD_REQUEST)
                return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)
            except PriceTable.DoesNotExist:
                return Response({"error": "'price_table' doesn't match with any price table."},status=status.HTTP_400_BAD_REQUEST)
            except Company.DoesNotExist:
                return Response({"error": "'company_code' doesn't match with any company."},status=status.HTTP_400_BAD_REQUEST)

        company = Company.objects.get(company_code=company_code)
        company.price_table = None
        company.save()
        return Response("Company updated.")

        #OBS: this is if i want to update more info besides table_code
        #  company = Company.objects.get(company_code=company_code)
        #  serializer = CompanySerializer(company, data=request.data, partial=True) # (partial=True)we dont want to update every field
        #  if serializer.is_valid(raise_exception=True):  # ????????????????
            #  serializer.save()
            #  return Response(serializer.data)
        #  else:
            #  return Response({"status": "Bad request."},status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, company_code):
        #  if has_role(request.user, "admin") or has_role(request.user, "admin_agent") or :
        if not company_code:
            return Response({"status": "Company_code is missing"},status=status.HTTP_400_BAD_REQUEST)
        try:
            company = Company.objects.get(company_code=company_code)
        except Company.DoesNotExist:
            return Response({"error": "'company_code' doesn't match with any company."},status=status.HTTP_400_BAD_REQUEST)
        if has_role(request.user, 'admin') or (has_role(request.user, 'admin_agent') and 
        request.user.company == company.contracting_company) or (has_role(request.user, 'agent') and 
        has_permission(request.user, 'delete_client_company') and request.user.company == company.contracting_company):
            if type(company.user_set.filter(is_active=True).all().first()) == User:
                return Response({'error': "You cannot delete this company as it has active users."},status=status.HTTP_401_UNAUTHORIZED)
            company.delete()
            return Response("Company deleted.")

        return Response({'error': "You don't have permission to access this resource."},status=status.HTTP_401_UNAUTHORIZED)

