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

}

// --------------------------------------------/mutations/---------------------------------------------

import {MutationTree} from "vuex"

export const mutations: MutationTree<OrderState> = { 
}
