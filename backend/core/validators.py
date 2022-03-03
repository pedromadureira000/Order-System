from rest_framework import serializers
from rolepermissions.checkers import has_permission, has_role
from rolepermissions.roles import get_user_roles
from core.facade import get_agent_client_tables, get_agent_companies, get_agent_item_tables
from core.roles import Agent
from django.utils.translation import gettext_lazy as _

# ---------------/ Django Role Permissions Validators

def contracting_can_create_user(contracting):
    active_users = contracting.user_set.filter(status=1)
    if active_users.count() >= contracting.active_users_limit:
        return False
    return True

def agent_has_access_to_this_client(agent, client):
    client_tables = get_agent_client_tables(agent)
    if client.client_table not in client_tables:
        return False
    else: 
        return True

def agent_has_access_to_this_client_user(agent, client_user):
    client_tables = get_agent_client_tables(agent)
    if client_user.client_table not in client_tables:
        return False
    else: 
        return True

def agent_has_permission_to_assign_this_client_table_to_client(agent, client_table):
    client_tables = get_agent_client_tables(agent)
    if not client_table in client_tables:
        return False
    return True

def agent_has_permission_to_assign_this_establishment_to_client(agent, establishment):
    client_tables = get_agent_client_tables(agent)
    if not establishment.company.client_table in client_tables:
        return False
    return True

def agent_permissions_exist_and_does_not_have_duplicates(agent_permissions):
    check_for_duplicate_values = []
    for permission in agent_permissions:
        if permission in check_for_duplicate_values:
            raise serializers.ValidationError(_("There are duplicate values for agent_permissions"))
        check_for_duplicate_values.append(permission)
        if not permission in Agent.available_permissions.keys():
            raise serializers.ValidationError(_(f"You can't assign '{permission}' permission to an agent.").format(permission=permission))

def req_user_is_agent_without_all_estabs(request_user):
    return has_role(request_user, 'agent') and not has_permission(request_user, 'access_all_establishments')

def agent_has_access_to_this_item_table(agent, item_table):
    item_tables = get_agent_item_tables(agent)
    if item_table not in item_tables:
        return False
    else: 
        return True

def agent_has_access_to_this_price_table(agent, price_table):
    companies = get_agent_companies(agent)
    if price_table.company not in companies:
        return False
    else: 
        return True

#----------------/ Django default Field Method

class UserContracting:
    """
    May be applied as a `default=...` value on a serializer field.
    Returns the current user.
    """
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.contracting
