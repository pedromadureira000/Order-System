from organization.facade import get_agent_companies
from .facade import get_agent_item_tables
from django.utils.translation import gettext_lazy as _

# ---------------/ Django Role Permissions Validators

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
