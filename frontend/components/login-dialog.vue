<template>
  <v-dialog v-model="visible" :retain-focus="false" max-width="500px">
      <v-card>
        <v-card-title>Login</v-card-title>
        <v-card-text>
          <v-container fluid>
              <v-text-field 
                required
                v-model="username"
                :error-messages="usernameErrors"
                :label="$t('Username')"
                @blur="$v.username.$touch()"
                type="text"
                name="username"
                autocomplete="username"
              ></v-text-field>
              <v-text-field
                required
                v-model="contracting_code"
                :error-messages="contracting_codeErrors"
                :label="$t('Contracting_code')"
                @blur="$v.contracting_code.$touch()"
                type="text"
                autocomplete="off"
              ></v-text-field>
              <v-text-field
                required
                v-model="password"
                :error-messages="passwordErrors"
                :label="$t('Password')"
                @blur="$v.password.$touch()"
                @keyup.enter="login"
                type="password"
              ></v-text-field>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn class="blue--text darken-1" text @click="close()">{{$t('Cancel')}}</v-btn>
          <v-btn class="blue--text darken-1" text @click="login()" :loading="loading" :disabled="loading">Login</v-btn>
        </v-card-actions>
      </v-card>
  </v-dialog>
</template>

<script>
import { validationMixin } from "vuelidate";
import { required } from "vuelidate/lib/validators";
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
      // clear form fields
      this.username = ""
      this.contracting_code = ""
      this.password = ""
      this.$v.$reset()
    },
    async login() {
      this.$v.login_group.$touch();
      if (this.$v.login_group.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
      } else {
        this.loading = true
        await this.$store.dispatch('user/login', {username: this.username, contracting_code: this.contracting_code, password: this.password} )
        if (this.$store.state.user.currentUser){
          this.visible = false
          // clear form fields
          this.username = ""
          this.contracting_code = ""
          this.password = ""
          this.$v.$reset()
        }      
        this.loading = false
      }
    }
  },

  computed: {
    usernameErrors() {
      const errors = [];
      if (!this.$v.username.$dirty) return errors;
      !this.$v.username.slugFieldValidator && errors.push(this.$t('SlugFieldErrorMessage'));
      !this.$v.username.required && errors.push(this.$t("This_field_is_required"));
      return errors;
    },
    contracting_codeErrors() {
      const errors = [];
      if (!this.$v.contracting_code.$dirty) return errors;
      !this.$v.contracting_code.slugFieldValidator && errors.push(this.$t('SlugFieldErrorMessage'));
      !this.$v.contracting_code.required && errors.push(this.$t("This_field_is_required"));
      return errors;
    },
    passwordErrors() {
      const errors = [];
      if (!this.$v.password.$dirty) return errors;
      !this.$v.password.required && errors.push(this.$t("This_field_is_required"));
      return errors;
    },
  },

	watch: {
		visible(newvalue) {
			if (newvalue === true && !this.$store.state.user.csrftoken){
				this.$store.dispatch('user/getCsrf')		
			}
		}
	},
}
</script>
<style scoped>
</style>
