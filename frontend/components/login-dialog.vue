<template>
  <v-dialog v-model="visible" max-width="500px">
    <v-card>
      <v-card-title>Log in</v-card-title>
      <v-card-text>
        <v-container fluid>
					<v-text-field
						v-model="username"
						:error-messages="usernameErrors"
						label="Username"
						required
						@blur="$v.username.$touch()"
					></v-text-field>
					<v-text-field
						v-model="contracting_code"
						:error-messages="contracting_codeErrors"
						label="Contracting"
						required
						@blur="$v.contracting_code.$touch()"
					></v-text-field>
					<v-text-field
						v-model="password"
						:error-messages="passwordErrors"
						label="Password"
						required
						@blur="$v.password.$touch()"
						type="password"
						@keyup.enter="login"
					></v-text-field>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
				<!--<v-btn class="mr-4 mt-3" @click="login()"> submit </v-btn> -->
				<v-btn class="blue--text darken-1" text @click="close()">Cancel</v-btn>
        <v-btn class="blue--text darken-1" text @click="login()" :loading="loading" :disabled="loading">Login</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required, helpers} from "vuelidate/lib/validators";
import {slugFieldValidator} from "~/helpers/validators"

export default {
  mixins: [validationMixin],

  validations: {
    username: { required, slugFieldValidator},
    contracting_code: {required, slugFieldValidator},
    password: { required },
    login_group:["username", "contracting_code", "password"]
  },

  data () {
    return {
      visible: false,
      loading: false,
      username: '',
      contracting_code: null,
      password: '',
    }
  },

  methods: {
    open() {
      this.visible = true
    },
    close () {
      this.visible = false
    },
    async login() {
      this.$v.login_group.$touch();
      if (this.$v.login_group.$invalid) {
        this.$store.dispatch("setAlert", { message: "Please fill the form correctly.", alertType: "error" }, { root: true })
      } else {
        this.loading = true
        await this.$store.dispatch('auth/login', {username: this.username, contracting_code: this.contracting_code, password: this.password} )
        if (this.$store.state.auth.currentUser){
          this.visible = false
        }      
        this.loading = false
      }
    }
  },

  computed: {
    usernameErrors() {
      const errors = [];
      if (!this.$v.username.$dirty) return errors;
      !this.$v.username.slugFieldValidator && errors.push("It must containing only letters, numbers, underscores or hyphens.");
      !this.$v.username.required && errors.push("Username is required");
      return errors;
    },
    contracting_codeErrors() {
      const errors = [];
      if (!this.$v.contracting_code.$dirty) return errors;
      !this.$v.contracting_code.slugFieldValidator && errors.push("It must containing only letters, numbers, underscores or hyphens.");
      !this.$v.contracting_code.required && errors.push("Contracting code required");
      return errors;
    },
    passwordErrors() {
      const errors = [];
      if (!this.$v.password.$dirty) return errors;
      !this.$v.password.required && errors.push("Password is required.");
      return errors;
    },
  },

	watch: {
		visible(newvalue, oldvalue) {
			if (newvalue === true && !this.$store.state.auth.csrftoken){
				this.$store.dispatch('auth/getCsrf')		
			}
		}
	},
}
</script>
