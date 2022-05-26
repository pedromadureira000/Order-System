<template>
  <v-dialog :retain-focus="false" :value="session_error" max-width="30%" persistent>
    <v-card>
      <v-card-text>
        <h4 class="pt-3">{{$t('SessionErrorText')}}</h4>
        <div class="d-flex justify-center mt-2">
          <v-btn class="blue--text darken-1" text @click="useHere()" :loading="loading" :disabled="loading">{{$t('Use_Here')}}</v-btn>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>

export default {
  data () {
    return {
      loading: false,
		}
  },

  methods: {
    async useHere() {
      this.loading = true
			await this.$store.dispatch('user/checkAuthenticated')
			if (this.$store.state.user.currentUser){
				this.$store.commit('user/toggleSessionError')	
			}      
			this.loading = false
    },
  },

  computed: {
    session_error(){
      return this.$store.state.user.sessionError
    }
  }
}
</script>
