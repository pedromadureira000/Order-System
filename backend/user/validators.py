from rest_framework import serializers
from rolepermissions.checkers import has_permission, has_role
from organization.facade import get_agent_client_tables
from .roles import Agent
from django.utils.translation import gettext_lazy as _

# ---------------/ Django Role Permissions Validators

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

def agent_permissions_exist_and_does_not_have_duplicates(agent_permissions):
    check_for_duplicate_values = []
    for permission in agent_permissions:
        if permission in check_for_duplicate_values:
            raise serializers.ValidationError(_("There are duplicate values for agent_permissions"))
        check_for_duplicate_values.append(permission)
        if not permission in Agent.available_permissions.keys():
            raise serializers.ValidationError(_("You can't assign '{permission}' permission to an agent.").format(permission=permission))

def req_user_is_agent_without_all_estabs(request_user):
    return has_role(request_user, 'agent') and not has_permission(request_user, 'access_all_establishments')
