from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.validators import UniqueTogetherValidator
from order.serializers import EstablishmentForCompanyWithEstab
from organization.facade import update_client_establishments
from user.validators import agent_has_permission_to_assign_this_client_table_to_client
from organization.validators import UserContracting, agent_has_permission_to_assign_this_establishment_to_client
from item.models import ItemTable, PriceTable
from organization.models import Client, ClientEstablishment, ClientTable, Company, Contracting, Establishment
from django.utils.translation import gettext_lazy as _

class ContractingPOSTSerializer(serializers.ModelSerializer):
    name = serializers.CharField(min_length=3, max_length=60)
    class Meta:
        model = Contracting
        fields = ['contracting_code', 'name', 'status', 'active_users_limit', 'note']

class ContractingPUTSerializer(serializers.ModelSerializer):
    name = serializers.CharField(min_length=3, max_length=60)
    class Meta:
        model = Contracting
        fields = ['contracting_code', 'name', 'status', 'active_users_limit', 'note']
        read_only_fields = ['contracting_code']

class CompanyPOSTSerializer(serializers.ModelSerializer):
    client_table=serializers.SlugRelatedField(slug_field='client_table_compound_id', 
            queryset=ClientTable.objects.all(), allow_null=True)
    item_table=serializers.SlugRelatedField(slug_field='item_table_compound_id',
            queryset=ItemTable.objects.all(), allow_null=True)
    contracting_id=serializers.HiddenField(default=UserContracting())
    class Meta:
        model = Company
        fields = ['company_compound_id', 'company_code', 'contracting_id', 'item_table', 'client_table', 'name',
                'cnpj_root','status', 'note']
        validators = [UniqueTogetherValidator(queryset=Company.objects.all(), fields=['company_code', 'contracting_id'], 
            message=_("The 'company_code' field must be unique."))]

    def validate_client_table(self, value):
        if value:
            # Contracting Ownership
            if value.contracting_id != self.context["request"].user.contracting_id:
                raise NotFound(detail={"error": [_("Client table not found.")]})
            return value
        return value

    def validate_item_table(self, value):
        if value:
            # Contracting Ownership
            if value.contracting_id != self.context["request"].user.contracting_id:
                raise NotFound(detail={"error": [_("Item table not found.")]})
            return value
        return value

    def create(self, validated_data):
        validated_data['company_compound_id'] = validated_data['contracting_id'] + \
                "*" + validated_data['company_code']
        return super().create(validated_data)

class CompanyPUTSerializer(serializers.ModelSerializer):
    client_table=serializers.SlugRelatedField(slug_field='client_table_compound_id', 
            queryset=ClientTable.objects.all(), allow_null=True)
    item_table=serializers.SlugRelatedField(slug_field='item_table_compound_id',
            queryset=ItemTable.objects.all(), allow_null=True)
    class Meta:
        model = Company
        fields = ['company_compound_id', 'company_code', 'item_table', 'client_table', 'name',
                'cnpj_root','status', 'note']
        read_only_fields = ['company_code']

    def validate_client_table(self, value):
        # If there is any clientEstab for this company, do not allow change this field.
        if self.instance.client_table != value:
            if ClientEstablishment.objects.filter(establishment__company=self.instance).first():
                raise serializers.ValidationError(_("The company must have no clients to be able to change the client table."))
            # No orders too
            if self.instance.order_set.first():
                raise serializers.ValidationError(_("The company must have no orders to be able to change the client table."))
        if value:
            # Contracting Ownership
            if value.contracting_id != self.context["request"].user.contracting_id:
                raise NotFound(detail={"error": [_("Client table not found.")]})
            return value

        return value

    def validate_item_table(self, value):
        # If there is any price_table for this company, do not allow change this field.
        if self.instance.item_table != value:
            if self.instance.pricetable_set.first():
                raise serializers.ValidationError(_("The company must have no price tables to be able to change the item table.")) #TODO translate
        if value:
            # Contracting Ownership
            if value.contracting_id != self.context["request"].user.contracting_id:
                raise NotFound(detail={"error": [_("Item table not found.")]})
            return value
        return value

class EstablishmentPOSTSerializer(serializers.ModelSerializer):
    company=serializers.SlugRelatedField(slug_field='company_compound_id', queryset=Company.objects.all())
    
    class Meta:
        model = Establishment
        fields = ['establishment_compound_id', 'establishment_code', 'company', 'name', 'cnpj', 'status', 'note']
        validators = [UniqueTogetherValidator(queryset=Establishment.objects.all(), fields=['establishment_code', 'company'],
            message=_("The 'establishment_code' field must be unique by company."))]

    def validate_company(self, value):
        if value:
            if value.contracting_id != self.context["request"].user.contracting_id:
                raise serializers.ValidationError(_("Company not found."))
            if value.status != 1:
                raise serializers.ValidationError(_("The company must be active."))
            return value
        return value

    def create(self, validated_data):
        # Create establishment_compound_id
        validated_data['establishment_compound_id'] = validated_data['company'].contracting_id + "*" + \
                validated_data['company'].company_code + "*" + validated_data['establishment_code']
        return super().create(validated_data)

class EstablishmentPUTSerializer(serializers.ModelSerializer):
    company=serializers.SlugRelatedField(slug_field='company_compound_id', read_only=True)
    
    class Meta:
        model = Establishment
        fields = ['establishment_compound_id', 'establishment_code', 'company', 'name', 'cnpj', 'status', 'note']
        read_only_fields = ['establishment_code', 'company']

class ClientTablePOSTSerializer(serializers.ModelSerializer):
    contracting_id=serializers.HiddenField(default=UserContracting())
    class Meta:
        model = ClientTable
        fields =  ['client_table_compound_id' ,'client_table_code', 'contracting_id', 'description', 'note']
        validators = [UniqueTogetherValidator(queryset=ClientTable.objects.all(), fields=['client_table_code', 'contracting_id'], 
            message=_("The 'client_table_code' field must be unique."))]

    def create(self, validated_data):
        # Create client_table_compound_id
        validated_data['client_table_compound_id'] = validated_data['contracting_id'] + \
                "*" + validated_data['client_table_code']
        return super().create(validated_data)

class ClientTablePUTSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientTable
        fields =  ['client_table_compound_id' ,'client_table_code', 'description', 'note']
        read_only_fields = ['client_table_code']

class ClientEstablishmentToClientSerializer(serializers.ModelSerializer):
    establishment = serializers.SlugRelatedField(slug_field='establishment_compound_id', queryset=Establishment.objects.all())
    price_table = serializers.SlugRelatedField(slug_field='price_table_compound_id', queryset=PriceTable.objects.all(), allow_null=True)
    class Meta:
        model=ClientEstablishment
        fields = ['establishment', 'price_table']

    def validate_establishment(self, value):
        # Contracting ownership
        if value.company.contracting_id != self.context["request"].user.contracting_id:
            raise serializers.ValidationError(_("Establishment not found."))
        return value

    def validate(self, attrs):
        price_table = attrs.get('price_table')
        establishment = attrs['establishment']
        if price_table:
            # validate if price_table belongs to the same company as the establishment
            if price_table.company != establishment.company:
                raise serializers.ValidationError(_("You can't add this price table to this 'client_establishment'."))
        return super().validate(attrs)

class CompaniesToCreateClientSerializer(serializers.ModelSerializer):
    client_table=serializers.SlugRelatedField(slug_field='client_table_compound_id', 
            queryset=ClientTable.objects.all(), allow_null=True)
    class Meta:
        model = Company
        fields = ['company_code', 'name', 'client_table']

class ClientSerializerPOST(serializers.ModelSerializer):
    client_establishments = ClientEstablishmentToClientSerializer(many=True)
    client_table = serializers.SlugRelatedField(slug_field='client_table_compound_id', queryset=ClientTable.objects.all())
    class Meta:
        model = Client
        fields =  ['client_compound_id', 'client_table', 'client_code', 'client_establishments',
                'vendor_code', 'name', 'cnpj', 'status', 'note']
        read_only_fields =  ['client_compound_id']
        validators = [UniqueTogetherValidator(queryset=Client.objects.all(), fields=['client_code', 'client_table'],
            message=_("The 'client_code' field must be unique by client table."))]

    def validate(self, attrs):
        request_user = self.context["request"].user
        client_establishments = attrs.get('client_establishments')
        request_user_is_agent_without_all_estabs = self.context['request_user_is_agent_without_all_estabs']
        # ----------------/ Establishments
        if client_establishments or client_establishments == []:
            establishments_list = []
            for client_establishment in client_establishments:
                # Deny duplicate establishments
                if client_establishment['establishment'] in establishments_list:
                    raise serializers.ValidationError(_("There is a duplicate establishment in 'client_establishments'"))
                establishments_list.append(client_establishment['establishment'])
                # Check if establishment.company.client_table belongs to Client client_table on POST request
                if client_establishment['establishment'].company.client_table != attrs.get("client_table"):
                    estab = client_establishment['establishment'].establishment_compound_id
                    raise serializers.ValidationError(_("The 'client_table' field from the company which owns the establishment {estab} does not correspond with the 'client_table' to which this client belongs.").format(estab=estab))
                if request_user_is_agent_without_all_estabs:
                    # Check if agent can access establishment
                    if not agent_has_permission_to_assign_this_establishment_to_client(request_user, client_establishment['establishment']):
                        raise serializers.ValidationError(_("You can't add this establishment to this client."))
        # ----------------/ Client Table
        # Client table Contracting ownership
        if attrs.get('client_table').contracting_id != request_user.contracting_id:
            raise serializers.ValidationError(_("Client table not found."))
        # Agent without all estabs has access to this client_table
        if request_user_is_agent_without_all_estabs:
            if not agent_has_permission_to_assign_this_client_table_to_client(request_user, attrs.get('client_table')):
                raise serializers.ValidationError(_("Can't access this client_table."))
        return attrs

    def create(self, validated_data):
        # Create client_compound_id
        client = Client.objects.create(
            client_compound_id = validated_data['client_table'].contracting_id + "*" + \
                    validated_data['client_table'].client_table_code + "*" + validated_data['client_code'],
            client_table=validated_data['client_table'],
            client_code=validated_data['client_code'],
            vendor_code=validated_data.get('vendor_code', ''), #Optional field
            name=validated_data['name'],
            cnpj=validated_data['cnpj'],
            status=validated_data['status'],
            note=validated_data.get('note', ''), #Optional field
        )
        client_establishments_list = []
        for client_establishment in validated_data['client_establishments']:
            client_establishments_list.append(ClientEstablishment(establishment=client_establishment['establishment'], 
                 client=client, price_table=client_establishment['price_table']))
        client.client_establishments.bulk_create(client_establishments_list)
        return client
    
class ClientSerializerPUT(serializers.ModelSerializer):
    client_establishments = ClientEstablishmentToClientSerializer(many=True)
    class Meta:
        model = Client
        fields =  ['client_compound_id', 'client_table', 'client_code', 'client_establishments',
                'vendor_code', 'name', 'cnpj', 'status', 'note']
        read_only_fields =  [ 'client_table', 'client_code']

    def validate(self, attrs):
        request_user = self.context["request"].user
        client_establishments = attrs.get('client_establishments')
        request_user_is_agent_without_all_estabs = self.context['request_user_is_agent_without_all_estabs']
        # ----------------/ Establishments
        if client_establishments or client_establishments == []:
            establishments_list = []
            for client_establishment in client_establishments:
                # Deny duplicate establishments
                if client_establishment['establishment'] in establishments_list:
                    raise serializers.ValidationError(_("There is a duplicate establishment in 'client_establishments'"))
                establishments_list.append(client_establishment['establishment'])
                # Check if establishment.company.client_table belongs to Client client_table
                if client_establishment['establishment'].company.client_table != self.instance.client_table:
                    estab = client_establishment['establishment'].establishment_compound_id
                    raise serializers.ValidationError(_("The 'client_table' field from the company which owns the establishment {estab} does not correspond with the 'client_table' to which this client belongs.").format(estab=estab))
                if request_user_is_agent_without_all_estabs:
                    # Check if agent can access establishment
                    if not agent_has_permission_to_assign_this_establishment_to_client(request_user, client_establishment['establishment']):
                        raise serializers.ValidationError(_("You can't add this establishment to this client."))
        return attrs

    def update(self, instance, validated_data):
        # When using 'return super().update ...' i can't return validated_data with nested related values to update
        client_establishments = validated_data.get('client_establishments')
        if client_establishments or client_establishments == []:
            client_establishments = validated_data.pop('client_establishments')
            update_client_establishments(instance, client_establishments)
        return super().update(instance, validated_data)
    
class CompaniesAndEstabsToDuplicateOrderSerializer(serializers.ModelSerializer):
    establishment_set = EstablishmentForCompanyWithEstab(many=True)
    class Meta:
        model = Company
        fields = ['company_code', 'name', 'company_compound_id', 'establishment_set']

