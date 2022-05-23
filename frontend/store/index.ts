export interface RootState {
  alert: {
    alertMessage: string;
    alertType: string;
    showAlert: boolean;
    alertID: number
  },
  connectionError: boolean,
  CDNBaseUrl: string

}

export const state = (): RootState => ({
  alert: {
    alertMessage: "",
    alertType: "info",
    showAlert: false,
    alertID: 0
  },
  connectionError: false,
  CDNBaseUrl: process.env.DEV ? 'http://localhost:8000' : 'https://amazoncdn.com' //TODO CDN
});

import { MutationTree } from "vuex";
export const mutations: MutationTree<RootState> = {
  setAlert(state, payload) {
    state.alert = {
      alertMessage: payload.message,
      alertType: payload.alertType,
      showAlert: true,
      alertID: Math.random()
    };
  },
  removeAlert(state) {
    state.alert = {
      alertMessage: "",
      alertType: "info",
      showAlert: false,
      alertID: state.alert.alertID
    };
  },
  // removeOneFromAlertqueue(state){
    // state.alert.alertqueue = state.alert.alertqueue - 1
  // }
  switchConnectionError(state){
    state.connectionError = !state.connectionError
  }

};

import { ActionTree, Commit } from "vuex";
export const actions: ActionTree<RootState, RootState> = {
  setAlert({ commit, state }: { commit: Commit, state: RootState }, 
           payload: {alertMessage: string, alertType: string, timeout?: number}) {
    // if showAlert is on. Close it and wait a few time to run the next.
    let timeout = 0
    if (state.alert.showAlert){
      commit("removeAlert")
      timeout = 300
    }
    setTimeout(() => {
      payload["timeout"] = payload["timeout"] ? payload["timeout"] : 3600; // <<<<<<<<< Default value
      commit("setAlert", payload);
      let current_alert = state.alert.alertID
      setTimeout(() => {
        if (state.alert.alertID == current_alert) {
          if (state.alert.alertType !== "error"){
            commit("removeAlert")
          }
        }
      }, payload.timeout);
    }, timeout);
  },
  removeAlert({ commit}: { commit: Commit}){
    // console.log(">>>>>>> removeAlert Action!!!!!!!!")
    commit('removeAlert')
  },
  switchConnectionError({ commit}: { commit: Commit}){
    commit('switchConnectionError')
  }
};
