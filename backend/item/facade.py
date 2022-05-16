from django.db.models.query import Prefetch
from rolepermissions.checkers import has_permission
from item.models import ItemCategory, Item, PriceItem, PriceTable, ItemTable
from organization.models import Company
#  from organization.facade import get_agent_companies  # ! This import is causing a circular dependency error
from organization import facade

def get_categories_by_agent(agent):
    if has_permission(agent, 'access_all_establishments'):
        return ItemCategory.objects.filter(item_table__contracting_id=agent.contracting_id)
    return ItemCategory.objects.filter(item_table__company__in=Company.objects.filter(establishment__in=agent.establishments.all()))

def get_items_by_agent(agent):
    if has_permission(agent, 'access_all_establishments'):
        return Item.objects.filter(item_table__contracting_id=agent.contracting_id)
    return Item.objects.filter(item_table__company__in=Company.objects.filter(establishment__in=agent.establishments.all()))

def get_price_tables_by_agent(agent): 
    if has_permission(agent, 'access_all_establishments'):
        return PriceTable.objects.filter(company__contracting_id=agent.contracting_id).select_related('company')
    return PriceTable.objects.filter(company__in=Company.objects.filter(establishment__in=agent.establishments.all())).select_related('company')

def get_agent_item_tables(agent):
    return ItemTable.objects.filter(company__in=facade.get_agent_companies(agent))

def get_categories_to_create_item_by_agent_without_all_estabs(agent, item_table_compound_id):
    return ItemCategory.objects.filter(item_table__company__in=Company.objects.filter(establishment__in=agent.establishments.all()), item_table__item_table_compound_id=item_table_compound_id)

def get_companies_to_create_pricetabe_by_agent(agent):
    return facade.get_agent_companies(agent).exclude(item_table=None).filter(status=1)

#------------------------------------/Reverse Foreign key Batch Updates/---------------------------------------------------

def update_price_items_from_price_table(price_table, price_items):
    price_items_set = {(price_item['item'].item_compound_id, price_item['unit_price']) for price_item in price_items}
    current_price_items = PriceItem.objects.filter(price_table=price_table)
    current_price_items_set = set(current_price_items.values_list('item__item_compound_id', 'unit_price'))
    intersection = price_items_set.intersection(current_price_items_set)
    to_delete = current_price_items_set.difference(intersection)
    to_create = price_items_set.difference(intersection)
    to_delete_item_list = [price_item[0] for price_item in to_delete]
    current_price_items.filter(item__item_compound_id__in=to_delete_item_list).delete()
    price_items_to_create = list(filter(lambda price_item: (price_item["item"].item_compound_id, price_item['unit_price']) in \
            to_create, price_items))
    if price_items_to_create:
        price_items_to_create = [PriceItem(item=obj['item'], unit_price=obj['unit_price'], price_table=price_table) for obj in  price_items_to_create]
        price_table.price_items.bulk_create(price_items_to_create)


