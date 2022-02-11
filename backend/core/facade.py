from django.contrib.auth.models import Permission
from django.db.models.query_utils import Q
from rolepermissions.checkers import has_permission, has_role
from rolepermissions.permissions import available_perm_status, grant_permission, revoke_permission
from core.models import AgentEstablishment, Client, ClientEstablishment, ClientTable, Company, User
from orders.models import PriceTable
from .roles import Agent



def company_has_active_users(company):
    if type(company.user_set.filter(is_active=True).all().first()) == User:
        return True
    return False

def get_all_users_by_erp(user):
    return User.objects.filter(is_superuser=False, contracting=user.contracting)

def get_all_users_by_admin_agent(user):
    return User.objects.filter(Q(is_superuser=False), Q(contracting=user.contracting), ~Q(groups__name='erp'))

def get_all_client_users_by_agent(user):
    if has_permission(user, 'access_all_establishments'):
        return User.objects.filter(Q(contracting=user.contracting), Q(groups__name='client_user'))
    return User.objects.filter(Q(contracting=user.contracting), Q(groups__name='client_user'), Q(client__client_table__company__in=Company.objects.filter(establishment__in=user.establishments.all())))

def get_agent_client_tables(agent):
    return ClientTable.objects.filter(company__in=Company.objects.filter(establishment__in=agent.establishments.all()))

def get_clients_by_agent(user):
    client_tables = get_agent_client_tables(user)
    return Client.objects.filter(client_table__in=client_tables)

#------------------------------------/Reverse Foreign key Batch Updates/---------------------------------------------------
def update_client_establishments(client, client_establishments):
    client_establishments_set = {client_estab['establishment'].establishment_compound_id for client_estab in client_establishments}
    current_client_establishments = ClientEstablishment.objects.filter(client=client)
    current_client_establishments_set = set(current_client_establishments.values_list('establishment__establishment_compound_id', flat=True))
    intersection = client_establishments_set.intersection(current_client_establishments_set)
    to_delete = current_client_establishments_set.difference(intersection)
    to_create = client_establishments_set.difference(intersection)
    # Delete
    delete_it = current_client_establishments.filter(establishment__establishment_compound_id__in=to_delete)
    delete_it.delete()
    # Create 
    establishments_to_create = list(filter(lambda estab: estab["establishment"].establishment_compound_id in to_create, client_establishments))
    client_establishments_to_create = [ClientEstablishment(establishment=obj['establishment'], client=client) for \
            obj in establishments_to_create]
    client.client_establishments.bulk_create(client_establishments_to_create)

def update_agent_permissions(agent, agent_permissions):
    agent_permissions = set(agent_permissions)
    #  all_agent_permissions = set(Agent.available_permissions.keys())
    current_agent_permissions = {k for k, v in available_perm_status(agent).items() if v == True} 
    permissions_to_delete = current_agent_permissions.difference(agent_permissions)
    permissions_to_create = agent_permissions.difference(current_agent_permissions)
    agent.user_permissions.remove(*agent.user_permissions.filter(codename__in=permissions_to_delete))
    agent.user_permissions.add(*Permission.objects.filter(codename__in=permissions_to_create))

def update_agent_establishments(agent, agent_establishments):
    agent_establishments_set = {agent_estab['establishment'].establishment_compound_id for agent_estab in agent_establishments}
    current_agent_establishments = AgentEstablishment.objects.filter(agent=agent)
    current_agent_establishments_set =  set(current_agent_establishments.values_list('establishment__establishment_compound_id', flat=True))
    intersection = agent_establishments_set.intersection(current_agent_establishments_set)
    to_delete = current_agent_establishments_set.difference(intersection)
    to_create = agent_establishments_set.difference(intersection)
    # Delete
    delete_it = current_agent_establishments.filter(establishment__establishment_compound_id__in=to_delete)
    delete_it.delete()
    # Create 
    establishments_to_create = list(filter(lambda estab: estab["establishment"].establishment_compound_id in to_create, agent_establishments))
    agent_establishments_to_create = [AgentEstablishment(establishment=obj['establishment'], agent=agent) for obj in establishments_to_create]
    agent.agent_establishments.bulk_create(agent_establishments_to_create)
