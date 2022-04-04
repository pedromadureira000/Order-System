from rest_framework import serializers
from rolepermissions.checkers import has_role
from organization.models import ClientEstablishment, Establishment
from .facade import update_ordered_items
from .models import Order, OrderedItem, OrderHistory
from item.models import Item
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied
from .validators import order_has_changed
from settings.utils import positive_number
import copy

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
                'order_date', 'invoicing_date', 'invoice_number', 'note']
        read_only_fields = ['order_number', 'company', 'client', 'client_user', 'price_table', 'order_date',
               'order_amount', 'invoice_number', 'invoicing_date']

    def validate_status(self, value):
        # An order can be created with 'typing' or 'transferred' status
        if value not in [1, 2]:
            raise serializers.ValidationError(_("Client user cannot choose a status other then 'Typing' and 'Transferred' when creating an order."))
        return value

    def validate_establishment(self, value):
        # Contracting ownership
        if value.establishment_compound_id.split("&")[0] != self.context['request'].user.contracting.contracting_code:
            raise serializers.ValidationError(_("Establishment not found."))
        return value

    def validate(self, attrs):
        request_user = self.context['request'].user
        client = request_user.client
        establishment = attrs['establishment']
        company = establishment.company
        #Check if the request_user is active
        if request_user.status != 1:
            raise PermissionDenied(detail={"error": [_("Your account is disabled.")]})
        #Check if the contracting is active
        if request_user.contracting.status != 1:
            raise PermissionDenied(detail={"error": [_("Your contracting is disabled.")]})
        # Check if client have access to this establishment 
        try:
            client_establishment = ClientEstablishment.objects.get(client=client, establishment=establishment)
        except ClientEstablishment.DoesNotExist:
            raise PermissionDenied(detail={"error": [_("Establishment not found.")]})
        # Check if ClientEstablishment has a price_table
        if not client_establishment.price_table:
            raise PermissionDenied(detail={"error": [_("You cannot buy from this establishment.")]})
        #Check if the client is active
        if client.status != 1:
            raise PermissionDenied(detail={"error": [_("The client company is disabled.")]})
        #Check if the company is active
        if company.status != 1:
            raise PermissionDenied(detail={"error": [_("The company is disabled.")]})
        #Check if the establishment is active
        if establishment.status != 1:
            raise PermissionDenied(detail={"error": [_("The establishment is disabled.")]})
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
                'order_amount', 'status', 'order_date', 'invoicing_date', 'invoice_number', 'note', 'agent_note']
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
        if not has_role(self.context['request'].user, 'erp_user'):
            raise serializers.ValidationError(_("You cannot send the 'invoice number' field."))
        return value

    def validate_invoicing_date(self, value):
        if not has_role(self.context['request'].user, 'erp_user'):
            raise serializers.ValidationError(_("You cannot send the 'invoicing date' field."))
        return value

    def validate(self, attrs):
        request_user = self.context['request'].user
        client = self.instance.client
        establishment = self.instance.establishment
        status = attrs.get("status")
        invoice_number = attrs.get("invoice_number")
        invoicing_date = attrs.get("invoicing_date")
        ordered_items = attrs.get('ordered_items')
        #Check if the request_user is active
        if request_user.status != 1:
            raise PermissionDenied(detail={"error": [_("Your account is disabled.")]})
        #Check if the contracting is active
        if request_user.contracting.status != 1:
            raise PermissionDenied(detail={"error": [_("Your contracting is disabled.")]})
        # Deny setting wrong invoice_number
        if (invoice_number and status != 4) or (invoice_number and status == 4 and self.instance.status != 3):
            raise serializers.ValidationError(_("You can only add invoice number when order status has changed from 'Registered' to 'Invoiced'."))
        # Deny setting wrong invoicing_date
        if (invoicing_date and status != 4) or (invoicing_date and status == 4 and self.instance.status != 3):
            raise serializers.ValidationError(_("You can only add invoicing date when order status has changed from 'Registered 'to 'Invoiced'."))
        # Force setting invoice_number when status changes from 'Registered' to 'Invoiced'.
        if status == 4 and self.instance.status == 3 and not invoice_number:
            raise serializers.ValidationError(_("You need send invoice number when order status has changed from 'Registered' to 'Invoiced'."))
        # Force setting invoicing_date when status changes from 'Registered' to 'Invoiced'.
        if status == 4 and self.instance.status == 3 and not invoicing_date:
            raise serializers.ValidationError(_("You need send invoicing date when order status has changed from 'Registered 'to 'Invoiced'."))
        if has_role(request_user, 'client_user'):
            try:
                client_establishment = ClientEstablishment.objects.get(client=client, establishment=establishment)
            except ClientEstablishment.DoesNotExist:
                raise PermissionDenied(detail={"error": [_("Establishment not found.")]})
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
                'order_date', 'invoicing_date', 'invoice_number', 'note', 'order_history']
        read_only_fields = fields

