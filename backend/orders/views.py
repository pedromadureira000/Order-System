from django.db import transaction
from django.db.models.deletion import ProtectedError
from rest_framework import status, mixins, generics
from rest_framework.response import Response
from core.models import User
from core.validators import agent_has_access_to_this_item_table, agent_has_access_to_this_price_table, req_user_is_agent_without_all_estabs
from orders.facade import get_categories_by_agent, get_items_by_agent, get_price_tables_by_agent
from orders.serializers import ItemSerializer, CategorySerializer, ItemTableSerializer, OrderSerializer, PriceTableSerializer
from orders.models import ItemTable, Order, Item, ItemCategory, PriceTable, PriceItem
from rest_framework.views import APIView
from rolepermissions.checkers import has_permission, has_role
from drf_yasg.utils import swagger_auto_schema
from core.views import not_found_response, protected_error_response, serializer_invalid_response, success_response, unauthorized_response, unknown_exception_response
from django.utils.translation import gettext_lazy as _

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
            if item_table_compound_id.split("#")[0] != request.user.contracting.contracting_code:
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
            if item_table_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('Item table'))
            try:
                item_table = ItemTable.objects.get(item_table_compound_id=item_table_compound_id)
            except ItemTable.DoesNotExist:
                return not_found_response(object_name=_('Item table'))
            try:
                item_table.delete()
                return success_response(detail=_("Item table deleted"))
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
            if category_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The item category')) 
            try:
                item_category = ItemCategory.objects.get(category_compound_id=category_compound_id)
            except ItemCategory.DoesNotExist:
                return not_found_response(object_name=_('The item category')) 
            serializer = CategorySerializer(item_category, data=request.data, partial=True, context={"request":request})
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
            if category_compound_id.split("#")[0] != request.user.contracting.contracting_code:
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
                return success_response(detail=_("Item category deleted"))
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
            serializer = ItemSerializer(data=request.data, context={"request": request})
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
            if item_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The item'))
            try:
                item = Item.objects.get(item_compound_id=item_compound_id)
            except Item.DoesNotExist:
                return not_found_response(object_name=_('The item'))
            serializer = ItemSerializer(item, data=request.data)
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
            if item_compound_id.split("#")[0] != request.user.contracting.contracting_code:
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
                return success_response(detail=_("Item deleted"))
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
                return Response(PriceTableSerializer(pricetables, many=True).data)
            pricetables = PriceTable.objects.filter(company__contracting=request.user.contracting).all()
            return Response(PriceTableSerializer(pricetables, many=True).data)
        return unauthorized_response
    @swagger_auto_schema(request_body=PriceTableSerializer) 
    @transaction.atomic
    def post(self, request):
        if has_permission(request.user, 'create_price_table'):
            req_user_is_agent_without_all_estabs(request.user)
            serializer = PriceTableSerializer(data=request.data, context={"request": request,
                "req_user_is_agent_without_all_estabs":req_user_is_agent_without_all_estabs})
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
    @swagger_auto_schema(request_body=PriceTableSerializer) 
    def put(self, request, price_table_compound_id):
        if has_permission(request.user, 'update_price_table'):
            if price_table_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The price table'))
            try:
                instance = PriceTable.objects.get(price_table_compound_id=price_table_compound_id)
            except PriceTable.DoesNotExist:
                return not_found_response(object_name=_('The price table'))
            req_user_is_agent_without_all_estabs(request.user)
            serializer = PriceTableSerializer(instance, data=request.data, context={"request": request,
                "req_user_is_agent_without_all_estabs":req_user_is_agent_without_all_estabs})
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
            if price_table_compound_id.split("#")[0] != request.user.contracting.contracting_code:
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
                return success_response(detail=_("Price table deleted successfully"))
            except ProtectedError:
                return protected_error_response(object_name=_('price table'))
            except Exception as error:
                print(error)
                return unknown_exception_response(action=_('delete price table'))
        return unauthorized_response

#  class AssignPriceTableView(APIView):
    #  @swagger_auto_schema(request_body=AssignPriceTableSerializer) 
    #  @transaction.atomic
    #  def post(self, request):
        #  serializer = AssignPriceTableSerializer(data=request.data)
        #  if serializer.is_valid():
            #  table_code = serializer.validated_data['table_code']
            #  company_code = serializer.validated_data['company_code']
            #  try:
                #  company = Company.objects.get(company_code=company_code)
                #  price_table = PriceTable.objects.get(table_code=table_code)
                #  company.price_table = price_table
                #  company.save()
                #  return Response("The price table has been assigned", status=status.HTTP_200_OK)
            #  except Company.DoesNotExist:
                #  return Response({"error": "Company has not found."}, status=status.HTTP_400_BAD_REQUEST)
            #  except Exception as error:
                #  print(error)
                #  return unknown_exception_response(action=_('assign price table to client'))

            #  return Response(serializer.data, status=status.HTTP_201_CREATED)
        #  return serializer_invalid_response(serializer.errors)
    
#  class PriceItemView(APIView):
    #  @swagger_auto_schema(request_body=PriceItemSerializer) 
    #  @transaction.atomic
    #  def post(self, request):
        #  if has_role(request.user, 'ERPClient'):
            #  item = request.data.get('item')
            #  pricetable = request.data.get('pricetable')
            #  if not item or not pricetable:
                #  return Response({"response": "Por favor envie os valores de 'item' e 'pricetable'."},
                                #  status=status.HTTP_400_BAD_REQUEST)
            #  try:
                #  pricetable = PriceTable.objects.get(table_code=pricetable)
            #  except PriceTable.DoesNotExist:
                #  return Response({"response":"A tabela informada nao existe."}, status=status.HTTP_404_NOT_FOUND)
            #  try:
                #  item = Item.objects.get(item_code=item)
            #  except Item.DoesNotExist:
                #  return Response({"response": "O item informado nao existe."}, status=status.HTTP_404_NOT_FOUND)
            #  if pricetable.contracting_company != request.user.company:
                #  return Response("You cannot access this price table.", status=status.HTTP_400_BAD_REQUEST)
            #  copy_data = request.data.copy()
            #  copy_data['item'] = item.pk
            #  copy_data['pricetable'] = pricetable.pk

            #  serializer = PriceItemSerializer(data=copy_data)
            #  serializer = PriceItemSerializer(data=request.data, context={"currentUser": request.user})
            #  if serializer.is_valid():
                #  serializer.save()
                #  return Response(serializer.data, status=status.HTTP_201_CREATED)
        #  return serializer_invalid_response(serializer.errors)
        #  return Response({"error": "You don't have permissions to access this resource."},
                        #  status=status.HTTP_401_UNAUTHORIZED)


#  class SpecificPriceItemView(APIView):
    #  def get(self, request, item_code, table_code):
        #  if has_role(request.user, 'ERPClient'):
            #  try:
                #  priceitem = PriceItem.objects.get(pricetable__table_code=table_code, item__item_code=item_code)
            #  except PriceItem.DoesNotExist:
                #  return Response(status=status.HTTP_404_NOT_FOUND)
            #  if priceitem.pricetable.contracting_company != request.user.company:
                #  return Response(status=status.HTTP_400_BAD_REQUEST)
            #  serializer = PriceItemSerializer(priceitem)
            #  return Response(serializer.data)

        #  return Response({"error": "You don't have permissions to access this resource."},
                        #  status=status.HTTP_401_UNAUTHORIZED)
    #  @swagger_auto_schema(request_body=PriceItemSerializer) 
    #  @transaction.atomic
    #  def put(self, request, item_code, table_code):
        #  if has_role(request.user, 'ERPClient'):
            #  try:
                #  pricetable = PriceTable.objects.get(table_code=table_code)
            #  except PriceTable.DoesNotExist:
                #  return Response({"response":"A tabela informada nao existe."}, status=status.HTTP_404_NOT_FOUND)
            #  try:
                #  item = Item.objects.get(item_code=item_code)
            #  except Item.DoesNotExist:
                #  return Response({"response": "O item informado nao existe."}, status=status.HTTP_404_NOT_FOUND)
            #  if pricetable.contracting_company != request.user.company:
                #  return Response("You cannot access this price table.", status=status.HTTP_400_BAD_REQUEST)
            #  try:
                #  instance = PriceItem.objects.get(item__item_code=item_code, pricetable__table_code=table_code)
            #  except PriceItem.DoesNotExist:
                #  return Response({"response": "O PriceItem imformado nao existe."}, status=status.HTTP_404_NOT_FOUND)
            #  serializer = SpecificPriceItemSerializer(instance, data=request.data, context={'currentUser': request.user, 'method': 'put'})
            #  if serializer.is_valid():
                #  serializer.save()
                #  return Response(serializer.data, status=status.HTTP_201_CREATED)
            #  return serializer_invalid_response(serializer.errors)
        #  return Response({"error": "You don't have permissions to access this resource."},
                        #  status=status.HTTP_401_UNAUTHORIZED)

    #  @transaction.atomic
    #  def delete(self, request, item_code, table_code):
        #  if has_role(request.user, 'ERPClient'):
            #  try:
                #  priceitem = PriceItem.objects.get(pricetable__table_code=table_code, item__item_code=item_code)
            #  except PriceItem.DoesNotExist:
                #  return Response(status=status.HTTP_404_NOT_FOUND)
            #  if not priceitem:
                #  return Response({"response": "Item preco nao encontrado."},
                                #  status=status.HTTP_404_NOT_FOUND)
            #  if priceitem.pricetable.contracting_company != request.user.company:
                #  return Response("You cannot access this price table.", status=status.HTTP_400_BAD_REQUEST)
            #  operation = priceitem.delete()
            #  data = {}
            #  if operation:
                #  data['success'] = 'deleted successful'
            #  else:
                #  data['failure'] = 'delete failed'
            #  return Response(data, status=status.HTTP_200_OK)

        #  return Response({"error": "You don't have permissions to access this resource."},
                        #  status=status.HTTP_401_UNAUTHORIZED)

class OrderView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = OrderSerializer

    def get(self, request):
      if has_permission(request.user, 'create_item'):
            if request.data.get('status'):
                try:
                    orders = Order.objects.filter(status=request.data['status'])
                except Order.DoesNotExist:
                    return Response({"response": "Error"}, status=status.HTTP_404_NOT_FOUND)
                serializer = OrderSerializer(orders, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'response': "Parameter 'status' is missing."},
                            status=status.HTTP_400_BAD_REQUEST)
      return Response({"error": "You don't have permissions to access this resource."},
                        status=status.HTTP_401_UNAUTHORIZED)

class SpecificOrderView(APIView):
    def get(self, request, code):
        if has_permission(request.user, 'create_item'):
            try:
                order = Order.objects.get(id=code)
            except Order.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        return Response({"error": "You don't have permissions to access this resource."}, status=status.HTTP_401_UNAUTHORIZED)
