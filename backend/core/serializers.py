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
    class Meta:
        model = Company
        fields =  ['name', 'cnpj', 'company_code', 'status', 'company_type'  ]
        #  read_only_fields =  ['name', 'cnpj', 'company_code', 'status', 'company_type'  ]

class UserSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField() 
    role =  serializers.ChoiceField(["admin_agent", "agent", "client"], write_only=True)
    #  agent_permissions =  serializers.DictField(child=serializers.BooleanField(), write_only=True)
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
        # ---/ Company Code
        try: 
            company = Company.objects.get(company_code=attrs['company_code'])
            self.company = company
        except Company.DoesNotExist:
            raise serializers.ValidationError("Company does not exist.")

        # ---/ Username
        user = company.user_set.filter(username=attrs["username"]).first()
        if user:
            raise serializers.ValidationError("This username is already being used.")

        # ---/ Role
        request_user = self.context.get("request_user")
        role = attrs.get("role")
        create_user_permission = "create_" + role
        if not has_permission(request_user, create_user_permission):
            raise serializers.ValidationError(f"You can't assign '{role}' role to an user.")

        # ---/ Agent Permissions

        if role == "agent":
            agent_permissions = attrs.get("agent_permissions")
            for permission in agent_permissions:
                if not permission in Agent.available_permissions.keys():
                    raise serializers.ValidationError(f"You can't assign '{permission}' permission to an agent.")

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
 

