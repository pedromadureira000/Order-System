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

  async fetchCategoriesToMakeOrder({commit, dispatch}: {commit: Commit, dispatch: Dispatch}, establishment_compound_id: string){
    try {
      let data = await api.fetchCategoriesToMakeOrder(establishment_compound_id)
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('fetchCategoriesToMakeOrder_error_msg'))
    }
  }, 

  async makeOrder({commit, dispatch}: {commit: Commit, dispatch: Dispatch}){
    try {
      let data = await api.makeOrder()
      dispatch("setAlert", {message: this.app.i18n.t('makeOrder_success_msg'), alertType: "success"}, { root: true })
      return data
    }
    catch(error){
      ErrorHandler(error, commit, dispatch, this.app.i18n, this.app.i18n.t('makeOrder_error_msg'))
    }
  }, 
}

// --------------------------------------------/mutations/---------------------------------------------

import {MutationTree} from "vuex"

export const mutations: MutationTree<OrderState> = { 
}
