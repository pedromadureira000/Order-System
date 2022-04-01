from django.contrib.auth.models import Permission
from django.db.models.query_utils import Q
from rolepermissions.checkers import has_permission
from rolepermissions.permissions import available_perm_status
from .models import AgentEstablishment, User
from organization.models import Company
from rolepermissions.roles import get_user_roles

def get_all_client_users_by_agent(agent):
    if has_permission(agent, 'access_all_establishments'):
        return User.objects.filter(Q(contracting=agent.contracting), Q(groups__name='client_user'))
    return User.objects.filter(Q(contracting=agent.contracting), Q(groups__name='client_user'), 
            Q(client__client_table__company__in=Company.objects.filter(establishment__in=agent.establishments.all())))

#------------------------------------/Reverse Foreign key Batch Updates/---------------------------------------------------

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

def get_update_permission(user):
    # TODO seems bugado
    role = get_user_roles(user)
    permission = 'update_' + role[0].get_name()
    return permission

