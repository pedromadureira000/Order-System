import {handleError} from "~/helpers/functions";
import {ActionTree, Commit, Dispatch} from "vuex"
import {RootState} from "@/store/index"
 // @ts-ignore: This module is dynamically added in nuxt.config.js
import api from "~api"
import {UserState} from "~/store/user"

// ------------------------------------------/ACTIONS/-------------------------------------------

export const actions: ActionTree<UserState, RootState> = {

	async createContracting({dispatch}: {dispatch: Dispatch,}, payload: any){
		try {
			let data = await api.createContracting(payload)
			console.log(">>>",data)
			dispatch("setAlert", {message: "Contracting created", alertType: "success"}, { root: true })
			return data
		}
		catch(e){
			let error: string[] = Object.values(e.response.data)
			let errorMessage = error[0][0]
			dispatch("setAlert", {message: errorMessage , alertType: "error"}, { root: true })
		}
	},

	async fetchContractingCompanies({dispatch}: {dispatch: Dispatch,}){
    try{
      let users = await api.fetchContractingCompanies()
      return users
    }
		catch(e){
      dispatch("setAlert", {message: "Something went wrong when trying to fetch contracting companies.", alertType: "error"}, { root: true })
		}
	},

  async updateContracting({commit, dispatch}: {commit: Commit, dispatch: Dispatch,}, payload: any){
    try {
    let data = await api.updateContracting(payload)
    console.log(">>",data)
    dispatch("setAlert", {message: "Contracting has been updated.", alertType: "success"}, { root: true })
    return data
    }
    catch(e){
      handleError(e.response, commit)
			let error: string[] = Object.values(e.response.data)
			let errorMessage = error[0][0]
			dispatch("setAlert", {message: errorMessage , alertType: "error"}, { root: true })
      // dispatch("setAlert", {message: "Something went wrong when trying to update price table.", alertType: "error"}, { root: true })
    }
  },

	async deleteContracting({dispatch}: {dispatch: Dispatch,}, payload: any){
		try {
			let data = await api.deleteContracting(payload)
			console.log(">>>",data)
			dispatch("setAlert", {message: "Contracting deleted", alertType: "success"}, { root: true })
			return "ok"
		}
		catch(e){
			// dispatch("setAlert", {message: "Something went wrong when trying to delete user.", alertType: "error"}, { root: true })
			let error: string[] = Object.values(e.response.data)
			let errorMessage = error[0]
			dispatch("setAlert", {message: errorMessage, alertType: "error"}, { root: true })
		}
	},

  //----------------/ Company APIs
 
	async createCompany({dispatch}: {dispatch: Dispatch,}, payload: any){
		try {
			let data = await api.createCompany(payload)
			console.log(">>>",data)
			dispatch("setAlert", {message: "Company created", alertType: "success"}, { root: true })
			return data
		}
		catch(e){
			let error: string[] = Object.values(e.response.data)
			let errorMessage = error[0][0]
			dispatch("setAlert", {message: errorMessage , alertType: "error"}, { root: true })
		}
	},

	async fetchCompanies({dispatch}: {dispatch: Dispatch,}){
    try {
      let companies = await api.fetchCompanies()
      return companies

    }
		catch(e){
      dispatch("setAlert", {message: "Something went wrong when trying to fetch companies.", alertType: "error"}, { root: true })
		}
	},

  async updateCompany({commit, dispatch}: {commit: Commit, dispatch: Dispatch,}, payload: any){
    try {
    let data = await api.updateCompany(payload)
    console.log(">>",data)
    dispatch("setAlert", {message: "Price table has been updated.", alertType: "success"}, { root: true })
    return data
    }
    catch(e){
      handleError(e.response, commit)
			let error: string[] = Object.values(e.response.data)
			let errorMessage = error[0][0]
			dispatch("setAlert", {message: errorMessage , alertType: "error"}, { root: true })
      // dispatch("setAlert", {message: "Something went wrong when trying to update price table.", alertType: "error"}, { root: true })
    }
  },

	async deleteCompany({dispatch}: {dispatch: Dispatch,}, payload: any){
		try {
			let data = await api.deleteCompany(payload)
			console.log(">>>",data)
			dispatch("setAlert", {message: "Company deleted", alertType: "success"}, { root: true })
			return "ok"
		}
		catch(e){
			// dispatch("setAlert", {message: "Something went wrong when trying to delete user.", alertType: "error"}, { root: true })
			let error: string[] = Object.values(e.response.data)
			let errorMessage = error[0]
			dispatch("setAlert", {message: errorMessage, alertType: "error"}, { root: true })
		}
	},

  //----------------/ Establishment APIs

	async fetchEstablishments({dispatch}: {dispatch: Dispatch,}){
    try {
      let establishments = await api.fetchEstablishments()
      return establishments
    }
		catch(e){
      dispatch("setAlert", {message: "Something went wrong when trying to fetch establishments.", alertType: "error"}, { root: true })
		}
	},

  //----------------/ Client Table APIs
  
	async fetchClientTables(){
		let client_tables = await api.fetchClientTables()
		return client_tables
	},

  //----------------/ Client APIs
  
	async fetchPriceTablesToCreateClient({dispatch}: {dispatch: Dispatch,}, company_compound_id: string){
    try {
      let price_tables = await api.fetchPriceTablesToCreateClient(company_compound_id)
      return price_tables
    }
		catch(e){
      dispatch("setAlert", {message: "Something went wrong when trying to fetch price tables.", alertType: "error"}, { root: true })
		}
	},

	async fetchEstablishmentsToCreateClient({dispatch}: {dispatch: Dispatch,}, client_table_compound_id: string){
    try {
      let establishments = await api.fetchEstablishmentsToCreateClient(client_table_compound_id)
      return establishments
    }
		catch(e){
      dispatch("setAlert", {message: "Something went wrong when trying to fetch establishments.", alertType: "error"}, { root: true })
		}
	},

	async fetchCompaniesToCreateClient({dispatch}: {dispatch: Dispatch,}){
    try {
      let companies = await api.fetchCompaniesToCreateClient()
      return companies
    }
		catch(e){
      dispatch("setAlert", {message: "Something went wrong when trying to fetch companies.", alertType: "error"}, { root: true })
		}
	},

	async createClient({dispatch}: {dispatch: Dispatch,}, payload: any){
		try {
			let data = await api.createClient(payload)
			console.log(">>>",data)
			dispatch("setAlert", {message: "Client created", alertType: "success"}, { root: true })
			return data
		}
		catch(e){
			let error: string[] = Object.values(e.response.data)
			let errorMessage = error[0][0]
			dispatch("setAlert", {message: errorMessage , alertType: "error"}, { root: true })
		}
	},

	async fetchClients({dispatch}: {dispatch: Dispatch,}){
    try {
      let clients = await api.fetchClients()
      return clients
    }
		catch(e){
      dispatch("setAlert", {message: "Something went wrong when trying to fetch clients.", alertType: "error"}, { root: true })
		}
	},
 
  async updateClient({commit, dispatch}: {commit: Commit, dispatch: Dispatch,}, payload: any){
    try {
    let data = await api.updateClient(payload)
    console.log(">>",data)
    dispatch("setAlert", {message: "Client has been updated.", alertType: "success"}, { root: true })
    return data
    }
    catch(e){
      handleError(e.response, commit)
			let error: string[] = Object.values(e.response.data)
			let errorMessage = error[0][0]
			dispatch("setAlert", {message: errorMessage , alertType: "error"}, { root: true })
      // dispatch("setAlert", {message: "Something went wrong when trying to update price table.", alertType: "error"}, { root: true })
    }
  },

	async deleteClient({dispatch}: {dispatch: Dispatch,}, payload: any){
		try {
			let data = await api.deleteClient(payload)
			dispatch("setAlert", {message: "Client deleted", alertType: "success"}, { root: true })
			return "ok"
		}
		catch(e){
			// dispatch("setAlert", {message: "Something went wrong when trying to delete client.", alertType: "error"}, { root: true })
			let error: string[] = Object.values(e.response.data)
			let errorMessage = error[0]
			dispatch("setAlert", {message: errorMessage, alertType: "error"}, { root: true })
		}
	},

}
