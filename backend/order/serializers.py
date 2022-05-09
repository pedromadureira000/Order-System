from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rolepermissions.checkers import has_role
from organization.models import Client, ClientEstablishment, Company, Establishment
from organization.validators import UserClientId
from user.models import User
from .facade import update_ordered_items
from .models import Order, OrderedItem, OrderHistory
from item.models import Item, PriceItem, PriceTable
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied
from .validators import order_has_changed
from settings.utils import positive_number
import copy
from decimal import ROUND_HALF_UP, Decimal

class fetchClientEstabsToCreateOrderSerializer(serializers.ModelSerializer):
    company=serializers.SlugRelatedField(slug_field='company_compound_id', read_only=True)
    company_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Establishment
        fields = ['establishment_compound_id', 'cnpj', 'establishment_code', 'name', 'company', 'company_name']

    def get_company_name(self, obj):
        return obj.company.name

class ItemAuxForOrderedItemAuxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['item_compound_id', 'barcode','unit', 'description', 'image'] 

class searchOnePriceItemToMakeOrderSerializer(serializers.ModelSerializer):
    item = ItemAuxForOrderedItemAuxSerializer()

    class Meta:
        model = PriceItem
        fields = ['item',  'unit_price']

class EstablishmentForCompanyWithEstab(serializers.ModelSerializer):
    class Meta:
        model = Establishment
        fields = ['establishment_compound_id', 'establishment_code', 'name']

class CompanyWithEstabsSerializer(serializers.ModelSerializer):
    client_table=serializers.SlugRelatedField(slug_field='client_table_compound_id', read_only=True)
    establishments = EstablishmentForCompanyWithEstab(many=True)
    class Meta:
        model = Company
        fields = ['company_compound_id', 'company_code', 'name', 'client_table', 'establishments']

class ClientsToFillFilterSelectorsToSearchOrdersSerializer(serializers.ModelSerializer):
    client_table=serializers.SlugRelatedField(slug_field='client_table_compound_id', read_only=True)
    class Meta:
        model = Client
        fields =  ['client_compound_id', 'client_code', 'client_table', 'name']

class OrderedItemPOSTSerializer(serializers.ModelSerializer):
    item = serializers.SlugRelatedField(slug_field='item_compound_id', queryset=Item.objects.all())
    quantity = serializers.DecimalField(max_digits=11, decimal_places=2,required=True, validators=[positive_number])
    class Meta:
        model = OrderedItem
        fields = ['item', 'quantity', 'unit_price', 'sequence_number', 'date']
        read_only_fields = ['unit_price', 'date', 'sequence_number']

class OrderPOSTSerializer(serializers.ModelSerializer):
    company = serializers.SlugRelatedField(slug_field='company_compound_id', read_only=True)
    establishment = serializers.SlugRelatedField(slug_field='establishment_compound_id', queryset=Establishment.objects.all())
    client = serializers.SlugRelatedField(slug_field='client_compound_id', read_only=True)
    client_user = serializers.SlugRelatedField(slug_field='user_code', read_only=True)
    price_table = serializers.SlugRelatedField(slug_field='price_table_compound_id', read_only=True)
    ordered_items = OrderedItemPOSTSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id','order_number', 'company', 'establishment', 'client', 'client_user', 'price_table', 'ordered_items',
                'order_amount', 'status', 'order_date', 'invoicing_date', 'invoice_number', 'note']
        read_only_fields = ['id', 'order_number', 'company', 'client', 'client_user', 'price_table', 'order_date',
               'order_amount', 'invoice_number', 'invoicing_date']

    def validate_status(self, value):
        # An order can be created with 'typing' or 'transferred' status
        if value not in [1, 2]:
            raise serializers.ValidationError(_("Client user cannot choose a status other then 'Typing' and 'Transferred' when creating an order."))
        return value

    def validate_establishment(self, value):
        # Contracting ownership
        if value.establishment_compound_id.split("*")[0] != self.context['request'].user.contracting.contracting_code:
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
                raise serializers.ValidationError(_("You cannot add the item whose code is '{item}' to the order.").format(item=ordered_item['item'].item_code))
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
        request_user = self.context['request'].user
        ordered_items = validated_data.pop('ordered_items')
        validated_data['company'] = validated_data['establishment'].company
        validated_data['client'] = request_user.client
        validated_data['client_user'] = request_user
        last_order = request_user.client.order_set.order_by("order_date").last()
        validated_data['order_number'] = last_order.order_number + 1 if last_order else 1
        validated_data['id'] = request_user.client.client_table.client_table_code + '.' + \
            self.context['request'].user.client.client_code + '.' + str(validated_data['order_number'])
        order = Order.objects.create(**validated_data)
        # Create OrderedItems
        ordered_items_list = []
        for index, ordered_item in enumerate(ordered_items):
            ordered_items_list.append(OrderedItem(item=ordered_item['item'], quantity=ordered_item['quantity'], 
                unit_price=ordered_item['unit_price'], order=order, sequence_number=index + 1))
        order.ordered_items.bulk_create(ordered_items_list)
        return order

class OrderedItemPUTSerializer(serializers.ModelSerializer):
    item = serializers.SlugRelatedField(slug_field='item_compound_id', queryset=Item.objects.all())
    quantity = serializers.DecimalField(max_digits=11, decimal_places=2,required=True, validators=[positive_number])
    class Meta:
        model = OrderedItem
        fields = ['item', 'quantity', 'unit_price', 'sequence_number', 'date']
        read_only_fields = ['unit_price', 'date']

# PUT will be used by client_user to edit ordered_items and note, and to change status to 'transferred'. This can only be done when the order status is 'typing'. 
#  agent/admin_agent/erp can update order status and create notes in the order history
class OrderPUTSerializer(serializers.ModelSerializer):
    company = serializers.SlugRelatedField(slug_field='company_compound_id', read_only=True)
    establishment = serializers.SlugRelatedField(slug_field='establishment_compound_id', read_only=True)
    client = serializers.SlugRelatedField(slug_field='client_compound_id', read_only=True)
    client_user = serializers.SlugRelatedField(slug_field='user_code', read_only=True)
    price_table = serializers.SlugRelatedField(slug_field='price_table_compound_id', read_only=True)
    ordered_items = OrderedItemPUTSerializer(many=True)
    #  agent_note = serializers.CharField(max_length=800, required=False, write_only=True)
    class Meta:
        model = Order
        fields = ['id','order_number', 'company', 'establishment', 'client', 'client_user', 'price_table', 'ordered_items', 
                'order_amount', 'status', 'order_date', 'invoicing_date', 'invoice_number', 'note', 'agent_note']
        read_only_fields = ['id', 'order_number', 'company', 'establishment', 'client', 'client_user', 'price_table', 
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
        if (invoice_number and status not in [4, 5] and self.instance.status not in [4, 5]):
            raise serializers.ValidationError(_("You can only add invoice number when order status is 'Invoiced' of 'Delivered'."))
        # Deny setting wrong invoicing_date
        if (invoicing_date and status not in [4, 5] and self.instance.status not in [4, 5]):
            raise serializers.ValidationError(_("You can only add invoicing date when order status is 'Invoiced' of 'Delivered'."))
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
                        raise serializers.ValidationError(_("You cannot add the item whose code is '{item}' to the order.").format(item=ordered_item['item'].item_code))
                    # Deny duplicate values
                    if ordered_item in check_for_duplicate_values:
                        raise serializers.ValidationError(_("There are duplicate items."))
                    check_for_duplicate_values.append(ordered_item)
                    # Add unit_price to ordered_item
                    ordered_item['unit_price'] = client_establishment.price_table.price_items.get(item=ordered_item['item']).unit_price 
                    #TODO N+1 query
                    order_amount += ordered_item['unit_price'] * ordered_item['quantity'] 
                attrs['order_amount'] = Decimal(order_amount).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        current_ordered_items = OrderedItem.objects.filter(order=self.instance)
        attrs['current_ordered_items'] = current_ordered_items
        if not order_has_changed(self.instance, attrs):
            raise serializers.ValidationError(_("You have not changed any fields."))
        return super().validate(attrs)

    def update(self, instance, validated_data):
        ordered_items = validated_data.get('ordered_items')
        if ordered_items or ordered_items == []:
            ordered_items = validated_data.pop('ordered_items')  
        # This is for accessing instance fields before they are updated 
        instance._old_instance = copy.copy(instance)
        instance._request_user = self.context['request'].user
        
        if has_role(self.context['request'].user, 'client_user') and ordered_items:
            update_ordered_items(instance, ordered_items, validated_data['current_ordered_items'])
        return super().update(instance, validated_data)

class OrderHistorySerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    class Meta:
        model = OrderHistory
        fields = ['history_type', 'history_description', 'user', 'agent_note', 'date']

class OrderGetSerializer(serializers.ModelSerializer):
    company = serializers.SlugRelatedField(slug_field='company_code', read_only=True)
    establishment = serializers.SlugRelatedField(slug_field='establishment_compound_id', read_only=True)
    client = serializers.SlugRelatedField(slug_field='client_compound_id', read_only=True)
    #  client_user = serializers.SlugRelatedField(slug_field='user_code', read_only=True)
    #  price_table = serializers.SlugRelatedField(slug_field='price_table_compound_id', read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'company', 'establishment', 'client', 'order_amount', 'status', 'order_date', 'invoicing_date', 'invoice_number']
        read_only_fields = fields

class CompanyAuxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['company_code', 'name']

class EstablishmentAuxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Establishment
        fields = ['establishment_compound_id', 'establishment_code', 'name', 'cnpj']

# Order Details Serializers
class ClientAuxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields =  ['client_compound_id', 'client_code', 'name', 'cnpj']

class ClientUserAuxSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        #  fields = ['username']
        fields = ['username', 'first_name', 'last_name']

class PriceTableAuxSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceTable
        fields = ['table_code', 'description']
        read_only_fields = fields

class OrderedItemAuxSerializer(serializers.ModelSerializer):
    item = ItemAuxForOrderedItemAuxSerializer()
    class Meta:
        model = OrderedItem
        fields = ['item', 'quantity', 'unit_price', 'date', 'sequence_number']
        read_only_fields = [*fields]

class OrderDetailsSerializer(serializers.ModelSerializer):
    establishment = EstablishmentAuxSerializer()
    company = CompanyAuxSerializer()
    client = ClientAuxSerializer()
    client_user = ClientUserAuxSerializer()
    price_table = PriceTableAuxSerializer()
    ordered_items = OrderedItemAuxSerializer(many=True)
    class Meta:
        model = Order
        fields = ['company', 'establishment', 'client', 'client_user', 'price_table', 'ordered_items', 'note', 'agent_note']
        read_only_fields = fields

class OrderDuplicateSerializer(serializers.ModelSerializer):
    company = serializers.SlugRelatedField(slug_field='company_code', read_only=True)
    establishment = serializers.SlugRelatedField(slug_field='establishment_compound_id', read_only=True)
    client = serializers.SlugRelatedField(slug_field='client_compound_id', read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'company', 'establishment', 'client', 'order_amount', 'status', 'order_date', 'invoicing_date', 'invoice_number']
        read_only_fields = fields

    def validate(self, attrs):
        request_user = self.context['request'].user
        client = request_user.client
        establishment = self.instance.establishment
        company = establishment.company
        # Contracting ownership
        if establishment.establishment_compound_id.split("*")[0] != request_user.contracting.contracting_code:
            raise serializers.ValidationError(_("Establishment not found."))
        #Check if the request_user is active
        if request_user.status != 1:
            raise PermissionDenied(detail={"error": [_("Your account is disabled.")]})
        #Check if the contracting is active
        if request_user.contracting.status != 1:
            raise PermissionDenied(detail={"error": [_("Your contracting is disabled.")]})
        #Check if the client is active
        if client.status != 1:
            raise PermissionDenied(detail={"error": [_("The client company is disabled.")]})
        #Check if the company is active
        if company.status != 1:
            raise PermissionDenied(detail={"error": [_("The company is disabled.")]})
        #Check if the establishment is active
        if establishment.status != 1:
            raise PermissionDenied(detail={"error": [_("The establishment is disabled.")]})
        # Check if client have access to this establishment 
        try:
            client_establishment = ClientEstablishment.objects.get(client=client, establishment=establishment)
        except ClientEstablishment.DoesNotExist:
            raise PermissionDenied(detail={"error": [_("Establishment not found.")]})
        # Check if ClientEstablishment has a price_table
        if not client_establishment.price_table:
            raise PermissionDenied(detail={"error": [_("You cannot buy from this establishment.")]})
        attrs['price_table'] = client_establishment.price_table

        # Check if item is available for this client by price table
        available_items = client_establishment.price_table.items.filter(status=1)
        order_amount = 0
        ordered_items = self.instance.ordered_items.all()
        attrs['ordered_items'] = []
        attrs['some_items_were_not_copied'] = False
        for ordered_item in ordered_items:
            if ordered_item.item in available_items:
                attrs['ordered_items'].append(ordered_item) 
                # Add unit_price to ordered_item
                ordered_item.unit_price = client_establishment.price_table.price_items.get(item=ordered_item.item).unit_price #TODO N+1 query
                order_amount += ordered_item.unit_price * ordered_item.quantity 
            else:
                attrs['some_items_were_not_copied'] = True
        attrs['order_amount'] = order_amount
        return super().validate(attrs)

    def update(self, instance, validated_data):
        request_user = self.context['request'].user
        establishment = instance.establishment
        company = establishment.company
        some_items_were_not_copied = validated_data.pop('some_items_were_not_copied')
        ordered_items = validated_data.pop('ordered_items')
        validated_data['establishment'] = establishment
        validated_data['company'] = company
        validated_data['client'] = request_user.client
        validated_data['client_user'] = request_user
        validated_data['status'] = 1
        last_order = request_user.client.order_set.order_by("order_date").last()
        validated_data['order_number'] = last_order.order_number + 1 if last_order else 1
        validated_data['id'] = request_user.client.client_table.client_table_code + '.' + \
            request_user.client.client_code + '.' + str(validated_data['order_number'])
        order = Order.objects.create(**validated_data)
        # Create OrderedItems
        ordered_items_list = []
        for index, ordered_item in enumerate(ordered_items):
            ordered_items_list.append(OrderedItem(item=ordered_item.item, quantity=ordered_item.quantity, 
                unit_price=ordered_item.unit_price, order=order, sequence_number=index + 1))
        order.ordered_items.bulk_create(ordered_items_list)
        #  if  validated_data['some_items_were_not_copied'] == True:
            #  order.some_items_were_not_copied = True
        #  return order
        return (order, some_items_were_not_copied)
