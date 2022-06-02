from typing import OrderedDict
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.validators import UniqueTogetherValidator
from item.serializers import CategoryPUTSerializer
from order.serializers import OrderGetSerializer, searchOnePriceItemToMakeOrderSerializer
from .facade import update_agent_establishments, update_agent_permissions
from .models import User
from rolepermissions.roles import get_user_roles
from .validators import agent_permissions_exist_and_does_not_have_duplicates 
from organization.validators import UserContracting, contracting_can_create_user, agent_has_access_to_this_client
from .models import AgentEstablishment
from organization.models import Client, Contracting, Establishment
from rolepermissions.roles import assign_role
from .models import status_choices
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token


#-------------------------------------------------/Auth Serializers

class SwaggerLoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    contracting_code = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

class SwaggerProfilePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    current_password = serializers.CharField(write_only=True)

class SwaggerDuplicateOrderResponse(serializers.Serializer):
    response_data = OrderGetSerializer()
    some_items_were_not_copied = serializers.BooleanField()

class PriceItemsResponse(serializers.Serializer):
    price_items = searchOnePriceItemToMakeOrderSerializer(many=True)
    current_page = serializers.IntegerField()
    lastPage = serializers.IntegerField()
    total = serializers.IntegerField()

class CategoriesToMakeOrderResponse(serializers.Serializer):
    class PriceTableAUX(serializers.Serializer):
        description = serializers.CharField()
        table_code = serializers.CharField()
    categories = CategoryPUTSerializer(many=True)
    price_table = PriceTableAUX()

#------------------------------------------------------/User serializers

class UserSerializer(serializers.ModelSerializer):
    contracting_id = serializers.HiddenField(default=UserContracting())
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField() 
    status = serializers.ChoiceField(choices=[x[0] for x in status_choices], required=False)
    contracting_code = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'contracting_id', 'first_name', 'last_name', 'email', 'status',
                'password', 'note', 'roles', 'permissions', 'contracting_code']
        extra_kwargs = {
            'password': {'write_only': True},
        }
        validators = [UniqueTogetherValidator(queryset=User.objects.all(), fields=['username', 'contracting_id'],
            message=_("The 'username' field must be unique."))]

    def validate(self, attrs):
        if self.context['request'].method == 'PUT':
            # I need to call it manually in the update view, because HiddenField don't work with partial=True
            self.validate_contracting_id(self.context["request"].user.contracting_id)
        return attrs

    def validate_contracting_id(self, value):
        if self.context['request'].method == 'POST':
            # validate the limit of users by contracting
            if not contracting_can_create_user(self.context["request"].user.contracting):
                raise PermissionDenied(_("You cannot create more users. Your contracting company already reach the active users limit.")) 
        # Validate contracting ownership
        if self.context['request'].method == 'PUT':
            if self.instance.contracting_id != value:
                raise serializers.ValidationError(_("User not found."))
        return value

    def update(self, instance, validated_data):
        if validated_data.get('username'): validated_data.pop('username')
        if validated_data.get('password'): validated_data.pop('password')
        # Don't log out the user in UpdateOwnProfile view
        if self.context.get("view") != "update own profile":
            validated_data['current_session_key'] = ''
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
        permissions = user.user_permissions.all()
        permissions_list = [perm.codename for perm in permissions]
        return permissions_list 

    def get_contracting_code(self, user):
        return user.contracting_id

class UpdateUserPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

class AgentEstablishmentToUserSerializer(serializers.ModelSerializer):
    establishment = serializers.SlugRelatedField(slug_field='establishment_compound_id', queryset=Establishment.objects.all())
    class Meta:
        model=AgentEstablishment
        fields = ['establishment']
    def validate_establishment(self, value):
    # Contracting Ownership
        if value.company.contracting_id != self.context['request'].user.contracting_id: 
            raise serializers.ValidationError(_("Establishment not found."))
        return value

class OwnProfileSerializer(UserSerializer):
    #  agent_establishments = AgentEstablishmentToUserSerializer(many=True, read_only=True)
    client_name = serializers.SerializerMethodField()
    contracting_code = serializers.SerializerMethodField()
    status = serializers.ChoiceField(choices=[x[0] for x in status_choices], read_only=True)

    class Meta:
        model = User
        fields = ['username', 'contracting_id', 'first_name', 'last_name', 'email', 'status', 'client', 'client_name',
                'roles', 'permissions', 'contracting_code']
        read_only_fields = ['status' , 'client', 'username']

    def get_contracting_code(self, user):
        return user.contracting_id

    def get_client_name(self, user):
        if user.client_id:
            return user.client.name
        return None

class ERPUserPOSTSerializer(UserSerializer):
    #overwrite UserSerializer contracting field
    contracting = serializers.SlugRelatedField(slug_field='contracting_code', queryset=Contracting.objects.all(), write_only=True)
    user_code = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = ['username', 'contracting', 'contracting_id','first_name', 'last_name', 'email', 'status',
                'roles', 'permissions', 'contracting_code', 'user_code', 'note', 'password']
        validators = [UniqueTogetherValidator(queryset=User.objects.all(), fields=['username', 'contracting'],
            message=_("The 'username' field must be unique."))]

    #overwrite UserSerializer validation
    def validate_contracting_id(self, value):
        return value

    def create(self, validated_data):  
        username = validated_data['username']
        contracting = validated_data['contracting']
        password=validated_data['password']
        email = validated_data['email']
        user = User.objects.create_user(username, contracting.contracting_code, password,\
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '' ),
            email=email,
            note=validated_data.get('note', ''),
            status=1
            )
        assign_role(user, 'erp_user')
        Token.objects.create(user=user)
        return user

    def get_user_code(self, user):
        return user.user_code

class ERPUserPUTSerializer(serializers.ModelSerializer):
    #OBS: I don't utilized the UserSerializer because I shouldn't have contracting_id field
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField() 
    status = serializers.ChoiceField(choices=[x[0] for x in status_choices])
    user_code = serializers.SerializerMethodField()
    contracting_code = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'status',
                'roles', 'permissions', 'contracting_code', 'user_code', 'note']
        read_only_fields = ['username']

    def get_user_code(self, user):
        return user.user_code

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
        permissions = user.user_permissions.all()
        permissions_list = [perm.codename for perm in permissions]
        return permissions_list 

    def get_contracting_code(self, user):
        return user.contracting_id

class AdminAgentPOSTSerializer(UserSerializer):
    def create(self, validated_data):  
        username = validated_data['username']
        contracting_id = validated_data['contracting_id']
        password=validated_data['password']
        email = validated_data['email']
        user = User.objects.create_user(username, contracting_id, password,\
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '' ),
            email=email,
            note=validated_data.get('note', ''),
            status=1
            )
        assign_role(user, 'admin_agent')
        return user

class AdminAgentPUTSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'status',
                'roles', 'permissions', 'contracting_code', 'user_code', 'note']
        read_only_fields = ['username', 'user_code']

class AgentPOSTSerializer(UserSerializer):
    agent_establishments = AgentEstablishmentToUserSerializer(many=True)
    agent_permissions = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta(UserSerializer.Meta):
        fields = ['username', 'contracting_id', 'first_name', 'last_name', 'email', 'status', 'password',
                'note', 'roles', 'permissions', 'agent_establishments', 'agent_permissions', 'contracting_code']
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
        contracting_id = validated_data['contracting_id']
        password=validated_data['password']
        email = validated_data['email']
        user = User.objects.create_user(username, contracting_id, password,\
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

class AgentPUTSerializer(UserSerializer):
    agent_establishments = AgentEstablishmentToUserSerializer(many=True)
    agent_permissions = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta(UserSerializer.Meta):
        fields = ['username', 'contracting_id', 'first_name', 'last_name', 'email', 'status',
                'note', 'roles', 'permissions', 'agent_establishments', 'agent_permissions', 'contracting_code']
        read_only_fields = ['username']
        extra_kwargs = {
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
        agent_permissions_exist_and_does_not_have_duplicates(value)
        return value

    def update(self, instance, validated_data):
        agent_permissions = validated_data.pop("agent_permissions")
        update_agent_permissions(instance, agent_permissions)
        agent_establishments = validated_data.pop("agent_establishments")
        if not 'access_all_establishments' in agent_permissions:
            update_agent_establishments(instance, agent_establishments)
        return super().update(instance, validated_data)

class ClientUserPOSTSerializer(UserSerializer):
    client = serializers.SlugRelatedField(slug_field='client_compound_id', queryset=Client.objects.all())

    class Meta(UserSerializer.Meta):
        fields = ['username',  'contracting_id', 'client', 'roles', 'permissions', 'first_name',
                'last_name', 'email', 'status', 'password', 'note', 'contracting_code']

    def validate_client(self, value):
        request_user = self.context["request"].user
        # Check if client is from the same contracting as the request user
        if value.client_table.contracting_id != request_user.contracting_id:
            raise serializers.ValidationError(_("Client table not found."))
        # Check if request user is agent without all estabs and can assign this client for a client_user
        if self.context['request_user_is_agent_without_all_estabs'] and not agent_has_access_to_this_client(request_user, value):
            raise serializers.ValidationError(_("You have no permission to assign this client to this client user.")) 
        return value

    def create(self, validated_data):  
        username = validated_data['username']
        contracting_id = validated_data['contracting_id']
        password=validated_data['password']
        email = validated_data['email']
        user = User.objects.create_user(username, contracting_id, password,\
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '' ),
            email=email,
            client=validated_data['client'],
            note=validated_data.get('note', ''),
            status=1
        )
        assign_role(user, 'client_user')
        return user

class ClientUserPUTSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ['username', 'client', 'roles', 'permissions', 'first_name',
                'last_name', 'email', 'status', 'note', 'contracting_code']
        read_only_fields = ['username', 'client']

    def validate_client(self, value):
        request_user = self.context["request"].user
        if self.context['request'].method == 'POST':
            # Check if client is from the same contracting as the request user
            if value.client_table.contracting_id != request_user.contracting_id:
                raise serializers.ValidationError(_("Client table not found."))
            # Check if request user is agent without all estabs and can assign this client for a client_user
            if self.context['request_user_is_agent_without_all_estabs'] and not agent_has_access_to_this_client(request_user, value):
                raise serializers.ValidationError(_("You have no permission to assign this client to this client user.")) 
            # Check if there is already an client user for this client
            if value.user_set.exists():
                raise serializers.ValidationError(_("You cannot create a client user for this client, because it already exists.")) 
        return value
