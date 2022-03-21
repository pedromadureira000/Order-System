import {handleError} from "~/helpers/functions";
import {ActionTree, Commit, Dispatch} from "vuex"
import {RootState} from "@/store/index"
 // @ts-ignore: This module is dynamically added in nuxt.config.js
import api from "~api"
import {UserState} from "~/store/user"

// ------------------------------------------/ACTIONS/-------------------------------------------

export const actions: ActionTree<UserState, RootState> = {

	async createContracting({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
		try {
			let data = await api.createContracting(payload)
			dispatch("setAlert", {message: this.app.i18n.t('createContracting_success_msg'), alertType: "success"}, { root: true })
			return data
		}
		catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t("createContracting_error_msg"))
		}
	},

	async fetchContractingCompanies({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try{
      let users = await api.fetchContractingCompanies()
      return users
    }
		catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchContractingCompanies_error_msg"))
		}
	},

  async updateContracting({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
    let data = await api.updateContracting(payload)
    dispatch("setAlert", {message: this.app.i18n.t('updateContracting_success_msg') , alertType: "success"}, { root: true })
    return data
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t('updateContracting_error_msg'))
		}
  },

	async deleteContracting({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
		try {
			let data = await api.deleteContracting(payload)
			dispatch("setAlert", {message: this.app.i18n.t('deleteContracting_success_msg'), alertType: "success"}, { root: true })
			return "ok"
		}
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t('deleteContracting_error_msg'))
		}
	},

  //----------------/ Company APIs
 
	async createCompany({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
		try {
			let data = await api.createCompany(payload)
			dispatch("setAlert", {message: this.app.i18n.t('createCompany_success_msg'), alertType: "success"}, { root: true })
			return data
		}
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t('createCompany_error_msg'))
		}
	},

	async fetchCompanies({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try {
      let companies = await api.fetchCompanies()
      return companies
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t('fetchCompanies_error_msg'))
		}
	},

  async updateCompany({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.updateCompany(payload)
			dispatch("setAlert", {message: this.app.i18n.t('updateCompany_success_msg'), alertType: "success"}, { root: true })
      return data
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t('updateCompany_error_msg'))
		}
  },

	async deleteCompany({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
		try {
			await api.deleteCompany(payload)
			dispatch("setAlert", {message: this.app.i18n.t('deleteCompany_success_msg'), alertType: "success"}, { root: true })
			return "ok"
		}
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t('deleteCompany_error_msg'))
		}
	},

  //----------------/ Establishment APIs

	async fetchEstablishments({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try {
      let establishments = await api.fetchEstablishments()
      return establishments
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t('fetchEstablishments_error_msg'))
		}
	},

  //----------------/ Client Table APIs
  
	async fetchClientTables({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try{
      let client_tables = await api.fetchClientTables()
      return client_tables
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t('fetchClientTables_error_msg'))
		}
	},

  //----------------/ Client APIs
  
	async fetchPriceTablesToCreateClient({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, company_compound_id: string){
    try {
      let price_tables = await api.fetchPriceTablesToCreateClient(company_compound_id)
      return price_tables
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t('fetchPriceTablesToCreateClient_error_msg'))
		}
	},

	async fetchEstablishmentsToCreateClient({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, client_table_compound_id: string){
    try {
      let establishments = await api.fetchEstablishmentsToCreateClient(client_table_compound_id)
      return establishments
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t('fetchEstablishmentsToCreateClient_error_msg'))
		}
	},

	async fetchCompaniesToCreateClient({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try {
      let companies = await api.fetchCompaniesToCreateClient()
      return companies
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t('fetchCompaniesToCreateClient_error_msg'))
		}
	},

	async createClient({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
		try {
			let data = await api.createClient(payload)
			dispatch("setAlert", {message: this.app.i18n.t('createClient_success_msg'), alertType: "success"}, { root: true })
			return data
		}
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t('createClient_error_msg'))
		}
	},

	async fetchClients({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try {
      let clients = await api.fetchClients()
      return clients
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t('fetchClients_error_msg'))
		}
	},
 
  async updateClient({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.updateClient(payload)
      dispatch("setAlert", {message: this.app.i18n.t('updateClient_success_msg'), alertType: "success"}, { root: true })
      return data
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t('updateClient_error_msg'))
		}
  },

	async deleteClient({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
		try {
			await api.deleteClient(payload)
      dispatch("setAlert", {message: this.app.i18n.t('deleteClient_success_msg'), alertType: "success"}, { root: true })
			return "ok"
		}
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t('deleteClient_error_msg'))
		}
	},

}
