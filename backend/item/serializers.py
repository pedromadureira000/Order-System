from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from organization.facade import get_agent_companies 
from item.facade import  update_price_items_from_price_table
from organization.models import Company
from organization.validators import UserContracting 
from item.validators import agent_has_access_to_this_item_table
from item.models import ItemTable, Item, ItemCategory, PriceTable, PriceItem
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import NotFound
from settings.utils import positive_number

class ItemTableSerializer(serializers.ModelSerializer):
    contracting=serializers.HiddenField(default=UserContracting())
    class Meta:
        model = ItemTable
        fields =  ['item_table_compound_id' ,'item_table_code', 'contracting', 'description', 'note']
        read_only_fields =  ['item_table_compound_id']
        validators = [UniqueTogetherValidator(queryset=ItemTable.objects.all(), fields=['item_table_code', 'contracting'], 
            message=_("The 'item_table_code' field must be unique."))]

    def create(self, validated_data):
        # Create item_table_compound_id
        validated_data['item_table_compound_id'] = validated_data['contracting'].contracting_code + \
                "&" + validated_data['item_table_code']
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Not allow to update this fields
        if validated_data.get('item_table_code'): validated_data.pop('item_table_code')
        return super().update(instance, validated_data)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['item_table', 'category_compound_id', 'category_code', 'description', 'note']
        read_only_fields =  ['category_compound_id']
        validators = [UniqueTogetherValidator(queryset=ItemCategory.objects.all(), fields=['item_table', 'category_code'], 
            message=_("The 'category_code' field must be unique by 'item_table'."))]

    def validate_item_table(self, value):
        request_user = self.context['request'].user
        if self.context['request'].method == 'POST':
            # If the request is for update the instance, some related fields may not be sent since 'parcial=True' is being used
            # item_table belongs to user contracting
            if value.contracting != request_user.contracting:
                raise NotFound(detail={"detail": [_("Item table not found.")]})
            # Agent without access to all establishments can't access an category from an item_table which he doesn't have access.
            if self.context['request_user_is_agent_without_all_estabs'] and not \
                    agent_has_access_to_this_item_table(request_user, value):
                raise NotFound(detail={"detail": [_("Item table not found.")]})
        return value

    def create(self, validated_data):
        validated_data['category_compound_id'] =  self.context['request'].user.contracting.contracting_code + \
                "&" + validated_data['item_table'].item_table_code + "&" + validated_data["category_code"]
        item_category = ItemCategory.objects.create(**validated_data)
        item_category.save()
        return item_category

    def update(self, instance, validated_data):
        # Not allow to update this fields
        if validated_data.get('category_code'): validated_data.pop('item_table_code')
        if validated_data.get('item_table'): validated_data.pop('item_table')
        return super().update(instance, validated_data)

class ItemSerializer(serializers.ModelSerializer):
    item_table = serializers.SlugRelatedField(slug_field='item_table_compound_id', queryset=ItemTable.objects.all())
    category = serializers.SlugRelatedField(slug_field='category_compound_id', queryset=ItemCategory.objects.all())
    class Meta:
        model = Item
        fields = ['item_compound_id', 'item_table', 'item_code', 'category', 'description', 'unit', 'barcode', 'status', 'image', 'technical_description'] 
        read_only_fields =  ['item_compound_id']
        validators = [UniqueTogetherValidator(queryset=Item.objects.all(), fields=['item_table', 'item_code'], 
            message=_("The 'item_code' field  must be unique by 'item_table'."))]

    def validate(self, attrs):
        request_user = self.context['request'].user
        item_table = attrs.get('item_table')
        category = attrs.get('category')
        if self.context['request'].method == 'POST':
            # item_table belongs to user contracting
            if item_table.contracting != request_user.contracting:
                raise NotFound(detail={"detail": [_("Item table not found.")]})
            # Category must have the same item_table that the item item_table
            if category.item_table != item_table:
                raise serializers.ValidationError(_("You cannot choose this category because it is from another item table."))
            # Agent without access to all establishments can't access an item from item_table which he doesn't have access.
            if self.context['request_user_is_agent_without_all_estabs'] and not agent_has_access_to_this_item_table(request_user, item_table):
                raise NotFound(detail={"detail": [_("Item table not found.")]})

        if self.context['request'].method == 'PUT':
            # Verify if agent can assign this category.
            if attrs.get('category'):
                # Category belongs to user contracting
                if category.item_table.contracting != request_user.contracting:
                    raise NotFound(detail={"detail": [_("Item category not found.")]})
                # Category must have the same item_table that the item item_table
                if category.item_table != self.instance.item_table:
                    raise serializers.ValidationError(_("You cannot choose this category because it is from another item table."))
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data['item_compound_id'] = self.context['request'].user.contracting.contracting_code + \
                "&" + validated_data['item_table'].item_table_code + "&" + validated_data["item_code"]
        item = Item.objects.create(**validated_data)
        return item

    def update(self, instance, validated_data):
        # Not allow to update this fields
        if validated_data.get('item_code'): validated_data.pop('item_code')
        if validated_data.get('item_table'): validated_data.pop('item_table')
        return super().update(instance, validated_data)

class ForTablePriceItemSerializer(serializers.ModelSerializer):
    item = serializers.SlugRelatedField(slug_field='item_compound_id', queryset=Item.objects.all())
    unit_price = serializers.DecimalField(max_digits=11, decimal_places=2,required=True, validators=[positive_number])

    class Meta:
        model = PriceItem
        fields = ['item', 'unit_price']

    def validate_item(self, value):
        request_user_is_agent_without_all_estabs = self.context['req_user_is_agent_without_all_estabs']
        request_user = self.context['request'].user
        item_id =  value.item_compound_id
        if request_user_is_agent_without_all_estabs and not agent_has_access_to_this_item_table(request_user,value.item_table):
            raise NotFound(detail={"detail": [_("Item with id '{item_id}' was not found.").format(item_id=item_id)]})
        return value

class PriceTableGetSerializer(serializers.ModelSerializer):
    company = serializers.SlugRelatedField(slug_field='company_compound_id', read_only=True)

    class Meta:
        model = PriceTable
        fields = ['price_table_compound_id', 'company', 'table_code', 'description', 'note']
        read_only_fields = fields

class PriceTablePOSTSerializer(serializers.ModelSerializer):
    price_items = ForTablePriceItemSerializer(many=True)
    company = serializers.SlugRelatedField(slug_field='company_compound_id', queryset=Company.objects.all())

    class Meta:
        model = PriceTable
        fields = ['price_table_compound_id', 'company', 'price_items', 'table_code', 'description', 'note']
        read_only_fields = ['price_table_compound_id']
        validators = [UniqueTogetherValidator(queryset=PriceTable.objects.all(), fields=['company', 'table_code'], 
            message=_("The 'table_code' field must be unique by 'company'."))]

    def validate(self, attrs):
        request_user = self.context['request'].user
        company = attrs.get('company')
        price_items = attrs.get('price_items')
        check_for_duplicate_values = []
        if price_items or price_items == []:
            for price_item in price_items:
                # Check if the item belongs to the company's item table
                if price_item['item'].item_table != company.item_table:
                    raise NotFound(detail={"detail": [_("The item must belong to the company that owns the price table.")]})
                # Deny duplicate values
                if price_item in check_for_duplicate_values:
                    raise serializers.ValidationError(_("There are duplicate price items."))
                check_for_duplicate_values.append(price_item)

        #---------------------------/ Company
        # Company is from the same contracting that request_user
        if company.contracting != request_user.contracting:
            raise NotFound(detail={"detail": [_("Company not found.")]})
        # User is agent without all estabs and don't have access to this company
        if self.context['req_user_is_agent_without_all_estabs'] and company not in get_agent_companies(request_user):
            raise NotFound(detail={"detail": [_("Company not found.")]})
        return super().validate(attrs)

    def create(self, validated_data):
        price_items = validated_data.pop('price_items')
        validated_data['price_table_compound_id'] = self.context['request'].user.contracting.contracting_code + \
                "&" + validated_data['company'].company_code + "&" + validated_data["table_code"]
        price_table = PriceTable.objects.create(**validated_data)
        price_table.save()
        price_items_list = []
        for price_item in price_items:
            price_items_list.append(PriceItem(item=price_item['item'], unit_price=price_item['unit_price'], price_table=price_table))
        price_table.price_items.bulk_create(price_items_list)
        return price_table

class SpecificPriceTablePUTSerializer(serializers.ModelSerializer):
    price_items = ForTablePriceItemSerializer(many=True)
    company = serializers.SlugRelatedField(slug_field='company_compound_id', read_only=True)

    class Meta:
        model = PriceTable
        fields = ['price_table_compound_id', 'company', 'price_items', 'table_code', 'description', 'note']
        read_only_fields = ['price_table_compound_id', 'company', 'table_code']

    def validate(self, attrs):
        price_items = attrs.get('price_items')
        check_for_duplicate_values = []
        if price_items or price_items == []:
            for price_item in price_items:
                # Check if the item belongs to the company's item table
                if price_item['item'].item_table != self.instance.company.item_table:
                    raise NotFound(detail={"detail": [_("The item must belong to the company that owns the price table.")]})
                # Deny duplicate values
                if price_item in check_for_duplicate_values:
                    raise serializers.ValidationError(_("There are duplicate price items."))
                check_for_duplicate_values.append(price_item)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        if validated_data.get('table_code'): validated_data.pop('table_code')
        if validated_data.get('company'): validated_data.pop('company')
        price_items = validated_data.get('price_items')
        if price_items or price_items == []:
            price_items = validated_data.pop('price_items')
            update_price_items_from_price_table(instance, price_items)
        return super().update(instance, validated_data)

class SpecificPriceItemSerializer(serializers.ModelSerializer):
    item = serializers.SlugRelatedField(slug_field='item_compound_id', read_only=True)
    price_table = serializers.SlugRelatedField(slug_field='price_table_compound_id', read_only=True)
    unit_price = serializers.DecimalField(max_digits=11, decimal_places=2,required=True, validators=[positive_number])
    class Meta:
        model = PriceItem
        fields = ['item', 'price_table', 'unit_price', 'last_modified', 'creation_date']
        read_only_fields =  ['item', 'price_table', 'last_modified', 'creation_date']
