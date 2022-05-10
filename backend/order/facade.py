from organization.facade import get_agent_companies
from organization.models import ClientEstablishment, Company, Establishment
from .models import Order, OrderedItem
from django.db.models import Prefetch
from django.db.models import Q

# ----------------------------/ Orders /-----------------------------
def get_orders_by_agent(agent):
    return Order.objects.filter(establishment__in=agent.establishments.all())

def fetch_comps_with_estabs_to_fill_filter_selectors_to_search_orders(user):
    establishments = Establishment.objects.all()
    return Company.objects.filter(contracting_id=user.contracting_id).prefetch_related(
        Prefetch('establishment_set', queryset=establishments, to_attr='establishments')
    )

def fetch_comps_with_estabs_to_fill_filter_selectors_to_search_orders_by_agent(user):
    return get_agent_companies(user).prefetch_related(
        Prefetch('establishment_set', queryset=user.establishments.all(), to_attr='establishments')
    )

def fetch_comps_with_estabs_to_fill_filter_selectors_to_search_orders_by_client_user(user):
    #  establishments = user.client.establishments.all()  <-- This would make a unnecessary query to 'client' 
    establishments = Establishment.objects.filter(clientestablishment__client_id=user.client_id)
    return Company.objects.filter(establishment__in=establishments).prefetch_related(
        Prefetch('establishment_set', queryset=establishments, to_attr='establishments')
    )

def get_comps_and_estabs_to_duplicate_order(cli_user, item_table_compound_id):
    cliestabs = ClientEstablishment.objects.filter(~Q(price_table=None),client_id=cli_user.client_id)
    establishments = Establishment.objects.filter(clientestablishment__in=cliestabs, status=1)
    return Company.objects.filter(status=1, establishment__in=establishments, item_table__item_table_compound_id=item_table_compound_id).prefetch_related(Prefetch('establishment_set', queryset=establishments, to_attr='establishments'))

def update_ordered_items(order, ordered_items, current_ordered_items):
    # Create set of OrderedItems as tuples
    ordered_items_set = {(ordered_item['item'].item_compound_id, ordered_item['quantity'], ordered_item['unit_price'], 
        ordered_item['sequence_number']) for ordered_item in ordered_items}
    current_ordered_items_set = set(current_ordered_items.values_list('item__item_compound_id', 'quantity', 'unit_price', 'sequence_number'))
    intersection = ordered_items_set.intersection(current_ordered_items_set)
    to_delete = current_ordered_items_set.difference(intersection)
    to_create = ordered_items_set.difference(intersection)
    to_delete_item_list = [ordered_item[0] for ordered_item in to_delete]
    current_ordered_items.filter(item__item_compound_id__in=to_delete_item_list).delete()
    # List the OrderedItems to be created from the serialized 'ordered_items'. 
    ordered_items_to_create = list(filter(lambda ordered_item: (ordered_item["item"].item_compound_id, 
        ordered_item['quantity'], ordered_item['unit_price'], ordered_item['sequence_number']) in to_create, ordered_items))
    if ordered_items_to_create:
        # Create a list with the real OrderedItem instances to be saved with bulk_create.
        ordered_items_to_create = [OrderedItem(item=obj['item'], quantity=obj['quantity'], unit_price=obj['unit_price'],
            order=order, sequence_number=obj['sequence_number']) for obj in  ordered_items_to_create]
        order.ordered_items.bulk_create(ordered_items_to_create)
