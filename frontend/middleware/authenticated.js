export default (ctx) => {
	if (!ctx.store.state.user.currentUser){
		ctx.redirect(302, '/')
	}	
}
