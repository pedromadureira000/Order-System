from typing import OrderedDict
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.validators import UniqueTogetherValidator
from core.facade import update_agent_establishments, update_agent_permissions, update_client_establishments
from core.models import User
from rolepermissions.roles import get_user_roles
from rolepermissions.permissions import available_perm_status
from core.validators import UserContracting, agent_has_permission_to_assign_this_client_table_to_client, agent_has_permission_to_assign_this_establishment_to_client, agent_permissions_exist_and_does_not_have_duplicates, contracting_can_create_user, agent_has_access_to_this_client, req_user_is_agent_without_all_estabs
from orders.models import ItemTable
from .models import Client, ClientEstablishment, ClientTable, Company, Contracting, AgentEstablishment, Establishment
from rolepermissions.roles import assign_role
from rolepermissions.permissions import available_perm_status
from .models import status_choices
from django.utils.translation import gettext_lazy as _

#-----------------------------------------------/Organizations Serializers

class ContractingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contracting
        fields = ['contracting_code', 'name', 'status', 'active_users_limit', 'note']

    def update(self, instance, validated_data):
        validated_data['contracting_code'] = instance.contracting_code
        return super().update(instance, validated_data)

class CompanySerializer(serializers.ModelSerializer):
    client_table=serializers.SlugRelatedField(slug_field='client_table_compound_id', 
            queryset=ClientTable.objects.all(), allow_null=True)
    item_table=serializers.SlugRelatedField(slug_field='item_table_compound_id',
            queryset=ItemTable.objects.all(), allow_null=True)
    contracting=serializers.HiddenField(default=UserContracting())
    class Meta:
        model = Company
        fields = ['company_compound_id', 'company_code', 'contracting', 'item_table', 'client_table', 'name',
                'cnpj','status', 'note']
        validators = [UniqueTogetherValidator(queryset=Company.objects.all(), fields=['company_code', 'contracting'], 
            message=_("The field 'company_code' must be unique."))]

    def validate_client_table(self, value):
        if value:
            # Contracting Ownership
            if value.contracting != self.context["request"].user.contracting:
                raise NotFound(detail={"detail": [_("Client table not found.")]})
            return value
        return value

    def validate_item_table(self, value):
        if value:
            # Contracting Ownership
            if value.contracting != self.context["request"].user.contracting:
                raise NotFound(detail={"detail": [_("Item table not found.")]})
            return value
        return value

    def create(self, validated_data):
        validated_data['company_compound_id'] = validated_data['contracting'].contracting_code + \
                "#" + validated_data['company_code']
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Not allow to update this fields
        validated_data['company_code'] = instance.company_code
        validated_data['contracting'] = instance.contracting
        return super().update(instance, validated_data)

class EstablishmentSerializer(serializers.ModelSerializer):
    company=serializers.SlugRelatedField(slug_field='company_compound_id', queryset=Company.objects.all())
    
    class Meta:
        model = Establishment
        fields = ['establishment_compound_id', 'establishment_code', 'company', 'name', 'cnpj', 'status', 'note']
        validators = [UniqueTogetherValidator(queryset=Establishment.objects.all(), fields=['establishment_code', 'company'],
            message=_("The field 'establishment_code' must be unique by company."))]

    def validate_company(self, value):
        if value:
            if value.contracting != self.context["request"].user.contracting:
                raise serializers.ValidationError(_("Company not found."))
            return value
        return value

    def create(self, validated_data):
        # Create establishment_compound_id
        validated_data['establishment_compound_id'] = validated_data['company'].contracting.contracting_code + "#" + \
                validated_data['company'].company_code + "#" + validated_data['establishment_code']
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Not allow to update this fields
        validated_data['establishment_code'] = instance.establishment_code
        validated_data['company'] = instance.company
        return super().update(instance, validated_data)


class ClientTableSerializer(serializers.ModelSerializer):
    contracting=serializers.HiddenField(default=UserContracting())
    class Meta:
        model = ClientTable
        fields =  ['client_table_compound_id' ,'client_table_code', 'contracting', 'description', 'note']
        read_only_fields =  ['client_table_compound_id']
        validators = [UniqueTogetherValidator(queryset=ClientTable.objects.all(), fields=['client_table_code', 'contracting'], 
            message=_("The field 'client_table_code' must be unique."))]

    def create(self, validated_data):
        # Create client_table_compound_id
        validated_data['client_table_compound_id'] = validated_data['contracting'].contracting_code + \
                "#" + validated_data['client_table_code']
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Not allow to update this fields
        validated_data['client_table_code'] = instance.client_table_code
        validated_data['contracting'] = instance.contracting
        return super().update(instance, validated_data)

#  class ClientEstablishmentSerializer(serializers.ModelSerializer):
    #  establishment = serializers.SlugRelatedField(slug_field='establishment_compound_id', queryset=Establishment.objects.all())
    #  price_table = serializers.SlugRelatedField(slug_field='price_table_compound_id', allow_null=True,
            #  queryset=PriceTable.objects.all(), required=False)
    #  class Meta:
        #  model=ClientEstablishment
        #  fields = ['establishment', 'price_table']

class ClientEstablishmentToClientSerializer(serializers.ModelSerializer):
    establishment = serializers.SlugRelatedField(slug_field='establishment_compound_id', queryset=Establishment.objects.all())
    class Meta:
        model=ClientEstablishment
        fields = ['establishment']

    def validate_establishment(self, value):
        if value:
        # - Contracting owership
            if value.company.contracting != self.context["request"].user.contracting:
                raise serializers.ValidationError(_("Establishment not found."))
        return value


class ClientSerializer(serializers.ModelSerializer):
    client_establishments = ClientEstablishmentToClientSerializer(many=True)
    client_table = serializers.SlugRelatedField(slug_field='client_table_compound_id', queryset=ClientTable.objects.all())
    class Meta:
        model = Client
        fields =  ['client_compound_id', 'client_table', 'client_code', 'client_establishments',
                'vendor_code', 'name', 'cnpj', 'status', 'note']
        read_only_fields =  ['client_compound_id']
        validators = [UniqueTogetherValidator(queryset=Client.objects.all(), fields=['client_code', 'client_table'],
            message=_("The field 'client_code' must be unique by client table."))]

    def validate(self, attrs):
        request_user = self.context["request"].user
        client_establishments = attrs.get('client_establishments')
        request_user_is_agent_without_all_estabs = req_user_is_agent_without_all_estabs(request_user)
        # ----------------/ Establishments
        if client_establishments or client_establishments == []:
            establishments_list = []
            for client_establishment in client_establishments:
                # Deny duplicate establishments
                if client_establishment['establishment'] in establishments_list:
                    raise serializers.ValidationError(_("There is a duplicate establishment in 'client_establishments'"))
                establishments_list.append(client_establishment['establishment'])
                # Check if establishment.company.client_table belongs to Client client_table
                if client_establishment['establishment'].company.client_table != attrs.get("client_table"):
                    raise serializers.ValidationError(_("The 'client_table' field must correspond to the company client_table "\
                            "associated with the added establishments."))
                if request_user_is_agent_without_all_estabs:
                    # Check if agent can access establishment
                    if not agent_has_permission_to_assign_this_establishment_to_client(request_user, client_establishment['establishment']):
                        raise serializers.ValidationError(_("You can't add this establishment to this client."))
        if self.context['request'].method == 'POST':
            # ----------------/ Client Table
            # Contracting owership
            if attrs.get('client_table').contracting != request_user.contracting:
                raise serializers.ValidationError(_("Client table not found."))
            if request_user_is_agent_without_all_estabs:
                if not agent_has_permission_to_assign_this_client_table_to_client(request_user, attrs.get('client_table')):
                    raise serializers.ValidationError(_("Can't access this client_table."))
        if self.context['request'].method == 'PUT':
            # Check if agent without all estabs have access to this client
            if request_user_is_agent_without_all_estabs and not agent_has_access_to_this_client(request_user, self.instance):
                raise serializers.ValidationError(_("You can't update this client."))
        return attrs

        # - Price Table
            #  if client_establishment['price_table']:  <-----------/ validate price_table owership
                #  if client_establishment['price_table'].company.contracting != request_user.contracting:
                    #  raise serializers.ValidationError(f"You can't access this resource.")

    def create(self, validated_data):
        # Create client_compound_id
        client = Client.objects.create(
            client_compound_id = validated_data['client_table'].contracting.contracting_code + "#" + \
                    validated_data['client_table'].client_table_code + "#" + validated_data['client_code'],
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
                 client=client))
        client.client_establishments.bulk_create(client_establishments_list)
        return client

    def update(self, instance, validated_data):
        validated_data['client_code'] = instance.client_code
        validated_data['client_table'] = instance.client_table
        # When using 'return super().update ...' i can't return validated_data with nested related values to update
        client_establishments = validated_data.get('client_establishments')
        if client_establishments or client_establishments == []:
            client_establishments = validated_data.pop('client_establishments')
            update_client_establishments(instance, client_establishments)
        return super().update(instance, validated_data)
    
#-------------------------------------------------/Auth Serializers

class SwaggerLoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    contracting_code = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

class SwaggerProfilePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    current_password = serializers.CharField(write_only=True)

#------------------------------------------------------/User serializers

class UserSerializer(serializers.ModelSerializer):
    contracting = serializers.HiddenField(default=UserContracting())
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField() 
    status = serializers.ChoiceField(choices=[x[0] for x in status_choices], required=False)

    class Meta:
        model = User
        fields = ['username', 'contracting', 'first_name', 'last_name', 'email', 'status',
                'password', 'note', 'roles', 'permissions']
        extra_kwargs = {
            'password': {'write_only': True},
        }
        validators = [UniqueTogetherValidator(queryset=User.objects.all(), fields=['username', 'contracting'],
            message=_("The field 'username' must be unique."))]

    def validate(self, attrs):
        if self.context['request'].method == 'PUT':
            # I need to call it manually in the update view, because HiddenField don't work with partial=True
            self.validate_contracting(self.context["request"].user.contracting)
        return attrs

    def validate_contracting(self, value):
        if self.context['request'].method == 'POST':
            # validate the limit of users by contracting
            if not contracting_can_create_user(value):
                raise serializers.ValidationError(_("You cannot create more users. Your contracting company already reach the active users limit."))
        # Validate contracting ownership
        if self.context['request'].method == 'PUT': # There is any problem for double validation?
            if self.instance.contracting.contracting_code != value.contracting_code:
                raise serializers.ValidationError(_("User not found."))
        return value

    def update(self, instance, validated_data):
        if validated_data.get('username'): validated_data.pop('username')
        if validated_data.get('password'): validated_data.pop('password')
        # Don't log out the user in UpdateOwnProfile view
        if self.context.get("view") != "update own profile":
            # Which is the best option?
            #  if LoggedInUser.objects.get(user=instance).exists()
                #  instance.logged_in_user.session_key = None
            try:
                instance.logged_in_user.delete()
            except User.logged_in_user.RelatedObjectDoesNotExist:
                pass
        return super().update(instance, validated_data)

    def get_roles(self, user):
        # If "user" is OrderedDict. This means receive data and not receive instance.
        # If "user" is model.User. This means we receive a instance.
        if isinstance(user, OrderedDict):
            roles = []
            return roles
        roles = []
        user_roles = get_user_roles(user) 
        for role in user_roles:
            roles.append(role.get_name())
        return roles

    def get_permissions(self, user):
        if isinstance(user, OrderedDict):
            permissions_list = []
            return permissions_list 
        permissions = available_perm_status(user)
        permissions_list = []
        for key, value in permissions.items():
            if value == True:
                permissions_list.append(key) 
        return permissions_list 

class AgentEstablishmentToUserSerializer(serializers.ModelSerializer):
    establishment = serializers.SlugRelatedField(slug_field='establishment_compound_id', queryset=Establishment.objects.all())
    class Meta:
        model=AgentEstablishment
        fields = ['establishment']
    def validate_establishment(self, value):
    # Contracting Ownership
        if value.company.contracting != self.context['request'].user.contracting: 
            raise serializers.ValidationError(_("Establishment not found."))
        return value

class OwnProfileSerializer(UserSerializer):
    agent_establishments = AgentEstablishmentToUserSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = ['username', 'contracting', 'first_name', 'last_name', 'email', 'status', 'client',
                'roles', 'agent_establishments', 'permissions']
        read_only_fields = ['roles', 'permissions', 'client', 'username', 'agent_establishments', 'status']

class AdminAgentSerializer(UserSerializer):
    def create(self, validated_data):  
        username = validated_data['username']
        contracting = validated_data['contracting']
        password=validated_data['password']
        email = validated_data['email']
        user = User.objects.create_user(username, contracting, password,\
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '' ),
            email=email,
            note=validated_data.get('note', ''),
            status=1
            )
        assign_role(user, 'admin_agent')
        return user

class AgentSerializer(UserSerializer):
    agent_establishments = AgentEstablishmentToUserSerializer(many=True)
    agent_permissions = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta(UserSerializer.Meta):
        fields = ['username', 'contracting', 'first_name', 'last_name', 'email', 'status', 'password',
                'note', 'roles', 'permissions', 'agent_establishments', 'agent_permissions']
        extra_kwargs = {
            'password': {'write_only': True},
            'agent_permissions': {'write_only': True},
        }
    def validate_agent_establishments(self, value):
        # Deny duplicate values
        check_for_duplicate_values = []
        for establishment in value:
            if establishment in check_for_duplicate_values:
                raise serializers.ValidationError(_("There are duplicate values for agent_establishments."))
            check_for_duplicate_values.append(establishment)
        return value

    def validate_agent_permissions(self, value):
        if value or value == []:
            agent_permissions_exist_and_does_not_have_duplicates(value)
        return value

    def create(self, validated_data):  
        username = validated_data['username']
        contracting = validated_data['contracting']
        password=validated_data['password']
        email = validated_data['email']
        user = User.objects.create_user(username, contracting, password,\
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '' ),
            email=email,
            note=validated_data.get('note', ''),
            status=1
            )
        assign_role(user, 'agent')
        agent_permissions = validated_data["agent_permissions"]
        agent_establishments = validated_data["agent_establishments"]
        update_agent_permissions(user, agent_permissions)
        if not 'access_all_establishments' in agent_permissions:
            establishment_to_add = []
            for agent_establishment in agent_establishments:
                establishment_to_add.append(AgentEstablishment(agent=user, establishment=agent_establishment['establishment']))
            user.agent_establishments.bulk_create(establishment_to_add)
        return user

    def update(self, instance, validated_data):
        agent_permissions = validated_data.get("agent_permissions")
        if agent_permissions or agent_permissions == []:
            agent_permissions = validated_data.pop("agent_permissions")
            update_agent_permissions(instance, agent_permissions)
        agent_establishments = validated_data.get("agent_establishments")
        if agent_establishments or agent_establishments == [] and not 'access_all_establishments' in agent_permissions:
            agent_establishments = validated_data.pop("agent_establishments")
            update_agent_establishments(instance, agent_establishments)
        return super().update(instance, validated_data)


class ClientUserSerializer(UserSerializer):
    client = serializers.SlugRelatedField(slug_field='client_compound_id', queryset=Client.objects.all())

    class Meta(UserSerializer.Meta):
        fields = ['username',  'contracting', 'client', 'roles', 'permissions', 'first_name',
                'last_name', 'email', 'status', 'password', 'note']

    def validate_client(self, value):
        request_user = self.context["request"].user
        if self.context['request'].method == 'POST':
            # Check if client is from the same contracting as the request user
            if value.client_table.contracting != request_user.contracting:
                raise serializers.ValidationError(_("Client table not found."))
            # Check if request user is agent without all estabs and can assign this client for a user_client
            if req_user_is_agent_without_all_estabs(request_user) and not agent_has_access_to_this_client(request_user, value):
                raise serializers.ValidationError(_("You have no permission to assign this client to this client user.")) 
        return value

    def create(self, validated_data):  
        username = validated_data['username']
        contracting = validated_data['contracting']
        password=validated_data['password']
        email = validated_data['email']
        user = User.objects.create_user(username, contracting, password,\
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '' ),
            email=email,
            client=validated_data['client'],
            note=validated_data.get('note', ''),
            status=1
        )
        assign_role(user, 'client_user')
        return user

    def update(self, instance, validated_data):
        if validated_data.get('client'): validated_data.pop('client')
        return super().update(instance, validated_data)
