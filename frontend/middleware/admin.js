// If fail in "authenticated" middleware, it will not enter this middleware
export default async (ctx) => {
		//Checks if admin module exist in user modules
    let user_roles = ctx.store.state.auth.currentUser.roles
		if (user_roles.includes('admin') || user_roles.includes('admin_agent') || user_roles.includes('agent')){  
			console.log('admin middleware passed')
			return;
		}else{
			ctx.redirect(302, '/')
		}
}
