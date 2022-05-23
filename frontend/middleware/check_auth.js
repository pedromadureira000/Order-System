import api from '~api'

export default async (ctx) => {
	// if (process.env.API_MOCK){
		// console.log(">>>>>>> 'API_MOCK'")
	// }
		// A middleware can be asynchronous. To do this return a  Promise or use async/await.
	if (process.server && ctx.req.headers.cookie){
		let csrftoken = ctx.req.headers.cookie
			.split(";")
			.find(c => c.trim().startsWith("csrftoken="));
		if (!csrftoken) {
			return;
		}
		const token = csrftoken.split("=")[1];
		ctx.store.commit('user/setCsrfOnServer', token) 

		const sessionid = ctx.req.headers.cookie
			.split(";")
			.find(c => c.trim().startsWith("sessionid="));
		if (!sessionid) {
			return;
		}
		try {
			// await ctx.store.dispatch('user/checkAuthenticated')	
      let data = await api.checkAuthenticated()	
			ctx.store.commit('user/SET_USER', data )
		}
		catch (error) { 
      // if ( error.message == 'timeout of 15000ms exceeded') { 
      // }
      // console.log('>>>> error middleware "check_auth": ', error)
		}
	}
}
