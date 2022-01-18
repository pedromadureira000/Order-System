from rest_framework import status, mixins, generics
from rest_framework.response import Response
from core.models import User
from orders.serializers import ItemSerializer, ItemUpdateSerializer, \
    BulkItemCreateSerializer, CategorySerializer, OrderSerializer, PriceTableSerializer, \
    PriceItemSerializer, AssignPriceTableSerializer
from orders.models import Order, Item, ItemCategory, PriceTable, PriceItem
from rest_framework.views import APIView
from rolepermissions.checkers import has_permission, has_role
from drf_yasg.utils import swagger_auto_schema


# --------------------------/ Item / --------------------------------------------

class ItemView(APIView):
    def get(self, request):
        if has_permission(request.user, 'get_items'):
            try:
                itens = Item.objects.all()
            except Item.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = ItemSerializer(itens, many=True)
            return Response(serializer.data)

        return Response({"error": "You don't have permissions to access this resource."},
                        status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        if has_permission(request.user, 'create_item'):
            if isinstance(request.data, dict):
                item = Item()
                serializer = ItemSerializer(item, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            if isinstance(request.data, list):
                serializer = BulkItemCreateSerializer(data=request.data, many=True)
                data = {}
                if serializer.is_valid():
                    data['success'] = 'criado com sucesso'
                    serializer.save()
                    return Response(data=data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "You don't have permissions to access this resource."},
                        status=status.HTTP_401_UNAUTHORIZED)


class SpecificItemView(APIView):
    def get(self, request, code):

      if has_permission(request.user, 'create_item'):
            try:
                item = Item.objects.get(item_code=code)
            except Item.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = ItemSerializer(item)
            return Response(serializer.data)

      return Response({"error": "You don't have permissions to access this resource."},
                        status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, code):
        if has_permission(request.user, 'create_item'):
            try:
                item = Item.objects.get(item_code=code)
            except Item.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = ItemUpdateSerializer(item, data=request.data)
            data = {}
            if serializer.is_valid():
                serializer.save()
                data['success'] = 'update successful'
                return Response(data=data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "You don't have permissions to access this resource."},
                        status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, code):
      if has_permission(request.user, 'create_item'):
            try:
                item = Item.objects.get(item_code=code)
            except Item.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            operation = item.delete()
            data = {}
            if operation:
                data['success'] = 'deleted successful'
            else:
                data['failure'] = 'delete failed'
            return Response(data=data)
      return Response({"error": "You don't have permissions to access this resource."},
                        status=status.HTTP_401_UNAUTHORIZED)


# --------------------------------/ Orders /---------------------------------/


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
      return Response({"error": "You don't have permissions to access this resource."},
                        status=status.HTTP_401_UNAUTHORIZED)


# -----------------------------------/ Category / ----------------------

class CategoryView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = CategorySerializer
    queryset = ItemCategory.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SpecificCategoryView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    serializer_class = CategorySerializer
    queryset = ItemCategory.objects.all()
    lookup_url_kwarg = 'code'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# -----------------------------------/ Price Table / ----------------------

class PriceTableView(APIView):
    def get(self, request):
        pricetables = PriceTable.objects.all()
        serializer = PriceTableSerializer(data=pricetables, many=True)
        serializer.is_valid() # i can't access serializer.data before access is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=PriceTableSerializer) 
    def post(self, request):
        serializer = PriceTableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SpecificPriceTableView(APIView):
    @swagger_auto_schema(request_body=PriceTableSerializer) 
    def put(self, request, table_code):
        #  if not table_code:
            #  return Response({"error": "'table_code' field is missing."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = PriceTable.objects.get(table_code=table_code)
            serializer = PriceTableSerializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PriceTable.DoesNotExist:
            return Response({"error": "Price table has not found."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print(error)
            return Response({"error": "Something went wrong when trying to update price table."}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=PriceTableSerializer) 
    def delete(self, request, table_code):
        try:
            instance = PriceTable.objects.get(table_code=table_code)
            instance.delete()
            return Response({"Successfully deleted"}, status=status.HTTP_200_OK)
        except PriceTable.DoesNotExist:
            return Response({"error": "Price table has not found."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print(error)
            return Response({"error": "Something went wrong when trying to delete price table."}, status=status.HTTP_400_BAD_REQUEST)


class AssignPriceTableView(APIView):
    @swagger_auto_schema(request_body=AssignPriceTableSerializer) 
    def post(self, request):
        serializer = AssignPriceTableSerializer(data=request.data)
        if serializer.is_valid():
            table_code = serializer.validated_data['table_code']
            company_code = serializer.validated_data['company_code']
            try:
                company = Company.objects.get(company_code=company_code)
                price_table = PriceTable.objects.get(table_code=table_code)
                company.price_table = price_table
                company.save()
                return Response("The price table has been assigned", status=status.HTTP_200_OK)
            except Company.DoesNotExist:
                return Response({"error": "Company has not found."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as error:
                print(error)
                return Response({"error": "Something went wrong when trying assign price table to user."},
                        status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# -----------------------------------/ PriceItem /-----------------------------

#  class PriceItemView(APIView):
    #  def get(self, request):
      #  if has_permission(request.user, 'create_item'):
            #  item_code = request.data.get('item_code')
            #  table_code = request.data.get('table_code')
            #  if not item_code or not table_code:
                #  return Response({"response": "Por favor envie os valores de 'item_code' e 'table_code'."},
                                #  status=status.HTTP_400_BAD_REQUEST)
            #  try:
                #  priceitem = PriceItem.objects.get(pricetable__table_code=table_code, item__item_code=item_code)

            #  except PriceItem.DoesNotExist:
                #  return Response(status=status.HTTP_404_NOT_FOUND)
            #  if not priceitem:
                #  return Response({"response": "Item preco nao encontrado."},
                                #  status=status.HTTP_404_NOT_FOUND)
            #  serializer = PriceItemSerializer(priceitem)
            #  return Response(serializer.data, status=status.HTTP_200_OK)

      #  return Response({"error": "You don't have permissions to access this resource."},
                        #  status=status.HTTP_401_UNAUTHORIZED)

    #  def post(self, request):
        #  item_code = request.data.get('item_code')
        #  table_code = request.data.get('table_code')
        #  if not item_code or not table_code:
            #  return Response({"response": "Por favor envie os valores de 'item_code' e 'table_code'."},
                            #  status=status.HTTP_400_BAD_REQUEST)
        #  try:
            #  pricetable = PriceTable.objects.get(table_code=table_code)
        #  except PriceTable.DoesNotExist:
            #  return Response({"response":"A tabela informada nao existe."}, status=status.HTTP_404_NOT_FOUND)
        #  try:
            #  item = Item.objects.get(item_code=item_code)
        #  except Item.DoesNotExist:
            #  return Response({"response": "O item informado nao existe."}, status=status.HTTP_404_NOT_FOUND)
        #  copy_data = request.data.copy()
        #  copy_data['item'] = item.pk
        #  copy_data['pricetable'] = pricetable.pk

        #  serializer = PriceItemSerializer(data=copy_data)
        #  if serializer.is_valid():
            #  serializer.save()
            #  return Response(serializer.data, status=status.HTTP_201_CREATED)
        #  return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #  def put(self, request):
        #  item_code = request.data.get('item_code')
        #  table_code = request.data.get('table_code')
        #  if not item_code or not table_code:
            #  return Response({"response": "Por favor envie os valores de 'item_code' e 'table_code'."},
                            #  status=status.HTTP_400_BAD_REQUEST)
        #  try:
            #  pricetable = PriceTable.objects.get(table_code=table_code)
        #  except PriceTable.DoesNotExist:
            #  return Response({"response":"A tabela informada nao existe."}, status=status.HTTP_404_NOT_FOUND)
        #  try:
            #  item = Item.objects.get(item_code=item_code)
        #  except Item.DoesNotExist:
            #  return Response({"response": "O item informado nao existe."}, status=status.HTTP_404_NOT_FOUND)
        #  copy_data = request.data.copy()
        #  copy_data['item'] = item.pk
        #  copy_data['pricetable'] = pricetable.pk
        #  try:
            #  instance = PriceItem.objects.get(item=copy_data['item'], pricetable=copy_data['pricetable'])
        #  except PriceItem.DoesNotExist:
            #  return Response({"response": "O PriceItem imformado nao existe."}, status=status.HTTP_404_NOT_FOUND)
        #  serializer = PriceItemSerializer(instance, data=copy_data)
        #  if serializer.is_valid():
            #  serializer.save()
            #  return Response(serializer.data, status=status.HTTP_201_CREATED)
        #  return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #  def delete(self, request):
      #  if has_permission(request.user, 'create_item'):
            #  item_code = request.data.get('item_code')
            #  table_code = request.data.get('table_code')
            #  if not item_code or not table_code:
                #  return Response({"response": "Por favor envie os valores de 'item_code' e 'table_code'."},
                                #  status=status.HTTP_400_BAD_REQUEST)
            #  try:
                #  priceitem = PriceItem.objects.get(pricetable__table_code=table_code, item__item_code=item_code)

            #  except PriceItem.DoesNotExist:
                #  return Response(status=status.HTTP_404_NOT_FOUND)
            #  if not priceitem:
                #  return Response({"response": "Item preco nao encontrado."},
                                #  status=status.HTTP_404_NOT_FOUND)
            #  operation = priceitem.delete()
            #  data = {}
            #  if operation:
                #  data['success'] = 'deleted successful'
            #  else:
                #  data['failure'] = 'delete failed'
            #  return Response(data, status=status.HTTP_200_OK)

      #  return Response({"error": "You don't have permissions to access this resource."},
                        #  status=status.HTTP_401_UNAUTHORIZED)
