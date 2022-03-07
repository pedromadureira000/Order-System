interface ItemState {
  test: boolean
}

export const state = (): ItemState => ({
  test: true
})  

import {handleError} from "~/helpers/functions";
// ------------------------------------------/actions/-------------------------------------------

import {ActionTree, Commit, Dispatch} from "vuex"
import {RootState} from "@/store/index"
 // @ts-ignore: This module is dynamically added in nuxt.config.js
import api from "~api"

export const actions: ActionTree<ItemState, RootState> = {

	async fetchItemTables({dispatch}: {dispatch: Dispatch,}){
    try {
		let item_tables = await api.fetchItemTables()
		return item_tables
    }
		catch(e){
      dispatch("setAlert", {message: "Something went wrong when trying to fetch client tables.", alertType: "error"}, { root: true })
		}
	},

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

  async fetchItems(){
    let items = await api.fetchItems()
    return items
  },

  async fetchCategories(){
    let items = await api.fetchCategories()
    return items
  },

  async fetchPriceTables(){
    let items = await api.fetchPriceTables()
    return items
  },

  async deletePriceTable({dispatch}: {dispatch: Dispatch,}, payload: any){
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

export const mutations: MutationTree<ItemState> = { 
}
