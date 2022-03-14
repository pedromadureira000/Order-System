<template>
	<div class="ma-4"><p class="ma-2">{{message}}</p></div>
</template>

<script>
export default {
    name: 'Home',
    data() {
      return {
        message: "" 
      }
    },
		computed: {
			user() {
				return this.$store.state.user.currentUser
			},
		},
		watch: {
			user(newValue, oldValue){
        /** console.log(`old value = ${oldValue}. New value = ${newValue}`  ) */
				if (newValue) {
          this.message = this.$t('Welcome_user_first_name') + newValue.first_name + "!";
				} else {
					this.message = this.$t("See_you_later")
				}
			}	
		},
		created() {
			if (this.$store.state.user.currentUser){
				this.message = this.$t('Welcome_user_first_name') + this.$store.state.user.currentUser.first_name + "!";
			} else {
				this.message = this.$t('Please_log_in')
			}
		}	
	}
</script>

<style>

</style>

