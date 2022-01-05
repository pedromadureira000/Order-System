export const user = {
  username: 'joao',
	first_name: 'Joao',
	last_name: 'Silva',
	email: 'jaaosilva@phsw.com',
  cpf: '231.002.999-00',
  company: {
      "name": "phsw",
      "cnpj": "40229893000166",
      "company_code": 123,
      "status": "A",
      "company_type": "L"
    },
  roles: [],
  permissions: [],
}

export const admin = {
  username: 'admin',
	first_name: 'User',
	last_name: 'Admin',
	email: 'admin@admin.com',
  cpf: '231.002.999-00',
  company: {
      "name": "phsw",
      "cnpj": "40229893000166",
      "company_code": 123,
      "status": "A",
      "company_type": "L"
    },
  roles: ['admin', 'client'],
  permissions: [
    'get_all_users',
    'create_admin_agent',
    'delete_admin_agent',
    'update_admin_agent',
    'get_all_admin_agents',
    'create_agent',
    'get_agents',
    'update_agent',
    'delete_agent',
    'create_client',
    'get_clients',
    'update_client',
    'delete_client',
    'create_item',
    'get_items',
    'update_item',
    'delete_item',
    'create_item_category',
    'get_item_category',
    'update_item_category',
    'delete_item_category',
    'create_price_table',
    'get_price_tables',
    'update_price_table',
    'delete_price_table',
    'crud_order']
}

export const users = [
	{
    username: 'joao',
		first_name: 'Joao',
		last_name: 'Silva',
		email: 'jaaosilva@phsw.com',
    cpf: '231.002.999-00',
    company: {
        "name": "phsw",
        "cnpj": "40229893000166",
        "company_code": 123,
        "status": "A",
        "company_type": "L"
      },
    roles: [],
    permissions: [],
	},
	{
    username: 'joao',
		first_name: 'Marcio',
		last_name: 'Luiz',
		email: 'marcioluiz@phsw.com',
    cpf: '231.002.999-00',
    company: {
        "name": "phsw",
        "cnpj": "40229893000166",
        "company_code": 123,
        "status": "A",
        "company_type": "L"
      },
    roles: [],
    permissions: [],
	},
	{
    username: 'joao',
		first_name: 'Luiz',
		last_name: 'Silva',
		email: 'luizsilva@phsw.com',
    cpf: '231.002.999-00',
    company: {
        "name": "phsw",
        "cnpj": "40229893000166",
        "company_code": 123,
        "status": "A",
        "company_type": "L"
      },
    roles: [],
    permissions: [],
	},
]
