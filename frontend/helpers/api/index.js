import axios from '~/plugins/axios'

export default {
	async checkAuthenticated(){
		return await axios.get("/api/user/checkauth").then((data)=> {return data.data})
	},

	async getCsrf(){
		return await axios.get("/api/user/getcsrf").then(() => {})
	},

	async login(payload){ 
		return await axios({
			method: "post",
			url: "/api/user/login",
			data: { username: payload.username, company_code: payload.company_code, password: payload.password },
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

	async createUser(payload){
    let data_body = {
      username: payload.username,
      company_code: payload.company_code,
			first_name: payload.first_name,
			last_name: payload.last_name,
			email: payload.email,
			cpf: payload.cpf,
			password: payload.password,
      role: payload.role,
      agent_permissions: []
		}
    if (payload.role === "agent"){
      let permissions = []
      for (const permission in payload.agentPermissions){
        if (payload.agentPermissions[permission] === true){
          permissions.push(permission)
        }
      }
      console.log(">>>>", permissions)
      data_body["agent_permissions"] =  permissions
    }
		return await axios({ 
		method: "post",
		url: "/api/user/user",
		data: data_body}).then((request) => {
					return request.data 
				})
	},

	async fetchUsersByAdmin(){
		return await axios({ 
		method: "get",
		url: "/api/user/user",
			}).then((request) => {
					return request.data 
				})
	},

	async deleteUserByAdmin(payload){
		return await axios({ 
		method: "delete",
		// url: `/api/user/${payload.username}&${payload.company_code}`,
		url: `/api/user/user/${payload.username}/${payload.company_code}`,
			}).then((request) => {
					return request.data 
				})
	},

	async updateCurrentUserProfile(payload){
		return await axios({ 
		method: "put",
		url: "/api/user/user",
		data:{
			first_name: payload.first_name,
			last_name: payload.last_name,
			email: payload.email,
			cpf: payload.cpf,
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

	// async passwordReset(email){
      // return await axios({
        // method: "post",
        // url: "/api/user/passwordreset/users/reset_password/",
        // data: { email: email},
      // })
        // .then(() => {})
	// },

	// async passwordResetConfirm(payload){
      // return await axios({
        // method: "post",
        // url: "/api/user/passwordreset/users/reset_password_confirm/",
        // data: { new_password: payload.new_password, token: payload.token, uid: payload.uid},
      // })
        // .then(() => {})
				// .catch((error) => {return {error: 'error', message: Object.values(error.response.data)[0][0]}})
	// },


	async createCompany(payload){
    let data_body = {
      name: payload.name,
      cnpj: payload.cnpj,
      company_code: payload.company_code,
      status: payload.status,
      company_type: payload.company_type,
      client_code: payload.client_code,
      vendor_code: payload.vendor_code,
      note: payload.note,
		}
		return await axios({ 
		method: "post",
		url: "/api/user/company",
		data: data_body}).then((request) => {
					return request.data 
				})
	},

	async updateCompany(payload){
		return await axios({ 
		method: "put",
		url: `/api/user/company/${payload.company_code}`,
		data:{
      // name: payload.name,
      // cnpj: payload.cnpj,
      company_code: payload.company_code,
      // status: payload.status,
      // company_type: payload.company_type
      price_table: payload.price_table
		}
			}).then((request) => {
					return request.data 
				})
	},
  
	async fetchCompanies(){
		return await axios({ 
		method: "get",
		url: "/api/user/company",
			}).then((request) => {
					return request.data 
				})
	},

	async deleteComapany(payload){
		return await axios({ 
		method: "delete",
		url: `/api/user/company/${payload.company_code}`,
			}).then((request) => {
					return request.data 
				})
	},

  //------------------------------------------------------/ Orders /---------------------------------------------------
  
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
		url: "/api/orders/item",
		data: data_body}).then((request) => {
					return request.data 
				})
	},

	async fetchItems(){
		return await axios({ 
		method: "get",
		url: "/api/orders/item",
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
		url: "/api/orders/category",
		data: data_body}).then((request) => {
					return request.data 
				})
	},

	async fetchCategories(){
		return await axios({ 
		method: "get",
		url: "/api/orders/category",
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
		url: "/api/orders/pricetable",
		data: data_body}).then((request) => {
					return request.data 
				})
	},


	async updatePriceTable(payload){
		return await axios({ 
		method: "put",
		url: `/api/orders/pricetable/${payload.table_code}`,
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
		url: "/api/orders/pricetable",
			}).then((request) => {
					return request.data 
				})
	},

	async deletePriceTable(payload){
		return await axios({ 
		method: "delete",
		url: `/api/orders/pricetable/${payload.table_code}`
			}).then((request) => {
					return request.data 
				})
	},
}
