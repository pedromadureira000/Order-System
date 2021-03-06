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
from user.validators import req_user_is_agent_without_all_estabs

class ItemTablePOSTSerializer(serializers.ModelSerializer):
    contracting_id=serializers.HiddenField(default=UserContracting())
    class Meta:
        model = ItemTable
        fields =  ['item_table_compound_id' ,'item_table_code', 'contracting_id', 'description', 'note']
        read_only_fields =  ['item_table_compound_id']
        validators = [UniqueTogetherValidator(queryset=ItemTable.objects.all(), fields=['item_table_code', 'contracting_id'], 
            message=_("The 'item_table_code' field must be unique."))]

    def create(self, validated_data):
        # Create item_table_compound_id
        validated_data['item_table_compound_id'] = validated_data['contracting_id'] + \
                "*" + validated_data['item_table_code']
        return super().create(validated_data)

class ItemTablePUTSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemTable
        fields =  ['item_table_compound_id' ,'item_table_code', 'description', 'note']
        read_only_fields =  ['item_table_compound_id','item_table_code']

class CategoryPOSTSerializer(serializers.ModelSerializer):
    item_table = serializers.SlugRelatedField(slug_field='item_table_compound_id', queryset=ItemTable.objects.all())
    class Meta:
        model = ItemCategory
        fields = ['item_table', 'category_compound_id', 'category_code', 'description', 'note']
        read_only_fields =  ['category_compound_id']
        validators = [UniqueTogetherValidator(queryset=ItemCategory.objects.all(), fields=['item_table', 'category_code'], 
            message=_("The 'category_code' field must be unique by 'item_table'."))]

    def validate_item_table(self, value):
        request_user = self.context['request'].user
        # If the request is for update the instance, some related fields may not be sent since 'parcial=True' is being used
        # item_table belongs to user contracting
        if value.contracting_id != request_user.contracting_id:
            raise NotFound(detail={"error": [_("Item table not found.")]})
        # Agent without access to all establishments can't access an category from an item_table which he doesn't have access.
        if req_user_is_agent_without_all_estabs(self.context['request'].user) and not \
                agent_has_access_to_this_item_table(request_user, value):
            raise NotFound(detail={"error": [_("Item table not found.")]})
        return value

    def create(self, validated_data):
        validated_data['category_compound_id'] =  self.context['request'].user.contracting_id + \
                "*" + validated_data['item_table'].item_table_code + "*" + validated_data["category_code"]
        item_category = ItemCategory.objects.create(**validated_data)
        item_category.save()
        return item_category

class CategoryPUTSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['item_table', 'category_compound_id', 'category_code', 'description', 'note']
        read_only_fields =  ['category_compound_id', 'item_table', 'category_code']

class ItemPOSTSerializer(serializers.ModelSerializer):
    item_table = serializers.SlugRelatedField(slug_field='item_table_compound_id', queryset=ItemTable.objects.all())
    category = serializers.SlugRelatedField(slug_field='category_compound_id', queryset=ItemCategory.objects.all())
    class Meta:
        model = Item
        fields = ['item_compound_id', 'item_table', 'item_code', 'category', 'description', 'unit', 'barcode', 'status',
                'image', 'technical_description'] 
        read_only_fields =  ['item_compound_id']
        validators = [UniqueTogetherValidator(queryset=Item.objects.all(), fields=['item_table', 'item_code'], 
            message=_("The 'item_code' field  must be unique by 'item_table'."))]

    def validate(self, attrs):
        request_user = self.context['request'].user
        item_table = attrs.get('item_table')
        category = attrs.get('category')
        # item_table belongs to user contracting
        if item_table.contracting_id != request_user.contracting_id:
            raise NotFound(detail={"error": [_("Item table not found.")]})
        # Category must have the same item_table that the item item_table
        if category.item_table != item_table:
            raise serializers.ValidationError(_("You cannot choose this category because it is from another item table."))
        # Agent without access to all establishments can't access an item from item_table which he doesn't have access.
        if self.context['request_user_is_agent_without_all_estabs'] and not agent_has_access_to_this_item_table(request_user, item_table):
            raise NotFound(detail={"error": [_("Item table not found.")]})
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data['item_compound_id'] = self.context['request'].user.contracting_id + \
                "*" + validated_data['item_table'].item_table_code + "*" + validated_data["item_code"]
        return super().create(validated_data)

class ItemPUTSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='category_compound_id', queryset=ItemCategory.objects.all())
    class Meta:
        model = Item
        fields = ['item_compound_id', 'item_table', 'item_code', 'category', 'description', 'unit', 'barcode',
                'status', 'image', 'technical_description'] 
        read_only_fields =  ['item_compound_id', 'item_code', 'item_table']

    def validate(self, attrs):
        request_user = self.context['request'].user
        category = attrs.get('category')
        # Verify if agent can assign this category.
        if attrs.get('category'):
            # Category belongs to user contracting
            if category.item_table.contracting_id != request_user.contracting_id:
                raise NotFound(detail={"error": [_("Item category not found.")]})
            # Category must have the same item_table that the item item_table
            if category.item_table != self.instance.item_table:
                raise serializers.ValidationError(_("You cannot choose this category because it is from another item table."))
        return super().validate(attrs)

class ItemGETSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['item_compound_id', 'item_table', 'item_code', 'category', 'description', 'unit', 'barcode',
                'status', 'image', 'technical_description'] 
        read_only_fields =  fields

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
            raise NotFound(detail={"error": [_("Item with id '{item_id}' was not found.").format(item_id=item_id)]})
        return value

class CompanyAUXSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['item_table', 'name', 'company_compound_id']
        read_only_fields = fields

class PriceTableGetSerializer(serializers.ModelSerializer):
    company = CompanyAUXSerializer()

    class Meta:
        model = PriceTable
        fields = ['price_table_compound_id', 'company', 'table_code', 'description', 'note']
        read_only_fields = fields

class PriceTablePOSTSerializer(serializers.ModelSerializer):
    price_items = ForTablePriceItemSerializer(many=True)
    company = serializers.SlugRelatedField(slug_field='company_compound_id', queryset=Company.objects.all())
    company_name = serializers.SerializerMethodField()
    item_table = serializers.SerializerMethodField()

    class Meta:
        model = PriceTable
        fields = ['price_table_compound_id', 'company_name', 'company', 'price_items', 'table_code', 'description', 'note', 'item_table']
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
                    raise NotFound(detail={"error": [_("The item must belong to the company that owns the price table.")]})
                # Deny duplicate values
                if price_item in check_for_duplicate_values:
                    raise serializers.ValidationError(_("There are duplicate price items."))
                check_for_duplicate_values.append(price_item)

        #---------------------------/ Company
        # Company is from the same contracting that request_user
        if company.contracting_id != request_user.contracting_id:
            raise NotFound(detail={"error": [_("Company not found.")]})
        # User is agent without all estabs and don't have access to this company
        if self.context['req_user_is_agent_without_all_estabs'] and company not in get_agent_companies(request_user):
            raise NotFound(detail={"error": [_("Company not found.")]})
        # Company has an item table
        if not company.item_table:
            raise NotFound(detail={"error": [_("The company must have an item table.")]})
        return super().validate(attrs)

    def create(self, validated_data):
        price_items = validated_data.pop('price_items')
        validated_data['price_table_compound_id'] = self.context['request'].user.contracting_id + \
                "*" + validated_data['company'].company_code + "*" + validated_data["table_code"]
        price_table = PriceTable.objects.create(**validated_data)
        price_table.save()
        price_items_list = []
        for price_item in price_items:
            price_items_list.append(PriceItem(item=price_item['item'], unit_price=price_item['unit_price'], price_table=price_table))
        price_table.price_items.bulk_create(price_items_list)
        return price_table

    def get_item_table(self, obj):
        return obj.company.item_table_id

    def get_company_name(self, obj):
        return obj.company.name

class SpecificPriceTablePUTSerializer(serializers.ModelSerializer):
    price_items = ForTablePriceItemSerializer(many=True)

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
                    raise NotFound(detail={"error": [_("The item must belong to the company that owns the price table.")]})
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
    unit_price = serializers.DecimalField(max_digits=11, decimal_places=2,required=True, validators=[positive_number])
    class Meta:
        model = PriceItem
        fields = ['item', 'price_table', 'unit_price', 'last_modified', 'creation_date']
        read_only_fields =  ['item', 'price_table', 'last_modified', 'creation_date']


class ItemForPriceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['item_compound_id', 'description', 'unit'] 

class PriceItemForAgentsSerializer(serializers.ModelSerializer):
    item = ItemForPriceItemSerializer()
    unit_price = serializers.DecimalField(max_digits=11, decimal_places=2,required=True, validators=[positive_number])

    class Meta:
        model = PriceItem
        fields = ['item', 'unit_price']
