from rolepermissions.roles import AbstractUserRole


class Erp(AbstractUserRole):
    available_permissions = {
        #ERP
        "create_company": True,
        "get_companies": True,
        "update_company": True,
        "delete_company": True,
        "create_establishment": True,
        "get_establishments": True,
        "update_establishment": True,
        "delete_establishment": True,
        "create_item_table": True,
        "update_item_table": True,
        "get_item_tables": True,
        "delete_item_table": True,
        "assign_item_table": True,
        "create_client_table": True,
        "update_client_table": True,
        "get_client_tables": True,
        "delete_client_table": True,
        "assign_client_table": True,
        "generate_boleto": True,
        "get_transfered_orders": True, #TODO do it is not the same as filtred 'get_orders' ?
        #AdminAgent
        "create_admin_agent": True,
        "delete_admin_agent": True,
        "update_admin_agent": True,
        "get_admin_agents": True,
        "create_agent": True,
        "get_agents": True,
        "update_agent": True,
        "delete_agent": True,
        # Agent
        "access_all_establishments": True,
        "create_client": True,
        "get_clients": True,
        "update_client": True,
            #  "add_establishment_to_client": True,
            #  "remove_establishment_from_client": True,
            #  "assign_pricetable_to_client": True,
        "delete_client": True,
        "create_client_user": True,
        "get_client_users": True,
        "update_client_user": True,
        "delete_client_user": True,
        "create_item": True,
        "get_items": True,
        "update_item": True,
        "delete_item": True,
        "create_item_category": True,
        "get_item_category": True,
        "update_item_category": True,
        "delete_item_category": True,
        "create_price_table": True,
        "get_price_tables": True,
        "update_price_table": True,
        "delete_price_table": True,
        "get_orders":True,
        "update_orders_status": True,
    }

class AdminAgent(AbstractUserRole):
    available_permissions = {
        "create_admin_agent": True,
        "delete_admin_agent": True,
        "update_admin_agent": True,
        "get_admin_agents": True,
        "create_agent": True,
        "get_agents": True,
        "update_agent": True,
        "delete_agent": True,
        # Agent
        "access_all_establishments": True,
        "create_client": True,
        "get_clients": True,
        "update_client": True,
        "delete_client": True,
        "create_client_user": True,
        "get_client_users": True,
        "update_client_user": True,
        "delete_client_user": True,
        "create_item": True,
        "get_items": True,
        "update_item": True,
        "delete_item": True,
        "create_item_category": True,
        "get_item_category": True,
        "update_item_category": True,
        "delete_item_category": True,
        "create_price_table": True,
        "get_price_tables": True,
        "update_price_table": True,
        "delete_price_table": True,
        "get_orders":True,
        "update_orders_status": True
    }

class Agent(AbstractUserRole):
    available_permissions = {
        "access_all_establishments": False,
        "create_client": False,
        "get_clients": False,
        "update_client": False,
        "delete_client": False,
        "create_client_user": False,
        "get_client_users": False,
        "update_client_user": False,
        "delete_client_user": False,
        "create_item": False,
        "get_items": False,
        "update_item": False,
        "delete_item": False,
        "create_item_category": False,
        "get_item_category": False,
        "update_item_category": False,
        "delete_item_category": False,
        "create_price_table": False,
        "get_price_tables": False,
        "update_price_table": False,
        "delete_price_table": False,
        #  "add_establishment_to_client": False,
        #  "get_client_establishments": False,
        #  "remove_establishment_from_client": False,
        #  "assign_pricetable_to_client": False,
        "get_orders":False,
        "update_orders_status": False
    }

class ClientUser(AbstractUserRole):
    available_permissions = {
        "make_order": True,
        "get_orders": True,
        "edit_order_in_typing": True,
        "save_order_as_template": True,
        "transfer_order": True
    }
