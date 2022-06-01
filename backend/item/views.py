from django.db import transaction
from django.db.models.deletion import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from item.facade import get_agent_item_tables

from organization.models import Company
from rest_framework.parsers import FormParser, MultiPartParser
from .validators import agent_has_access_to_this_item_table, agent_has_access_to_this_price_table 
from user.validators import req_user_is_agent_without_all_estabs
from .facade import get_categories_by_agent, get_categories_to_create_item_by_agent_without_all_estabs, get_companies_to_create_pricetabe_by_agent, get_items_by_agent, get_price_tables_by_agent
from .serializers import ItemGETSerializer, ItemPOSTSerializer, ItemPUTSerializer, CategoryPOSTSerializer, CategoryPUTSerializer, ItemTablePOSTSerializer, ItemTablePUTSerializer, PriceItemForAgentsSerializer, PriceTableGetSerializer, PriceTablePOSTSerializer, SpecificPriceTablePUTSerializer, SpecificPriceItemSerializer
from .models import ItemTable, Item, ItemCategory, PriceTable, PriceItem
from rest_framework.views import APIView
from settings.utils import has_permission, has_role
from drf_yasg.utils import swagger_auto_schema
from settings.response_templates import error_response, not_found_response, protected_error_response, serializer_invalid_response,  unauthorized_response, unknown_exception_response
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from organization.serializers import CompanyPOSTSerializer
from drf_yasg import openapi
from rest_framework.decorators import action
import math

class ItemTableView(APIView):
    #  @swagger_auto_schema(method='get', responses={200: ItemTablePOSTSerializer}, operation_description='GET /item/item_table/') 
    @swagger_auto_schema(method='get', responses={200: ItemTablePOSTSerializer(many=True)}) 
    @action(detail=False, methods=['get'])
    def get(self, request):
        user = request.user
        if has_permission(user, 'get_item_tables'):
            item_tables = ItemTable.objects.filter(contracting_id=user.contracting_id)
            data = ItemTablePOSTSerializer(item_tables, many=True).data
            return Response(data)
        return unauthorized_response
    @swagger_auto_schema(request_body=ItemTablePOSTSerializer) 
    @transaction.atomic
    def post(self, request):
            if has_permission(request.user, 'create_item_table'):
                data = request.data
                serializer = ItemTablePOSTSerializer(data=data, context={"request":request})
                if serializer.is_valid():
                    try:
                        serializer.save()
                        return Response(serializer.data)
                    except Exception as error:
                        transaction.rollback()
                        #  print(error)
                        return unknown_exception_response(action=_('create item table'))
                return serializer_invalid_response(serializer.errors)
            return unauthorized_response

class SpecificItemTable(APIView):
    @transaction.atomic
    @swagger_auto_schema(request_body=ItemTablePUTSerializer) 
    def put(self, request, item_table_compound_id):
        if has_permission(request.user, 'update_item_table'):
            if item_table_compound_id.split("*")[0] != request.user.contracting_id:
                return Response({"error":[_( "The item table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            try:
                item_table = ItemTable.objects.get(item_table_compound_id=item_table_compound_id)
            except ItemTable.DoesNotExist:
                return Response({"error":[_( "The item table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            serializer = ItemTablePUTSerializer(item_table, data=request.data, partial=True)
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    #  print(error)
                    return unknown_exception_response(action=_('update item table'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic
    def delete(self, request, item_table_compound_id):
        if has_permission(request.user, 'delete_item_table'):
            if item_table_compound_id.split("*")[0] != request.user.contracting_id:
                return Response({"error":[_( "The item table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            try:
                item_table = ItemTable.objects.get(item_table_compound_id=item_table_compound_id)
            except ItemTable.DoesNotExist:
                return Response({"error":[_( "The item table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            try:
                item_table.delete()
                return Response(_("Item table deleted"))
            except ProtectedError:
                return Response({"error":[_("You cannot delete this item table because it has records linked to it.")]}, 
                        status=status.HTTP_400_BAD_REQUEST) 
            except Exception as error:
                transaction.rollback()
                #  print(error)
                return unknown_exception_response(action=_('delete item table'))
        return unauthorized_response

class fetchItemTablesToCreateItemOrCategoryOrPriceTable(APIView):
    @swagger_auto_schema(method='get', responses={200: ItemTablePOSTSerializer(many=True)}) 
    @action(detail=False, methods=['get'])
    def get(self, request):
        if has_permission(request.user, 'create_item') or has_permission(request.user,  'create_item_category') or \
                has_permission(request.user, 'create_price_table'):
            if req_user_is_agent_without_all_estabs(request.user):
                item_tables = get_agent_item_tables(request.user)
                return Response(ItemTablePOSTSerializer(item_tables, many=True).data)
            item_tables = ItemTable.objects.filter(contracting_id=request.user.contracting_id)
            serializer = ItemTablePOSTSerializer(item_tables, many=True)
            return Response(serializer.data)
        return unauthorized_response

class GetCategoriesView(APIView):
    @swagger_auto_schema(method='get', responses={200: CategoryPUTSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def get(self, request, item_table_compound_id):
        if has_permission(request.user, 'get_item_category'):
            if has_role(request.user, 'agent'):
                item_categories = get_categories_by_agent(request.user).filter(item_table__item_table_compound_id=item_table_compound_id)
                return Response(CategoryPUTSerializer(item_categories, many=True).data)
            item_categories = ItemCategory.objects.filter(item_table__contracting_id=request.user.contracting_id, 
                    item_table__item_table_compound_id=item_table_compound_id)
            serializer = CategoryPUTSerializer(item_categories, many=True)
            return Response(serializer.data)
        return unauthorized_response

class CategoryView(APIView):
    @transaction.atomic
    @swagger_auto_schema(request_body=CategoryPOSTSerializer) 
    def post(self, request):
        if has_permission(request.user, 'create_item_category'):
            serializer = CategoryPOSTSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    #  print(error)
                    return unknown_exception_response(action=_('create item category'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response

class SpecificCategoryView(APIView):
    @transaction.atomic
    @swagger_auto_schema(request_body=CategoryPUTSerializer) 
    def put(self, request, category_compound_id):
        user = request.user
        if has_permission(user, 'update_item_category'):
            if category_compound_id.split("*")[0] != request.user.contracting_id:
                return Response({"error":[_( "The item category was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            try:
                item_category = ItemCategory.objects.get(category_compound_id=category_compound_id)
            except ItemCategory.DoesNotExist:
                return Response({"error":[_( "The item category was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            # Check if agent without all estabs have access to this item category
            request_user_is_agent_without_all_estabs = req_user_is_agent_without_all_estabs(request.user)
            if request_user_is_agent_without_all_estabs and not \
                    agent_has_access_to_this_item_table(request.user, item_category.item_table):
                return Response({"error":[_( "The item category was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            serializer = CategoryPUTSerializer(item_category, data=request.data, partial=True, context={"request":request,
                "request_user_is_agent_without_all_estabs": request_user_is_agent_without_all_estabs})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    #  print(error)
                    return unknown_exception_response(action=_('update item category'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic
    def delete(self, request, category_compound_id):
        if has_permission(request.user, 'delete_item_category'):
            if category_compound_id.split("*")[0] != request.user.contracting_id:
                return Response({"error":[_( "The item category was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            try:
                item_category = ItemCategory.objects.get(category_compound_id=category_compound_id)
            except ItemCategory.DoesNotExist:
                return Response({"error":[_( "The item category was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            if req_user_is_agent_without_all_estabs(request.user) and \
                    not agent_has_access_to_this_item_table(request.user, item_category.item_table):
                return unauthorized_response
            try:
                item_category.delete()
                return Response(_("Item category deleted"))
            except ProtectedError as er:
                return Response({"error":[_("You cannot delete this item category because it has records linked to it.")]}, 
                        status=status.HTTP_400_BAD_REQUEST) 
            except Exception as error:
                transaction.rollback()
                #  print(error)
                return unknown_exception_response(action=_('delete item category'))
        return unauthorized_response

class fetchCategoriesToCreateItem(APIView):
    @swagger_auto_schema(method='get', responses={200: CategoryPUTSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def get(self, request, item_table_compound_id):
        if has_permission(request.user, 'create_item'):
            if item_table_compound_id.split("*")[0] != request.user.contracting_id:
                return Response({"error":[_( "The item table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            try:
                ItemTable.objects.get(item_table_compound_id=item_table_compound_id)
            except ItemTable.DoesNotExist:
                return Response({"error":[_( "The item table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            if req_user_is_agent_without_all_estabs(request.user):
                categories = get_categories_to_create_item_by_agent_without_all_estabs(request.user, item_table_compound_id)
                return Response(CategoryPUTSerializer(categories, many=True).data)
            categories = ItemCategory.objects.filter(item_table__item_table_compound_id=item_table_compound_id).order_by('category_code')
            return Response(CategoryPUTSerializer(categories, many=True).data)
        return unauthorized_response

page_query_string = openapi.Parameter('page', openapi.IN_QUERY, description="page number", type=openapi.TYPE_INTEGER)
items_per_page_query_string = openapi.Parameter('items_per_page', openapi.IN_QUERY, description="items per page", 
        type=openapi.TYPE_INTEGER)
sort_by_query_string = openapi.Parameter('sort_by', openapi.IN_QUERY, description="sort by", type=openapi.TYPE_STRING)
sort_desc_query_string = openapi.Parameter('sort_desc', openapi.IN_QUERY, description="sort desc", type=openapi.TYPE_STRING)
item_table_query_string = openapi.Parameter('item_table', openapi.IN_QUERY, description="item_table_compound_id field", type=openapi.TYPE_STRING)
category_query_string = openapi.Parameter('category', openapi.IN_QUERY, description="category_compound_id field", type=openapi.TYPE_STRING)
item_code_query_string = openapi.Parameter('item_code', openapi.IN_QUERY, description="item_code", 
        type=openapi.TYPE_STRING)
description_query_string = openapi.Parameter('description', openapi.IN_QUERY, description="description field", 
        type=openapi.TYPE_STRING)

class ItemView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(method='get', responses={200: ItemGETSerializer}, manual_parameters=[page_query_string, items_per_page_query_string, sort_by_query_string, sort_desc_query_string, item_table_query_string, category_query_string, item_code_query_string, description_query_string]) 
    @action(detail=False, methods=['get'])
    def get(self, request):
        if has_permission(request.user, 'get_items'):
            kwargs = {}
            sort_desc = True if request.GET.get("sort_desc") == "true" else False
            sort_by = request.GET.get("sort_by") if request.GET.get("sort_by") in ["item_code", "description"] else "item_code"
            if sort_desc:
                sort_by = '-' + sort_by
            page = request.GET.get("page")
            page = int(page) if page and page.isdigit() else 1
            items_per_page = request.GET.get("items_per_page")
            items_per_page = int(items_per_page) if items_per_page in ["5", "10", "15"] else 10
            start = (page - 1) * items_per_page
            end = page * items_per_page
            if request.GET.get("item_table"): kwargs.update({"item_table__item_table_compound_id": request.GET.get("item_table")})
            #  if request.GET.get("category"): kwargs.update({"category__category_compound_id": request.GET.get("category")})
            if request.GET.get("category"): 
                category_code = request.GET.get("category").split('*')[2]
                kwargs.update({"category__category_code__startswith": category_code})
            if request.GET.get("item_code"): kwargs.update({"item_code": request.GET.get("item_code")})
            if request.GET.get("description"): kwargs.update({"description__icontains": request.GET.get("description")})
            if has_role(request.user, 'agent'):
                items = get_items_by_agent(request.user).filter(**kwargs).order_by(sort_by)
                total = items.count()
                lastPage = math.ceil(total / items_per_page)
                return Response({"items": ItemGETSerializer(items[start:end], many=True).data, "current_page": page,
                    "lastPage": lastPage, "total": total })
            items = Item.objects.filter(item_table__contracting_id=request.user.contracting_id, **kwargs).order_by(sort_by)
            total = items.count()
            lastPage = math.ceil(total / items_per_page)
            return Response({"items": ItemGETSerializer(items[start:end], many=True).data, "current_page": page,
                "lastPage": lastPage, "total": total})
        return unauthorized_response
    @transaction.atomic
    @swagger_auto_schema(request_body=ItemPOSTSerializer) 
    def post(self, request, format=None):
        if has_permission(request.user, 'create_item'):
            serializer = ItemPOSTSerializer(data=request.data, context={"request": request, 
                "request_user_is_agent_without_all_estabs": req_user_is_agent_without_all_estabs(request.user)})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Exception as error:
                    transaction.rollback()
                    #  print(error)
                    return unknown_exception_response(action=_('create item'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response

class SpecificItemView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @transaction.atomic
    @swagger_auto_schema(request_body=ItemPUTSerializer) 
    def put(self, request, item_compound_id):
        if has_permission(request.user, 'update_item'):
            if item_compound_id.split("*")[0] != request.user.contracting_id:
                return not_found_response(object_name=_('The item'))
            try:
                item = Item.objects.get(item_compound_id=item_compound_id)
            except Item.DoesNotExist:
                return not_found_response(object_name=_('The item'))
            request_user_is_agent_without_all_estabs = req_user_is_agent_without_all_estabs(request.user)
            # Agent without access to all establishments can't access an item from item_table which he doesn't have access.
            if request_user_is_agent_without_all_estabs and not \
                    agent_has_access_to_this_item_table(request.user, item.item_table):
                return not_found_response(object_name=_('The item'))
            serializer = ItemPUTSerializer(item, data=request.data, context={"request": request,
                "request_user_is_agent_without_all_estabs": request_user_is_agent_without_all_estabs})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(data=serializer.data)
                except Exception as error:
                    transaction.rollback()
                    #  print(error)
                    return unknown_exception_response(action=_('update item'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic
    def delete(self, request, item_compound_id):
        if has_permission(request.user, 'delete_item'):
            if item_compound_id.split("*")[0] != request.user.contracting_id:
                return not_found_response(object_name=_('The item'))
            try:
                item = Item.objects.get(item_compound_id=item_compound_id)
            except Item.DoesNotExist:
                return not_found_response(object_name=_('The item'))
            if req_user_is_agent_without_all_estabs(request.user) and \
                    not agent_has_access_to_this_item_table(request.user, item.item_table):
                return unauthorized_response
            try:
                item.delete()
                return Response(_("Item deleted"))
            except ProtectedError:
                return protected_error_response(object_name=_('item'))
            except Exception as error:
                transaction.rollback()
                #  print(error)
                return unknown_exception_response(action=_('delete item'))
        return unauthorized_response

class fetchCompaniesToCreatePriceTable(APIView):
    @swagger_auto_schema(method='get', responses={200: CompanyPOSTSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def get(self, request):
        if has_permission(request.user, 'create_price_table'):
            if req_user_is_agent_without_all_estabs(request.user):
                companies = get_companies_to_create_pricetabe_by_agent(request.user)
                return Response(CompanyPOSTSerializer(companies, many=True).data)
            companies = Company.objects.filter(status=1, contracting_id=request.user.contracting_id).exclude(item_table=None)
            serializer = CompanyPOSTSerializer(companies, many=True)
            return Response(serializer.data)
        return

#  class fetchItemsToCreatePriceTable(APIView):
    #  def get(self, request, item_table_compound_id):
        #  if has_permission(request.user, 'create_price_table'):
            #  if item_table_compound_id.split("*")[0] != request.user.contracting_id:
                #  return Response({"error":[_( "The item table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            #  try:
                #  item_table = ItemTable.objects.get(item_table_compound_id=item_table_compound_id)
            #  except ItemTable.DoesNotExist:
                #  return Response({"error":[_( "The item table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            #  if req_user_is_agent_without_all_estabs(request.user):
                #  agent_item_tables = get_agent_item_tables(request.user)
                #  if item_table in agent_item_tables:
                    #  items = Item.objects.filter(item_table=item_table, status=1)
                    #  return Response(ItemPOSTSerializer(items, many=True).data)
                #  return Response({"error":[_( "The item table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            #  items = Item.objects.filter(item_table=item_table, status=1)
            #  return Response(ItemPOSTSerializer(items, many=True).data)
        #  return unauthorized_response

class PriceTableView(APIView):
    @swagger_auto_schema(method='get', responses={200: PriceTablePOSTSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def get(self, request):
        if has_permission(request.user, 'get_price_tables'):
            if has_role(request.user, 'agent'):
                pricetables = get_price_tables_by_agent(request.user)
                return Response(PriceTableGetSerializer(pricetables, many=True).data)
            pricetables = PriceTable.objects.filter(company__contracting_id=request.user.contracting_id).select_related('company')
            return Response(PriceTableGetSerializer(pricetables, many=True).data)
        return unauthorized_response
    @swagger_auto_schema(request_body=PriceTablePOSTSerializer) 
    @transaction.atomic
    def post(self, request):
        if has_permission(request.user, 'create_price_table'): 
            serializer = PriceTablePOSTSerializer(data=request.data, context={"request": request,
                "req_user_is_agent_without_all_estabs":req_user_is_agent_without_all_estabs(request.user)})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Exception as error:
                    transaction.rollback()
                    #  print(error)
                    return unknown_exception_response(action=_('create price table'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response

class SpecificPriceTableView(APIView):
    @transaction.atomic
    @swagger_auto_schema(request_body=SpecificPriceTablePUTSerializer) 
    def put(self, request, price_table_compound_id):
        if has_permission(request.user, 'update_price_table'):
            if price_table_compound_id.split("*")[0] != request.user.contracting_id:
                return Response({"error":[_( "The price table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            try:
                instance = PriceTable.objects.get(price_table_compound_id=price_table_compound_id)
            except PriceTable.DoesNotExist:
                return Response({"error":[_( "The price table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            # Agent without access to all establishments should not access some price_tables
            request_user_is_agent_without_all_estabs = req_user_is_agent_without_all_estabs(request.user)
            if request_user_is_agent_without_all_estabs and not agent_has_access_to_this_price_table(request.user, instance):
                return Response({"error":[_( "The price table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            serializer = SpecificPriceTablePUTSerializer(instance, data=request.data, 
                    context={"request": request,"req_user_is_agent_without_all_estabs": request_user_is_agent_without_all_estabs})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    #  print(error)
                    return unknown_exception_response(action=_('update price table'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic
    def delete(self, request, price_table_compound_id):
        if has_permission(request.user, 'delete_price_table'):
            if price_table_compound_id.split("*")[0] != request.user.contracting_id:
                return Response({"error":[_( "The price table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            try:
                instance = PriceTable.objects.get(price_table_compound_id=price_table_compound_id)
            except PriceTable.DoesNotExist:
                return Response({"error":[_( "The price table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            if req_user_is_agent_without_all_estabs(request.user) and \
                    not agent_has_access_to_this_price_table(request.user, instance):
                return unauthorized_response
            try:
                instance.delete()
                return Response(_("Price table deleted successfully"))
            except ProtectedError:
                return Response({"error":[_("You cannot delete this price table because it has records linked to it.")]}, 
                        status=status.HTTP_400_BAD_REQUEST) 
            except Exception as error:
                #  print(error)
                return unknown_exception_response(action=_('delete price table'))
        return unauthorized_response

class PriceItemForAgentsView(APIView):
    @swagger_auto_schema(method='get', responses={200: PriceItemForAgentsSerializer(many=True)}) 
    @action(detail=False, methods=['get'])
    def get(self, request, price_table_compound_id):
        if has_permission(request.user, 'get_price_tables'):
            try:
                price_table = PriceTable.objects.get(price_table_compound_id=price_table_compound_id)
            except PriceTable.DoesNotExist:
                return Response({"error":[_( "The price table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            try:
                price_items = PriceItem.objects.filter(price_table=price_table)
            except PriceItem.DoesNotExist:
                return Response({"error":[_("The price items were not found.")]}, status=status.HTTP_404_NOT_FOUND)
            if req_user_is_agent_without_all_estabs(request.user):
                agent_price_tables = get_price_tables_by_agent(request.user)
                if not price_table in agent_price_tables:
                    return Response({"error":[_( "The price table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            return Response(PriceItemForAgentsSerializer(price_items, many=True).data)
        return unauthorized_response

class SpecificPriceItemView(APIView):

    request_schema_dict = openapi.Schema(
        title=_("Update order"),
        type=openapi.TYPE_OBJECT,
        properties={
            'unit_price': openapi.Schema(type=openapi.TYPE_NUMBER, description=_('Unit price'), example=12.33),
        }
    )

    #  item_compound_id = openapi.Parameter('item_compound_id', in_=openapi.IN_QUERY, description='Item identifier', 
            #  type=openapi.TYPE_STRING, required=False, example="asdfasdf")

    @swagger_auto_schema(request_body=request_schema_dict, responses={200: 'Price item updated successfully.'}) 
    @transaction.atomic
    def put(self, request, price_table_compound_id, item_compound_id):
        if has_permission(request.user, 'create_or_update_price_item'):
            if price_table_compound_id.split("*")[0] != request.user.contracting_id:
                return not_found_response(object_name=_('The client'))
            if item_compound_id.split("*")[0] != request.user.contracting_id:
                return not_found_response(object_name=_('The item'))
            try:
                price_table = PriceTable.objects.get(price_table_compound_id=price_table_compound_id)
            except PriceTable.DoesNotExist:
                return Response({"error":[_( "The price table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            try:
                item = Item.objects.get(item_compound_id=item_compound_id)
            except Item.DoesNotExist:
                return not_found_response(object_name=_('The item'))
            # Check if the item belongs to the company's item table
            if item.item_table != price_table.company.item_table:
                return error_response(detail=_("The item must belong to the company that owns the price table."),
                        status=status.HTTP_400_BAD_REQUEST)
            test_request_data = SpecificPriceItemSerializer(data=request.data)
            # It's need to validate before creating
            if not test_request_data.is_valid():
                return serializer_invalid_response(test_request_data.errors)
            try:
                instance, created = PriceItem.objects.get_or_create(item=item, price_table=price_table)
            except Exception as error:
                transaction.rollback()
                #  print(error)
                return unknown_exception_response(action=_('get or create price item'))
            serializer = SpecificPriceItemSerializer(instance, data=request.data, context={"request": request})
            # If no change was made on update request, just return the instance
            if not created:
                if instance.unit_price == Decimal(request.data['unit_price']):
                    #This 'if' clause is for precaution
                    if serializer.is_valid(): 
                        return Response(serializer.data)
                    return serializer_invalid_response(serializer.errors)
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(_('Price item updated successfully.'))
                except Exception as error:
                    transaction.rollback()
                    #  print(error)
                    return unknown_exception_response(action=_('create or update price item'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic
    def delete(self, request, price_table_compound_id, item_compound_id):
        if has_permission(request.user, 'create_or_update_price_item'):
            if price_table_compound_id.split("*")[0] != request.user.contracting_id:
                return Response({"error":[_( "The price table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            if item_compound_id.split("*")[0] != request.user.contracting_id:
                return not_found_response(object_name=_('The item'))
            try:
                instance = PriceItem.objects.get(price_table__price_table_compound_id=price_table_compound_id,
                        item__item_compound_id=item_compound_id)
            except PriceItem.DoesNotExist:
                return not_found_response(object_name=_('The price item'))
            try:
                instance.delete()
                return Response(_("Price item deleted successfully"))
            except ProtectedError:
                return protected_error_response(object_name=_('price item'))
            except Exception as error:
                #  print(error)
                return unknown_exception_response(action=_('delete price item'))
        return unauthorized_response
