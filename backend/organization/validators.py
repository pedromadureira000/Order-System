from organization.facade import get_agent_client_tables
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

def agent_has_permission_to_assign_this_establishment_to_client(agent, establishment):
    client_tables = get_agent_client_tables(agent)
    if not establishment.company.client_table in client_tables:
        return False
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

class UserClientId:
    """
    May be applied as a `default=...` value on a serializer field.
    Returns the current user.
    """
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.client_id

