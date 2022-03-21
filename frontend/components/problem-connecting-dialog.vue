<template>
  <v-dialog :value="connection_error" max-width="35%" persistent>
    <v-card>
      <v-card-text>
        <v-container fluid>
          <h2>{{$t('ProblemConnectingTitle')}}</h2>
          <p class="mt-1">{{$t('Check_your_internet_connection')}}</p>
        </v-container>
      </v-card-text>
      <!-- <v-card-actions class="d-flex justify-center"> -->
        <!-- <v-btn class="blue--text darken-1" text @click="Close()" :loading="loading" :disabled="loading"></v-btn> -->
      <!-- </v-card-actions> -->
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
    verifyConnection() {
      this.loading = true
      while (this.$store.state.connectionError == true) {
        setTimeout(() => {
          console.log(">>>>>>> Inside net loop")
          if (this.window.navigator.onLine) {
            this.$store.dispatch('switchConnectionError')
            this.loading = false
          }
          else {this.verifyConnection()}
        }, 2500);
      }
    },
  },

  computed: {
    connection_error(){
      return this.$store.state.connectionError
    }
  },

  watch: {
    connection_error(new_value) {
      if (new_value === true){
        this.verifyConnection()
      }
    }
  }

}
</script>
