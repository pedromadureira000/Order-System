from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from item.models import ItemCategory, ItemTable, PriceItem, PriceTable
from item.serializers import CategoryPOSTSerializer
from organization.facade import get_clients_by_agent
from organization.models import Client, Company, Establishment
from user.validators import req_user_is_agent_without_all_estabs
from .facade import fetch_comps_with_estabs_to_fill_filter_selectors_to_search_orders, fetch_comps_with_estabs_to_fill_filter_selectors_to_search_orders_by_agent, fetch_comps_with_estabs_to_fill_filter_selectors_to_search_orders_by_client_user, get_order_details, get_order_history, get_orders_by_agent
from .serializers import ClientsToFillFilterSelectorsToSearchOrdersSerializer, CompanyWithEstabsSerializer, OrderDetailsSerializer, OrderGetSerializer, OrderHistorySerializer, OrderPOSTSerializer,OrderPUTSerializer, fetchClientEstabsToCreateOrderSerializer, searchOnePriceItemToMakeOrderSerializer
from .models import Order, OrderHistory
from rest_framework.views import APIView
from rolepermissions.checkers import has_permission, has_role
from drf_yasg.utils import swagger_auto_schema
from settings.response_templates import not_found_response, serializer_invalid_response, unauthorized_response, unknown_exception_response
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi

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

# return Response({"error":[_( "The item was not found.")]}, status=status.HTTP_404_NOT_FOUND)
class SearchPriceItemsToMakeOrder(APIView):
    def get(self, request, establishment_compound_id, category_compound_id, item_description):
        if has_permission(request.user, 'create_order'):
            try:
                price_table = PriceTable.objects.get(clientestablishment__client=request.user.client, 
                        clientestablishment__establishment__establishment_compound_id=establishment_compound_id)
            except PriceTable.DoesNotExist:
                return Response({"error":[_( "The price table was not found.")]}, status=status.HTTP_404_NOT_FOUND)
            if item_description == 'dontsearchanyitemdescription':
                item_description = ''
            if category_compound_id == 'all':
                price_items = PriceItem.objects.filter(price_table=price_table, item__status=1, 
                    item__description__icontains=item_description)
            else:
                price_items = PriceItem.objects.filter(price_table=price_table, item__status=1, 
                    item__category__category_compound_id=category_compound_id, item__description__icontains=item_description)
            return Response(searchOnePriceItemToMakeOrderSerializer(price_items, many=True).data)
        return unauthorized_response

class fetchCategoriesToMakeOrderAndGetPriceTableInfo(APIView):
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
            # Get price table description and code
            try: 
                price_table = PriceTable.objects.get(clientestablishment__establishment__establishment_compound_id=establishment_compound_id, 
                        clientestablishment__client_id=request.user.client_id)
            except PriceTable.DoesNotExist:
                return Response({"error":[_( "The price table was not found.")]}, status=status.HTTP_404_NOT_FOUND) 
            return Response({'categories': serializer.data, 'price_table': {"description": price_table.description, "table_code": price_table.table_code}})
        return unauthorized_response
 
class fetchDataToFillFilterSelectorsToSearchOrders(APIView):
    def get(self, request):    
        if has_permission(request.user, 'get_orders'):
            if has_role(request.user, 'client_user'):
                comps_with_estabs = fetch_comps_with_estabs_to_fill_filter_selectors_to_search_orders_by_client_user(request.user)
                comps_with_estabs_serializer = CompanyWithEstabsSerializer(comps_with_estabs, many=True)
                return Response(comps_with_estabs_serializer.data)
            if req_user_is_agent_without_all_estabs(request.user):
                comps_with_estabs = fetch_comps_with_estabs_to_fill_filter_selectors_to_search_orders_by_agent(request.user)
                comps_with_estabs_serializer = CompanyWithEstabsSerializer(comps_with_estabs, many=True)
                return Response(comps_with_estabs_serializer.data)
            comps_with_estabs = fetch_comps_with_estabs_to_fill_filter_selectors_to_search_orders(request.user)
            comps_with_estabs_serializer = CompanyWithEstabsSerializer(comps_with_estabs, many=True)
            return Response(comps_with_estabs_serializer.data)
        return unauthorized_response

class fetchClientsToFillFilterSelectorToSearchOrders(APIView):
    def get(self, request):    
        if has_permission(request.user, 'get_orders') and not has_role(request.user, 'client_user'):
            if req_user_is_agent_without_all_estabs(request.user):
                clients = get_clients_by_agent(request.user)
                client_serializer = ClientsToFillFilterSelectorsToSearchOrdersSerializer(clients, many=True)
                return Response(client_serializer.data)
            clients = Client.objects.filter(client_table__contracting_id=request.user.contracting_id)
            client_serializer = ClientsToFillFilterSelectorsToSearchOrdersSerializer(clients, many=True)
            return Response(client_serializer.data)
        return unauthorized_response

company_query_string = openapi.Parameter('company', openapi.IN_QUERY, description="company_compound_id", type=openapi.TYPE_STRING)
establishment_query_string = openapi.Parameter('establishment', openapi.IN_QUERY, description="establishment_compound_id", 
        type=openapi.TYPE_STRING)
client_query_string = openapi.Parameter('client', openapi.IN_QUERY, description="client_compound_id", type=openapi.TYPE_STRING)
invoice_number_query_string = openapi.Parameter('invoice_number', openapi.IN_QUERY, description="Order invoice_number field.", 
        type=openapi.TYPE_STRING)
order_number_query_string = openapi.Parameter('order_number', openapi.IN_QUERY, description="Order order_number field.", type=openapi.TYPE_STRING)
#  period_query_string = openapi.Parameter('period', openapi.IN_QUERY, description="Period in ?? format.", type=openapi.TYPE_STRING)
status_query_string = openapi.Parameter('status', openapi.IN_QUERY, description="pending = Typing, Transferred or Registered; 0 = Canceled; 1 = Typing; 2 = Transferred; 3 = Registered; 4 = Invoiced; 5 = Delivered", type=openapi.TYPE_STRING)
class OrderView(APIView):
    @transaction.atomic
    @swagger_auto_schema(manual_parameters=[company_query_string, establishment_query_string, client_query_string, 
        invoice_number_query_string, order_number_query_string, status_query_string]) 
    def get(self, request):
        if has_permission(request.user, 'get_orders'):
            kwargs = {}
            if request.GET.get("company"): kwargs.update({"company__company_compound_id": request.GET.get("company")})
            if request.GET.get("establishment"): kwargs.update({"establishment__establishment_compound_id": request.GET.get("establishment")})
            if request.GET.get("client"): kwargs.update({"client__client_compound_id": request.GET.get("client")})
            if request.GET.get("invoice_number"): kwargs.update({"invoice_number": request.GET.get("invoice_number")})
            if request.GET.get("order_number"): kwargs.update({"order_number": request.GET.get("order_number")})
            #  if request.GET.get("period"): kwargs.update({"period": request.GET.get("period")})
            if request.GET.get("status"): kwargs.update({"status": request.GET.get("status")})
            #  print('>>>>>>>kwargs: ', kwargs)
            if kwargs.get("status") and kwargs["status"] == "pending":
                kwargs.pop("status")
                kwargs.update({"status__in": [1,2,3] })
            if has_role(request.user, 'client_user'):
                if kwargs.get("client"): kwargs.pop("client")
                orders = Order.objects.filter(client=request.user.client, **kwargs )
                return Response(OrderGetSerializer(orders, many=True).data)
            if req_user_is_agent_without_all_estabs(request.user):
                orders = get_orders_by_agent(request.user).filter(**kwargs)
                return Response(OrderGetSerializer(orders, many=True).data)
            orders = Order.objects.filter(company__contracting=request.user.contracting, **kwargs)
            return Response(OrderGetSerializer(orders, many=True).data)
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
    def get(self, request, client_compound_id, establishment_compound_id, order_number):
        if has_permission(request.user, 'get_orders'):
            if client_compound_id.split("*")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The client'))
            if establishment_compound_id.split("*")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The order'))
            # Client user can't access order from another client
            if has_role(request.user, 'client_user'):
                if client_compound_id != request.user.client.client_compound_id:
                    return not_found_response(object_name=_('The order'))
            # Agent without all estabs can't access order from some clients
            if req_user_is_agent_without_all_estabs(request.user):
                if not request.user.establishments.filter(establishment_compound_id=establishment_compound_id).first():
                    return not_found_response(object_name=_('The order'))
            try:
                order = get_order_details(client_compound_id, establishment_compound_id, order_number)
            except Order.DoesNotExist:
                return not_found_response(object_name=_('The order'))
            return Response(OrderDetailsSerializer(order).data)
        return unauthorized_response
    @transaction.atomic
    @swagger_auto_schema(request_body=OrderPUTSerializer) 
    def put(self, request, client_compound_id, establishment_compound_id, order_number):
        if has_permission(request.user, 'update_order_status') or has_role(request.user, 'client_user'):
            if client_compound_id.split("*")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The client'))
            if establishment_compound_id.split("*")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The order'))
            try:
                order = Order.objects.get(client__client_compound_id=client_compound_id, 
                        establishment__establishment_compound_id=establishment_compound_id, order_number=order_number)
            except Order.DoesNotExist:
                return not_found_response(object_name=_('The order'))
            if has_role(request.user, 'client_user'):
                if order.client != request.user.client:
                    return not_found_response(object_name=_('The order'))
            if req_user_is_agent_without_all_estabs(request.user):
                if not request.user.establishments.filter(id=order.establishment_id).first():
                    return not_found_response(object_name=_('The order'))
            serializer = OrderPUTSerializer(order, data=request.data, context={"request": request})
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

class OrderHistoryView(APIView):
    @transaction.atomic
    def get(self, request, client_compound_id, establishment_compound_id, order_number):
        if has_permission(request.user, 'get_orders'):
            if client_compound_id.split("*")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The client'))
            if establishment_compound_id.split("*")[0] != request.user.contracting.contracting_code:
                return not_found_response(object_name=_('The order'))
            # Client user can't access order from another client
            if has_role(request.user, 'client_user'):
                if client_compound_id != request.user.client.client_compound_id:
                    return not_found_response(object_name=_('The order'))
            # Agent without all estabs can't access order from some clients
            if req_user_is_agent_without_all_estabs(request.user):
                if not request.user.establishments.filter(establishment_compound_id=establishment_compound_id).first():
                    return not_found_response(object_name=_('The order'))
            try:
                order_history = get_order_history(client_compound_id, establishment_compound_id, order_number)
            except OrderHistory.DoesNotExist:
                return not_found_response(object_name=_('The order history'))
            return Response(OrderHistorySerializer(order_history, many=True).data)
        return unauthorized_response
