<template>
  <div>
     <!-- Change Password Dialog -->
    <v-dialog :retain-focus="false" :value="show_change_password_dialog" max-width="30%" persistent>
      <!-- Once in using :value insted of v-model i need to user 'persistent' prop -->
      <v-card>
        <v-card-title>{{$t('Change_Password')}}</v-card-title>
        <v-card-text>
          <v-container fluid>
              <!-- Password -->
              <v-text-field
                type="password"
                :label="$t('Password')"
                v-model="password"
                :error-messages="passwordErrors"
                required
                @blur="$v.password.$touch()"
              />
              <!-- Password Confirm -->
              <v-text-field
                type="password"
                :label="$t('Password_Confirm')"
                v-model="password_confirm"
                :error-messages="passConfirmErrors"
                required
                @blur="$v.password_confirm.$touch()"
              />
          </v-container>
        </v-card-text>
        <v-divider></v-divider>
        <!-- Submit Button -->
        <v-card-actions class="d-flex justify-space-around" style="width:100%;">
          <v-btn class="blue--text darken-1" text @click="closeDialog">{{$t('Cancel')}}</v-btn>
          <v-btn 
            class="blue--text darken-1" 
            text 
            @click="changeUsersPassword()"
            :loading="loading_password"
            :disabled="loading_password"
          >{{$t('Save')}}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import {
  required,
  sameAs,
  minLength,
  maxLength,
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
export default {
  name: "change_users_password",
  mixins: [validationMixin],
  props: ['user', 'show_change_password_dialog'],
  data() {
    return {
      password: null,
      password_confirm: null,
      loading_password: false,
    }
  },

  validations: {
    password: {
      required,
      minLength: minLength(6),
      maxLength: maxLength(20),
    },
    password_confirm: {
      password_confirm: sameAs("password"),
    },
    userPasswordGroup: [
      "password",
      "password_confirm",
    ]
  },

  computed: {
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
      !this.$v.password_confirm.password_confirm && errors.push(this.$t('password_confirm_does_not_match'));
      return errors;
    },
  },

  methods: {
    async changeUsersPassword() {
      this.$v.userPasswordGroup.$touch();
      if (this.$v.userPasswordGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
      } else {
        this.loading_password = true;
        
        let success = await this.$store.dispatch('user/updateUserPassword', {username: this.user.username, contracting_code: this.user.contracting_code, password: this.password})
        if (success === 'ok'){
          this.$emit('hide-change-password-dialog')
        }
        this.loading_password = false;
        // Clearing fields
        this.password = ""
        this.password_confirm = ""
        this.$v.$reset()
      }
    },
    closeDialog(){
      this.$emit('hide-change-password-dialog')
      // Clearing fields
      this.password = ""
      this.password_confirm = ""
      this.$v.$reset()
    }
  },

  /** mounted() { */
  /** } */
}
</script>
