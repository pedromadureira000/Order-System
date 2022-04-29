interface OrderState {
  test: boolean
}

export const state = (): OrderState => ({
  test: true
})  

import {ErrorHandler} from "~/helpers/functions";
// ------------------------------------------/actions/-------------------------------------------

import {ActionTree, Commit, Dispatch} from "vuex"
import {RootState} from "@/store/index"
 // @ts-ignore: This module is dynamically added in nuxt.config.js
import api from "~api"

export const actions: ActionTree<OrderState, RootState> = {

  async fetchClientEstabsToCreateOrder({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try {
      let data = await api.fetchClientEstabsToCreateOrder()
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('fetchClientEstabsToCreateOrder_error_msg'))
    }
  },

  async searchOnePriceItemToMakeOrder({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.searchOnePriceItemToMakeOrder(payload)
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('searchOnePriceItemToMakeOrder_error_msg'))
    }
  },

  async searchPriceItemsToMakeOrder({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.searchPriceItemsToMakeOrder(payload)
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('searchPriceItemsToMakeOrder_error_msg'))
    }
  },

  async fetchCategoriesToMakeOrderAndGetPriceTableInfo({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, establishment_compound_id: string){
    try {
      let data = await api.fetchCategoriesToMakeOrderAndGetPriceTableInfo(establishment_compound_id)
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('fetchCategoriesToMakeOrderAndGetPriceTableInfo_error_msg'))
    }
  }, 

  async makeOrder({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      await api.makeOrder(payload)
      dispatch("setAlert", {message: this.app.i18n.t('makeOrder_success_msg'), alertType: "success"}, { root: true })
      return 'ok'
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('makeOrder_error_msg'))
    }
  }, 

  async fetchDataToFillFilterSelectorsToSearchOrders({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try {
      let data = await api.fetchDataToFillFilterSelectorsToSearchOrders()
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('fetchDataToFillFilterSelectorsToSearchOrders_error_msg'))
    }
  }, 

  async fetchClientsToFillFilterSelectorToSearchOrders({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try {
      let data = await api.fetchClientsToFillFilterSelectorToSearchOrders()
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, 
                   this.app.i18n.t('fetchClientsToFillFilterSelectorToSearchOrders_error_msg'))
    }
  }, 

  async searchOrders({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, query_strings: string){
    try {
      let data = await api.searchOrders(query_strings)
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('searchOrders_error_msg'))
    }
  },  

  async fetchOrderDetails({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, id: string){
    try {
      let data = await api.fetchOrderDetails(id)
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('fetchOrderDetails_error_msg'))
    }
  }, 

  async fetchOrderHistory({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, id: string){
    try {
      let data = await api.fetchOrderHistory(id)
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('fetchOrderHistory_error_msg'))
    }
  }, 


  async updateOrder({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, payload: any){
    try {
      let data = await api.updateOrder(payload)
      dispatch("setAlert", {message: this.app.i18n.t('updateOrder_success_msg'), alertType: "success"}, { root: true })
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('updateOrder_error_msg'))
    }
  }, 
}

// --------------------------------------------/mutations/---------------------------------------------

import {MutationTree} from "vuex"

export const mutations: MutationTree<OrderState> = { 
}
