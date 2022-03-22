<template>
  <div>
     <!-- Menu Items -->
    <v-menu
      bottom
      left
     >
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          icon
          v-bind="attrs"
          v-on="on"
        >
          <v-icon>mdi-dots-vertical</v-icon>
        </v-btn>
      </template>

      <v-list>
        <v-list-item
          @click="show_edit_dialog = true"
          v-if="haveEditClientUserPermission()"
        >
          <v-list-item-icon>
            <v-icon>mdi-pencil</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title v-text="$t('Edit')"></v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item
          @click="show_delete_confirmation_dialog = true"
          v-if="haveDeleteClientUserPermission()"
        >
          <v-list-item-icon>
            <v-icon>mdi-delete</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title v-text="$t('Delete')"></v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-menu>
     <!-- Edit Dialog -->
    <v-dialog v-model="show_edit_dialog" max-width="50%">
      <v-card>
        <v-card-title>{{$t('Edit')}}</v-card-title>
        <v-card-text>
          <v-container fluid>
              <!-- First Name -->
              <v-text-field
                :label="$t('First_name')"
                v-model="first_name"
                :error-messages="firstNameErrors"
                required
                @blur="$v.first_name.$touch()"
              />
              <!-- Last name -->
              <v-text-field
                :label="$t('Last_name')"
                v-model="last_name"
                :error-messages="lastNameErrors"
                required
                @blur="$v.last_name.$touch()"
              />
              <!-- Email -->
              <v-text-field
                label="Email"
                type="email"
                v-model="email"
                :error-messages="emailErrors"
                required
                @blur="$v.email.$touch()"
              />
              <!-- Status -->
              <v-radio-group v-model="status" style="width: 25%;" label='Status' class="mb-3">
                <v-radio
                  :label="$t('Active')"
                  value=1
                ></v-radio>
                <v-radio
                  :label="$t('Disabled')"
                  value=0
                ></v-radio>
              </v-radio-group>
              <!-- Note -->
              <v-text-field
                :label="$t('Note')"
                v-model="note"
                :error-messages="noteErrors"
                @blur="$v.note.$touch()"
                class="mb-3"
              />
              <!-- Password -->
              <!-- <v-text-field -->
                <!-- type="password" -->
                <!-- :label="$t('Password')" -->
                <!-- v-model="password" -->
                <!-- :error-messages="passwordErrors" -->
                <!-- required -->
                <!-- @blur="$v.password.$touch()" -->
              <!-- /> -->
              <!-- Password Confirm -->
              <!-- <v-text-field -->
                <!-- type="password" -->
                <!-- :label="$t('Password_Confirm')" -->
                <!-- v-model="password_confirm" -->
                <!-- :error-messages="passConfirmErrors" -->
                <!-- required -->
                <!-- @blur="$v.password_confirm.$touch()" -->
              <!-- /> -->
          </v-container>
        </v-card-text>
        <v-divider></v-divider>
        <!-- Submit Button -->
        <v-card-actions class="d-flex justify-space-around" style="width:100%;">
          <v-btn class="blue--text darken-1" text @click="show_edit_dialog = false">{{$t('Cancel')}}</v-btn>
          <v-btn class="blue--text darken-1" text @click="updateClientUser()">{{$t('Save')}}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="show_delete_confirmation_dialog" max-width="30%">
      <v-card>
        <v-card-title>{{$t('Are_you_sure_you_want_to_delete')}}</v-card-title>
        <v-card-text class="d-flex justify-center">
          <v-card-actions class="d-flex justify-space-around" style="width:100%;">
            <v-btn class="black--text darken-1" text @click="show_delete_confirmation_dialog = false">{{$t('Cancel')}}</v-btn>
            <v-btn class="red--text darken-1" text @click="deleteClientUser()">{{$t('Delete')}}</v-btn>
          </v-card-actions>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import {
  required,
  /** minLength, */
  maxLength,
  email
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
export default {
  mixins: [validationMixin],
  components: {
    "dots-menu-update-delete": require("@/components/dots-menu-update-delete.vue").default,
  },
  props: ['client_user'],
  data() {
    return {
      show_edit_dialog: false,
      show_delete_confirmation_dialog: false,
      first_name: null,
      last_name: null,
      email: null,
      /** password: null, */
      /** password_confirm: null, */
      status: null,
      note: "",
      loading: false,
    }
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
    note: {
      maxLength: maxLength(800)
    },
    /** password: { */
      /** required, */
      /** minLength: minLength(6), */
      /** maxLength: maxLength(20), */
    /** }, */
    /** password_confirm: { */
      /** password_confirm: sameAs("password"), */
    /** }, */
    clientUserInfoGroup: [
      "first_name",
      "last_name",
      "email",
      "note",
      /** "password", */
      /** "password_confirm", */
    ],
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
      !this.$v.email.email && errors.push(this.$t("Must be valid e-mail"));
      !this.$v.email.required && errors.push(this.$t("This_field_is_required"));      
      return errors;
    },
    noteErrors() {
      const errors = [];
      if (!this.$v.note.$dirty) return errors;
      !this.$v.note.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 800));
      return errors;
    },
    /** passwordErrors() { */
      /** const errors = []; */
      /** if (!this.$v.password.$dirty) return errors; */
      /** !this.$v.password.required && errors.push(this.$t("This_field_is_required")); */
      /** !this.$v.password.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 20)); */
      /** !this.$v.password.minLength && errors.push(this.$formatStr(this.$t("This_field_must_have_at_least_X_characters"), 6)); */
      /** this.password === this.current_password && errors.push(this.$t("Password_must_be_different_from_current_password")) */
      /** return errors; */
    /** }, */
    /** passConfirmErrors() { */
      /** const errors = []; */
      /** if (!this.$v.password_confirm.$dirty) return errors; */
      /** /* !this.$v.password_confirm.required && errors.push("Password is required."); */ 
      /** !this.$v.password_confirm.password_confirm && errors.push(this.$t('password_confirm_does_not_match')); */
      /** return errors; */
    /** }, */
  },

  methods: {
    async updateClientUser(){
      try {
        let data = await this.$store.dispatch("user/updateClientUser", {
          contracting_code: this.client_user.contracting_code,
          username: this.client_user.username,
          first_name: this.first_name,
          last_name: this.last_name,
          email: this.email,
          status: this.status,
          note: this.note,
        })
        console.log(">>>>>>> damn it: ", data)
        // Reactivity for client_user list inside client_user.vue 
        this.client_user.first_name = data.first_name
        this.client_user.last_name = data.last_name
        this.client_user.status = data.status
        this.client_user.email = data.email
        this.client_user.note = data.note
        this.client_user.complete_name =  `${data.first_name} ${data.last_name}`
      } catch(e){
      // error is being handled inside action
      }
    },

    async deleteClientUser(){
      let data = await this.$store.dispatch(
        'user/deleteClientUser', {
          contracting_code: this.client_user.contracting_code,
          username: this.client_user.username
        }
      )
      if (data === "ok"){
        this.$emit('client-user-deleted')
      }

    },

    haveEditClientUserPermission(){
      let user = this.$store.state.user.currentUser;
      return user.permissions.includes("update_client_user")
    },

    haveDeleteClientUserPermission(){
      let user = this.$store.state.user.currentUser;
      return user.permissions.includes("delete_client_user")
    },
  },

  mounted() {
    this.first_name = this.client_user.first_name
    this.last_name = this.client_user.last_name
    this.email = this.client_user.email
    this.status = String(this.client_user.status)
    this.note = this.client_user.note
  }
}
</script>
