from django.db.models.deletion import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from organization.facade import get_clients_by_agent, get_companies_to_create_client, get_establishments_to_create_client
from organization.serializers import  ClientSerializer, ClientTableSerializer, CompanySerializer, ContractingSerializer, EstablishmentSerializer
from organization.models import Client, ClientTable, Company, Contracting, Establishment
from rolepermissions.checkers import has_permission, has_role
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from organization.validators import agent_has_access_to_this_client
from user.validators import req_user_is_agent_without_all_estabs
from django.utils.translation import gettext_lazy as _
from settings.response_templates import error_response, success_response, not_found_response, serializer_invalid_response, protected_error_response, unknown_exception_response, unauthorized_response

class ContractingView(APIView):
    def get(self, request):
        if has_permission(request.user, 'get_contracting'):
            contractings = Contracting.objects.all()
            data = ContractingSerializer(contractings, many=True).data
            return Response(data)
        return unauthorized_response
    @swagger_auto_schema(request_body=ContractingSerializer) 
    @transaction.atomic
    def post(self, request):
            if has_permission(request.user, 'create_contracting'):
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
        if has_permission(request.user, 'update_contracting'):
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
        if has_permission(request.user, 'delete_contracting'):
            try:
                contracting = Contracting.objects.get(contracting_code=contracting_code)
            except Contracting.DoesNotExist:
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
        print('========================> : ',company_compound_id )
        if has_permission(request.user, 'update_company'):
            if company_compound_id.split("&")[0] != request.user.contracting.contracting_code:
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
            if company_compound_id.split("&")[0] != request.user.contracting.contracting_code:
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
            if establishment_compound_id.split("&")[0] != request.user.contracting.contracting_code:
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
            if establishment_compound_id.split("&")[0] != request.user.contracting.contracting_code:
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
            if client_table_compound_id.split("&")[0] != request.user.contracting.contracting_code:
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
            if client_table_compound_id.split("&")[0] != request.user.contracting.contracting_code:
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

class GetEstablishmentsToCreateClient(APIView):
    def get(self, request, client_table_compound_id):
        if has_permission(request.user, 'create_client'):
            if client_table_compound_id.split("&")[0] != request.user.contracting.contracting_code:
                return error_response(detail="You cannot access this 'client_table'", status=status.HTTP_403_FORBIDDEN) #TODO translate
            request_user_is_agent_without_all_estabs = req_user_is_agent_without_all_estabs(request.user)
            establishments = get_establishments_to_create_client(request.user, client_table_compound_id,request_user_is_agent_without_all_estabs)
            return Response(EstablishmentSerializer(establishments, many=True).data)

class GetCompaniesToCreateClient(APIView):
    def get(self, request):
        if has_permission(request.user, 'create_client'):
            request_user_is_agent_without_all_estabs = req_user_is_agent_without_all_estabs(request.user)
            companies = get_companies_to_create_client(request.user, request_user_is_agent_without_all_estabs)
            return Response(CompanySerializer(companies, many=True).data)

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
            if client_compound_id.split("&")[0] != user.contracting.contracting_code:
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
            if client_compound_id.split("&")[0] != request.user.contracting.contracting_code:
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
