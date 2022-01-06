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
						v-model="company_code"
						:error-messages="company_codeErrors"
						label="Company"
						required
						@blur="$v.company_code.$touch()"
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

					<router-link
						to="/passwordreset" 
						tabindex="-1"
						@click="visible = false"
					>
						<div @click="visible = false">I forgot my password</div>
					</router-link><br />

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
import { required, alphaNum, integer} from "vuelidate/lib/validators";

export default {
  mixins: [validationMixin],

  validations: {
    username: { required, alphaNum},
    company_code: {required, integer},
    password: { required },
    login_group:["username", "company_code", "password"]
  },

  data () {
    return {
      visible: false,
      loading: false,
      username: '',
      company_code: null,
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
        await this.$store.dispatch('auth/login', {username: this.username, company_code: this.company_code, password: this.password} )
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
      !this.$v.username.alphaNum && errors.push("Must have only alphanumeric characters.");
      !this.$v.username.required && errors.push("Username is required");
      return errors;
    },
    company_codeErrors() {
      const errors = [];
      if (!this.$v.company_code.$dirty) return errors;
      !this.$v.company_code.integer && errors.push("Must be a integer");
      !this.$v.company_code.required && errors.push("Company required");
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
