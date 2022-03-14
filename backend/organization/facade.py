from organization.models import Client, ClientEstablishment, ClientTable, Company, Establishment
from user.models import User

def company_has_active_users(company):
    if type(company.user_set.filter(is_active=True).all().first()) == User:
        return True
    return False

def get_agent_companies(agent):
    return Company.objects.filter(establishment__in=agent.establishments.all())

def get_agent_client_tables(agent):
    return ClientTable.objects.filter(company__in=get_agent_companies(agent))

def get_clients_by_agent(user):
    client_tables = get_agent_client_tables(user)
    return Client.objects.filter(client_table__in=client_tables)

#---/ Client
def get_companies_to_create_client(request_user, req_user_is_agent_without_all_estabs):
    if req_user_is_agent_without_all_estabs:
        return get_agent_companies(request_user).exclude(client_table=None)
    return Company.objects.filter(contracting=request_user.contracting).exclude(client_table=None)

def get_establishments_to_create_client(request_user, client_table_compound_id, req_user_is_agent_without_all_estabs):
    if req_user_is_agent_without_all_estabs:
        return request_user.establishments.filter(company__client_table__client_table_compound_id=client_table_compound_id)
    return Establishment.objects.filter(company__client_table__client_table_compound_id=client_table_compound_id)

#  def get_items_by_category():
    #  itens_actives = Item.objects.filter(active=True)
    #  return ItemCategory.objects.prefetch_related(
        #  Prefetch('item_set', queryset=itens_actives, to_attr='items')).all()



#------------------------------------/Reverse Foreign key Batch Updates/---------------------------------------------------

def update_client_establishments(client, client_establishments):
    client_establishments_set = {(client_estab['establishment'].establishment_compound_id, client_estab['price_table'].price_table_compound_id if client_estab['price_table'] else None) for client_estab in client_establishments}
    current_client_establishments = ClientEstablishment.objects.filter(client=client)
    current_client_establishments_set = set(current_client_establishments.values_list('establishment__establishment_compound_id', 'price_table__price_table_compound_id'))
    intersection = client_establishments_set.intersection(current_client_establishments_set)
    to_create = client_establishments_set.difference(intersection)
    to_delete = current_client_establishments_set.difference(intersection)
    to_delete_establishment_list = [cli_estab[0] for cli_estab in to_delete]
    # Delete client estabs
    current_client_establishments.filter(establishment__establishment_compound_id__in=to_delete_establishment_list).delete()
    # List the ClientEstablishments to be created from the serialized 'client_establishments'. 
    client_establishments_to_create = list(filter(lambda cli_estab: (cli_estab['establishment'].establishment_compound_id, cli_estab['price_table'].price_table_compound_id if cli_estab['price_table'] else None) in to_create, client_establishments))
    # Create client estabs
    if client_establishments_to_create:
        client_establishments_to_create = [ClientEstablishment(client=client, establishment=item['establishment'], 
            price_table=item['price_table']) for item in client_establishments_to_create]
        client.client_establishments.bulk_create(client_establishments_to_create)
