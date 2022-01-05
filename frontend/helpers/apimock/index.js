import {eraseCookie, setCookie} from '../functions'
import {user, admin, users} from './db_user'

function mockasync (data) {
  return new Promise((resolve, reject) => {
    setTimeout(() => resolve(data), 600)
  })
}

function mockasyncerror (message = 'Something went wrong') {
  return new Promise((resolve, reject) => {
    setTimeout(() => reject(new Error(message)), 600)
  })
}

export default {	
	checkAuthenticated(){
		return mockasync(user)
	},

	getCsrf(){
		setCookie('csrftoken', 'sometoken', 1)
		return mockasync('ok')
	},

	login(payload){ 
		if (typeof payload.username === 'string' && typeof payload.company_code === 'number' && 
        typeof payload.password === 'string' && typeof payload.csrftoken === 'string'){
		if (payload.username === "admin" && payload.company_code === 'phsw'){
			return mockasync(admin)
		}else{
			setCookie('sessionid', 'anothertoken', 1)
			return mockasync(user)
		}
		}else {
			mockasyncerror()
		}
	},

	logout(){
		eraseCookie('sessionid')
		eraseCookie('csrftoken')
		return mockasync("User logged out.")
	},

	updateUserProfile(payload){ 
    //TODO some fields should be optional
		if (typeof payload.first_name === 'string' && typeof payload.last_name === 'string' 
      && typeof payload.email === 'string' && payload.cpf === 'string'){
			let updated_user = {...user, ...payload}
			return mockasync(updated_user)	
		}else {
			mockasyncerror()
		// if (typeof payload.email === 'string' && typeof payload.password === 'string' && typeof payload.csrftoken === 'string'){
		}
	},

	updatePassword(payload){
		if (typeof payload.current_password === 'string' && typeof payload.password === 'string'){
			eraseCookie('sessionid')
			eraseCookie('csrftoken')
			return mockasync("Passsword changed.")
		}else {
			mockasyncerror()
		}

	},

	passwordReset(email){
		if (typeof email === 'string'){
			return mockasync("Email was been sent")
		}else {
			mockasyncerror()
		}
	},

	passwordResetConfirm(payload){
		if (typeof payload.new_password === 'string' && typeof payload.token === 'string' && typeof payload.uid === 'string'){
			return mockasync("Passsword was been changed")
		}else {
			mockasyncerror()
		}
	},

	createUser(payload){
    //TODO some fields should be optional (use types!)
		if (typeof payload.first_name === 'string' && typeof payload.last_name === 'string' &&
        typeof payload.username === 'string' && typeof payload.company_code === 'number' &&
        typeof payload.email === 'string' && typeof payload.password === 'string' && payload.cpf === 'string')
        {	 
          delete payload.password	
          delete payload.company_code
          payload['roles'] = []
          payload['permissions'] = []
          payload['company'] = {
            "name": `Company: ${payload.company_code}`,
            "cnpj": "30228893000166",
            "company_code": payload.company_code,
            "status": "A",
            "company_type": "L"
          }
          return mockasync(payload)	
        }
		else {
			mockasyncerror("createUser Error")
		}
	},

	fetchUsersByAdmin(){
		return mockasync(users)
	},

	deleteUserByAdmin(id){
		return mockasync('ok')	
	}
}
