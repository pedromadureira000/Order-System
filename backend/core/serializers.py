from typing import OrderedDict
#  from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from core.facade import update_agent_establishments, update_agent_permissions, update_client_establishments
from core.models import User
from rolepermissions.roles import clear_roles, get_user_roles, remove_role
from rolepermissions.permissions import available_perm_status
from core.validators import OnlyLettersNumbersDashAndUnderscoreUsernameValidator, UserContracting, agent_has_permission_to_assign_this_client_table_to_client, agent_has_permission_to_assign_this_establishment_to_client, agent_permissions_exist, contracting_can_create_user, has_permission_to_create_user, agent_has_access_to_this_client, has_permission_to_update_user
from orders.models import ItemTable, PriceTable
from .models import Client, ClientEstablishment, ClientTable, Company, Contracting, AgentEstablishment, Establishment
from rolepermissions.roles import assign_role
from rolepermissions.checkers import has_permission, has_role
from rolepermissions.permissions import grant_permission

from rolepermissions.permissions import available_perm_status
#-------------------------------------------------/Auth Serializers

class SwaggerLoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    contracting_code = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
 

class SwaggerProfilePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    current_password = serializers.CharField(write_only=True)

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
            #  queryset=ClientTable.objects.filter(contracting=sel), allow_null=True)
    item_table=serializers.SlugRelatedField(slug_field='item_table_compound_id',
            queryset=ItemTable.objects.all(), allow_null=True)
    contracting=serializers.HiddenField(default=UserContracting())
    class Meta:
        model = Company
        fields = ['company_compound_id', 'company_code', 'contracting', 'item_table', 'client_table', 'name',
                'cnpj','status', 'note']
        validators = [UniqueTogetherValidator(queryset=Company.objects.all(), fields=['company_code', 'contracting'], 
            message="The field 'company_code' must be unique.")]

    def validate_client_table(self, value):
        if value:
            if value.contracting != self.context["request"].user.contracting:
                raise serializers.ValidationError(f"You can't access this client_table.")
            return value
        return value

    def validate_item_table(self, value):
        if value:
            if value.contracting != self.context["request"].user.contracting:
                raise serializers.ValidationError(f"You can't access this item_table.")
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
            message="The field 'establishment_code' and 'company' must be a unique set.")]

    def validate_company(self, value):
        if value:
            if value.contracting != self.context["request"].user.contracting:
                raise serializers.ValidationError(f"You can't access this company.")
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
            message="The field 'client_table_code' must be unique.")]

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
                raise serializers.ValidationError(f"Can't access this establishment.")
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
            message="The field 'client_code' and 'client_table' must be a unique set.")]

    def validate(self, attrs):
        request_user = self.context.get("request").user
        client_establishments = attrs['client_establishments']
        req_user_is_agent_without_all_estabs = has_role(request_user, 'agent') and not has_permission(request_user, 'access_all_establishments')
        # ----------------/ Client Table
        # - Contracting owership
        if attrs.get('client_table').contracting != request_user.contracting:
            raise serializers.ValidationError(f"Can't access this client_table.")
        if req_user_is_agent_without_all_estabs:
            if not agent_has_permission_to_assign_this_client_table_to_client(request_user, attrs.get('client_table')):
                raise serializers.ValidationError(f"Can't access this client_table.")

        # ----------------/ Establishments
        # - Duplicated Establishments
        establishments_list = []
        for client_establishment in client_establishments:
            if client_establishment['establishment'] in establishments_list:
                raise serializers.ValidationError(f"There is a duplicated establishment in 'client_establishments'")
            establishments_list.append(client_establishment['establishment'])
        # - Establishment.company.client_table Belongs to Client client_table
            if client_establishment['establishment'].company.client_table != attrs.get("client_table"):
                raise serializers.ValidationError(f"The 'client_table' field must correspond to the company client_table "\
                        "associated with the added establishments.")
            if req_user_is_agent_without_all_estabs:
                # -  Agent can access establishment
                if not agent_has_permission_to_assign_this_establishment_to_client(request_user, client_establishment['establishment']):
                    raise serializers.ValidationError(f"You can't add this establishment to this client.")
        if self.context['method'] == 'put' and req_user_is_agent_without_all_estabs and not agent_has_access_to_this_client(request_user, self.instance):
            raise serializers.ValidationError(f"You can't update this client.")

        return attrs

        # - Price Table
            #  if client_establishment['price_table']:  <-----------/ validate price_table owership
                #  if client_establishment['price_table'].company.contracting != request_user.contracting:
                    #  raise serializers.ValidationError(f"You can't access this resource.")

    def create(self, validated_data):
        # Create client_compound_id
        client = Client(
            client_compound_id = validated_data['client_table'].contracting.contracting_code + "#" + \
                    validated_data['client_table'].client_table_code + "#" + validated_data['client_code'],
            client_table=validated_data['client_table'],
            client_code=validated_data['client_code'],
            vendor_code=validated_data['vendor_code'],
            name=validated_data['name'],
            cnpj=validated_data['cnpj'],
            status=validated_data['status'],
            note=validated_data['note']
        )
        client.save()
        client_establishments_list = []
        for client_establishment in validated_data['client_establishments']:
            client_establishments_list.append(ClientEstablishment(establishment=client_establishment['establishment'], 
                 client=client))
        client.client_establishments.bulk_create(client_establishments_list)
        return client

    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        instance.cnpj = validated_data['cnpj']
        instance.status = validated_data['status']
        instance.note = validated_data['note']
        instance.vendor_code = validated_data['vendor_code']
        update_client_establishments(instance, validated_data['client_establishments'])
        instance.save()
        return instance
    
#------------------------------------------------------/User serializers

class AgentEstablishmentToUserSerializer(serializers.ModelSerializer):
    establishment = serializers.SlugRelatedField(slug_field='establishment_compound_id', queryset=Establishment.objects.all())
    class Meta:
        model=AgentEstablishment
        fields = ['establishment']
        #  validators = [UniqueTogetherValidator(queryset=AgentEstablishment.objects.all(), fields=['establishment', 'agent'],
            #  message="The field 'establishment' and 'agent' must be a unique set.")]

    def validate_establishment(self, value):
    #-------/Establishments has the same contracting as the user
        if value.company.contracting != self.context['request'].user.contracting: 
            raise serializers.ValidationError(f"Can't access this establishment.")
        return value
        #  if value:
            #  if value.company.contracting != self.context['request'].user.contracting: 
                #  raise serializers.ValidationError(f"You can't access this resource.")
        #  return value


class UserSerializer(serializers.ModelSerializer):
    contracting = serializers.HiddenField(default=UserContracting())
    client = serializers.SlugRelatedField(slug_field='client_compound_id', queryset=Client.objects.all(), allow_null=True)
    agent_establishments = AgentEstablishmentToUserSerializer(many=True, allow_null=True)
    role = serializers.ChoiceField(["admin_agent", "agent", "client_user"], write_only=True)
    agent_permissions = serializers.ListField(child=serializers.CharField(), write_only=True, allow_null=True )
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField() 

    class Meta:
        ref_name = "User Serializer" # fixes name collision with djoser when fetching urls with swagger
        model = User
        fields = ['username', 'contracting', 'client', 'agent_establishments', 'first_name', 'last_name', 'email', 'cpf',  'status',
                'password', 'roles', 'permissions', 'role', 'agent_permissions', 'note']
        read_only_fields = ['roles', 'permissions']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'write_only': True},
            'agent_permissions': {'write_only': True},
        }
        validators = [UniqueTogetherValidator(queryset=User.objects.all(), fields=['username', 'contracting'],
            message="The field 'username' must be unique.")]

    def validate(self, attrs):
        if self.context.get("method") == "post":
            request_user = self.context.get("request").user
            # -----------------------------/ Status field and contracting user limit validation
            contracting = attrs.get('contracting')
            if contracting_can_create_user(contracting):
                self.context['status'] = 1
            else: 
                raise serializers.ValidationError(f"You cannot create more users. Your contracting company already reach the active users limit.")
            #  -----------------------------/ Has permission to create user
            role = attrs.get("role")
            if not has_permission_to_create_user(request_user, role):
                raise serializers.ValidationError(f"You can't assign '{role}' role to an user.")
            # -----------------------------/ Per role validations
            if role == "agent":
                #------/Permissions exist
                agent_permissions_exist(attrs.get("agent_permissions"))
            if role == "client_user":
                #------/Enforce Client
                if attrs.get('client') == None:
                    raise serializers.ValidationError(f"'client' field must be sent.")
                #------/Client is from the same contracting
                if attrs.get('client').client_table.contracting != request_user.contracting: #TODO client_compound_id check
                    raise serializers.ValidationError(f"Can't access this client.")
                # -----/AgentEstablishments validation for Agent
                if has_role(request_user, 'agent'):
                    if not has_permission(request_user, 'access_all_establishments'):
                        if not agent_has_access_to_this_client(request_user, attrs.get('client')):
                            raise serializers.ValidationError(f"You have no permission to assign this client to this user.") 
            return attrs
        if self.context.get("method") == "put":
            request_user = self.context.get("request").user
            instance = self.instance
            if self.context.get("view") == "update own profile":
                return attrs
            if self.context.get("view") == "update user":
                if not has_permission_to_update_user(request_user, instance):
                    raise serializers.ValidationError(f"You have no permission to update this user.") 
                if has_role(instance, 'agent'):
                    if not agent_has_access_to_this_client(request_user, instance.client): #TODO test this validation
                        raise serializers.ValidationError(f"You have no permission update this client user.") 
                    agent_permissions = attrs.get('agent_permissions')
                    if agent_permissions:
                        agent_permissions_exist(agent_permissions)
            return attrs

    def create(self, validated_data):  
        username = validated_data['username']
        contracting = validated_data['contracting']
        password=validated_data['password']
        email = validated_data['email']
        user = User.objects.create_user(username, contracting, password,\
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '' ),
            cpf=validated_data.get('cpf', '' ),
            email=email,
            client=validated_data.get('client', None),
            note=validated_data.get('note', ''),
            status=self.context['status']
            )
        role = validated_data["role"]
        assign_role(user, role)
        agent_permissions = validated_data["agent_permissions"]
        agent_establishments = validated_data["agent_establishments"]
        if role == "agent":
            for permission in agent_permissions:
                grant_permission(user, permission)
            if not 'access_all_establishments' in agent_permissions:
                establishment_to_add = []
                for agent_establishment in agent_establishments:
                    establishment_to_add.append(AgentEstablishment(agent=user, establishment=agent_establishment['establishment']))
                user.agent_establishments.bulk_create(establishment_to_add)
        return user

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.cpf = validated_data.get('cpf', instance.cpf)
        if self.context.get("view") == "update user" and has_role(instance, 'agent'):
            agent_permissions = validated_data.get("agent_permissions")
            agent_establishments = validated_data.get("agent_establishments")
            if agent_permissions or agent_permissions == []:
                update_agent_permissions(instance, agent_permissions)
                instance.logged_in_user.session_key = None
            if agent_establishments or agent_establishments == [] and not 'access_all_establishments' in agent_permissions:
                update_agent_establishments(instance, agent_establishments)
        return instance

    def get_roles(self, user):
        if isinstance(user, OrderedDict):
            #  print('>>>>>>> "user" is OrderedDict. This means receive data and not receive instance.' )
            roles = []
            return roles
        #  print('>>>>>>> "user" is model.User. This means we receive a instance.' )
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
