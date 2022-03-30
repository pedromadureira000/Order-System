interface ItemState {
  test: boolean
}

export const state = (): ItemState => ({
  test: true
})  

import {ErrorHandler} from "~/helpers/functions";
// ------------------------------------------/actions/-------------------------------------------

import {ActionTree, Commit, Dispatch} from "vuex"
import {RootState} from "@/store/index"
 // @ts-ignore: This module is dynamically added in nuxt.config.js
import api from "~api"

export const actions: ActionTree<ItemState, RootState> = {

  async createItemTable({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.createItemTable(payload)
      dispatch("setAlert", {message: this.app.i18n.t('createItemTable_success_msg'), alertType: "success"}, { root: true })
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("createItemTable_error_msg"))
    }
  },

	async fetchItemTables({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try {
		let item_tables = await api.fetchItemTables()
		return item_tables
    }
		catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchItemTables_error_msg"))
		}
	},

  async updateItemTable({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
    let data = await api.updateItemTable(payload)
    dispatch("setAlert", {message: this.app.i18n.t('updateItemTable_success_msg'), alertType: "success"}, { root: true })
    return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("updateItemTable_error_msg"))
    }
  },

  async deleteItemTable({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      await api.deleteItemTable(payload)
      dispatch("setAlert", {message: this.app.i18n.t('deleteItemTable_success_msg'), alertType: "success"}, { root: true })
      return "ok"
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("deleteItemTable_error_msg"))
    }
  },

  // ----------- Category
  
  async createCategory({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.createCategory(payload)
      dispatch("setAlert", {message: this.app.i18n.t('createCategory_success_msg'), alertType: "success"}, { root: true })
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("createCategory_error_msg"))
    }
  },

  async fetchCategories({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try{
      let items = await api.fetchCategories()
      return items
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchCategories_error_msg"))
    }
  },

  async updateCategory({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
    let data = await api.updateCategory(payload)
    dispatch("setAlert", {message: this.app.i18n.t('updateCategory_success_msg'), alertType: "success"}, { root: true })
    return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("updateCategory_error_msg"))
    }
  },

  async deleteCategory({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      await api.deleteCategory(payload)
      dispatch("setAlert", {message: this.app.i18n.t('deleteCategory_success_msg'), alertType: "success"}, { root: true })
      return "ok"
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("deleteCategory_error_msg"))
    }
  },
  // ---------- Item
  
  async fetchItemTablesToCreateItemOrCategoryOrPriceTable({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try{
      let item_tables = await api.fetchItemTablesToCreateItemOrCategoryOrPriceTable()
      return item_tables
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchItemTablesToCreateItemOrCategoryOrPriceTable_error_msg"))
    }
  },

  async fetchCategoriesToCreateItem({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, item_table_compound_id: string){
    try{
      let categories = await api.fetchCategoriesToCreateItem(item_table_compound_id)
      return categories
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchCategoriesToCreateItem_error_msg"))
    }
  },
  
  async createItem({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.createItem(payload)
      dispatch("setAlert", {message: this.app.i18n.t('createItem_success_msg'), alertType: "success"}, { root: true })
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("createItem_error_msg"))
    }
  },

  async fetchItems({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try{
      let items = await api.fetchItems()
      return items
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchItems_error_msg"))
    }
  },

  async updateItem({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
    let data = await api.updateItem(payload)
    dispatch("setAlert", {message: this.app.i18n.t('updateItem_success_msg'), alertType: "success"}, { root: true })
    return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("updateItem_error_msg"))
    }
  },

  async deleteItem({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      await api.deleteItem(payload)
      dispatch("setAlert", {message: this.app.i18n.t('deleteItem_success_msg'), alertType: "success"}, { root: true })
      return "ok"
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("deleteItem_error_msg"))
    }
  },

  // -------- PriceTable
  async fetchCompaniesToCreatePriceTable({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try {
      let companies = await api.fetchCompaniesToCreatePriceTable()
      return companies
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchCompaniesToCreatePriceTable_error_msg"))
    }
  },

  
  async fetchItemsToCreatePriceTable({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, item_table_compound_id: string){
    try {
      let items = await api.fetchItemsToCreatePriceTable(item_table_compound_id)
      return items
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchItemsToCreatePriceTable_error_msg"))
    }
  },

  async fetchPriceItemsFromThePriceTable({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, price_table_compound_id: string){
    try {
      let price_items = await api.fetchPriceItemsFromThePriceTable(price_table_compound_id)
      return price_items
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchPriceItemsFromThePriceTable_error_msg"))
    }
  },

  async createPriceTable({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.createPriceTable(payload)
      dispatch("setAlert", {message: this.app.i18n.t('createPriceTable_success_msg'), alertType: "success"}, { root: true })
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("createPriceTable_error_msg"))
    }
  },

  async fetchPriceTables({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try {
      let items = await api.fetchPriceTables()
      return items
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("fetchPriceTables_error_msg"))
    }
  },

  async updatePriceTable({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
    let data = await api.updatePriceTable(payload)
      dispatch("setAlert", {message: this.app.i18n.t('updatePriceTable_success_msg'), alertType: "success"}, { root: true })
    return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("updatePriceTable_error_msg"))
    }
  },

  async deletePriceTable({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      await api.deletePriceTable(payload)
      dispatch("setAlert", {message: this.app.i18n.t('deletePriceTable_success_msg'), alertType: "success"}, { root: true })
      return "ok"
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t("deletePriceTable_error_msg"))
    }
  },
}

// --------------------------------------------/mutations/---------------------------------------------

import {MutationTree} from "vuex"

export const mutations: MutationTree<ItemState> = { 
}
