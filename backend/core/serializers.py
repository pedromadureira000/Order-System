from typing import OrderedDict
from django.utils.timezone import now
from rest_framework import serializers
from core.models import User
from rolepermissions.roles import get_user_roles
from rolepermissions.permissions import available_perm_status
from core.validators import OnlyLettersNumbersDashAndUnderscoreUsernameValidator
from .models import Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields =  ['name', 'cnpj', 'company_code', 'status', 'company_type'  ]
        read_only_fields =  ['name', 'cnpj', 'company_code', 'status', 'company_type'  ]


class UserSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField() 
    email = serializers.EmailField()
    username = serializers.CharField(validators=[OnlyLettersNumbersDashAndUnderscoreUsernameValidator])
    company_code = serializers.CharField(write_only=True)

    class Meta:
        ref_name = "User Serializer" # fixes name collision with djoser when fetching urls with swagger
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'cpf', 'company_code', 'password', 'roles', 'permissions', 'company']
        read_only_fields = ['roles', 'permissions', 'company']
        extra_kwargs = {
            'password': {'write_only': True},
            'company_code': {'write_only': True}
        }

    def validate(self, attrs):
        try: 
            company = Company.objects.get(company_code=attrs['company_code'])
            self.company = company
        except Company.DoesNotExist:
            raise serializers.ValidationError("Company does not exist.")

        user = company.user_set.filter(username=attrs["username"]).first()
        if user:
            raise serializers.ValidationError("This username is already being used.")


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
        
        password = self.validated_data['password']
        user.set_password(password)
        user.save()
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
 

