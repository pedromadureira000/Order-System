from rest_framework import serializers
from orders.models import Order, Item, ItemCategory, PriceTable, PriceItem


# -------------------------/ item / --------------------------------


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['image', 'item_code', 'category', 'name', 'description', 'unit', 'barcode', 'active', 'id']


# cannot update itens if Serializer have the primary key field
class ItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['category', 'name', 'description', 'unit', 'barcode', 'active', 'image']


class BulkItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['item_code', 'category', 'name', 'description', 'unit', 'barcode', 'active']

    def create(self, validated_data):
        instance = Item(**validated_data)
        instance.save()
        return instance

# --------------------------------------/ order / ----------------------------


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['company', 'user', 'status', 'order_date', 'billing_date', 'order_amount']


# --------------------------------/ Category / ------------------------------------


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['id', 'category_code', 'verbose_name', 'description']


# ---------------------------------/ PriceItem /-------------------------------

class PriceItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = PriceItem
        fields = ['item', 'price_unit']


# ------------------------------/ sales table / --------------------------------

class PriceTableSerializer(serializers.ModelSerializer):
    price_items = PriceItemSerializer(many=True)

    class Meta:
        model = PriceTable
        fields = ['table_code', 'verbose_name', 'description', 'price_items']

    def create(self, validated_data):
        print(validated_data)
        price_items = validated_data.pop('price_items')
        salestable = PriceTable.objects.create(**validated_data)
        for priceitem in price_items:
            PriceItem.objects.create(pricetable=salestable, **priceitem)
        return salestable

    def update(self, instance, validated_data):
        #  price_items_data = validated_data.pop('price_items')    
        #code above will return ('item', <Item: fiat>), ('price_unit', Decimal('10.00'))
        price_items_data = PriceItemSerializer(validated_data.pop('price_items'), many=True).data  
        #Code above return ('item', 1), ('price_unit', '10.00')
        query = instance.price_items.all()
        price_items_query_serialized = PriceItemSerializer(query, many=True).data
        #  price_items_query_serialized = PriceItemSerializer(data=query, many=True)
        #  price_items_query_serialized.is_valid()
        #  price_items_query_serialized = price_items_query_serialized.data
        price_items_query_list = []
        for price_item in price_items_query_serialized:
            new_price_item = list()
            for k, v in price_item.items():
                new_price_item.append((k, v))
            price_items_query_list.append(tuple(new_price_item))
        price_items_query_set = set(price_items_query_list)
        #  print("price_items_query_set: ", price_items_query_set)
        price_items_data_list = []
        for price_item in price_items_data:
            new_price_item = list()
            for k, v in price_item.items():
                new_price_item.append((k, v))
            price_items_data_list.append(tuple(new_price_item))
        price_items_data_set = set(price_items_data_list)
        #  print('price_items_data_set: ', price_items_data_set )
        intersection = price_items_query_set.intersection(price_items_data_set)
        to_delete = price_items_query_set.difference(intersection)
        to_create = price_items_data_set.difference(price_items_query_set)

        #  print("INTERSECTION",intersection )
        #  print("to delete",to_delete )
        #  print("to create", to_create)

        # Delete
        for priceitem in to_delete:
            price_item_object_to_delete = PriceItem.objects.get(pricetable=instance, item=priceitem[0][1]).delete()
            #  print('got it(todelete)--:', price_item_object_to_delete)
        # Create
        for priceitem in to_create:
            price_item_object_to_create = PriceItem(pricetable=instance, item=Item.objects.get(id=priceitem[0][1]), price_unit=priceitem[1][1])
            price_item_object_to_create.save()
            #  print('got it--(tocreate):', price_item_object_to_create)
        instance.verbose_name = validated_data.get('verbose_name', instance.verbose_name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance




