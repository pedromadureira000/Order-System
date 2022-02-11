import re
from rest_framework import serializers
from rolepermissions.checkers import has_permission, has_role
from rolepermissions.roles import get_user_roles
from core.facade import get_agent_client_tables

from core.models import ClientTable
from core.roles import Agent

# ---------------/ DRF Serializer Field Validators

def OnlyLettersNumbersDashAndUnderscoreUsernameValidator(value):
    if not re.fullmatch('^[a-zA-Z0-9_.-]*$', value):
        raise serializers.ValidationError('The username must have only letters, numbers, "-" and "_".')


# ---------------/ Django Role Permissions Object Validators
def is_adminAgent_or_erpClient(user):
    return has_role(user, ['erp', 'admin_agent'])


def has_any_permission_to_create_user(user):
    return True if is_adminAgent_or_erpClient(user) or has_permission(user, 'create_client_user') else False

def has_any_permission_to_update_user(user):
    return True if is_adminAgent_or_erpClient(user) or has_permission(user, 'update_client_user') else False

def has_any_permission_to_delete_user(user):
    return True if is_adminAgent_or_erpClient(user) or has_permission(user, 'delete_client_user') else False

def has_permission_to_create_user(user, role):
    create_user_permission = "create_" + role
    if not has_permission(user, create_user_permission):
        return False
    return True

def has_permission_to_update_user(request_user, user):
    role = get_user_roles(user)[0] # An user will have just one role
    if not has_permission(request_user, "update_" + role.get_name()):
        return False
    return True

def has_permission_to_delete_user(request_user, user):
    if user.is_superuser or has_role(user, 'erp'):
        return False
    if has_role(request_user, ['erp', 'admin_agent']):
        return True
    if has_role(request_user, 'agent') and has_permission(request_user, 'delete_client_user') and has_role(user, 'client_user'):
        if has_permission(request_user, 'access_all_establishments'):
            return True
        client_tables = get_agent_client_tables(request_user)
        if user.client.client_table in client_tables:
            return True
    return False

def contracting_can_create_user(contracting):
    active_users = contracting.user_set.filter(status=1)
    if active_users.count() >= contracting.active_users_limit:
        return False
    return True

def agent_has_access_to_this_client(user, client):
    client_tables = get_agent_client_tables(user)
    if client.client_table not in client_tables:
        return False
    else: 
        return True

def agent_has_permission_to_assign_this_client_table_to_client(user, client_table):
    client_tables = get_agent_client_tables(user)
    if not client_table in client_tables:
        return False
    return True

def agent_has_permission_to_assign_this_establishment_to_client(user, establishment):
    client_tables = get_agent_client_tables(user)
    if not establishment.company.client_table in client_tables:
        return False
    return True


def agent_permissions_exist(agent_permissions):
    for permission in agent_permissions:
        if not permission in Agent.available_permissions.keys():
            print('========================> : Terrible error' )
            raise serializers.ValidationError(f"You can't assign '{permission}' permission to an agent.")


#----------------/ Django default Field Method
class UserContracting:
    """
    May be applied as a `default=...` value on a serializer field.
    Returns the current user.
    """
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.contracting
