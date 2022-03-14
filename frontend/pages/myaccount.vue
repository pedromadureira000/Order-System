<template>
  <div>
    <div class="ma-3">
      <h3>{{$t('Update_Account_Information')}}</h3>
      <form @submit.prevent="updateCurrentUserProfile">
        <div class="mb-3">
          <v-text-field
            :label="$t('First_Name')"
            v-model="first_name"
            :error-messages="firstNameErrors"
            required
            @blur="$v.first_name.$touch()"
          />
        </div>
        <div class="mb-3">
          <v-text-field
            :label="$t('Last_Name')"
            v-model="last_name"
            :error-messages="lastNameErrors"
            required
            @blur="$v.last_name.$touch()"
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="Email"
            v-model="email"
            :error-messages="emailErrors"
            required
            @blur="$v.email.$touch()"
          />
        </div>
        <!-- <div class="mb-3"> -->
          <!-- <v-text-field -->
            <!-- label="CPF" -->
            <!-- v-model="cpf" -->
            <!-- :error-messages="cpfErrors" -->
            <!-- required -->
            <!-- @blur="$v.cpf.$touch()" -->
          <!-- /> -->
        <!-- </div> -->
        <v-btn 
          color="primary"
          type="submit"
          :loading="loading_profile"
          :disabled="loading_profile"
        >{{$t('Save')}}</v-btn>
      </form>

      <h3 class="mt-4">{{$t('Change_Password')}}</h3>
      <p class="caption">{{$t('After_change_your_password_you_will_be_logged_out')}}</p>

      <form @submit.prevent="passwordSubmit">
        <div class="mb-3">
          <v-text-field
            type="password"
            :label="$t('Current_password')"
            v-model="current_password"
            :error-messages="currentPassErrors"
            required
            @blur="$v.current_password.$touch()"
          />
        </div>
        <div class="mb-3">
          <v-text-field
            type="password"
            :label="$t('Password')"
            v-model="password"
            :error-messages="passwordErrors"
            required
            @blur="$v.password.$touch()"
          />
        </div>
        <div class="mb-3">
          <v-text-field
            type="password"
            :label="$t('Password_Confirm')"
            v-model="password_confirm"
            :error-messages="passConfirmErrors"
            required
            @blur="$v.password_confirm.$touch()"
          />
        </div>
        <v-btn 
          color="primary" 
          type="submit"
          :loading="loading_password"
          :disabled="loading_password"
        >{{$t('Save')}}</v-btn>
      </form>
    </div>
  </div>
</template>

<script>
import {
  required,
  sameAs,
  minLength,
  maxLength,
  email
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
/** import {cpfFieldValidator} from "~/helpers/validators" */

export default {
	middleware: ['authenticated'],
  mixins: [validationMixin],

  data() {
    return {
			first_name: this.$store.state.user.currentUser.first_name,
			last_name: this.$store.state.user.currentUser.last_name,
			email: this.$store.state.user.currentUser.email,
			/** cpf: this.$store.state.user.currentUser.cpf, */
      current_password: "",
      password: "",
      password_confirm: "",
      loading_password: false,
      loading_profile: false,
    };
  },

  validations: {
    first_name: {
      required,
      maxLength: maxLength(50),
    },
    last_name: {
      required,
      maxLength: maxLength(50),
    },
    email: {
      required,
      email,
    },
    /** cpf: {   */
      /** required, */
      /** cpfFieldValidator */
    /** }, */
    current_password: {
      required,
      minLength: minLength(6),
      maxLength: maxLength(20),
    },
    password: {
      required,
      minLength: minLength(6),
      maxLength: maxLength(20),
    },
    password_confirm: {
      password_confirm: sameAs("password"),
    },
    profileGroup: ["first_name", "last_name", "email"],
    passwordUpdateGroup: ["current_password","password", "password_confirm"],
  },

  methods: {
    async updateCurrentUserProfile() {
      this.$v.profileGroup.$touch();
      if (this.$v.profileGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
      } else {
        if (
          this.first_name === this.$store.state.user.currentUser.first_name &&
          this.last_name === this.$store.state.user.currentUser.last_name &&
          this.email === this.$store.state.user.currentUser.email
          /** && this.cpf === this.$store.state.user.currentUser.cpf */
        ){ this.$store.dispatch('setAlert', {message: this.$t('You_have_not_changed_any_fields'), alertType: 'warning'}, { root: true }) }
        else {
          this.loading_profile = true;
          await this.$store.dispatch('user/updateCurrentUserProfile', {
            first_name: this.first_name,
            last_name: this.last_name,
            email: this.email,
            /** cpf: this.cpf */
          })
          this.loading_profile = false;
        }	
      }
    },
    async passwordSubmit() {
      this.$v.passwordUpdateGroup.$touch();
      if (this.$v.passwordUpdateGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
      } else {
        this.loading_password = true;
        await this.$store.dispatch('user/updatePassword', {password: this.password, current_password: this.current_password})
        this.loading_password = false;
      }
    },
  },
  computed: {
    firstNameErrors() {
      const errors = [];
      if (!this.$v.first_name.$dirty) return errors;
      !this.$v.first_name.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.first_name.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 50));
      return errors;
    },
    lastNameErrors() {
      const errors = [];
      if (!this.$v.last_name.$dirty) return errors;
      !this.$v.last_name.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.last_name.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 50));
      return errors;
    },
    emailErrors() {
      const errors = [];
      if (!this.$v.email.$dirty) return errors;
      !this.$v.email.email && errors.push("Must be valid e-mail");
      !this.$v.email.required && errors.push(this.$t("This_field_is_required"));      
      return errors;
    },
    /** cpfErrors() {  */
      /** const errors = []; */
      /** if (!this.$v.cpf.$dirty) return errors; */
      /** !this.$v.cpf.required && errors.push(this.$t("This_field_is_required")); */
      /** !this.$v.cpf.cpfFieldValidator && errors.push(this.$t("cfp_validation_error")); */
      /** return errors; */
    /** }, */
    currentPassErrors() {
      const errors = [];
      if (!this.$v.current_password.$dirty) return errors;
      !this.$v.current_password.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.current_password.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 20));
      !this.$v.current_password.minLength && errors.push(this.$formatStr(this.$t("This_field_must_have_at_least_X_characters"), 6));
      return errors;
    },
    passwordErrors() {
      const errors = [];
      if (!this.$v.password.$dirty) return errors;
      !this.$v.password.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.password.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 20));
      !this.$v.password.minLength && errors.push(this.$formatStr(this.$t("This_field_must_have_at_least_X_characters"), 6));
      this.password === this.current_password && errors.push(this.$t("Password_must_be_different_from_current_password"))
      return errors;
    },
    passConfirmErrors() {
      const errors = [];
      if (!this.$v.password_confirm.$dirty) return errors;
      /* !this.$v.password_confirm.required && errors.push("Password is required."); */
      !this.$v.password_confirm.password_confirm && errors.push(this.$t('password_confirm_does_not_match'));
      return errors;
    },
  }
}
</script>
<style scoped>
.v-application .mb-3 {
    margin-bottom: 0px !important;
}
</style>
