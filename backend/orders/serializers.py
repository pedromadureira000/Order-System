from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from core.facade import get_agent_companies, get_agent_item_tables, update_price_items_from_price_table
from core.models import Company
from core.validators import UserContracting, agent_has_access_to_this_item_table, agent_has_access_to_this_price_table, req_user_is_agent_without_all_estabs
from orders.models import ItemTable, Order, Item, ItemCategory, PriceTable, PriceItem

class ItemTableSerializer(serializers.ModelSerializer):
    contracting=serializers.HiddenField(default=UserContracting())
    class Meta:
        model = ItemTable
        fields =  ['item_table_compound_id' ,'item_table_code', 'contracting', 'description', 'note']
        read_only_fields =  ['item_table_compound_id']
        validators = [UniqueTogetherValidator(queryset=ItemTable.objects.all(), fields=['item_table_code', 'contracting'], 
            message="The field 'item_table_code' must be unique.")]

    def create(self, validated_data):
        # Create item_table_compound_id
        validated_data['item_table_compound_id'] = validated_data['contracting'].contracting_code + \
                "#" + validated_data['item_table_code']
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Not allow to update this fields
        validated_data['item_table_code'] = instance.item_table_code
        validated_data['contracting'] = instance.contracting
        return super().update(instance, validated_data)

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['item_compound_id', 'item_table', 'item_code', 'category', 'description', 'unit', 'barcode', 'status', 'image', 'technical_description'] 
        read_only_fields =  ['item_compound_id']
        validators = [UniqueTogetherValidator(queryset=Item.objects.all(), fields=['item_table', 'item_code'], 
            message="The field 'item_code' must be unique by 'item_table'.")]

    def validate(self, attrs):
        request_user = self.context['request'].user
        item_table = attrs.get('item_table')
        category = attrs.get('category')
        if self.context['method'] == 'post':
            # item_table belongs to user contracting
            if item_table.contracting != request_user.contracting:
                raise serializers.ValidationError(f"You cannot access this item_table.")
            # Category belongs to user contracting
            if category.item_table.contracting != request_user.contracting:
                raise serializers.ValidationError(f"You cannot access this category.")
            # Category must have the same item_table that the item item_table
            if category.item_table != item_table:
                raise serializers.ValidationError(f"You cannot choose this category, because it is from another item table.")
            # Agent without access to all establishments can't access an item from item_table which he doesn't have access.
            if req_user_is_agent_without_all_estabs(request_user) and not agent_has_access_to_this_item_table(request_user, item_table):
                raise serializers.ValidationError(f"You have no access to this item table.")
        if self.context['method'] == "put":
            if attrs.get('category'):
                # Category belongs to user contracting
                if category.item_table.contracting != request_user.contracting:
                    raise serializers.ValidationError(f"You cannot access this category.")
                # Category must have the same item_table that the item item_table
                if category.item_table != self.instance.item_table:
                    raise serializers.ValidationError(f"You cannot choose this category, because it is from another item table.")
                # Agent without access to all establishments can't access an item from item_table which he doesn't have access.
            if req_user_is_agent_without_all_estabs(request_user) and not \
                    agent_has_access_to_this_item_table(request_user, self.instance.item_table):
                raise serializers.ValidationError(f"You have no access to this item table.")
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data['item_compound_id'] = self.context['request'].user.contracting.contracting_code + \
                "#" + validated_data['item_table'].item_table_code + "#" + validated_data["item_code"]
        item = Item.objects.create(**validated_data)
        return item

    def update(self, instance, validated_data):
        # Not allow to update this fields
        validated_data['item_code'] = instance.item_code
        validated_data['item_table'] = instance.item_table
        return super().update(instance, validated_data)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['item_table', 'category_compound_id', 'category_code', 'description', 'note']
        read_only_fields =  ['category_compound_id']
        validators = [UniqueTogetherValidator(queryset=ItemCategory.objects.all(), fields=['item_table', 'category_code'], 
            message="The field 'category_code' must be unique by 'item_table'.")]

    def validate(self, attrs):
        request_user = self.context['request'].user
        item_table = attrs.get('item_table')
        if self.context['method'] == 'post':
            # item_table belongs to user contracting
            if item_table.contracting != request_user.contracting:
                raise serializers.ValidationError(f"You cannot access this item_table")
            # Agent without access to all establishments can't access an category from an item_table which he doesn't have access.
            if req_user_is_agent_without_all_estabs(request_user) and not agent_has_access_to_this_item_table(request_user, item_table):
                raise serializers.ValidationError(f"You cannot access this item_table")
        # If the request is for update the instance, some related fields may not be sent since 'parcial=True' is being used
        if self.context['method'] == 'put':
            item_table = self.instance.item_table
            # Agent without access to all establishments can't access an category from an item_table which he doesn't have access.
            if req_user_is_agent_without_all_estabs(request_user) and not agent_has_access_to_this_item_table(request_user, item_table):
                raise serializers.ValidationError(f"You cannot access this item_table")
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data['category_compound_id'] =  self.context['request'].user.contracting.contracting_code + \
                "#" + validated_data['item_table'].item_table_code + "#" + validated_data["category_code"]
        item_category = ItemCategory.objects.create(**validated_data)
        item_category.save()
        return item_category

    def update(self, instance, validated_data):
        # Not allow to update this fields
        validated_data['category_code'] = instance.category_code
        validated_data['item_table'] = instance.item_table
        return super().update(instance, validated_data)

class ForTablePriceItemSerializer(serializers.ModelSerializer):
    item = serializers.SlugRelatedField(slug_field='item_code', queryset=Item.objects.all())

    class Meta:
        model = PriceItem
        fields = ['item', 'unit_price']

class PriceTableSerializer(serializers.ModelSerializer):
    #  price_items = ForTablePriceItemSerializer(many=True)
    price_items = ForTablePriceItemSerializer(many=True)
    company = serializers.SlugRelatedField(slug_field='company_compound_id', queryset=Company.objects.all())

    class Meta:
        model = PriceTable
        fields = ['price_table_compound_id', 'company', 'price_items', 'table_code', 'description', 'note']
        validators = [UniqueTogetherValidator(queryset=ItemCategory.objects.all(), fields=['company', 'table_code'], 
            message="The field 'table_code' must be unique by 'company'.")]

    def validate(self, attrs):
        request_user = self.context['request'].user
        price_items = attrs.get('price_items')
        company = attrs.get('company')
        request_user_is_agent_without_all_estabs = req_user_is_agent_without_all_estabs(request_user)
        #--------------------------/ PriceItems
        # 'if clause' is used because it will work for post and put methods
        if price_items:
            if request_user_is_agent_without_all_estabs:
                agent_item_tables = get_agent_item_tables(request_user)
            for price_item in price_items:
                # If price_item is from the same contracting
                if price_item["item"].item_compound_id.split("#")[0] != request_user.contracting.contracting_code:
                    raise serializers.ValidationError(f"You cannot add this item as a item_price.")
                # If request user is agent without all estabs and have access to this item
                if request_user_is_agent_without_all_estabs and price_item["item"].item_table not in agent_item_tables:
                    #TODO test
                    raise serializers.ValidationError(f"You cannot add this item as a item_price.")
        #---------------------------/ Company
        if self.context['method'] == 'post':
            # Company is from the same contracting that request_user
            if company.contracting != request_user.contracting:
                raise serializers.ValidationError(f"You have no access to this company.")
            # User is agent without all estabs and don't have access to this company
            if request_user_is_agent_without_all_estabs and company not in get_agent_companies(request_user): #TODO test
                raise serializers.ValidationError(f"You have no access to this company.")
        if self.context['method'] == 'put':
            # Agent without access to all establishments should not access some price_tables
            if request_user_is_agent_without_all_estabs and not agent_has_access_to_this_price_table(request_user, self.instance):
                raise serializers.ValidationError(f"You cannot update this price table.")
        return super().validate(attrs)

    def create(self, validated_data):
        price_items = validated_data.pop('price_items')
        price_table = PriceTable.objects.create(company=validated_data['company'], **validated_data)
        price_table.save()
        price_items_list = []
        for price_item in price_items:
            price_items_list.append(PriceItem(item=price_item['item'], unit_price=price_item['unit_price'], price_table=price_table))
        price_table.price_items.bulk_create(price_items_list)
        return price_table

    def update(self, instance, validated_data):
        price_items = validated_data.get('price_items')
        if price_items or price_items == []:
            price_items = validated_data.pop('price_items')
            update_price_items_from_price_table(instance, price_items)
        return super().update(instance, validated_data)

#  class AssignPriceTableSerializer(serializers.Serializer):
    #  table_code = serializers.CharField(write_only=True)
    #  company_code = serializers.CharField(write_only=True)

#  class PriceItemSerializer(serializers.ModelSerializer):
    #  item = serializers.SlugRelatedField(slug_field='item_code', queryset=Item.objects.all())
    #  price_table = serializers.SlugRelatedField(slug_field='table_code', queryset=PriceTable.objects.all())

    #  class Meta:
        #  model = PriceItem
        #  fields = ['item', 'price_table', 'unit_price', 'date']
        #  read_only_fields =  ['date']

    #  def validate(self, attrs):
        #  try:
            #  item = Item.objects.get(item_code=attrs.get('item'))
            #  price_table = PriceTable.objects.get(table_code=attrs.get('price_table'))
        #  except Item.DoesNotExist:
            #  raise serializers.ValidationError(f"Item not found.")
        #  except PriceTable.DoesNotExist:
            #  raise serializers.ValidationError(f"Price table note found.")
        #  if item.contracting_company != self.context.get('currentUser').company:
            #  raise serializers.ValidationError(f"You cannot access this item.")
        #  if price_table.contracting_company != self.context.get('currentUser').company:
            #  raise serializers.ValidationError(f"You cannot access this price table.")
        #  return attrs

#  class SpecificPriceItemSerializer(serializers.ModelSerializer):
    #  item = serializers.SlugRelatedField(slug_field='item_code', read_only=True)
    #  price_table = serializers.SlugRelatedField(slug_field='table_code', read_only=True)

    #  class Meta:
        #  model = PriceItem
        #  fields = ['item', 'price_table','unit_price', 'date']


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['order_number', 'company', 'establishment', 'client_user', 'price_table', 'status', 'order_date', 'billing_date', 'order_amount', 'invoice_number', 'note']
