<template>
  <div>
    <dots-menu :menu_items="menu_items" :handleClick="handleClick"/>
     <!-- Edit Dialog -->
    <v-dialog :retain-focus="false" v-model="show_edit_dialog" max-width="50%">
      <v-card>
        <v-card-title>{{$t('Edit')}}</v-card-title>
        <v-card-text>
          <v-container fluid>
              <!-- Client -->
              <v-row align="center">
                <v-col
                  class="d-flex"
                  cols="12"
                  sm="6"
                >
                  <v-select
                    disabled
                    :label="$t('Client')"
                    :items="clients"
                    :item-text="(x) =>  x.client_code + ' - ' + x.name"
                    v-model="client_from_client_user"
                  ></v-select>
                </v-col>
              </v-row>
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
              <v-textarea
                outlined
                :label="$t('Note')"
                v-model="note"
                :error-messages="noteErrors"
                @blur="$v.note.$touch()"
                class="mb-3"
              />
          </v-container>
        </v-card-text>
        <v-divider></v-divider>
        <!-- Submit Button -->
        <v-card-actions class="d-flex justify-space-around" style="width:100%;">
          <v-btn class="blue--text darken-1" text @click="show_edit_dialog = false">{{$t('Cancel')}}</v-btn>
          <v-btn 
            class="blue--text darken-1" 
            text 
            @click="updateClientUser()"
            :loading="loading"
            :disabled="loading"
          >{{$t('Save')}}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- Delete Confirmation Dialog -->
    <delete-confirmation-dialog 
      @delete-item="deleteClientUser" 
      @cancel="show_delete_confirmation_dialog = false" 
      :show_delete_confirmation_dialog="show_delete_confirmation_dialog"
    />

     <!-- Change Password Dialog -->
    <change-users-password 
      :user="client_user" 
      :show_change_password_dialog="show_change_password_dialog" 
      @hide-change-password-dialog="show_change_password_dialog = false"
    />
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
    "dots-menu": require("@/components/dots-menu.vue").default,
    "change-users-password": require("@/components/admin/user/change-users-password.vue").default,
    "delete-confirmation-dialog": require("@/components/delete-confirmation-dialog.vue").default,
  },
  props: ['client_user', 'clients'],
  data() {
    return {
      client_from_client_user: null,
      show_edit_dialog: false,
      show_delete_confirmation_dialog: false,
      first_name: null,
      last_name: null,
      email: null,
      status: null,
      note: "",
      loading: false,
      show_change_password_dialog: false,
      menu_items: [
      ...(this.hasUpdateClientUserPermission() ? [{ 
          title: this.$t('Edit'),
          icon: 'mdi-pencil',
          async click(){
            this.show_edit_dialog = true
          }
        }] : [] ),
        ...(this.hasDeleteClientUserPermission() ? [{ 
          title: this.$t('Delete'),
          icon: 'mdi-delete',
          async click(){
            this.show_delete_confirmation_dialog = true
          }
        }] : []),
      ...(this.hasUpdateClientUserPermission() ? [{ 
          title: this.$t('Change_Password'),
          icon: 'mdi-lock',
          async click(){
            this.show_change_password_dialog = true
          }
        }] : [] ),
      ]
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
    clientUserInfoGroup: [
      "first_name",
      "last_name",
      "email",
      "note",
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
  },

  methods: {
    handleClick(index){
      //this.menu_items[id].click()  #will get errors because the function click will not access properties with its own 'this'
      this.menu_items[index].click.call(this) // will call the function but the function will use the vue instance 'this' context.
    },

    async updateClientUser(){
      this.$v.clientUserInfoGroup.$touch();
      if (this.$v.clientUserInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let data = await this.$store.dispatch("user/updateClientUser", {
          contracting_code: this.client_user.contracting_code,
          username: this.client_user.username,
          first_name: this.first_name,
          last_name: this.last_name,
          email: this.email,
          status: this.status,
          note: this.note,
        })
        this.loading = false;
        if (data){
          // Reactivity for client_user list inside client_user.vue 
          this.client_user.first_name = data.first_name
          this.client_user.last_name = data.last_name
          this.client_user.status = data.status
          this.client_user.email = data.email
          this.client_user.note = data.note
          this.client_user.complete_name =  `${data.first_name} ${data.last_name}`
            // Close dialog
          this.show_edit_dialog = false
        }
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

    hasUpdateClientUserPermission(){
      let user = this.$store.state.user.currentUser;
      return user.permissions.includes("update_client_user")
    },

    hasDeleteClientUserPermission(){
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
    /** defauld value for client_from_client_user */
    let client = this.clients.find(el=>el.client_compound_id === this.client_user.client)
    this.client_from_client_user = client.client_code + ' - ' + client.name
  }
}
</script>
