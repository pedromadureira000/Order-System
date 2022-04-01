from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from user.validators import req_user_is_agent_without_all_estabs
from .facade import get_orders_by_agent
from .serializers import OrderDetailsSerializer, OrderPOSTSerializer,OrderPUTSerializer
from .models import Order
from rest_framework.views import APIView
from rolepermissions.checkers import has_permission, has_role
from drf_yasg.utils import swagger_auto_schema
from settings.response_templates import not_found_response, serializer_invalid_response, unauthorized_response, unknown_exception_response
from django.utils.translation import gettext_lazy as _

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
            try:
                order = Order.objects.get(establishment__establishment_compound_id=establishment_compound_id, order_number=order_number)
            except Order.DoesNotExist:
                return not_found_response(object_name=_('The order'))
            if req_user_is_agent_without_all_estabs(request.user):
                if order.establishment not in request.user.establishments.all(): #TODO get_or_none. Avoid search for all
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
                if order.establishment not in request.user.establishments.all(): #TODO get_or_none. Avoid search for all
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
