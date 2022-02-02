from rest_framework import serializers
from orders.models import Order, Item, ItemCategory, PriceTable, PriceItem


# -------------------------/ item / --------------------------------

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['name', 'item_code','category', 'description', 'unit', 'barcode', 'active', 'image', 'note'] 

    def create(self, validated_data):
        contracting_company = self.context.get('request_user').company
        item = Item.objects.create(contracting_company=contracting_company, **validated_data)
        item.save()
        return item


# --------------------------------------/ order / ----------------------------


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['company', 'user', 'status', 'order_date', 'billing_date', 'order_amount', 'table_code', 'invoice_number']


# --------------------------------/ Category / ------------------------------------


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['category_code', 'name', 'description', 'note']

    def create(self, validated_data):
        contracting_company = self.context.get('request_user').company
        item_category = ItemCategory.objects.create(contracting_company=contracting_company, **validated_data)
        item_category.save()
        return item_category


# ---------------------------------/ PriceItem /-------------------------------

class PriceItemSerializer(serializers.ModelSerializer):
    item = serializers.SlugRelatedField(slug_field='item_code', queryset=Item.objects.all())
    pricetable = serializers.SlugRelatedField(slug_field='table_code', queryset=PriceTable.objects.all())

    class Meta:
        model = PriceItem
        fields = ['item', 'pricetable', 'price_unit', 'date']
        read_only_fields =  ['date']

    def validate(self, attrs):
        try:
            item = Item.objects.get(item_code=attrs.get('item'))
            pricetable = PriceTable.objects.get(table_code=attrs.get('pricetable'))
        except Item.DoesNotExist:
            raise serializers.ValidationError(f"Item not found.")
        except PriceTable.DoesNotExist:
            raise serializers.ValidationError(f"Price table note found.")
        if item.contracting_company != self.context.get('currentUser').company:
            raise serializers.ValidationError(f"You cannot access this item.")
        if pricetable.contracting_company != self.context.get('currentUser').company:
            raise serializers.ValidationError(f"You cannot access this price table.")
        return attrs

class SpecificPriceItemSerializer(serializers.ModelSerializer):
    item = serializers.SlugRelatedField(slug_field='item_code', read_only=True)
    pricetable = serializers.SlugRelatedField(slug_field='table_code', read_only=True)

    class Meta:
        model = PriceItem
        fields = ['item', 'pricetable','price_unit', 'date']


class ForTablePriceItemSerializer(serializers.ModelSerializer):
    item = serializers.SlugRelatedField(slug_field='item_code', queryset=Item.objects.all())

    class Meta:
        model = PriceItem
        fields = ['item', 'price_unit']

# ------------------------------/ Price table / --------------------------------

class PriceTableSerializer(serializers.ModelSerializer):
    #  price_items = ForTablePriceItemSerializer(many=True)
    price_items = ForTablePriceItemSerializer(many=True)

    class Meta:
        model = PriceTable
        fields = ['table_code', 'name', 'description', 'price_items', 'note']


    def validate_price_items(self, value):
        for price_item in value:
            if price_item["item"].contracting_company != self.context.get('request_user').company:
                raise serializers.ValidationError(f"You cannot add this item as a item_price.")
        return value

    def validate_table_code(self, value):
        if self.context.get('method') == "put":
            price_table = PriceTable.objects.get(table_code=value)
            if price_table.contracting_company != self.context.get('request_user').company:
                raise serializers.ValidationError(f"You cannot update this price table.")
            return value
        if self.context.get('method') == "post":
            return value

    def create(self, validated_data):
        price_items = validated_data.pop('price_items')
        price_table = PriceTable.objects.create(contracting_company=self.context.get('request_user').company, **validated_data)
        price_table.save()
        for priceitem in price_items:
            PriceItem.objects.create(pricetable=price_table, **priceitem)
        return price_table

    def update(self, instance, validated_data):
        #  price_items_data = validated_data.pop('price_items')    
        #code above will return ('item', <Item: fiat>), ('price_unit', Decimal('10.00'))
        price_items_data = ForTablePriceItemSerializer(validated_data.pop('price_items'), many=True).data  
        #Code above return ('item', 1), ('price_unit', '10.00')
        query = instance.price_items.all()
        price_items_query_serialized = ForTablePriceItemSerializer(query, many=True).data
        #  price_items_query_serialized = ForTablePriceItemSerializer(data=query, many=True)
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
            price_item_object_to_delete = PriceItem.objects.get(pricetable=instance, item__item_code=priceitem[0][1]).delete()
            #  print('got it(todelete)--:', price_item_object_to_delete)
        # Create
        for priceitem in to_create:
            price_item_object_to_create = PriceItem(pricetable=instance, item=Item.objects.get(item_code=priceitem[0][1]), price_unit=priceitem[1][1])
            price_item_object_to_create.save()
            #  print('got it--(tocreate):', price_item_object_to_create)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance


class AssignPriceTableSerializer(serializers.Serializer):
    table_code = serializers.CharField(write_only=True)
    company_code = serializers.CharField(write_only=True)

