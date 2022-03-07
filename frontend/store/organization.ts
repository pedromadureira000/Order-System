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

	async fetchClientTables(){
		let client_tables = await api.fetchClientTables()
		return client_tables
	},
}
