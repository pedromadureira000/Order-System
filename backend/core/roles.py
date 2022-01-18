from rolepermissions.roles import AbstractUserRole


class Admin(AbstractUserRole):
    available_permissions = {
        "create_contracting_company": True,
        "get_companies": True,
        "update_contracting_company": True,
        "delete_contracting_company": True,
        "get_all_users": True,
        "create_admin_agent": True,
        "delete_admin_agent": True,
        "update_admin_agent": True,
        "get_all_admin_agents": True,
        #AdminAgent
        "create_client_company": True,
        "get_client_companies": True,
        "update_client_company": True,
        "delete_client_company": True,
        "create_agent": True,
        "get_agents": True,
        "update_agent": True,
        "delete_agent": True,
        # Agent
        "create_client": True,
        "get_clients": True,
        "update_client": True,
        "delete_client": True,
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
    }


class AdminAgent(AbstractUserRole):
    available_permissions = {
        "create_client_company": True,
        "get_client_companies": True,
        "update_client_company": True,
        "delete_client_company": True,
        "create_agent": True,
        "get_agents": True,
        "update_agent": True,
        "delete_agent": True,
        # Agent
        "create_client": True,
        "get_clients": True,
        "update_client": True,
        "delete_client": True,
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
    }

class Agent(AbstractUserRole):
    available_permissions = {
        "create_client": False,
        "get_clients": False,
        "update_client": False,
        "delete_client": False,
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
    }

class Client(AbstractUserRole):
    available_permissions = {
        "crud_order": True,
    }

class ERPClient(AbstractUserRole):
    available_permissions = {
        "generate_boleto": True,
        "get_transfered_orders": True,                                                                                                             
        "update_orders_status": True,                                                                                                              
        "update_price_table": True,                                                                                                                
        "update_items_table": True,                                                                                                                
        "update_item_category": True,    
    }
