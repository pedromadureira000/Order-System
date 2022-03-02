from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rolepermissions.checkers import has_role
from core.facade import get_agent_companies, get_agent_item_tables, update_price_items_from_price_table
from core.models import ClientEstablishment, Company, Establishment
from core.validators import ClientCompanyFromCurrentUser, UserContracting, agent_has_access_to_this_item_table, agent_has_access_to_this_price_table, req_user_is_agent_without_all_estabs
from orders.facade import update_ordered_items
from orders.models import ItemTable, Order, Item, ItemCategory, OrderedItem, PriceTable, PriceItem, OrderHistory
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import NotFound, PermissionDenied
from orders.validators import non_negative_number, order_has_changed, positive_number
import copy

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
        if validated_data.get('item_table_code'): validated_data.pop('item_table_code')
        return super().update(instance, validated_data)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = ['item_table', 'category_compound_id', 'category_code', 'description', 'note']
        read_only_fields =  ['category_compound_id']
        validators = [UniqueTogetherValidator(queryset=ItemCategory.objects.all(), fields=['item_table', 'category_code'], 
            message="The field 'category_code' must be unique by 'item_table'.")]

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
                "#" + validated_data['item_table'].item_table_code + "#" + validated_data["category_code"]
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
            message="The field 'item_code' must be unique by 'item_table'.")]

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
                raise serializers.ValidationError(f"You cannot choose this category, because it is from another item table.")
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
                    raise serializers.ValidationError(f"You cannot choose this category, because it is from another item table.")
        return super().validate(attrs)

    def create(self, validated_data):
        validated_data['item_compound_id'] = self.context['request'].user.contracting.contracting_code + \
                "#" + validated_data['item_table'].item_table_code + "#" + validated_data["item_code"]
        item = Item.objects.create(**validated_data)
        return item

    def update(self, instance, validated_data):
        # Not allow to update this fields
        if validated_data.get('item_code'): validated_data.pop('item_code')
        if validated_data.get('item_table'): validated_data.pop('item_table')
        return super().update(instance, validated_data)

class ForTablePriceItemSerializer(serializers.ModelSerializer):
    item = serializers.SlugRelatedField(slug_field='item_compound_id', queryset=Item.objects.all())

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
            message="The field 'table_code' must be unique by 'company'.")]

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
                "#" + validated_data['company'].company_compound_id + "#" + validated_data["table_code"]
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

class AssignPriceTableToClientEstablishment(serializers.ModelSerializer):
    establishment = serializers.SlugRelatedField(slug_field='establishment_compound_id', read_only=True)
    client = serializers.SlugRelatedField(slug_field='client_compound_id', read_only=True)
    price_table = serializers.SlugRelatedField(slug_field='price_table_compound_id', queryset=PriceTable.objects.all(), 
            allow_null=True)
    class Meta:
        model=ClientEstablishment
        fields = ['establishment', 'price_table', 'client']
        validators = [UniqueTogetherValidator(queryset=ClientEstablishment.objects.all(), fields=['client', 'establishment'], 
            message="The field 'establishment' must be unique per client.")]

    #OBS: if the agent without all estabs can't access to an establishment this goes for the 'price_table' too.
    def validate(self, attrs):
        price_table = attrs.get('price_table')
        establishment = self.instance.establishment
        if price_table:
            # validate if price_table belongs to the same company as the establishment
            if price_table.company != establishment.company:
                raise serializers.ValidationError(_("You can't add this price table to this 'client_establishment'."))
        return super().validate(attrs)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class SpecificPriceItemSerializer(serializers.ModelSerializer):
    item = serializers.SlugRelatedField(slug_field='item_compound_id', read_only=True)
    price_table = serializers.SlugRelatedField(slug_field='price_table_compound_id', read_only=True)
    unit_price = serializers.DecimalField(max_digits=11, decimal_places=2,required=True, validators=[non_negative_number])
    class Meta:
        model = PriceItem
        fields = ['item', 'price_table', 'unit_price', 'last_modified', 'creation_date']
        read_only_fields =  ['item', 'price_table', 'last_modified', 'creation_date']

class OrderedItemSerializer(serializers.ModelSerializer):
    item = serializers.SlugRelatedField(slug_field='item_compound_id', queryset=Item.objects.all())
    quantity = serializers.DecimalField(max_digits=11, decimal_places=2,required=True, validators=[positive_number])
    class Meta:
        model = OrderedItem
        fields = ['item', 'quantity', 'unit_price', 'date']
        read_only_fields = ['unit_price', 'date']

class OrderPOSTSerializer(serializers.ModelSerializer):
    company = serializers.SlugRelatedField(slug_field='company_compound_id', read_only=True)
    establishment = serializers.SlugRelatedField(slug_field='establishment_compound_id', queryset=Establishment.objects.all())
    client = serializers.SlugRelatedField(slug_field='client_compound_id', read_only=True)
    client_user = serializers.SlugRelatedField(slug_field='user_code', read_only=True)
    price_table = serializers.SlugRelatedField(slug_field='price_table_compound_id', read_only=True)
    ordered_items = OrderedItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['order_number', 'company', 'establishment', 'client', 'client_user', 'price_table', 'ordered_items', 'order_amount', 'status', 
                'order_date', 'billing_date', 'invoice_number', 'note']
        read_only_fields = ['order_number', 'company', 'client', 'client_user', 'price_table', 'order_date',
               'order_amount', 'invoice_number', 'billing_date']

    def validate_status(self, value):
        # An order can be created with 'typing' or 'transferred' status
        if value not in [1, 2]:
            raise serializers.ValidationError(_("Client user cannot choose a status other then 'Typing' and 'Transferred' when creating an order."))
        return value

    def validate_establishment(self, value):
        # Contracting ownership
        if value.establishment_compound_id.split("#")[0] != self.context['request'].user.contracting.contracting_code:
            raise serializers.ValidationError(_("Establishment not found."))
        return value

    def validate(self, attrs):
        request_user = self.context['request'].user
        client = request_user.client
        establishment = attrs['establishment']
        company = establishment.company
        #Check if the request_user is active
        if request_user.status != 1:
            raise PermissionDenied(detail={"detail": [_("Your account is disabled.")]})
        #Check if the contracting is active
        if request_user.contracting.status != 1:
            raise PermissionDenied(detail={"detail": [_("Your contracting is disabled.")]})
        # Check if client have access to this establishment 
        try:
            client_establishment = ClientEstablishment.objects.get(client=client, establishment=establishment)
        except ClientEstablishment.DoesNotExist:
            raise PermissionDenied(detail={"detail": [_("Establishment not found.")]})
        # Check if ClientEstablishment has a price_table
        if not client_establishment.price_table:
            raise PermissionDenied(detail={"detail": [_("You cannot buy from this establishment.")]})
        #Check if the client is active
        if client.status != 1:
            raise PermissionDenied(detail={"detail": [_("The client company is disabled.")]})
        #Check if the company is active
        if company.status != 1:
            raise PermissionDenied(detail={"detail": [_("The company is disabled.")]})
        #Check if the establishment is active
        if establishment.status != 1:
            raise PermissionDenied(detail={"detail": [_("The establishment is disabled.")]})
        attrs['price_table'] = client_establishment.price_table
        # Check if item is available for this client by price table
        available_items = client_establishment.price_table.items.filter(status=1)
        check_for_duplicate_values = []
        order_amount = 0
        if not attrs['ordered_items']:
            raise serializers.ValidationError(_("You must add at least one item to the order."))
        for ordered_item in attrs['ordered_items']:
            if ordered_item['item'] not in available_items:
                raise serializers.ValidationError(_("You cannot add this item to the order."))
            # Deny duplicate values
            if ordered_item in check_for_duplicate_values:
                raise serializers.ValidationError(_("There are duplicate items."))
            check_for_duplicate_values.append(ordered_item)
            # Add unit_price to ordered_item
            ordered_item['unit_price'] = client_establishment.price_table.price_items.get(item=ordered_item['item']).unit_price #TODO N+1 query
            order_amount += ordered_item['unit_price'] * ordered_item['quantity'] 
        attrs['order_amount'] = order_amount
        return super().validate(attrs)

    def create(self, validated_data):
        ordered_items = validated_data.pop('ordered_items')
        validated_data['company'] = validated_data['establishment'].company
        validated_data['client'] = self.context['request'].user.client
        validated_data['client_user'] = self.context['request'].user
        last_order = validated_data['establishment'].order_set.order_by("order_date").last()
        validated_data['order_number'] = last_order.order_number + 1 if last_order else 1
        order = Order.objects.create(**validated_data)
        # Create OrderedItems
        ordered_items_list = []
        for ordered_item in ordered_items:
            ordered_items_list.append(OrderedItem(item=ordered_item['item'], quantity=ordered_item['quantity'], 
                unit_price=ordered_item['unit_price'], order=order))
        order.ordered_items.bulk_create(ordered_items_list)
        return order

# PUT will be used by client_user to edit ordered_items and note, and to change status to 'transferred'. This can only be done when the order status is 'typing'. 
#  agent/admin_agent/erp can update order status and create notes in the order history
class OrderPUTSerializer(serializers.ModelSerializer):
    company = serializers.SlugRelatedField(slug_field='company_compound_id', read_only=True)
    establishment = serializers.SlugRelatedField(slug_field='establishment_compound_id', read_only=True)
    client = serializers.SlugRelatedField(slug_field='client_compound_id', read_only=True)
    client_user = serializers.SlugRelatedField(slug_field='user_code', read_only=True)
    price_table = serializers.SlugRelatedField(slug_field='price_table_compound_id', read_only=True)
    ordered_items = OrderedItemSerializer(many=True)
    agent_note = serializers.CharField(max_length=800, required=False, write_only=True)
    class Meta:
        model = Order
        fields = ['order_number', 'company', 'establishment', 'client', 'client_user', 'price_table', 'ordered_items', 
                'order_amount', 'status', 'order_date', 'billing_date', 'invoice_number', 'note', 'agent_note']
        read_only_fields = ['order_number', 'company', 'establishment', 'client', 'client_user', 'price_table', 
                'order_date', 'order_amount']
    def validate_note(self, value):
        if not has_role(self.context['request'].user, 'client_user'): 
            raise serializers.ValidationError(_("You cannot update 'note' field."))
        return value

    def validate_status(self, value):
        # Client user can only update status from 1 to 2 or from 1 to 0 (typing to transferred or typing to canceled)
        if has_role(self.context['request'].user, 'client_user'): 
            if self.instance.status == 1 and value not in [0, 1, 2]:
                raise serializers.ValidationError(_("Client user cannot choose a status other then 'Typing' and 'Transferred' when updating an order."))
            # Client user can only update order if status is "Typing"
            if self.instance.status != 1:
                raise serializers.ValidationError(_("You cannot update this order."))
        #  Order with 'Typing' status can only be transferred, canceled or stay with the same status
        if self.instance.status == 1 and value not in [0, 1, 2]:
            raise serializers.ValidationError(_("You cannot choose this option as status."))
        # Transferred order can only be changed to canceled, registered or stay with the same status
        if self.instance.status == 2 and value not in [0, 2, 3]:
            raise serializers.ValidationError(_("You cannot choose this option as status."))
        # Registered order can only be changed to canceled, invoiced or stay with the same status
        if self.instance.status == 3 and value not in [0, 3, 4]:
            raise serializers.ValidationError(_("You cannot choose this option as status."))
        # Invoiced order can only be changed to canceled, delivered, come back to registered or stay with the same status
        if self.instance.status == 4 and value not in [0, 3 ,4, 5]:
            raise serializers.ValidationError(_("You cannot choose this option as status."))
        # Delivered order can only be changed to canceled, come back to invoiced and stay with the same status
        if self.instance.status == 5 and value not in [0, 4, 5]:
            raise serializers.ValidationError(_("You cannot choose this option as status."))
        # Canceled order can't change status
        if self.instance.status == 0 and value != self.instance.status:
            raise serializers.ValidationError(_("You cannot choose this option as status.")) #TODO made a better message
        return value

    def validate_invoice_number(self, value):
        if not has_role(self.context['request'].user, 'erp'):
            raise serializers.ValidationError(_("You cannot send the 'invoice number' field."))
        return value

    def validate_billing_date(self, value):
        if not has_role(self.context['request'].user, 'erp'):
            raise serializers.ValidationError(_("You cannot send the 'billing date' field."))
        return value

    def validate(self, attrs):
        request_user = self.context['request'].user
        client = self.instance.client
        establishment = self.instance.establishment
        status = attrs.get("status")
        invoice_number = attrs.get("invoice_number")
        billing_date = attrs.get("billing_date")
        ordered_items = attrs.get('ordered_items')
        #Check if the request_user is active
        if request_user.status != 1:
            raise PermissionDenied(detail={"detail": [_("Your account is disabled.")]})
        #Check if the contracting is active
        if request_user.contracting.status != 1:
            raise PermissionDenied(detail={"detail": [_("Your contracting is disabled.")]})
        # Deny setting wrong invoice_number
        if (invoice_number and status != 4) or (invoice_number and status == 4 and self.instance.status != 3):
            raise serializers.ValidationError(_("You can only add invoice number when order status has changed from 'Registered' to 'Billed'."))
        # Deny setting wrong billing_date
        if (billing_date and status != 4) or (billing_date and status == 4 and self.instance.status != 3):
            raise serializers.ValidationError(_("You can only add billing date when order status has changed from 'Registered 'to 'Billed'."))
        # Force setting invoice_number when status changes from 'Registered' to 'Billed'.
        if status == 4 and self.instance.status == 3 and not invoice_number:
            raise serializers.ValidationError(_("You need send invoice number when order status has changed from 'Registered' to 'Billed'."))
        # Force setting billing_date when status changes from 'Registered' to 'Billed'.
        if status == 4 and self.instance.status == 3 and not billing_date:
            raise serializers.ValidationError(_("You need send billing date when order status has changed from 'Registered 'to 'Billed'."))
        if has_role(request_user, 'client_user'):
            try:
                client_establishment = ClientEstablishment.objects.get(client=client, establishment=establishment)
            except ClientEstablishment.DoesNotExist:
                raise PermissionDenied(detail={"detail": [_("Establishment not found.")]})
            check_for_duplicate_values = []
            order_amount = 0
            if self.instance.status != 1:
                raise serializers.ValidationError(_("You cannot update this order."))
            # client user cannot remove all items from the order.
            if ordered_items == []:
                raise serializers.ValidationError(_("You must add at least one item to the order."))
            if ordered_items:
                available_items = client_establishment.price_table.items.filter(status=1)
                for ordered_item in ordered_items:
                    if ordered_item['item'] not in available_items:
                        raise serializers.ValidationError(_("You cannot add this item to the order."))
                    # Deny duplicate values
                    if ordered_item in check_for_duplicate_values:
                        raise serializers.ValidationError(_("There are duplicate items."))
                    check_for_duplicate_values.append(ordered_item)
                    # Add unit_price to ordered_item
                    ordered_item['unit_price'] = client_establishment.price_table.price_items.get(item=ordered_item['item']).unit_price 
                    #TODO N+1 query
                    order_amount += ordered_item['unit_price'] * ordered_item['quantity'] 
                attrs['order_amount'] = order_amount
        if not order_has_changed(self.instance, attrs):
            raise serializers.ValidationError(_("You have not changed any fields."))
        return super().validate(attrs)

    def update(self, instance, validated_data):
        ordered_items = validated_data.get('ordered_items')
        if ordered_items:
            ordered_items = validated_data.pop('ordered_items')  
        # This is for accessing instance fields before they are updated 
        instance._old_instance = copy.copy(instance)
        instance._request_user = self.context['request'].user
        
        if has_role(self.context['request'].user, 'client_user') and ordered_items:
            update_ordered_items(instance, ordered_items)
        return super().update(instance, validated_data)

class OrderHistorySerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='user_code', read_only=True)
    class Meta:
        model = OrderHistory
        fields = ['history_type', 'history_description', 'user', 'agent_note', 'date']

class OrderDetailsSerializer(serializers.ModelSerializer):
    company = serializers.SlugRelatedField(slug_field='company_compound_id', read_only=True)
    establishment = serializers.SlugRelatedField(slug_field='establishment_compound_id', read_only=True)
    client = serializers.SlugRelatedField(slug_field='client_compound_id', read_only=True)
    client_user = serializers.SlugRelatedField(slug_field='user_code', read_only=True)
    price_table = serializers.SlugRelatedField(slug_field='price_table_compound_id', read_only=True)
    ordered_items = OrderedItemSerializer(many=True)
    order_history = OrderHistorySerializer(many=True)
    class Meta:
        model = Order
        fields = ['order_number', 'company', 'establishment', 'client', 'client_user', 'price_table', 'ordered_items', 'order_amount', 'status', 
                'order_date', 'billing_date', 'invoice_number', 'note', 'order_history']
        read_only_fields = fields

