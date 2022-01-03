 from rolepermissions.roles import AbstractUserRole


class Admin(AbstractUserRole):
    available_permissions = {
        "get_all_users": True,
        "create_admin_agent": True,
        "delete_admin_agent": True,
        "update_admin_agent": True,
        "get_all_admin_agents": True,
         #AdminAgent
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
        # Client
        "crud_order": True,
    }


class AdminAgent(AbstractUserRole):
    available_permissions = {
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
    }

class Agent(AbstractUserRole):
    available_permissions = {
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
