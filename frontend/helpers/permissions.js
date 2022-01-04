export const adminAgentPermissions = [
  "create_agent",
  "get_agents",
  "update_agent",
  "delete_agent",
]

export const agentPermissions = [
  "create_client",
  "get_clients",
  "update_client",
  "delete_client",
]

export const adminPermissions = [
  "get_all_users",
  "create_admin_agent",
  "delete_admin_agent",
  "update_admin_agent",
  "get_all_admin_agents",
  ...adminAgentPermissions,
  ...agentPermissions
]

export const orderPermissions = [
  "crud_order",
]

export const itemPermissions = [
  "create_item",
  "get_items",
  "update_item",
  "delete_item",
]

export const categoryPermissions = [
  "create_item_category",
  "get_item_category",
  "update_item_category",
  "delete_item_category",
]

export const priceTablePermissions = [
  "create_price_table",
  "get_price_tables",
  "update_price_table",
  "delete_price_table",
]

