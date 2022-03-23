export const messages = {
  en: {
    //--------------------------------------------------------------------/Store APIs Success Messages (dispatch success dialog)
    // user
    login_success_msg: "Logged in with success.",
    logout_success_msg: "Logged out in with success.",
    updateCurrentUserProfile_succes_msg: "Your profile has been updated.",
    updatePassword_success_msg: "Your password has been updated.",
    createClientUser_success_msg: "Client user created",
    updateClientUser_success_msg: "Client user updated",
    deleteClientUser_success_msg: "Client user deleted",
    createAgent_success_msg: "Agent created",
    updateAgent_success_msg: "Agent updated",
    deleteAgent_success_msg: "Agent deleted",
    //organizations
    createContracting_success_msg: "Contracting company created",
    updateContracting_success_msg: "The Contracting company has been updated.",
    deleteContracting_success_msg: "Contracting deleted",
    createCompany_success_msg: "Company created.",
    updateCompany_success_msg: "Company updated.",
    deleteCompany_success_msg: "Company deleted.",
    createClient_success_msg: "Client created.",
    updateClient_success_msg: "Client updated.",
    deleteClient_success_msg: "Client deleted.",
    createEstablishment_success_msg: "Establishment created.",
    updateEstablishment_success_msg: "Establishment updated.",
    deleteEstablishment_success_msg: "Establishment deleted.",
    createClientTable_success_msg: "Client table created.",
    updateClientTable_success_msg: "Client table updated.",
    deleteClientTable_success_msg: "Client table deleted.",
    //--------------------------------------------------------------------/Store APIs Error Messages (default_error_msg parameter)
    //user
    checkAuthenticated_error_msg: "Something went wrong when trying to get the user profile.",
    getCsrf_error_msg: "Something went wrong when trying to get CSRF Token.",
    login_error_msg: "Something went wrong when trying to log in the user.",
    logout_error_msg: "Something went wrong when trying to log out the user.",
    updateCurrentUserProfile_error_msg: "Something went wrong when trying to update the user's profile.",
    updatePassword_error_msg: "Something went wrong when trying to update the user's password.",
    fetchClientsToCreateClientUser_error_msg: "Something went wrong when trying to fetch clients to create a client user.",
    createClientUser_error_msg: "Something went wrong when trying to create a client user.",
    fetchClientUsers_error_msg: "Something went wrong when trying to fetch client users.",
    updateClientUser_error_msg: "Something went wrong when trying to update the client user.",
    deleteClientUser_error_msg: "Something went wrong when trying to delete the client user.",
    createAgent_error_msg: "Something went wrong when trying to create a agent.",
    fetchAgents_error_msg: "Something went wrong when trying to fetch agents.",
    updateAgent_error_msg: "Something went wrong when trying to update the agent.",
    deleteAgent_error_msg: "Something went wrong when trying to delete the agent.",
    //organizations.js
    createContracting_error_msg: "Something went wrong when trying to create a contracting company.",
    fetchContractingCompanies_error_msg: "Something went wrong when trying to fetch contracting companies.",
    updateContracting_error_msg: "Something went wrong when trying to update the contracting company.",
    deleteContracting_error_msg: "Something went wrong when trying to delete the contracting company.",
    createCompany_error_msg: "Something went wrong when trying to create a company.",
    fetchCompanies_error_msg: "Something went wrong when trying to fetch companies.",
    updateCompany_error_msg: "Something went wrong when trying to update the company.",
    deleteCompany_error_msg: "Something went wrong when trying to delete the company.",
    fetchEstablishments_error_msg: "Something went wrong when trying to fetch establishments.",
    fetchClientTables_error_msg: "Something went wrong when trying to fetch client tables.",
    fetchPriceTablesToCreateClient_error_msg: "Something went wrong when trying to fetch price tables to create a client.",
    fetchEstablishmentsToCreateClient_error_msg: "Something went wrong when trying to fetch establishments to create a client.",
    fetchCompaniesToCreateClient_error_msg: "Something went wrong when trying to fetch companies to create a client.",
    createClient_error_msg: "Something went wrong when trying to create a client.",
    fetchClients_error_msg: "Something went wrong when trying to fetch clients.",
    updateClient_error_msg: "Something went wrong when trying to update the client.",
    deleteClient_error_msg: "Something went wrong when trying to delete the client.",
    fetchCompaniesToCreateEstablishment_error_msg: "Something went wrong when trying to fetch companies to create an establishment.",
    createEstablishment_error_msg: "Something went wrong when trying to create an establishment.",
    updateEstablishment_error_msg: "Something went wrong when trying to update the establishment.",
    deleteEstablishment_error_msg: "Something went wrong when trying to update the establishment.",
    createClientTable_error_msg: "Something went wrong when trying to create a client table.",
    updateClientTable_error_msg: "Something went wrong when trying to update the client table.",
    deleteClientTable_error_msg: "Something went wrong when trying to delete the client table.",

    // -------------------------------------------------------------------/ Error Handler
    // Fields
    Client_establishments: "Client establishments",
    Vendor_code: "Vendor code",
    Cnpj: "CNPJ",
    Price_table: "Price table",
    Client_table_code: "Client table code",
    Description: "Description",
    Item_table: "Item table",
    Cnpj_root: "cnpj_root",
    Establishment_code: "Establishment_code",
    First_name: "First_name",
    Last_name: "Last_name",
    Agent_establishments: "Agent establishments",
    Agent_permissions: "Agent permissions",
    Ordered_items: "Ordered items",
    Quantity: "Quantity",
    Invoicing_date: "Invoicing date",
    Invoice_number: "Invoice number",
    Agent_note: "Agent note",
    Category_code: "Category code",
    Item_code: "Item_code",
    Unit: "Unit",
    Category: "Category",
    Barcode: "Barcode",
    Technical_description: "Technical description",
    Item_table_code: "Item table code",
    Unit_price: "Unit price",
    Price_items: "Price items",
    Table_code: "Table code",
    // Error messages
    Request_Time_out: "The request timed out.",
    Connection_error: "Connection error",
    Something_went_wrong: "Something went wrong.",
    Server_error: "Server error.",
    // -------------------------------------------------------------------/ Layouts
    // -------------------------------/ default
    // Menu Itens
    Home: 'Home',
    About: 'About',
    Organizations: 'Organizations',
    Users: 'Users',
    Items: 'Items',
    Orders: 'Orders',
    // Submenu
    My_Account: 'My Account',
    Logout: 'Logout',
    // -------------------------------/ error
    _404_Not_Found: '404 - Page Not Found',
    An_error_occurred: 'An error occurred',
    Home_Page: 'Home Page',

    // -------------------------------------------------------------------/ Pages
    // -------------------------------/index
    Order_System: 'Order System',
    Please_log_in: 'Please log in ...',
    See_you_later: 'See you later!',
    Welcome_user_first_name: 'Welcome ',
    //--------------------------------/myaccount
    First_Name: 'First Name',
    Last_Name: 'Last Name',
    Update_Account_Information: 'Update Account Information',
    Change_Password: 'Change Password',
    After_change_your_password_you_will_be_logged_out: 'After change your password you will be logged out.',
    Current_password: 'Current password',
    Password_Confirm: 'Password Confirm',
    You_have_not_changed_any_fields: 'You have not changed any fields.',
    "Must be valid e-mail" : "Must be valid e-mail",
    // cpf_validation_error: 'This field should have the format 999.999.999-99',
    Password_must_be_different_from_current_password: 'The password should not be equal to the current password.',
    password_confirm_does_not_match: 'The password confirmation fail.',
    // -------------------------------/admin/organizations
    Contracting: 'Contracting',
    Company: 'Company',
    Establishment: 'Establishment',
    Client_Table: 'Client Table',
    Client: 'Client',
    // -------------------------------/admin/organizations/contracting
    Fetching_contracting_companies: 'Fetching contracting companies ...',
    Fetching_contracting_companies_ERROR: 'Error loading contracting companies',
    // Fields
    Name: 'Name',
    Contracting_code: 'Contracting code',
    Active_users_limit: 'Active users limit',
    Active: 'Active',
    Disabled: 'Disabled',
    Note: 'Note',
    // Others
    Contracting_Company_Status: 'Contracting Company Status',
    Submit: 'Submit',
    Edit_Contracting: 'Edit Contracting',
    Create_Contracting: 'Create Contracting',
    Actions: 'Actions',
    // ValidationErrors
    This_field_must_have_at_least_X_characters: 'This field must have at least {0} characters.',
    This_field_must_have_up_to_X_characters: 'This field must have up to {0} characters.',
    This_value_must_be_greater_than_X: 'This value must be greater than {0}.',
    This_value_must_be_less_than_X: 'This value must be less than {0}.',
    It_must_containing_only_letters_numbers_underscores_or_hyphens: 'It must containing only letters, numbers, underscores or hyphens.',
    This_field_is_required: 'This field is required.',
    This_value_must_be_a_integer:'This value must be a integer.',
    Please_fill_the_form_correctly: 'Please fill the form correctly.',
    // -------------------------------/admin/organizations/company
    Company_code: 'Company code',
    Root_of_CNPJ: 'Root of CNPJ',
    None: 'None',
    Item_Table: 'Item Table',
    Company_Status: 'Company Status',
    Edit_Company: 'Edit Company',
    cnpjRootValidationError: "This field must be in the format '99.999.999'",
    Fetching_data: 'Fetching data ...',
    Error_fetching_data: 'Error fetching data.',
    Create_Company: 'Create Company',
    // Fields
    CNPJ_Root: 'CNPJ Root',
    Client_table: 'Client table',
    // -------------------------------/admin/organizations/establishment
    Create_Establishment: "Create Establishment",
    Establishment_Status: "Establishment Status",
    Edit_Establishment: "Edit Establishment",
    // -------------------------------/admin/organizations/client_table
    "Create Client Table": "Create Client Table",
    "Edit Client Table": "Edit Client Table",
    "Client Table Code": "Client Table Code",
    
    // -------------------------------/admin/organizations/client
    cnpjValidationError: "This field must be in the format '99.999.999/9999-99'",
    Create_Client: "Create Client",
    Client_code: "Client code",
    Client_Status: "Client Status",
    Edit_Client: "Edit Client",
    Vendor_Code: "Vendor Code",
    Client_Establishments: "Client Establishments",
    // ------------------------------------------------------------------------------------/admin/user
    ERP_User: 'ERP User',
    Admin_Agent: 'Admin Agent',
    Agent: 'Agent',
    Client_User: 'Client User',
    // -------------------------------/admin/user/ERP_User
    // -------------------------------/admin/user/Agent
    "Create Agent": "Create Agent",
    "Edit Agent": "Edit Agent",
    "Agent Establishments" : "Agent Establishments",
    "Agent Permissions": "Agent Permissions",
    // -------------------------------/admin/user/client_user
    "Create Client User": "Create Client User",
    "Edit Client User": "Edit Client User",
    "Complete name" : "Complete name",
    // -----------------------------------------------------------------------------------/admin/item
    Price_Table: 'Price Table',
    Item_Category: 'Item Category',
    // -------------------------------------------------------------------/ Components
    // -------------------------------/Problem Connecting Error dialog
    ProblemConnectingTitle: "Problema de conexão",
    Check_your_internet_connection: "Verifique sua conexão de internet e tente novamente.",
    // -------------------------------/Session Error dialog
    SessionErrorText: 'A aplicação já está aberta em outra janela. Clique em "Usar aqui" para usar a aplicação nessa janela.',
    Use_Here: 'Usar aqui',
    // -------------------------------/Login dialog
    Username: 'Username',
    Password: 'Password',
    SlugFieldErrorMessage: 'It must containing only letters, numbers, underscores or hyphens.',
    // -------------------------------/admin/organization/contracting_edit_menu
    Edit: 'Edit',
    Cancel: 'Cancel',
    Delete: 'Delete',
    Save: 'Save',
    Are_you_sure_you_want_to_delete: 'Are you sure you want to delete this item?',
    //-------------------------------/admin/organization/price-table-v-select
    Empty: 'Empty',
  },

//====================================================================================
  
  'pt-BR': {
    //--------------------------------------------------------------------/Store APIs Success Messages (dispatch success dialog)
    // user
    login_success_msg: "Usuário logado.",
    logout_success_msg: "Usuário deslogado.",
    updateCurrentUserProfile_succes_msg: "Seu perfil foi atualizado.",
    updatePassword_success_msg: "Sua senha foi atualizada.",
    createClientUser_success_msg: "Usuário cliente criado.",
    updateClientUser_success_msg: "Usuário cliente atualizado.",
    deleteClientUser_success_msg: "Usuário cliente excluído.",
    createAgent_success_msg: "Agente criado.",
    updateAgent_success_msg: "Agente atualizado.",
    deleteAgent_success_msg: "Agente excluído.",
    //organizations
    createContracting_success_msg: "Contratante criada.",
    updateContracting_success_msg: "Contratante atualizada.",
    deleteContracting_success_msg: "Contratante excluída.",
    createCompany_success_msg: "Empresa criada.",
    updateCompany_success_msg: "Empresa atualizada.",
    deleteCompany_success_msg: "Empresa excluída.",
    createClient_success_msg: "Cliente criado.",
    updateClient_success_msg: "Cliente atualizado.",
    deleteClient_success_msg: "Cliente excluído",
    createEstablishment_success_msg: "Estabelecimento criado.",
    updateEstablishment_success_msg: "Estabelecimento atualizado.",
    deleteEstablishment_success_msg: "Estabelecimento excluído.",
    createClientTable_success_msg: "Tabela de clientes criada.",
    updateClientTable_success_msg: "Tabela de clientes atualizada.",
    deleteClientTable_success_msg: "Tabela de clientes excluída.",
    //--------------------------------------------------------------------/Store APIs Error Messages (default_error_msg parameter)
    //user
    checkAuthenticated_error_msg: "Algo deu errado ao tentar obter o perfil do usuário.",
    getCsrf_error_msg: "Algo deu errado ao tentar obter o Token CSRF.",
    login_error_msg: "Algo deu errado ao tentar logar o usuário.",
    logout_error_msg: "Algo deu errado ao tentar desconectar o usuário.",
    updateCurrentUserProfile_error_msg: "Algo deu errado ao tentar atualizar o perfil do usuário.",
    updatePassword_error_msg: "Algo deu errado ao tentar atualizar a senha do usuário.",
    fetchClientsToCreateClientUser_error_msg: "Algo deu errado ao tentar buscar clientes para criar usuário cliente.",
    createClientUser_error_msg: "Algo deu errado ao tentar criar um usuário cliente.",
    fetchClientUsers_error_msg: "Algo deu errado ao tentar buscar usuários clientes.",
    updateClientUser_error_msg: "Algo deu errado ao tentar atualizar o usuário cliente.",
    deleteClientUser_error_msg: "Algo deu errado ao tentar excluir o usuário cliente.",
    createAgent_error_msg: "Algo deu errado ao tentar criar um agente.",
    fetchAgents_error_msg: "Algo deu errado ao tentar buscar agentes.",
    updateAgent_error_msg: "Algo deu errado ao tentar atualizar o agente.",
    deleteAgent_error_msg: "Algo deu errado ao tentar excluir o agentes.",
    //organizations.js
    createContracting_error_msg: "Algo deu errado ao tentar criar empresa contratante.",
    fetchContractingCompanies_error_msg: "Algo deu errado ao tentar buscar contratantes.",
    updateContracting_error_msg: "Algo deu errado ao tentar atualizar contratante.",
    deleteContracting_error_msg: "Algo deu errado ao tentar deletar a contratante.",
    createCompany_error_msg: "Algo deu errado ao tentar criar uma empresa.",
    fetchCompanies_error_msg: "Algo deu errado ao tentar buscar empresas.",
    updateCompany_error_msg: "Algo deu errado ao tentar atualizar a empresa.",
    deleteCompany_error_msg: "Algo deu errado ao tentar excluir a empresa.",
    fetchEstablishments_error_msg: "Algo deu errado ao tentar buscar estabelecimentos.",
    fetchClientTables_error_msg: "Algo deu errado ao tentar buscar tabelas de clientes.",
    fetchPriceTablesToCreateClient_error_msg: "Algo deu errado ao tentar buscar tabelas de preço na pagina de criação de cliente.",
    fetchEstablishmentsToCreateClient_error_msg: "Algo deu errado ao tentar buscar estabelecimentos na pagina de criação de cliente.",
    fetchCompaniesToCreateClient_error_msg: "Algo deu errado ao tentar buscar empresas na pagina de criação de cliente.",
    createClient_error_msg: "Algo deu errado ao tentar criar cliente",
    fetchClients_error_msg: "Algo deu errado ao tentar buscar clientes",
    updateClient_error_msg: "Algo deu errado ao tentar atualizar o cliente.",
    deleteClient_error_msg: "Algo deu errado ao tentar excluir o cliente.",
    fetchCompaniesToCreateEstablishment_error_msg: "Algo deu errado ao tentar buscar empresas na pagina de criação de estabelecimento.",
    createEstablishment_error_msg: "Algo deu errado ao tentar criar um estabelecimento.",
    updateEstablishment_error_msg: "Algo deu errado ao tentar atualizar o estabelecimento.",
    deleteEstablishment_error_msg:  "Algo deu errado ao tentar excluir o estabelecimento.",
    createClientTable_error_msg: "Algo deu errado ao tentar criar o estabelecimento.",
    updateClientTable_error_msg: "Algo deu errado ao tentar atualizar o estabelecimento.",
    deleteClientTable_error_msg: "Algo deu errado ao tentar excluir o estabelecimento.",

    // -------------------------------------------------------------------/ Error Handler
    // Fields
    Client_establishments: "Estabelecimentos do cliente",
    Vendor_code: "Código do vendedor",
    Cnpj: "CNPJ",
    Price_table: "Tabela de preço",
    Client_table_code: "Código da tabela de clientes",
    Description: "Descrição",
    Item_table: "Tabela de itens",
    Cnpj_root: "Raiz do CNPJ",
    Establishment_code: "Código do estabelecimento",
    First_name: "Nome",
    Last_name: "Sobrenome",
    Agent_establishments: "Estabelecimentos do agente",
    Agent_permissions: "Permissões do agente",
    Ordered_items: "Itens pedidos",
    Quantity: "Quantidade",
    Invoicing_date: "Data do faturamento",
    Invoice_number: "Número da nota",
    Agent_note: "Observação do agente",
    Category_code: "Código da categoria",
    Item_code: "Código do item",
    Unit: "Unidade",
    Category: "Categoria",
    Barcode: "Código de barras",
    Technical_description: "Descrição técnica",
    Item_table_code: "Código da tabela de itens",
    Unit_price: "Preço unitário",
    Price_items: "Itens preço",
    Table_code: "Código da tabela",
    // Error messages(from store actions(default_error_msg parameter) and handleError function)
    Request_Time_out: "A requisição excedeu o tempo limite.",
    Connection_error: "Erro de conexão",
    Something_went_wrong: "Algo deu errado.",
    Server_error: "Error no servidor.",

    // -------------------------------------------------------------------/ Layouts
    // -------------------------------/ default
    // Menu Itens
    Home: 'Home',
    About: 'Sobre nós',
    Organizations: 'Organizações',
    Users: 'Usuários',
    Items: 'Itens',
    Orders: 'Pedidos',
    // Submenu
    My_Account: 'Minha conta',
    Logout: 'Sair',
    // -------------------------------/ error
    _404_Not_Found: '404 - Página não encontrada.',
    An_error_occurred: 'Ocorreu um erro.',
    Home_Page: 'Ir para a Home',
    // -------------------------------------------------------------------/ Pages
    // -------------------------------/index
    Order_System: 'Sistema de Pedidos',
    Please_log_in: 'Por favor faça login ...',
    See_you_later: 'Até mais!',
    Welcome_user_first_name: 'Bem-vindo ',
    //--------------------------------/myaccount
    First_Name: 'Nome',
    Last_Name: 'Sobrenome',
    Update_Account_Information: 'Atualizar Perfil',
    Change_Password: 'Alterar Senha',
    After_change_your_password_you_will_be_logged_out: 'Após mudar sua senha voce será deslogado.',
    Current_password: 'Senha atual',
    Password_Confirm: 'Confirmar Senha',
    You_have_not_changed_any_fields: 'Você não alterou nenhum campo.',
    "Must be valid e-mail" : "O e-mail deve ter um formato valido.",
    // cpf_validation_error: 'Esse campo deve ter o formato 999.999.999-99',
    Password_must_be_different_from_current_password: 'A senha deve ser diferente da senha atual.',
    password_confirm_does_not_match: 'As senhas não coincidem.',
    // -------------------------------/admin/organizations
    Contracting: 'Contratante',
    Company: 'Empresa',
    Establishment: 'Estabelecimento',
    Client_Table: 'Tabela de cliente',
    Client: 'Cliente',
    // -------------------------------/admin/organizations/contracting
    Fetching_contracting_companies: 'Buscando empresas contratantes...',
    Fetching_contracting_companies_ERROR: 'Erro ao buscar empresas contratantes.',
    // Fields
    Name: 'Nome',
    Contracting_code: 'Código da contratante',
    Active_users_limit: 'Limite de usuários ativos',
    Active: 'Ativo',
    Disabled: 'Desabilitado',
    Note: 'Observação',
    // Others
    Contracting_Company_Status: 'Status da contratante',
    Submit: 'Enviar',
    Edit_Contracting: 'Editar contratante',
    Create_Contracting: 'Criar contratante',
    Actions: 'Ações',
    // ValidationErrors
    This_field_must_have_at_least_X_characters: 'Esse campo deve ter pelo menos {0} caracteres.',
    This_field_must_have_up_to_X_characters: 'Esse campo deve ter no máximo {0} caracteres.',
    This_value_must_be_greater_than_X: 'Esse valor deve ser maior que {0}.',
    This_value_must_be_less_than_X: 'Esse valor deve ser menor que {0}.',
    It_must_containing_only_letters_numbers_underscores_or_hyphens: 'Esse campo deve conter apenas letras, numeros, underscores ou hifens.',
    This_field_is_required: 'Esse campo é obrigatório.',
    This_value_must_be_a_integer:'Esse valor deve ser um número inteiro.',
    Please_fill_the_form_correctly: 'Por favor preencha o formulário corretamente.',
    // -------------------------------/admin/organizations/company
    Company_code: 'Código da empresa',
    Root_of_CNPJ: 'Raiz do CNPJ',
    None: 'Vazio',
    Item_Table: 'Tabela de itens',
    Company_Status: 'Status da Empresa',
    Edit_Company: 'Editar Empresa',
    cnpjRootValidationError: "Esse campo deve estar no formato '99.999.999'",
    Fetching_data: 'Carregando dados ...',
    Error_fetching_data: 'Erro ao carregar dados.',
    Create_Company: 'Criar Empresa',
    // Fields
    CNPJ_Root: 'Raiz CNPJ',
    Client_table: 'Tabela de clientes',
    // -------------------------------/admin/organizations/establishment
    Create_Establishment: "Criar Estabelecimento",
    Establishment_Status: "Status do Estabelecimento",
    Edit_Establishment: "Editar Estabelecimento",
    // -------------------------------/admin/organizations/client_table
    "Create Client Table": "Criar Tabela de Clientes",
    "Edit Client Table": "Editar Tabela de Clientes",
    "Client Table Code": "Código da tabela de clientes",
    
    // -------------------------------/admin/organizations/client
    cnpjValidationError: "Esse campo deve estar no formato '99.999.999/9999-99'",
    Create_Client: "Criar Cliente",
    Client_code: "Código do cliente",
    Client_Status: "Status do Cliente",
    Edit_Client: "Editar Cliente",
    Vendor_Code: "Código do Vendedor",
    Client_Establishments: "Estabelecimentos do Cliente",
    // ---------------------------------------------------------------------------------------/admin/user
    ERP_User: 'Usuário ERP',
    Admin_Agent: 'Agente Admin',
    Agent: 'Agente',
    Client_User: 'Usuário Cliente',
    // -------------------------------/admin/user/ERP_User
    // -------------------------------/admin/user/Agent
    "Create Agent": "Criar Agente",
    "Edit Agent": "Editar Agente",
    "Agent Establishments" : "Estabelecimentos do Agente",
    "Agent Permissions": "Permissões do Agente",
    // -------------------------------/admin/user/client_user
    "Create Client User": "Criar Usuário Cliente",
    "Edit Client User": "Editar Usuário Cliente",
    "Complete name" : "Nome completo",

    // ----------------------------------------------------------------------------------------/admin/item
    Price_Table: 'Tabela de Preço',
    Item_Category: 'Categoria de Itens',
    // -------------------------------------------------------------------/ Components
    // -------------------------------/Problem Connecting Error dialog
    ProblemConnectingTitle: "Problem connecting",
    Check_your_internet_connection: "Check your internet connection and try again.",
    // -------------------------------/Session Error dialog
    SessionErrorText: 'The application is open in another window. Click "Use Here" to use the application in this window.',
    Use_Here: 'Use here',
    // -------------------------------/Login dialog
    Username: 'Username',
    Password: 'Senha',
    SlugFieldErrorMessage: 'Esse campo deve conter apenas, números, underscores ou hifens.',
    // -------------------------------/admin/organization/contracting_edit_menu
    Edit: 'Editar',
    Cancel: 'Cancelar',
    Delete: 'Excluir',
    Save: 'Salvar',
    Are_you_sure_you_want_to_delete: 'Tem certeza que quer deletar esse item?',
    //-------------------------------/admin/organization/price-table-v-select
    Empty: 'Vazio',
  },
}
