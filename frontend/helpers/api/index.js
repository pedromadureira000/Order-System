import axios from '~/plugins/axios'

export default {

  // --------------------------------------/ CRUD Organization APIs /----------------------------------------
  
	async createContracting(payload){
    let data_body = {
      name: payload.name,
      contracting_code: payload.contracting_code,
      active_users_limit: payload.active_users_limit,
      status: payload.status,
      note: payload.note,
		}
		return await axios({ 
		method: "post",
		url: "/api/organization/contracting",
		data: data_body}).then((request) => {
					return request.data 
				})
	},

	async fetchContractingCompanies(){
		return await axios({ 
		method: "get",
		url: "/api/organization/contracting",
			}).then((request) => {
					return request.data 
				})
	},

	async updateContracting(payload){
		return await axios({ 
		method: "put",
		url: `/api/organization/contracting/${payload.contracting_code}`,
		data:{
      name: payload.name,
      active_users_limit: payload.active_users_limit,
      status: payload.status,
      note: payload.note,
		}
			}).then((request) => {
					return request.data 
				})
	},
  
	async deleteContracting(payload){
		return await axios({ 
		method: "delete",
		url: `/api/organization/contracting/${payload.contracting_code}`,
			}).then((request) => {
					return request.data 
				})
	},

  // -----------------------------/ Company
  
	async createCompany(payload){
    let data_body = {
      name: payload.name,
      company_code: payload.company_code,
      cnpj_root: payload.cnpj_root,
      client_table: payload.client_table,
      item_table: payload.item_table,
      status: payload.status,
      note: payload.note,
		}
		return await axios({ 
		method: "post",
		url: "/api/organization/company",
		data: data_body}).then((request) => {
					return request.data 
				})
	},

	async fetchCompanies(){
		return await axios({ 
		method: "get",
		url: "/api/organization/company",
			}).then((request) => {
					return request.data 
				})
	},

	async updateCompany(payload){
		return await axios({ 
		method: "put",
    url: `/api/organization/company/${payload.company_compound_id}`,
		data:{
      name: payload.name,
      cnpj_root: payload.cnpj_root,
      client_table: payload.client_table,
      item_table: payload.item_table,
      status: payload.status,
      note: payload.note,
		}
			}).then((request) => {
					return request.data 
				})
	},
  
	async deleteCompany(payload){
		return await axios({ 
		method: "delete",
		url: `/api/organization/company/${payload.company_compound_id}`,
			}).then((request) => {
					return request.data 
				})
	}, 

// ------------------------/ Client Table

	async createClientTable(payload){
    let data_body = {
      description: payload.description,
      client_table_code: payload.client_table_code,
      note: payload.note,
		}
		return await axios({ 
		method: "post",
		url: "/api/organization/client_table",
		data: data_body}).then((request) => {
					return request.data 
				})
	},

	async fetchClientTables(){
		return await axios({ 
		method: "get",
		url: "/api/organization/client_table",
			}).then((request) => {
					return request.data 
				})
	},

	async updateClientTable(payload){
		return await axios({ 
		method: "put",
    url: `/api/organization/client_table/${payload.client_table_compound_id}`,
		data:{
      client_table_compound_id: payload.client_table_compound_id,
      description: payload.description,
      note: payload.note,
		}
			}).then((request) => {
					return request.data 
				})
	},
  
	async deleteClientTable(payload){
		return await axios({ 
		method: "delete",
		url: `/api/organization/client_table/${payload.client_table_compound_id}`,
			}).then((request) => {
					return request.data 
				})
	}, 

  //------------------------- Client API
  
	async fetchPriceTablesToCreateClient(company_compound_id){
		return await axios({ 
		method: "get",
		url: `/api/organization/price_tables_to_create_client/${company_compound_id}`,
			}).then((request) => {
					return request.data 
				})
	},

	async fetchCompaniesToCreateClient(){
		return await axios({ 
		method: "get",
		url: "/api/organization/companies_to_create_client",
			}).then((request) => {
					return request.data 
				})
	},

	async fetchEstablishmentsToCreateClient(client_table_compound_id){
		return await axios({ 
		method: "get",
		url: `/api/organization/establishments_to_create_client/${client_table_compound_id}`,
			}).then((request) => {
					return request.data 
				})
	},
  
	async createClient(payload){
    let data_body = {
      client_table: payload.client_table,
      client_establishments: payload.client_establishments,
      client_code: payload.client_code,
      vendor_code: payload.vendor_code,
      name: payload.name,
      status: payload.status,
      cnpj: payload.cnpj,
      note: payload.note,
		}
		return await axios({ 
		method: "post",
		url: "/api/organization/client",
		data: data_body}).then((request) => {
					return request.data 
				})
	},

  	async fetchClients(){
		return await axios({ 
		method: "get",
		url: "/api/organization/client",
			}).then((request) => {
					return request.data 
				})
	},

	async updateClient(payload){
		return await axios({ 
		method: "put",
    url: `/api/organization/client/${payload.client_compound_id}`,
		data:{
      name: payload.name,
      cnpj: payload.cnpj,
      status: payload.status,
      client_establishments: payload.client_establishments,
      vendor_code: payload.vendor_code,
      note: payload.note,
		}
			}).then((request) => {
					return request.data 
				})
	},

	async deleteClient(payload){
		return await axios({ 
		method: "delete",
		url: `/api/organization/client/${payload.client_compound_id}`,
			}).then((request) => {
					return request.data 
				})
	}, 

  //------------- Establishment
  //
	async fetchCompaniesToCreateEstablishment(){
		return await axios({ 
		method: "get",
		url: "/api/organization/companies_to_create_establishment",
			}).then((request) => {
					return request.data 
				})
	},

	async createEstablishment(payload){
    let data_body = {
      name: payload.name,
      establishment_code: payload.establishment_code,
      company: payload.company,
      cnpj: payload.cnpj,
      status: payload.status,
      note: payload.note
		}
		return await axios({ 
		method: "post",
		url: "/api/organization/establishment",
		data: data_body}).then((request) => {
					return request.data 
				})
	},

  
  async fetchEstablishments(){
		return await axios({ 
		method: "get",
		url: "/api/organization/establishment",
			}).then((request) => {
					return request.data 
				})
	},

	async updateEstablishment(payload){
		return await axios({ 
		method: "put",
    url: `/api/organization/establishment/${payload.establishment_compound_id}`,
		data:{
      name: payload.name,
      cnpj: payload.cnpj,
      status: payload.status,
      note: payload.note
		}
			}).then((request) => {
					return request.data 
				})
	},

	async deleteEstablishment(payload){
		return await axios({ 
		method: "delete",
		url: `/api/organization/establishment/${payload.establishment_compound_id}`,
			}).then((request) => {
					return request.data 
				})
	}, 


  // --------------------------------------/ Auth APIs /----------------------------------------
	async checkAuthenticated(){
    return await axios.get("/api/user/own_profile").then((data)=> {return data.data})
	},

	async getCsrf(){
		return await axios.get("/api/user/getcsrf").then(() => {})
	},

	async login(payload){ 
		return await axios({
			method: "post",
			url: "/api/user/login",
			data: { username: payload.username, contracting_code: payload.contracting_code, password: payload.password },
			headers: { "X-CSRFToken": payload.csrftoken },
		})
			.then((response) => {
				return response.data
			})
		},	

	async logout(){
		return await axios({
				method: "post",
				url: "/api/user/logout",
			})
				.then(() => {})
		},

	async updateCurrentUserProfile(payload){
		return await axios({ 
		method: "put",
		url: "/api/user/own_profile",
		data:{
			first_name: payload.first_name,
			last_name: payload.last_name,
			email: payload.email,
			// cpf: payload.cpf,
		}
			}).then((request) => {
					return request.data 
				})
	},

	async updatePassword(payload){
		return await axios({ 
		method: "put",
		url: "/api/user/update_user_password",
		data:{
			current_password: payload.current_password,
			password: payload.password,
		}
			}).then((request) => {
					return request.data 
				})
	},



  // --------------------------------------/ CRUD User APIs /----------------------------------------
  // ---- Agent
  
	async fetchEstablishmentsToCreateAgent(){
		return await axios({ 
		method: "get",
		url: "/api/user/establishments_to_create_agent",
			}).then((request) => {
					return request.data 
				})
	},

	async createAgent(payload){
    let data_body = {
      agent_permissions: payload.permissions,
      agent_establishments: payload.agent_establishments,
      username: payload.username,
      client: payload.client,
			first_name: payload.first_name,
			last_name: payload.last_name,
			email: payload.email,
			note: payload.note,
			password: payload.password,
		}
		return await axios({ 
		method: "post",
		url: "/api/user/agent",
		data: data_body}).then((request) => {
					return request.data 
				})
	},

	async fetchAgents(){
		return await axios({ 
		method: "get",
		url: "/api/user/agent",
			}).then((request) => {
					return request.data 
				})
	},

	async updateAgent(payload){
    let data_body = {
      agent_permissions: payload.permissions,
      agent_establishments: payload.agent_establishments,
			first_name: payload.first_name,
			last_name: payload.last_name,
			email: payload.email,
			note: payload.note,
      status: payload.status,  
			// password: payload.password,
		}
		return await axios({ 
		method: "put",
		url: `/api/user/agent/${payload.contracting_code}/${payload.username}`,
		data: data_body}).then((request) => {
					return request.data 
				})
	},
	async deleteAgent(payload){
		return await axios({ 
		method: "delete",
		url: `/api/user/agent/${payload.contracting_code}/${payload.username}`,
			}).then((request) => {
					return request.data 
				})
	},

  // ------- Client User
  
	async fetchClientsToCreateClientUser(){
		return await axios({ 
		method: "get",
		url: "/api/user/clients_to_create_client_user",
			}).then((request) => {
					return request.data 
				})
	},

	async createClientUser(payload){
    let data_body = {
      username: payload.username,
      client: payload.client,
			first_name: payload.first_name,
			last_name: payload.last_name,
			email: payload.email,
			note: payload.note,
			// status: payload.status,  
			password: payload.password,
		}
		return await axios({ 
		method: "post",
		url: "/api/user/client_user",
		data: data_body}).then((request) => {
					return request.data 
				})
	},

	async fetchClientUsers(){
		return await axios({ 
		method: "get",
		url: "/api/user/client_user",
			}).then((request) => {
					return request.data 
				})
	},

	async updateClientUser(payload){
    let data_body = {
			first_name: payload.first_name,
			last_name: payload.last_name,
			email: payload.email,
			note: payload.note,
      status: payload.status,  
			// password: payload.password,
		}
		return await axios({ 
		method: "put",
		url: `/api/user/client_user/${payload.contracting_code}/${payload.username}`,
		data: data_body}).then((request) => {
					return request.data 
				})
	},
	async deleteClientUser(payload){
		return await axios({ 
		method: "delete",
		url: `/api/user/client_user/${payload.contracting_code}/${payload.username}`,
			}).then((request) => {
					return request.data 
				})
	},

  //------------------------------------------------------/ CRUD Item APIs /---------------------------------------------------
  
	async fetchItemTables(){
		return await axios({ 
		method: "get",
		url: "/api/item/item_table",
			}).then((request) => {
					return request.data 
				})
	},
  
	async createItem(payload){
    let data_body = {
      name: payload.name, 
      item_code: payload.item_code,
      description: payload.description,
      category: payload.category, 
      unit: payload.unit, 
      barcode: payload.barcode, 
      active: payload.active
		}
    //TODO Image
		return await axios({ 
		method: "post",
		url: "/api/item/item",
		data: data_body}).then((request) => {
					return request.data 
				})
	},

	async fetchItems(){
		return await axios({ 
		method: "get",
		url: "/api/item/item",
			}).then((request) => {
					return request.data 
				})
	},

	async createCategory(payload){
    let data_body = {
        name: payload.name, 
        category_code: payload.category_code,
        description: payload.description,
		}
		return await axios({ 
		method: "post",
		url: "/api/item/category",
		data: data_body}).then((request) => {
					return request.data 
				})
	},

	async fetchCategories(){
		return await axios({ 
		method: "get",
		url: "/api/item/category",
			}).then((request) => {
					return request.data 
				})
	},

	async createPriceTable(payload){
    let data_body = {
        name: payload.name, 
        table_code: payload.table_code,
        description: payload.description,
        price_items: payload.price_items
		}
		return await axios({ 
		method: "post",
		url: "/api/item/pricetable",
		data: data_body}).then((request) => {
					return request.data 
				})
	},

	async updatePriceTable(payload){
		return await axios({ 
		method: "put",
		url: `/api/item/pricetable/${payload.table_code}`,
		data:{
      name: payload.name, 
      table_code: payload.table_code,
      description: payload.description,
      price_items: payload.price_items
		}
			}).then((request) => {
					return request.data 
				})
	},

	async fetchPriceTables(){
		return await axios({ 
		method: "get",
		url: "/api/item/pricetable",
			}).then((request) => {
					return request.data 
				})
	},

	async deletePriceTable(payload){
		return await axios({ 
		method: "delete",
		url: `/api/item/pricetable/${payload.table_code}`
			}).then((request) => {
					return request.data 
				})
	},
}

  //------------------------------------------------------/ Order APIs /---------------------------------------------------
