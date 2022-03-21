from django.db import transaction
from django.db.models.deletion import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from .validators import agent_has_access_to_this_item_table, agent_has_access_to_this_price_table 
from user.validators import req_user_is_agent_without_all_estabs
from .facade import get_categories_by_agent, get_items_by_agent, get_price_tables_by_agent
from .serializers import ForTablePriceItemSerializer, ItemSerializer, CategorySerializer, ItemTableSerializer, PriceTableGetSerializer, PriceTablePOSTSerializer, SpecificPriceTablePUTSerializer, SpecificPriceItemSerializer
from .models import ItemTable, Item, ItemCategory, PriceTable, PriceItem
from rest_framework.views import APIView
from rolepermissions.checkers import has_permission, has_role
from drf_yasg.utils import swagger_auto_schema
from settings.response_templates import error_response, not_found_response, protected_error_response, serializer_invalid_response,  unauthorized_response, unknown_exception_response
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

class ItemTableView(APIView):
    def get(self, request):
        user = request.user
        if has_permission(user, 'get_item_tables'):
            item_table = ItemTable.objects.filter(contracting=user.contracting)
            data = ItemTableSerializer(item_table, many=True).data
            return Response(data)
        return unauthorized_response
    @swagger_auto_schema(request_body=ItemTableSerializer) 
    @transaction.atomic
    def post(self, request):
            if has_permission(request.user, 'create_item_table'):
                data = request.data
                serializer = ItemTableSerializer(data=data, context={"request":request})
                if serializer.is_valid():
                    try:
                        serializer.save()
                        return Response(serializer.data)
                    except Exception as error:
                        transaction.rollback()
                        print(error)
                        return unknown_exception_response(action=_('create item table'))
                return serializer_invalid_response(serializer.errors)
            return unauthorized_response

class SpecificItemTable(APIView):
    @transaction.atomic
    @swagger_auto_schema(request_body=ItemTableSerializer) 
    def put(self, request, item_table_compound_id):
        if has_permission(request.user, 'update_item_table'):
            if item_table_compound_id.split("&")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('Item table'))
            try:
                item_table = ItemTable.objects.get(item_table_compound_id=item_table_compound_id)
            except ItemTable.DoesNotExist:
                return not_found_response(object_name=_('Item table'))
            serializer = ItemTableSerializer(item_table, data=request.data, partial=True)
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return unknown_exception_response(action=_('update item table'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic
    def delete(self, request, item_table_compound_id):
        if has_permission(request.user, 'delete_item_table'):
            if item_table_compound_id.split("&")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('Item table'))
            try:
                item_table = ItemTable.objects.get(item_table_compound_id=item_table_compound_id)
            except ItemTable.DoesNotExist:
                return not_found_response(object_name=_('Item table'))
            try:
                item_table.delete()
                return Response("Item table deleted")
            except ProtectedError:
                return protected_error_response(object_name=_('item table'))
            except Exception as error:
                transaction.rollback()
                print(error)
                return unknown_exception_response(action=_('delete item table'))
        return unauthorized_response

class CategoryView(APIView):
    def get(self, request):
        if has_permission(request.user, 'get_item_category'):
            if has_role(request.user, 'agent'):
                item_categories = get_categories_by_agent(request.user)
                return Response(CategorySerializer(item_categories, many=True).data)
            item_categories = ItemCategory.objects.filter(item_table__contracting=request.user.contracting).all()
            serializer = CategorySerializer(item_categories, many=True)
            return Response(serializer.data)
        return unauthorized_response
    @transaction.atomic
    @swagger_auto_schema(request_body=CategorySerializer) 
    def post(self, request):
        if has_permission(request.user, 'create_item_category'):
            serializer = CategorySerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return unknown_exception_response(action=_('create item category'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response

class SpecificCategoryView(APIView):
    @transaction.atomic
    @swagger_auto_schema(request_body=CategorySerializer) 
    def put(self, request, category_compound_id):
        user = request.user
        if has_permission(user, 'update_item_category'):
            if category_compound_id.split("&")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The item category')) 
            try:
                item_category = ItemCategory.objects.get(category_compound_id=category_compound_id)
            except ItemCategory.DoesNotExist:
                return not_found_response(object_name=_('The item category')) 
            # Check if agent without all estabs have access to this item category
            request_user_is_agent_without_all_estabs = req_user_is_agent_without_all_estabs(request_user)
            if request_user_is_agent_without_all_estabs and not \
                    agent_has_access_to_this_item_table(request.user, item_category.item_table):
                return not_found_response(object_name=_('The item category')) 
            serializer = CategorySerializer(item_category, data=request.data, partial=True, context={"request":request,
                "request_user_is_agent_without_all_estabs": request_user_is_agent_without_all_estabs})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return unknown_exception_response(action=_('update item category'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic
    def delete(self, request, category_compound_id):
        if has_permission(request.user, 'delete_item_category'):
            if category_compound_id.split("&")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The category'))
            try:
                item_category = ItemCategory.objects.get(category_compound_id=category_compound_id)
            except ItemCategory.DoesNotExist:
                return not_found_response(object_name=_('The item category')) 
            if req_user_is_agent_without_all_estabs(request.user) and \
                    not agent_has_access_to_this_item_table(request.user, item_category.item_table):
                return unauthorized_response
            try:
                item_category.delete()
                return Response("Item category deleted")
            except ProtectedError as er:
                return protected_error_response(object_name=_('item category'))
            except Exception as error:
                transaction.rollback()
                print(error)
                return unknown_exception_response(action=_('delete item category'))
        return unauthorized_response

class ItemView(APIView):
    def get(self, request):
        if has_permission(request.user, 'get_items'):
            if has_role(request.user, 'agent'):
                items = get_items_by_agent(request.user)
                return Response(ItemSerializer(items, many=True).data)
            items = Item.objects.filter(item_table__contracting=request.user.contracting).all()
            return Response(ItemSerializer(items, many=True).data)
        return unauthorized_response
    @transaction.atomic
    @swagger_auto_schema(request_body=ItemSerializer) 
    def post(self, request):
        if has_permission(request.user, 'create_item'):
            serializer = ItemSerializer(data=request.data, context={"request": request, 
                "request_user_is_agent_without_all_estabs": req_user_is_agent_without_all_estabs(request.user)})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return unknown_exception_response(action=_('create item'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response

class SpecificItemView(APIView):
    @transaction.atomic
    @swagger_auto_schema(request_body=ItemSerializer) 
    def put(self, request, item_compound_id):
        if has_permission(request.user, 'update_item'):
            if item_compound_id.split("&")[0] != request.user.contracting.contracting_code:
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
            serializer = ItemSerializer(item, data=request.data, context={"request": request,
                "request_user_is_agent_without_all_estabs": request_user_is_agent_without_all_estabs})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(data=serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return unknown_exception_response(action=_('update item'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic
    def delete(self, request, item_compound_id):
        if has_permission(request.user, 'delete_item'):
            if item_compound_id.split("&")[0] != request.user.contracting.contracting_code:
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
                return Response("Item deleted")
            except ProtectedError:
                return protected_error_response(object_name=_('item'))
            except Exception as error:
                transaction.rollback()
                print(error)
                return unknown_exception_response(action=_('delete item'))
        return unauthorized_response

class PriceTableView(APIView):
    def get(self, request):
        if has_permission(request.user, 'get_price_tables'):
            if has_role(request.user, 'agent'):
                pricetables = get_price_tables_by_agent(request.user)
                return Response(PriceTableGetSerializer(pricetables, many=True).data)
            pricetables = PriceTable.objects.filter(company__contracting=request.user.contracting).all()
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
                    print(error)
                    return unknown_exception_response(action=_('create price table'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response

class SpecificPriceTableView(APIView):
    @transaction.atomic
    @swagger_auto_schema(request_body=SpecificPriceTablePUTSerializer) 
    def put(self, request, price_table_compound_id):
        if has_permission(request.user, 'update_price_table'):
            if price_table_compound_id.split("&")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The price table'))
            try:
                instance = PriceTable.objects.get(price_table_compound_id=price_table_compound_id)
            except PriceTable.DoesNotExist:
                return not_found_response(object_name=_('The price table'))
            # Agent without access to all establishments should not access some price_tables
            request_user_is_agent_without_all_estabs = req_user_is_agent_without_all_estabs(request.user)
            if request_user_is_agent_without_all_estabs and not agent_has_access_to_this_price_table(request.user, instance):
                return not_found_response(object_name=_('The price table'))
            serializer = SpecificPriceTablePUTSerializer(instance, data=request.data, 
                    context={"request": request,"req_user_is_agent_without_all_estabs": request_user_is_agent_without_all_estabs})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return unknown_exception_response(action=_('update price table'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic
    def delete(self, request, price_table_compound_id):
        if has_permission(request.user, 'delete_price_table'):
            if price_table_compound_id.split("&")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The price table'))
            try:
                instance = PriceTable.objects.get(price_table_compound_id=price_table_compound_id)
            except PriceTable.DoesNotExist:
                return not_found_response(object_name=_('The price table'))
            if req_user_is_agent_without_all_estabs(request.user) and \
                    not agent_has_access_to_this_price_table(request.user, instance):
                return unauthorized_response
            try:
                instance.delete()
                return Response("Price table deleted successfully")
            except ProtectedError:
                return protected_error_response(object_name=_('price table'))
            except Exception as error:
                print(error)
                return unknown_exception_response(action=_('delete price table'))
        return unauthorized_response

class GetPriceItemByClientUserView(APIView):
    def get(self, request, establishment_compound_id):
        if has_role(request.user, 'client_user'):
            try:
                price_table = PriceTable.objects.get(clientestablishment__client__client_compound_id=request.user.client.client_compound_id, clientestablishment__establishment__establishment_compound_id=establishment_compound_id)
            except PriceTable.DoesNotExist:
                return not_found_response(object_name=_('The price table'))
            try:
                price_items = PriceItem.objects.filter(price_table=price_table)
            except PriceItem.DoesNotExist:
                return not_found_response(object_name=_('The price items'))
            return Response(ForTablePriceItemSerializer(price_items, many=True).data)
        return unauthorized_response

class PriceItemForAgentsView(APIView):
    def get(self, request, price_table_compound_id):
        if has_permission(request.user, 'get_price_tables'):
            try:
                price_table = PriceTable.objects.get(price_table_compound_id=price_table_compound_id)
            except PriceTable.DoesNotExist:
                return not_found_response(object_name=_('The price table'))
            try:
                price_items = PriceItem.objects.filter(price_table=price_table)
            except PriceItem.DoesNotExist:
                return not_found_response(object_name=_('The price items'))
            if req_user_is_agent_without_all_estabs(request.user):
                agent_price_tables = get_price_tables_by_agent(request.user)
                if not price_table in agent_price_tables:
                    return not_found_response(object_name=_('The price table'))
            return Response(ForTablePriceItemSerializer(price_items, many=True).data)
        return unauthorized_response

class SpecificPriceItemView(APIView):
    @swagger_auto_schema(request_body=SpecificPriceItemSerializer) 
    @transaction.atomic
    def put(self, request, price_table_compound_id, item_compound_id):
        if has_permission(request.user, 'create_or_update_price_item'):
            if price_table_compound_id.split("&")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The client'))
            if item_compound_id.split("&")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The item'))
            try:
                price_table = PriceTable.objects.get(price_table_compound_id=price_table_compound_id)
            except PriceTable.DoesNotExist:
                return not_found_response(object_name=_('The price table'))
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
                print(error)
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
                    print(error)
                    return unknown_exception_response(action=_('create or update price item'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    @transaction.atomic
    def delete(self, request, price_table_compound_id, item_compound_id):
        if has_permission(request.user, 'create_or_update_price_item'):
            if price_table_compound_id.split("&")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The price table'))
            if item_compound_id.split("&")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The item'))
            try:
                instance = PriceItem.objects.get(price_table__price_table_compound_id=price_table_compound_id,
                        item__item_compound_id=item_compound_id)
            except PriceItem.DoesNotExist:
                return not_found_response(object_name=_('The price item'))
            try:
                instance.delete()
                return Response("Price item deleted successfully")
            except ProtectedError:
                return protected_error_response(object_name=_('price item'))
            except Exception as error:
                print(error)
                return unknown_exception_response(action=_('delete price item'))
        return unauthorized_response