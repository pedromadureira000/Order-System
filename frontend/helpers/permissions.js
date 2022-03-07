//----------/ Organizations

export const CRUDcontractingPermissions = [
  "create_contracting",
  "get_contracting",
  "update_contracting",
  "delete_contracting",
]
export const CRUDcompanyPermissions = [
  "create_company",
  "get_companies",
  "update_company",
  "delete_company",
]
export const CRUDestablishmentPermissions = [
  "create_establishment",
  "get_establishments",
  "update_establishment",
  "delete_establishment",
] 
export const CRUDclientTablePermissions = [
  "create_client_table",
  "update_client_table",
  "get_client_tables",
  "delete_client_table",
]
export const CRUDclientPermissions = [
  "create_client",
  "get_clients",
  "update_client",
  "delete_client",
]

//----------/ Users

export const CRUDerpUserPermissions = [
  "create_erp_user",
  "get_erp_user",
  "update_erp_user",
  "delete_erp_user",
]
export const CRUDadminAgentPermissions = [
  "create_admin_agent",
  "delete_admin_agent",
  "update_admin_agent",
  "get_admin_agents",
]
export const CRUDagentPermissions = [
  "create_agent",
  "get_agents",
  "update_agent",
  "delete_agent",
]
export const CRUDclientUserPermissions = [
  "create_client_user",
  "get_client_users",
  "update_client_user",
  "delete_client_user",
]
//----------/ Items

export const CRUDitemTablePerms = [
  "create_item_table",
  "update_item_table",
  "get_item_tables",
  "delete_item_table",
]
export const CRUDitemCategoryPerms = [
  "create_item_category",
  "get_item_category",
  "update_item_category",
  "delete_item_category",
]
export const CRUDitemPermissions = [
  "create_item",
  "get_items",
  "update_item",
  "delete_item",
]
export const CRUDpriceTablePerms = [
  "create_price_table",
  "get_price_tables",
  "update_price_table",
  "delete_price_table",
]

//------------/ Roles Permissions

export const super_user = [
  "create_contracting",
  "get_contracting",
  "update_contracting",
  "delete_contracting",
  "create_erp_user",
  "get_erp_user",
  "update_erp_user",
  "delete_erp_user",
]
export const erp_user = [
  "create_company",
  "get_companies",
  "update_company",
  "delete_company",
  "create_establishment",
  "get_establishments",
  "update_establishment",
  "delete_establishment",
  "create_item_table",
  "update_item_table",
  "get_item_tables",
  "delete_item_table",
  "create_client_table",
  "update_client_table",
  "get_client_tables",
  "delete_client_table",
  "create_or_update_price_item",
]
export const adminAgent = [
  "create_admin_agent",
  "delete_admin_agent",
  "update_admin_agent",
  "get_admin_agents",
  "create_agent",
  "get_agents",
  "update_agent",
  "delete_agent",
  "delete_order",
]
export const agent = [
  "access_all_establishments",
  "create_client",
  "get_clients",
  "update_client",
  "delete_client",
  "create_client_user",
  "get_client_users",
  "update_client_user",
  "delete_client_user",
  "create_item",
  "get_items",
  "update_item",
  "delete_item",
  "create_item_category",
  "get_item_category",
  "update_item_category",
  "delete_item_category",
  "create_price_table",
  "get_price_tables",
  "update_price_table",
  "delete_price_table",
  "get_orders",
  "update_order_status",
]
export const client_user = [
  "get_orders",
]
