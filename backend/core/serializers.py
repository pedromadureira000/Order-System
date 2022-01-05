from typing import OrderedDict
from django.utils.timezone import now
from rest_framework import serializers
from core.models import User
from rolepermissions.roles import get_user_roles
from rolepermissions.permissions import available_perm_status
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields =  ['name', 'cnpj', 'company_code', 'status', 'company_type'  ]
        read_only_fields =  ['name', 'cnpj', 'company_code', 'status', 'company_type'  ]


class UserSerializer(serializers.ModelSerializer):
    #  TODO add unique toguether constraitValidation
    company = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField() # will call get_<field_name> by default
    permissions = serializers.SerializerMethodField() 
    email = serializers.EmailField()
    username = serializers.CharField()
    company_code = serializers.IntegerField(write_only=True)
    #  company = serializers.RelatedField(read_only=True)  <<< this not work well
    #  company =  CompanySerializer(read_only=True) # <<< this not work as read_only field

    class Meta:
        ref_name = "User Serializer" # fixes name collision with djoser when fetching urls with swagger
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'cpf', 'company_code', 'password', 'roles', 'permissions', 'company']
        read_only_fields = ['roles', 'permissions', 'company']
        extra_kwargs = {
            'password': {'write_only': True},
            'company_code': {'write_only': True}
        }

    def validate_company_code(self, value):
        print('========================> : INSIDE Validate company_code' )
        try: 
            company = Company.objects.get(company_code=value)
            #  company = Company.objects.filter(company_code=company_code).first()[0]  <=== get or none
            return company
        except Company.DoesNotExist:
            raise serializers.ValidationError("Company does not exist.")


    def create(self, validated_data):  
        print('========================> : INSIDE CREATE' )
        username = self.validated_data['username']
        company = self.validated_data['company_code']
        #  company_code = self.validated_data['company_code']
        user = User(
            first_name=self.validated_data.get('first_name', ''),
            last_name=self.validated_data.get('last_name', '' ),
            cpf=self.validated_data.get('cpf', '' ),
            username=username,
            company=company,
            #  user_code=username + "#" + company_code,
            user_code=username + "#" + str(company.company_code),
            email=self.validated_data['email']
        )
        
        password = self.validated_data['password']
        user.set_password(password)
        user.save()
        return user  # this need to be returned

    def update(self, instance, validated_data):
        print('========================> : INSIDE UPDATE' )
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
 

