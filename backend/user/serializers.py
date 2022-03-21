from typing import OrderedDict
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .facade import update_agent_establishments, update_agent_permissions
from .models import User
from rolepermissions.roles import get_user_roles
from rolepermissions.permissions import available_perm_status
from .validators import agent_permissions_exist_and_does_not_have_duplicates 
from organization.validators import UserContracting, contracting_can_create_user, agent_has_access_to_this_client
from .models import AgentEstablishment
from organization.models import Client, Contracting, Establishment
from rolepermissions.roles import assign_role
from rolepermissions.permissions import available_perm_status
from .models import status_choices
from django.utils.translation import gettext_lazy as _

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
    contracting_code = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'contracting', 'first_name', 'last_name', 'email', 'status',
                'password', 'note', 'roles', 'permissions', 'contracting_code']
        extra_kwargs = {
            'password': {'write_only': True},
        }
        validators = [UniqueTogetherValidator(queryset=User.objects.all(), fields=['username', 'contracting'],
            message=_("The 'username' field must be unique."))]

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

    def get_contracting_code(self, user):
        return user.contracting.contracting_code

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
    client = serializers.SlugRelatedField(slug_field='client_compound_id', queryset=Client.objects.all())
    contracting_code = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = ['username', 'contracting', 'first_name', 'last_name', 'email', 'status', 'client',
                'roles', 'agent_establishments', 'permissions', 'contracting_code']
        read_only_fields = ['roles', 'permissions', 'client', 'username', 'agent_establishments', 'status', 'contracting_code']

    def get_contracting_code(self, user):
        return user.contracting.contracting_code

class ERPUserSerializer(UserSerializer):
    #overwrite UserSerializer contracting field
    contracting = serializers.SlugRelatedField(slug_field='contracting_code', queryset=Contracting.objects.all())
    #overwrite UserSerializer validation
    def validate_contracting(self, value):
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
        assign_role(user, 'erp')
        return user

    def update(self, instance, validated_data):
        # prevent change of contracting
        validated_data.pop('contracting') if validated_data.get('contracting') else None
        return super().update(instance, validated_data)

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
            # Check if request user is agent without all estabs and can assign this client for a client_user
            if self.context['request_user_is_agent_without_all_estabs'] and not agent_has_access_to_this_client(request_user, value):
                raise serializers.ValidationError(_("You have no permission to assign this client to this client user.")) 
            # Check if there is already an client user for this client
            if value.user_set.exists():
                raise serializers.ValidationError(_("You cannot create a client user for this client, because it already exists.")) 
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