<template>
  <v-dialog :retain-focus="false" :value="connection_error" max-width="35%" persistent>
    <v-card>
      <v-card-text>
        <v-container fluid>
          <h2 style="text-align: center;">{{$t('ProblemConnectingTitle')}}</h2>
          <p class="mt-2">{{$t('Check_your_internet_connection')}}</p>
        <div class="d-flex justify-center">
          <v-btn class="blue--text darken-1" text @click="Close()" :loading="loading" :disabled="loading"></v-btn>
        </div>
        </v-container>
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
    async verifyConnection() {
      this.loading = true
      await new Promise(resolve => setTimeout(resolve, 2500))
      let data = await this.$store.dispatch('testConnection')
      if (data == 'ok') {
        this.loading = false
        this.$store.dispatch('switchConnectionError', false)
      }
        else {this.verifyConnection()}
      }
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
