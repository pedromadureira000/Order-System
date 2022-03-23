class User {
	username!: string;
	first_name!: string;
	last_name!: string;
	email!: string;
  // cpf!: string;
  company!: string;
	roles!: string[];
	permissions!: string[];
  contracting_code!: string
}

export interface UserState {
	currentUser: User | null,
	csrftoken: string,
	sessionError: boolean
}

export const state = (): UserState => ({
	currentUser: null,
	csrftoken: "",
	sessionError: false
})  

// ------------------------------------------/ACTIONS/-------------------------------------------

import {ActionTree, Commit, Dispatch} from "vuex"
import {RootState} from "@/store/index"
 // @ts-ignore: This module is dynamically added in nuxt.config.js
import api from "~api"

export const actions: ActionTree<UserState, RootState> = {

// -----------------------------------------/ Auth API
	
	async checkAuthenticated({commit, dispatch}: {commit: Commit, dispatch: Dispatch}) {
		try {
			let data: any = await api.checkAuthenticated()
			commit("SET_USER", data);
		} catch (error) {
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("checkAuthenticated_error_msg"))
		}	
	},

	getCsrf({commit, dispatch}: {commit: Commit, dispatch: Dispatch}) {
		try {
			api.getCsrf() 
			commit("setCsrf");
		} catch (error) {
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("getCsrf_error_msg"))
		}
	},

	async login({commit, dispatch, state}: {commit: Commit, dispatch: Dispatch, state: UserState}, payload: any){
		payload["csrftoken"] = state.csrftoken
		try {
			let data = await api.login(payload)
			commit("SET_USER", data);
			commit("setCsrf");
			dispatch("setAlert", {message: this.app.i18n.t('login_success_msg'), alertType: "success"}, { root: true })
		} catch(error){
        ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("login_error_msg"))
		}
	},
	
	async logout({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
		try {
		let data = await api.logout()
		commit("deleteUser");
		dispatch("setAlert", {message: this.app.i18n.t('logout_success_msg'), alertType: "success"}, { root: true })
		this.$router.push("/")
		} catch (error) {
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("logout_error_msg"))
		}
	},

	async updateCurrentUserProfile({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
		try {
      let data = await api.updateCurrentUserProfile(payload)
      commit("SET_USER", data )
      dispatch("setAlert", {message: this.app.i18n.t('updateCurrentUserProfile_succes_msg'), alertType: "success"}, { root: true })
		}
		catch(error){
        ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("updateCurrentUserProfile_error_msg"))
		}
	},

	async updatePassword({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
		try {
			await api.updatePassword(payload)
			commit("deleteUser")
			dispatch("setAlert", {message: this.app.i18n.t('updatePassword_success_msg'), alertType: "success"}, { root: true })
			setTimeout(() => {
				this.$router.push("/")
			}, 600);
		}
		catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("updatePassword_error_msg"))
		}
	},

	// ----------------------------------------/ User API
  // ------------/ERP user
  	async fetchContractingCompaniesToCreateERPuser({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try{
      let users = await api.fetchContractingCompaniesToCreateERPuser()
      return users
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchContractingCompaniesToCreateERPuser_msg_error"))
    }
	},

	async createERPuser({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
		try {
			let data = await api.createERPuser(payload)
			dispatch("setAlert", {message: this.app.i18n.t('createERPuser_success_msg') , alertType: "success"}, { root: true })
			return data
		}
		catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('createERPuser_error_msg'))
		}
	},

	async fetchERPusers({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try{
      let users = await api.fetchERPusers()
      return users
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchERPusers_error_msg"))
    }
	},

  async updateERPuser({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.updateERPuser(payload)
      dispatch("setAlert", {message: this.app.i18n.t('updateERPuser_success_msg'), alertType: "success"}, { root: true })
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('updateERPuser_error_msg'))
    }
  },

	async deleteERPuser({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
		try {
			await api.deleteERPuser(payload)
			dispatch("setAlert", {message: this.app.i18n.t('deleteERPuser_success_msg'), alertType: "success"}, { root: true })
			return "ok"
		}
		catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("deleteERPuser_error_msg"))
		}
	},

 //------------Admin Agent

	async createAdminAgent({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
		try {
			let data = await api.createAdminAgent(payload)
			dispatch("setAlert", {message: this.app.i18n.t('createAdminAgent_success_msg') , alertType: "success"}, { root: true })
			return data
		}
		catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('createAdminAgent_error_msg'))
		}
	},

	async fetchAdminAgents({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try{
      let users = await api.fetchAdminAgents()
      return users
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchAdminAgents_error_msg"))
    }
	},

  async updateAdminAgent({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.updateAdminAgent(payload)
      dispatch("setAlert", {message: this.app.i18n.t('updateAdminAgent_success_msg'), alertType: "success"}, { root: true })
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('updateAdminAgent_error_msg'))
    }
  },

	async deleteAdminAgent({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
		try {
			await api.deleteAdminAgent(payload)
			dispatch("setAlert", {message: this.app.i18n.t('deleteAdminAgent_success_msg'), alertType: "success"}, { root: true })
			return "ok"
		}
		catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("deleteAdminAgent_error_msg"))
		}
	},

 // ----------- Agent
  
  	async fetchEstablishmentsToCreateAgent({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try{
      let users = await api.fetchEstablishmentsToCreateAgent()
      return users
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchEstablishmentsToCreateAgent_error_msg"))
    }
	},
  
	async createAgent({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
		try {
			let data = await api.createAgent(payload)
			dispatch("setAlert", {message: this.app.i18n.t('createAgent_success_msg') , alertType: "success"}, { root: true })
			return data
		}
		catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('createAgent_error_msg'))
		}
	},

	async fetchAgents({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try{
      let users = await api.fetchAgents()
      return users
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchAgents_error_msg"))
    }
	},

  async updateAgent({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.updateAgent(payload)
      dispatch("setAlert", {message: this.app.i18n.t('updateAgent_success_msg'), alertType: "success"}, { root: true })
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('updateAgent_error_msg'))
    }
  },

	async deleteAgent({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
		try {
			await api.deleteAgent(payload)
			dispatch("setAlert", {message: this.app.i18n.t('deleteAgent_success_msg'), alertType: "success"}, { root: true })
			return "ok"
		}
		catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("deleteAgent_error_msg"))
		}
	},

 //------Client User 

	async fetchClientsToCreateClientUser({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try{
      let users = await api.fetchClientsToCreateClientUser()
      return users
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchClientsToCreateClientUser_error_msg"))
    }
	},
  
	async createClientUser({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
		try {
			let data = await api.createClientUser(payload)
			dispatch("setAlert", {message: this.app.i18n.t('createClientUser_success_msg') , alertType: "success"}, { root: true })
			return data
		}
		catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('createClientUser_error_msg'))
		}
	},

	async fetchClientUsers({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try{
      let users = await api.fetchClientUsers()
      return users
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchClientUsers_error_msg"))
    }
	},

  async updateClientUser({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.updateClientUser(payload)
      dispatch("setAlert", {message: this.app.i18n.t('updateClientUser_success_msg'), alertType: "success"}, { root: true })
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('updateClientUser_error_msg'))
    }
  },

	async deleteClientUser({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
		try {
			await api.deleteClientUser(payload)
			dispatch("setAlert", {message: this.app.i18n.t('deleteClientUser_success_msg'), alertType: "success"}, { root: true })
			return "ok"
		}
		catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("deleteClientUser_error_msg"))
		}
	},

}

// --------------------------------------------/MUTATIONS/---------------------------------------------

import {MutationTree} from "vuex"
import {ErrorHandler} from "~/helpers/functions";

export const mutations: MutationTree<UserState> = { 
	SET_USER(state, user: User) {
		state.currentUser = user;
	},
	deleteUser(state) {
		state.currentUser = null;
	},

	setCsrf(state) {
		let name = "csrftoken"
		let cookieValue = "";
		if (document.cookie && document.cookie !== "") {
			const cookies = document.cookie.split(";");
			for (let i = 0; i < cookies.length; i++) {
				const cookie = cookies[i].trim();
				// Does this cookie string begin with the name we want?
				if (cookie.substring(0, name.length + 1) === name + "=") {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
			}
		}

		state.csrftoken = cookieValue;
	},
	setCsrfOnServer(state, token: string){
		state.csrftoken = token
	},

	toggleSessionError(state){
		state.sessionError = !state.sessionError
	},
}
