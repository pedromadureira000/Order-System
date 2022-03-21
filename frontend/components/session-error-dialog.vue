<template>
  <v-dialog :value="session_error" max-width="500px" persistent>
    <v-card>
      <v-card-text>
        <v-container fluid>
          <h4>{{$t('SessionErrorText')}}</h4>
        </v-container>
      </v-card-text>
      <v-card-actions class="d-flex justify-center">
        <v-btn class="blue--text darken-1" text @click="useHere()" :loading="loading" :disabled="loading">{{$t('Use_Here')}}</v-btn>
      </v-card-actions>
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
