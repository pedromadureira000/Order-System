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
