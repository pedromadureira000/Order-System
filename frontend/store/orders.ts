interface OrdersState {
  test: boolean
}

export const state = (): OrdersState => ({
  test: true
})  

// ------------------------------------------/actions/-------------------------------------------

import {ActionTree, Commit, Dispatch} from "vuex"
import {RootState} from "@/store/index"
 // @ts-ignore: This module is dynamically added in nuxt.config.js
import api from "~api"

export const actions: ActionTree<OrdersState, RootState> = {
  async createItem({dispatch}: {dispatch: Dispatch,}, payload: any){
    try {
      let data = await api.createItem(payload)
      console.log(">>>",data)
      dispatch("setAlert", {message: "Item created!", alertType: "success"}, { root: true })
      return data
    }
    catch(e){
      let error: string[] = Object.values(e.response.data)
      let errorMessage = error[0][0]
      dispatch("setAlert", {message: errorMessage , alertType: "error"}, { root: true })
    }
  },

  async createCategory({dispatch}: {dispatch: Dispatch,}, payload: any){
    try {
      let data = await api.createCategory(payload)
      console.log(">>>",data)
      dispatch("setAlert", {message: "Category created", alertType: "success"}, { root: true })
      return data
    }
    catch(e){
      let error: string[] = Object.values(e.response.data)
      let errorMessage = error[0][0]
      dispatch("setAlert", {message: errorMessage , alertType: "error"}, { root: true })
    }
  },

  async createPriceTable({dispatch}: {dispatch: Dispatch,}, payload: any){
    try {
      let data = await api.createPriceTable(payload)
      console.log(">>>",data)
      dispatch("setAlert", {message: "Price table created", alertType: "success"}, { root: true })
      return data
    }
    catch(e){
      let error: string[] = Object.values(e.response.data)
      let errorMessage = error[0][0]
      dispatch("setAlert", {message: errorMessage , alertType: "error"}, { root: true })
    }
  },

  async updatePriceTable({commit, dispatch}: {commit: Commit, dispatch: Dispatch,}, payload: any){
    try {
    let data = await api.updatePriceTable(payload)
    console.log(">>",data)
    dispatch("setAlert", {message: "Price table has been updated.", alertType: "success"}, { root: true })
    }
    catch(e){
      handleError(e.response, commit)
      dispatch("setAlert", {message: "Something went wrong when trying to update price table.", alertType: "error"}, { root: true })
      // handleError(e.response, commit)
      // let error: string[] = Object.values(e.response.data)  TODO ??
      // let errorMessage = error[0][0]
      // dispatch("setAlert", {message: errorMessage , alertType: "error"}, { root: true })
    }
  },

  async fetchItems({dispatch}: {dispatch: Dispatch,}){
    let items = await api.fetchItems()
    return items
  },

  async fetchCategories({dispatch}: {dispatch: Dispatch,}){
    let items = await api.fetchCategories()
    return items
  },

  async fetchPriceTables({dispatch}: {dispatch: Dispatch,}){
    let items = await api.fetchPriceTables()
    return items
  },


  async deletePriceTable({commit, dispatch}: {commit: Commit, dispatch: Dispatch,}, payload: any){
    try {
      let data = await api.deletePriceTable(payload)
      console.log(">>>",data)
      dispatch("setAlert", {message: "User deleted", alertType: "success"}, { root: true })
      return "ok"
    }
    catch(e){
      let error: string[] = Object.values(e.response.data)
      let errorMessage = error[0]
      dispatch("setAlert", {message: errorMessage, alertType: "error"}, { root: true })
    }
  },

}

// --------------------------------------------/mutations/---------------------------------------------

import {MutationTree} from "vuex"
import {handleError} from "~/helpers/functions";

export const mutations: MutationTree<OrdersState> = { 
	// SET_USER(state, user: User) {
		// state.currentUser = user;
	// },
}
