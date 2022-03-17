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
	
	async checkAuthenticated({commit}: {commit: Commit}) {
		try {
			let data: any = await api.checkAuthenticated()
			commit("SET_USER", data);
		} catch (error) {
			console.log(error);
		}	
	},

	getCsrf({commit}: {commit: Commit}) {
		try {
			api.getCsrf() 
			console.log("Csrftoken recived");
			commit("setCsrf");
			
		} catch (error) {
			console.log(error)	
		}
	},

	async login({commit, dispatch, state}: {commit: Commit, dispatch: Dispatch, state: UserState}, payload: any){
		payload["csrftoken"] = state.csrftoken
		try {
			let data = await api.login(payload)
			console.log(data)
			commit("SET_USER", data);
			commit("setCsrf");
			dispatch("setAlert", {message: "Logged in with success.", alertType: "success"}, { root: true })
		} catch(e){
			console.log("error when trying to login: ", e)
			dispatch("setAlert", {message: "Login Failed", alertType: "error"}, { root: true })
			// return "not ok"
		}
	},
	
	async logout({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
		try {
		let data = await api.logout()
		console.log(data)
		commit("deleteUser");
		dispatch("setAlert", {message: "Logged out in with success.", alertType: "success"}, { root: true })
		this.$router.push("/")
		} catch (error) {
			console.log("error when trying to log out: ", error )
			//>>>>>>>>>>>>>>>>>>>>>>TODO<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		}
	},

	async updateCurrentUserProfile({commit, dispatch}: {commit: Commit, dispatch: Dispatch,}, payload: any){
		try {
      let data = await api.updateCurrentUserProfile(payload)
      console.log(">>",data)
      commit("SET_USER", data )
      dispatch("setAlert", {message: "Your profile has been updated.", alertType: "success"}, { root: true })
		}
		catch(e){
			handleError(e.response, commit)
			let error: string[] = Object.values(e.response.data)
			let errorMessage = error[0][0]
			dispatch("setAlert", {message: errorMessage , alertType: "error"}, { root: true })
			// dispatch("setAlert", {message: "Something went wrong when trying to update profile.", alertType: "error"}, { root: true })
		}
	},

	async updatePassword({commit, dispatch}: {commit: Commit, dispatch: Dispatch,}, payload: any){
		try {
			let data = await api.updatePassword(payload)
			console.log(">>>>>>>>>>", data)
			commit("deleteUser")
			dispatch("setAlert", {message: "Your password has been updated.", alertType: "success"}, { root: true })
			setTimeout(() => {
				this.$router.push("/")
			}, 600);
		}
		catch(e){
			console.log("error in updatePassword action: ", e);
			dispatch("setAlert", {message: "Something went wrong when trying to update password.", alertType: "error"}, { root: true })
		}
	},

	// ----------------------------------------/ User API
  
	async createUser({dispatch}: {dispatch: Dispatch,}, payload: any){
		try {
			let data = await api.createUser(payload)
			console.log(">>>",data)
			dispatch("setAlert", {message: "User created", alertType: "success"}, { root: true })
			return data
		}
		catch(e){
			// dispatch("setAlert", {message: "Something went wrong when trying to create user.", alertType: "error"}, { root: true })
			// let errorMessage: string = Object.values(e.response.data)[0][0] <<< why i got this ts error? "Object is of type "unknown""
			let error: string[] = Object.values(e.response.data)
			let errorMessage = error[0][0]
			dispatch("setAlert", {message: errorMessage , alertType: "error"}, { root: true })
		}
	},

	async fetchUsersByAdmin(){
		let users = await api.fetchUsersByAdmin()
		return users
	},

	async deleteUserByAdmin({dispatch}: {dispatch: Dispatch,}, payload: any){
		try {
			let data = await api.deleteUserByAdmin(payload)
			console.log(">>>",data)
			dispatch("setAlert", {message: "User deleted", alertType: "success"}, { root: true })
			return "ok"
		}
		catch(e){
			// dispatch("setAlert", {message: "Something went wrong when trying to delete user.", alertType: "error"}, { root: true })
			let error: string[] = Object.values(e.response.data)
			let errorMessage = error[0]
			dispatch("setAlert", {message: errorMessage, alertType: "error"}, { root: true })
		}
	},

}

// --------------------------------------------/MUTATIONS/---------------------------------------------

import {MutationTree} from "vuex"
import {handleError} from "~/helpers/functions";

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
