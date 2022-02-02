from typing import OrderedDict
#  from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from core.models import User
from rolepermissions.roles import get_user_roles
from rolepermissions.permissions import available_perm_status
from core.validators import OnlyLettersNumbersDashAndUnderscoreUsernameValidator, contracting_can_create_user, has_permission_to_create_user
from .models import Client, ClientTable, Company, Contracting, AgentEstablishment, Establishment
from rolepermissions.roles import assign_role
from rolepermissions.checkers import has_permission, has_role
from rolepermissions.permissions import grant_permission
from .roles import Agent


class ContractingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contracting
        fields = ['contracting_code', 'name', 'status', 'active_users_limit', 'note']

    def update(self, instance, validated_data):
        validated_data['contracting_code'] = instance.contracting_code
        return super().update(instance, validated_data)


class CompanySerializer(serializers.ModelSerializer):
    contracting=serializers.SlugRelatedField(slug_field='contracting_code', queryset=Contracting.objects.all())
    class Meta:
        model = Company
        fields = ['company_id', 'company_code', 'contracting', 'item_table', 'client_table', 'name', 'cnpj', 'status', 'note']
        validators = [UniqueTogetherValidator(queryset=Company.objects.all(), fields=['company_code', 'contracting'], 
            message="The field 'company_code' and 'contracting' must be a unique set.")]

    def create(self, validated_data):
        # Create company_id
        validated_data['company_id'] = validated_data['contracting'].contracting_code + "#" + validated_data['company_code']
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Not allow to update this fields
        validated_data['company_code'] = instance.company_code
        validated_data['contracting'] = instance.contracting
        return super().update(instance, validated_data)

class EstablishmentSerializer(serializers.ModelSerializer):
    company=serializers.SlugRelatedField(slug_field='company_code', queryset=Company.objects.all())
    
    class Meta:
        model = Establishment
        fields = ['establishment_id', 'name', 'establishment_code', 'company', 'cnpj', 'status', 'note']
        validators = [UniqueTogetherValidator(queryset=Establishment.objects.all(), fields=['establishment_code', 'company'],
            message="The field 'establishment_code' and 'company' must be a unique set.")]

    #  def validate(self, attrs):
        #  print('>>>>>>>>>>>>>>>>>>: ', type(attrs['establishment_code']))
        #  return super().validate(attrs)

    def create(self, validated_data):
        # Create establishment_id
        validated_data['establishment_id'] = validated_data['company'].contracting.contracting_code + "#" + \
                validated_data['company'].company_code + "#" + validated_data['establishment_code']
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Not allow to update this fields
        validated_data['establishment_code'] = instance.establishment_code
        validated_data['company'] = instance.company
        return super().update(instance, validated_data)

class EstablishmentSerializerToAgentEstab(serializers.ModelSerializer):
    company=serializers.SlugRelatedField(slug_field='company_code', queryset=Company.objects.all())
    
    class Meta:
        model = Establishment
        fields = ['establishment_code', 'company']


class AgentEstablishmentSerializer(serializers.ModelSerializer):
    #  establishment = serializers.SlugRelatedField(slug_field='establishment_code', queryset=Establishment.objects.all())
    establishment = EstablishmentSerializerToAgentEstab()
    class Meta:
        model=AgentEstablishment
        fields = ['establishment']


class ClientSerializer(serializers.ModelSerializer):
    price_table = serializers.StringRelatedField()
    class Meta:
        model = Client
        fields =  ['name', 'cnpj', 'status', 'price_table', 'client_code', 'vendor_code', 'note']
        read_only_fields =  ['price_table']

    #  def validate_company_type(self, value):
        #  request_user = self.context.get("request_user")
        #  if value == "C" and not has_permission(request_user, "create_contracting_company"): 
            ##if have create permission, it goes for update too.
            #  raise serializers.ValidationError(f"You can't create/update contracting companies.")
        #  if value != "C" and not has_permission(request_user, "create_client_company"):
            #  raise serializers.ValidationError(f"You can't create/update client companies.")
        #  return value

    def validate(self, attrs):
        # - Company type
        request_user = self.context.get("request_user")
        if attrs.get('company_type') == "C" and not has_permission(request_user, "create_contracting_company"): 
            ##  if have create permission, it goes for update too.
            raise serializers.ValidationError(f"You can't create/update contracting companies.")
        if attrs.get('company_type') != "C" and not has_permission(request_user, "create_client_company"):
            raise serializers.ValidationError(f"You can't create/update client companies.")
        return attrs

    def create(self, validated_data):  
        request_user = self.context.get("request_user")
        company = Company(
            name=validated_data.get('name', ''),
            cnpj=validated_data.get('cnpj', '' ),
            company_code=validated_data.get('company_code', '' ),
            status=validated_data.get('status', '' ),
            company_type=validated_data.get('company_type', '' ),
            client_code=validated_data.get('client_code', '' ),
            vendor_code=validated_data.get('vendor_code', '' ),
            note=validated_data.get('note', '' ),
        )
        if company.company_type != "C":
            company.contracting_company = request_user.company
        company.save()
        return company


class UserSerializer(serializers.ModelSerializer):
    #  company = serializers.SerializerMethodField()
    #  company_code = serializers.CharField(write_only=True)
    contracting = serializers.SlugRelatedField(slug_field='contracting_code', queryset=Contracting.objects.all())
    client = serializers.SlugRelatedField(slug_field='client_code', queryset=Client.objects.all(), allow_null=True)
    establishments = AgentEstablishmentSerializer(many=True, allow_null=True)
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField() 
    role =  serializers.ChoiceField(["admin_agent", "agent", "client_user"], write_only=True)
    agent_permissions =  serializers.ListField(child=serializers.CharField(), write_only=True, allow_null=True )
    email = serializers.EmailField()
    username = serializers.CharField(validators=[OnlyLettersNumbersDashAndUnderscoreUsernameValidator])

    class Meta:
        ref_name = "User Serializer" # fixes name collision with djoser when fetching urls with swagger
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'cpf', 'password', 'roles', 'permissions', 'contracting', \
                'client', 'establishments', 'role', 'agent_permissions']
        read_only_fields = ['roles', 'permissions']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'write_only': True},
            'agent_permissions': {'write_only': True},
        }

    def validate(self, attrs):
        if self.context.get("method") == "post":
            request_user = self.context.get("request_user")

            # ---/ Status field and contracting user limit validation

            contracting = attrs.get('contracting')
            if contracting_can_create_user(contracting):
                self.context['status'] = 1
            else: 
                raise serializers.ValidationError(f"You cannot create more users. Your contracting company already reach the active users limit.")

            # ---/ Has permission to create user

            role = attrs.get("role")
            if not has_permission_to_create_user(request_user, role):
                raise serializers.ValidationError(f"You can't assign '{role}' role to an user.")

            # ---/ Per role validations

            if role == "agent":
                #-/Permissions
                agent_permissions = attrs.get("agent_permissions")
                establishments = attrs.get("establishments")
                access_all_establishments = False
                for permission in agent_permissions:
                    if not permission in Agent.available_permissions.keys():
                        raise serializers.ValidationError(f"You can't assign '{permission}' permission to an agent.")
                    if permission == "access_all_establishments":
                        access_all_establishments = True
                #-/Establishments
                agent_permissions = attrs.get("agent_permissions")
                if not access_all_establishments:
                    for establishment in establishments:
                        if establishment not in []:
                            raise serializers.ValidationError(f"You can't assign '{permission}' permission to an agent.")

            if role == "client_user":
                pass
                #  try: 
                    #  client_table = ClientTable.objects.get(client_table_code=attrs.get('client_table_code'), contracting=request_user.contracting)
                    #  client = Client.objects.get(client_code=attrs.get('client_code'), client_table=client_table )
                    #  self.context['client'] = client
                #  except Client.DoesNotExist:
                    #  raise serializers.ValidationError("Client company does not exist.")

            return attrs

        if self.context.get("method") == "put":
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
            client=self.context.get('client', None),
            note=validated_data.get('note', ''),
            status=self.context.get('status')
            ) #contracting == contracting_code
        #  user = User(
            #  first_name=validated_data.get('first_name', ''),
            #  last_name=validated_data.get('last_name', '' ),
            #  cpf=validated_data.get('cpf', '' ),
            #  username=username,
            #  client=self.client,
            #  user_code=username + "#" + self.company.company_code,
            #  email=validated_data['email']
        #  )
        #  password = validated_data['password']
        #  user.set_password(password)
        #  user.save()
        role = validated_data["role"]
        assign_role(user, role)
        agent_permissions = validated_data["agent_permissions"]
        establishments = validated_data["establishments"]
        if role == "agent":
            for permission in agent_permissions:
                grant_permission(user, permission)
            for establishment in establishments:
              print('========================> : ', establishment )
                #  user.agentestablishment_set.bulk_create()

        return user  # this need to be returned

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.cpf = validated_data.get('cpf', instance.cpf)
        instance.save()
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

    #  def get_company(self, user):
        #  if isinstance(user, OrderedDict):
            #  company_serialized = CompanySerializer(user['company_code'])
            #  return company_serialized.data
        #  company_serialized = CompanySerializer(user.company)
        #  return company_serialized.data

#--------------/Swagger

class SwaggerLoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    contracting_code = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
 

class SwaggerProfilePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    current_password = serializers.CharField(write_only=True)
