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

	async fetchItemTables({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try {
		let item_tables = await api.fetchItemTables()
		return item_tables
    }
		catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t("error..."))
		}
	},

  async createItem({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.createItem(payload)
      console.log(">>>",data)
      dispatch("setAlert", {message: "Item created!", alertType: "success"}, { root: true })
      return data
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t("error..."))
    }
  },

  async createCategory({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.createCategory(payload)
      console.log(">>>",data)
      dispatch("setAlert", {message: "Category created", alertType: "success"}, { root: true })
      return data
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t("error..."))
    }
  },

  async createPriceTable({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.createPriceTable(payload)
      console.log(">>>",data)
      dispatch("setAlert", {message: "Price table created", alertType: "success"}, { root: true })
      return data
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t("error..."))
    }
  },

  async updatePriceTable({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
    let data = await api.updatePriceTable(payload)
    console.log(">>",data)
    dispatch("setAlert", {message: "Price table has been updated.", alertType: "success"}, { root: true })
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t("error..."))
    }
  },

  async fetchItems({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try{
      let items = await api.fetchItems()
      return items
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t("error..."))
    }
  },

  async fetchCategories({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try{
      let items = await api.fetchCategories()
      return items
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t("error..."))
    }
  },

  async fetchPriceTables({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try {
      let items = await api.fetchPriceTables()
      return items
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t("error..."))
    }
  },

  async deletePriceTable({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.deletePriceTable(payload)
      console.log(">>>",data)
      dispatch("setAlert", {message: "Price table deleted", alertType: "success"}, { root: true })
      return "ok"
    }
    catch(error){
      handleError(error, commit, dispatch, this.app.i18n, this.app.i18n.t("error..."))
    }
  },
}

// --------------------------------------------/mutations/---------------------------------------------

import {MutationTree} from "vuex"

export const mutations: MutationTree<ItemState> = { 
}
