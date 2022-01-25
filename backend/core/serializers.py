from typing import OrderedDict
from django.utils.timezone import now
from rest_framework import serializers
from core.models import User
from rolepermissions.roles import get_user_roles
from rolepermissions.permissions import available_perm_status
from core.validators import OnlyLettersNumbersDashAndUnderscoreUsernameValidator
from .models import Company
from rolepermissions.roles import assign_role
from rolepermissions.checkers import has_permission, has_role
from rolepermissions.permissions import grant_permission
from .roles import Agent

class CompanySerializer(serializers.ModelSerializer):
    price_table = serializers.StringRelatedField()
    class Meta:
        model = Company
        fields =  ['name', 'cnpj', 'company_code', 'status', 'company_type', 'price_table', 'client_code', 'vendor_code', 'note']
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
    company = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField() 
    role =  serializers.ChoiceField(["admin_agent", "agent", "client"], write_only=True)
    agent_permissions =  serializers.ListField(child=serializers.CharField(), write_only=True)
    email = serializers.EmailField()
    username = serializers.CharField(validators=[OnlyLettersNumbersDashAndUnderscoreUsernameValidator])
    company_code = serializers.CharField(write_only=True)

    class Meta:
        ref_name = "User Serializer" # fixes name collision with djoser when fetching urls with swagger
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'cpf', 'company_code', 'password', 'roles', 'permissions', 'company', 'role', 'agent_permissions']
        read_only_fields = ['roles', 'permissions', 'company']
        extra_kwargs = {
            'password': {'write_only': True},
            'company_code': {'write_only': True},
            'role': {'write_only': True},
            'agent_permissions': {'write_only': True},
        }

    def validate(self, attrs):
        if self.context.get("method") == "post":
            request_user = self.context.get("request_user")

            # ---/ Role

            role = attrs.get("role")
            create_user_permission = "create_" + role
            if not has_permission(request_user, create_user_permission):
                raise serializers.ValidationError(f"You can't assign '{role}' role to an user.")

            # ---/ Company 

            try: 
                company = Company.objects.get(company_code=attrs['company_code'])
                self.company = company
            except Company.DoesNotExist:
                raise serializers.ValidationError("Company does not exist.")

            #  print(">>>>>>>>>>>>>>>company.contracting_company:", company.contracting_company)
            #  print(">>>>>>>>>>>>>>>request_user.company:",  request_user.company)
            if role == "agent" and not has_role(request_user, 'admin'):
                if company != request_user.company:
                    raise serializers.ValidationError("You can't assign this company to an agent.")
                    #  raise serializers.ValidationError("You can't assign to an agent a different company then yours.") <--
                if company.company_type !=  "C":
                    raise serializers.ValidationError("The agent's company must be a contracting company.")

            if role == "client":
                if company.company_type ==  "C":
                    #  raise serializers.ValidationError("You can't assign a contracting company to a client.")  <--
                    raise serializers.ValidationError("You can't assign this company to a client.")
                if company.contracting_company != request_user.company:
                    # You shouldn't assign a company that does not belong to your company
                    raise serializers.ValidationError("You can't assign this company to a client.")


            if role == "admin_agent" and company.company_type !=  "C":
                raise serializers.ValidationError("You can't assign this company to an admin_agent, because it's not a contracting company.")
            # ---/ Username

            user = company.user_set.filter(username=attrs["username"]).first()
            if user:
                raise serializers.ValidationError("This username is already being used.")

            # ---/ Agent Permissions

            if role == "agent": 
                agent_permissions = attrs.get("agent_permissions")
                for permission in agent_permissions:
                    if not permission in Agent.available_permissions.keys():
                        raise serializers.ValidationError(f"You can't assign '{permission}' permission to an agent.")
            return attrs

        if self.context.get("method") == "put":
            return attrs

    def create(self, validated_data):  
        #  print('========================> : INSIDE CREATE' )
        username = validated_data['username']
        user = User(
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '' ),
            cpf=validated_data.get('cpf', '' ),
            username=username,
            company=self.company,
            user_code=username + "#" + self.company.company_code,
            email=validated_data['email']
        )
        password = validated_data['password']
        user.set_password(password)
        user.save()
        role = validated_data["role"]
        assign_role(user, role)
        agent_permissions = validated_data["agent_permissions"]
        if role == "agent":
            for permission in agent_permissions:
                grant_permission(user, permission)
        return user  # this need to be returned

    def update(self, instance, validated_data):
        #  print('========================> : INSIDE UPDATE' )
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.cpf = validated_data.get('cpf', instance.cpf)
        instance.save()
        return instance

    def get_roles(self, user):
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

    def get_company(self, user):
        if isinstance(user, OrderedDict):
            company_serialized = CompanySerializer(user['company_code'])
            return company_serialized.data
        company_serialized = CompanySerializer(user.company)
        return company_serialized.data

#--------------/Swagger

class SwaggerLoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    company_code = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
 

class SwaggerProfilePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    current_password = serializers.CharField(write_only=True)
 

