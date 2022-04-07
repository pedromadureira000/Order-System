from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from item.models import ItemCategory, ItemTable, PriceItem, PriceTable
from item.serializers import CategoryPOSTSerializer
from organization.models import Company, Establishment
from user.validators import req_user_is_agent_without_all_estabs
from .facade import get_orders_by_agent
from .serializers import OrderDetailsSerializer, OrderPOSTSerializer,OrderPUTSerializer, fetchClientEstabsToCreateOrderSerializer, searchOnePriceItemToMakeOrderSerializer
from .models import Order
from rest_framework.views import APIView
from rolepermissions.checkers import has_permission, has_role
from drf_yasg.utils import swagger_auto_schema
from settings.response_templates import not_found_response, serializer_invalid_response, unauthorized_response, unknown_exception_response
from django.utils.translation import gettext_lazy as _

class fetchClientEstabsToCreateOrder(APIView):
    def get(self, request):
        if has_permission(request.user, 'create_order'):
            establishments = Establishment.objects.filter(clientestablishment__in=request.user.client.client_establishments.filter(establishment__status=1).exclude(price_table=None))
            serializer = fetchClientEstabsToCreateOrderSerializer(establishments, many=True)
            return Response(serializer.data)
        return unauthorized_response

class searchOnePriceItemToMakeOrder(APIView):
    def get(self, request, establishment_compound_id, item_code):
        if has_permission(request.user, 'create_order'):
            try:
                price_table = PriceTable.objects.get(clientestablishment__client=request.user.client, 
                        clientestablishment__establishment__establishment_compound_id=establishment_compound_id)
            except PriceTable.DoesNotExist:
                return not_found_response(object_name=_('The item'))
            try:
                price_item = PriceItem.objects.get(price_table=price_table, item__item_code=item_code, item__status=1)
            except PriceItem.DoesNotExist:
                return not_found_response(object_name=_('The item'))
            return Response(searchOnePriceItemToMakeOrderSerializer(price_item).data)
        return unauthorized_response

class SearchPriceItemsToMakeOrder(APIView):
      #  // EX priceItemObj: {item: '123$123$111111', item_description: 'Nice Item', category: 'category 1', unit_price: 1055.55} 
    def get(self, request, establishment_compound_id):
        if has_permission(request.user, 'create_order'):
            try:
                price_table = PriceTable.objects.get(clientestablishment__client=request.user.client, 
                        clientestablishment__establishment__establishment_compound_id=establishment_compound_id)
            except PriceTable.DoesNotExist:
                return Response({"error":[_( "The price table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
                #  return Response({"error":[_( "The item was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            price_items = PriceItem.objects.filter(price_table=price_table, item__status=1)
            return Response(searchOnePriceItemToMakeOrderSerializer(price_items, many=True).data)
        return unauthorized_response

class fetchCategoriesToMakeOrder(APIView):
    def get(self, request, establishment_compound_id):    
        if has_permission(request.user, 'create_order'):
            try:
                comp= Company.objects.get(establishment__establishment_compound_id=establishment_compound_id, 
                        client_table=request.user.client.client_table)
                item_table = ItemTable.objects.get(company=comp)
            except Company.DoesNotExist:
                return Response({"error":[_( "You do not have access to this establishment.")]}, 
                        status=status.HTTP_404_NOT_FOUND) #TODO translate
            except ItemTable.DoesNotExist:
                return Response({"error":[_( "The company from this establishment does not have a item table.")]}, 
                        status=status.HTTP_404_NOT_FOUND) #TODO translate 
            categories = ItemCategory.objects.filter(item_table=item_table)
            serializer = CategoryPOSTSerializer(categories, many=True)
            return Response(serializer.data)
        return unauthorized_response

class OrderView(APIView):
    @transaction.atomic
    def get(self, request):
        if has_permission(request.user, 'get_orders'):
            if has_role(request.user, 'client_user'):
                orders = Order.objects.filter(client=request.user.client).all()
                return Response(OrderPOSTSerializer(orders, many=True).data)
            if has_role(request.user, 'agent'):
                orders = get_orders_by_agent(request.user)
                return Response(OrderPOSTSerializer(orders, many=True).data)
            orders = Order.objects.filter(company__contracting=request.user.contracting).all()
            return Response(OrderPOSTSerializer(orders, many=True).data)
        return unauthorized_response
    @swagger_auto_schema(request_body=OrderPOSTSerializer) 
    @transaction.atomic
    def post(self, request):
        if has_role(request.user, 'client_user'):
            serializer = OrderPOSTSerializer(data=request.data, context={"request": request})
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

class SpecificOrderView(APIView):
    def get(self, request, establishment_compound_id, order_number):
        if has_permission(request.user, 'get_orders'):
            if establishment_compound_id.split("&")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The order'))
            try:
                order = Order.objects.get(establishment__establishment_compound_id=establishment_compound_id, order_number=order_number)
            except Order.DoesNotExist:
                return not_found_response(object_name=_('The order'))
            if has_role(request.user, 'client_user'):
                if order.client != request.user.client:
                    return not_found_response(object_name=_('The order'))
            if req_user_is_agent_without_all_estabs(request.user):
                if not request.user.establishments.filter(id=order.establishment_id).first():
                    return not_found_response(object_name=_('The order'))
            return Response(OrderDetailsSerializer(order).data)
        return unauthorized_response
    @transaction.atomic
    @swagger_auto_schema(request_body=OrderPUTSerializer) 
    def put(self, request, establishment_compound_id, order_number):
        if has_permission(request.user, 'update_order_status') or has_role(request.user, 'client_user'):
            if establishment_compound_id.split("&")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The order'))
            try:
                order = Order.objects.get(establishment__establishment_compound_id=establishment_compound_id, order_number=order_number)
            except Order.DoesNotExist:
                return not_found_response(object_name=_('The order'))
            if has_role(request.user, 'client_user'):
                if order.client != request.user.client:
                    return not_found_response(object_name=_('The order'))
            if req_user_is_agent_without_all_estabs(request.user):
                if not request.user.establishments.filter(id=order.establishment_id).first():
                    return not_found_response(object_name=_('The order'))
            serializer = OrderPUTSerializer(order, data=request.data, partial=True, context={"request": request})
            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response(serializer.data)
                except Exception as error:
                    transaction.rollback()
                    print(error)
                    return unknown_exception_response(action=_('update order by client user'))
            return serializer_invalid_response(serializer.errors)
        return unauthorized_response
    #  @transaction.atomic
    #  def delete(self, request, establishment_compound_id, order_number):
        #  if has_permission(request.user, 'delete_order'):
            #  if establishment_compound_id.split("#")[0] != request.user.contracting.contracting_code:
                #  return not_found_response(object_name=_('The order'))
            #  try:
                #  order = Order.objects.get(establishment__establishment_compound_id=establishment_compound_id, order_number=order_number)
            #  except Order.DoesNotExist:
                #  return not_found_response(object_name=_('The order'))
            #  if order.status not in [0, 4, 5]:
                #  return error_response(detail=_("You cannot delete an order with a status other than 'Canceled', 'Invoiced' or 'Delivered'"), 
                    #  status=status.HTTP_400_BAD_REQUEST)
            #  try:
                #  order._request_user = request.user
                #  order.delete()
                #  return Response(_("Order deleted successfully"))
            #  except ProtectedError:
                #  return protected_error_response(object_name=_('order'))
            #  except Exception as error:
                #  print(error)
                #  return unknown_exception_response(action=_('delete order'))
        #  return unauthorized_response
