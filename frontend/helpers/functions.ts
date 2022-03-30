import {Commit, Dispatch} from "vuex"
//Organization
let contracting_fields = ['contracting_code', 'active_users_limit']
let company_fields = ['company_code','item_table', 'client_table','cnpj_root']
let establishment_fields = ['company' ,'establishment_code']
let client_table_fields = ['client_table_code']
let client_fields = ['client_code', 'client_table', 'vendor_code', 'establishment', 'price_table']
// User
let common_user_fields = ['username', 'first_name','last_name', 'email', 'password']
let erp_user_fields  = ['contracting']
let client_user_fields = ['client']
// Item
let item_table_fields = ['item_table_code']
let item_fields = ['item_code', 'category', 'unit', 'barcode', 'technical_description']
let category_fields = ['category_code']
let price_table_fields = ['unit_price', 'table_code']
// Order

// commum fields
let common_fields_list = ['name', 'cnpj', 'status', 'description', 'note']
// field_list
let field_list = contracting_fields.concat(company_fields, establishment_fields, client_table_fields, client_fields, common_user_fields, erp_user_fields, client_user_fields, item_table_fields, item_fields, category_fields, price_table_fields, common_fields_list)

let nested_field_list = ['client_establishments', 'agent_establishments', 'agent_permissions', 'price_items']

export const doesHttpOnlyCookieExist = (cookiename: string): boolean => {
	var d = new Date();
	d.setTime(d.getTime() + (1000));
	var expires = "expires=" + d.toUTCString();
	document.cookie = cookiename + "=new_value;path=/;" + expires;
	return document.cookie.indexOf(cookiename + '=') == -1;
}

export const setCookie = (name: string, value: string, days: number) => {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

export const getCookie = (name: string) => {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

export const eraseCookie = (name: string) => {   
    document.cookie = name +'=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

export const ErrorHandler = (error: any, commit: Commit, dispatch: Dispatch, i18n: any, 
                            default_error_msg: any = i18n.t('Something_went_wrong')  ) => { 
  // error.response.data = null  // <<- this line is for test some errors
  // -----------/ Time-out Error
  if (error.message == 'timeout of 15000ms exceeded'){
    dispatch("setAlert", {message: i18n.t("Request_Time_out"), alertType: "error"}, { root: true })
  } 
  // ----------/ Internet Connection Error
  else if (error.message === 'Network Error' || !window.navigator.onLine){ // TODO: I'm not sure about it.
    dispatch("setAlert", {message: i18n.t("Connection_error"), alertType: "error"}, { root: true })
    dispatch("switchConnectionError")
  // ---------/ Other Error
  } 
  else if (error.response && error.response.data){
    let response = error.response
    let  first_key = Object.keys(error.response.data)[0]
    // 2 Sessions At the same time.
    if (response.data ===  "Session already open." || response.data === "A Sessão já esta aberta."){
      commit("toggleSessionError")
    }
    //  This will occur when a user attempt to access an API with an old session after he has been logged out.
    else if (response.data ===  "Invalid session. Try to login again." || response.data === "Sessão invalida. Tente logar novamente."){
      // commit("toggleInvalidSessionError") TODO
    }
    // 500 Server Error
    else if (response.status ===  500){
        dispatch("setAlert", {message: i18n.t("Server_error"), alertType: "error"}, { root: true })
    }
    else if (first_key){
      // 'detail' DRF Errors
      if (first_key == 'detail'){
        let errorMessage = response.data[first_key]
        dispatch("setAlert", {message: errorMessage , alertType: "error"}, { root: true })
      }
      // 'non_field_errors' and 'error'
      else if (first_key == 'non_field_errors' || first_key == 'error') {
        let errorMessage = response.data[first_key][0]
        dispatch("setAlert", {message: errorMessage , alertType: "error"}, { root: true })
      }
      // DRF Normal Field Errors
      else if (field_list.includes(first_key)){
        let errorMessage = response.data[first_key][0]
        // Translation Gambiarra: TODO Fix it
        if (errorMessage.includes('is not valid cnpj')){
          errorMessage = errorMessage.replace('is not valid cnpj', 'não é um CNPJ valido')
        } 
        //
        dispatch("setAlert", {message: i18n.t(first_key.substring(0,1).toUpperCase() + first_key.substring(1)) + ": " + errorMessage , 
                 alertType: "error"}, { root: true })
      }
      // DRF Nested Field Errors
      else if (nested_field_list.includes(first_key)){
        let nested_values_list = response.data[first_key]
        // Check if the first element of the nested_values_list is a string. EX: {"client_establishments":["This field is required."]}
        if (typeof nested_values_list[0] == 'string') {
          let errorMessage = response.data[first_key][0]
          dispatch("setAlert", {message: i18n.t(first_key.substring(0,1).toUpperCase() + first_key.substring(1)) + ": " + errorMessage ,
                   alertType: "error"}, { root: true })
        } 
        // Check if the first element or the nested_values_list is an Object. EX: {"price_items": [{},{"item": ["This field is required."]}]}
        else if (typeof nested_values_list[0] === 'object'){
          // catch the first nested_error which is not empty
          let nested_error = nested_values_list.find((el: Object): Object => Object.keys(el).length > 0)
          let second_key = Object.keys(nested_error)[0]
          let errorMessage = nested_error[second_key]
          dispatch("setAlert", {message: i18n.t(first_key.substring(0,1).toUpperCase() + first_key.substring(1)) + ": [" +
                  i18n.t(second_key.substring(0,1).toUpperCase() + second_key.substring(1)) + ": " + errorMessage + "].",
                  alertType: "error"}, { root: true })
        }
      }
      else {
        dispatch("setAlert", {message: default_error_msg, alertType: "error"}, { root: true })
      }
    }
    // Default Error
    else {
      console.log(">>>>>>> No 'first_key'")
      dispatch("setAlert", {message: default_error_msg, alertType: "error"}, { root: true })
    }
  } 
  else { // Case where error.response does not exist and it's not a Internet Connection or Time-out error
    console.log(">>>>>>> Something very wrong happened here. 'error.response' is empty.") //TODO communicate the ADM.
    dispatch("setAlert", {message: default_error_msg, alertType: "error"}, { root: true })
  }
}
