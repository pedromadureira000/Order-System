<template>
  <div>
     <!-- Menu Items -->
    <dots-menu-update-delete :menu_items="menu_items" :handleClick="handleClick"/>
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

              <!-- Agent Permissions -->
              <v-expansion-panels class="mb-5">
                <v-expansion-panel>
                  <v-expansion-panel-header>{{$t('Agent Permissions')}}</v-expansion-panel-header>
                  <v-expansion-panel-content
                    class="px-0 mb-2"
                    fluid
                    style="display: flex; justify-content: space-between;"
                  >
                    <v-checkbox 
                      :label="$t('Select all')"
                      style="margin-right: 27px;"
                      @change="selectAllPermissions"
                      v-model="select_all_permissions"
                    ></v-checkbox>
                    <v-divider class="mt-2 mb-4"></v-divider>
                    <v-row
                      class="px-0 mb-2"
                      fluid
                      style="display: flex; justify-content: space-around;"
                    >
                      <v-checkbox 
                        v-for="(value, key) in agentPermissions"
                        :key="key"
                        v-model="permissions"
                        :value="value"
                        :label="$t(value)"
                      ></v-checkbox>
                    </v-row>
                  </v-expansion-panel-content>
                </v-expansion-panel>
              </v-expansion-panels>
              <!-- Agent Establishments -->
              <v-expansion-panels class="mb-5">
                <v-expansion-panel>
                  <v-expansion-panel-header>{{$t('Agent Establishments')}}</v-expansion-panel-header>
                    <v-expansion-panel-content>
                      <v-checkbox 
                        :label="$t('Select all')"
                        style="margin-right: 27px;"
                        @change="selectAllEstablishments"
                        v-model="select_all_establishments"
                      ></v-checkbox>
                      <v-divider class="mt-2 mb-4"></v-divider>
                      <v-container
                        v-for="establishment in establishments"
                        :key="establishment.establishment_compound_id"
                        class="grey lighten-5 mb-6"
                      >
                        <v-row align="center" class="ml-1 mt-0">
                          <v-col>
                            <v-checkbox
                              :label="establishment.establishment_code + ' - ' + establishment.name + ' (' + $t('Company') + ': ' + establishment.company + ')'"
                              v-model="agent_establishments"
                              :value='establishment.AUX_agent_estab'
                              hide-details
                              class="shrink mr-2 mt-0"
                            ></v-checkbox>
                          </v-col>
                        </v-row>
                      </v-container>
                    </v-expansion-panel-content>
                </v-expansion-panel>
              </v-expansion-panels>
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
            @click="updateAgent()"
            :loading="loading"
            :disabled="loading"
          >{{$t('Save')}}</v-btn>
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
            <v-btn class="red--text darken-1" text @click="deleteAgent()">{{$t('Delete')}}</v-btn>
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
  props: ['agent', 'establishments'],
  data() {
    return {
      select_all_permissions: false,
      select_all_establishments: false,
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
      agent_establishments: [],
      permissions: [],
      agentPermissions: [
          "access_all_establishments",
          "create_client",
          "get_clients",
          "update_client",
          "delete_client",
          "create_client_user",
          "get_client_users",
          "update_client_user",
          "delete_client_user",
          "create_item",
          "get_items",
          "update_item",
          "delete_item",
          "create_item_category",
          "get_item_category",
          "update_item_category",
          "delete_item_category",
          "create_price_table",
          "get_price_tables",
          "update_price_table",
          "delete_price_table",
          "get_orders",
          "update_order_status"
      ],
      menu_items: [
        { 
          title: this.$t('Edit'),
          icon: 'mdi-pencil',
          async click(){
            this.show_edit_dialog = true
          }
        },
        { 
          title: this.$t('Delete'),
          icon: 'mdi-delete',
          async click(){
            this.show_delete_confirmation_dialog = true
          }
        },
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
    /** password: { */
      /** required, */
      /** minLength: minLength(6), */
      /** maxLength: maxLength(20), */
    /** }, */
    /** password_confirm: { */
      /** password_confirm: sameAs("password"), */
    /** }, */
    agentInfoGroup: [
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
    handleClick(index){
      //this.menu_items[id].click()  #will get errors because the function click will not access properties with its own 'this'
      this.menu_items[index].click.call(this) // will call the function but the function will use the vue instance 'this' context.
    },

    async updateAgent(){
      this.$v.agentInfoGroup.$touch();
      if (this.$v.agentInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let data = await this.$store.dispatch("user/updateAgent", {
          agent_establishments: this.agent_establishments,
          permissions: this.permissions,
          contracting_code: this.agent.contracting_code,
          username: this.agent.username,
          first_name: this.first_name,
          last_name: this.last_name,
          email: this.email,
          status: this.status,
          note: this.note,
        })
        this.loading = false;
        if (data){
          // Reactivity for agent list inside agent.vue 
          this.agent.first_name = data.first_name
          this.agent.last_name = data.last_name
          this.agent.status = data.status
          this.agent.email = data.email
          this.agent.note = data.note
          this.agent.complete_name =  `${data.first_name} ${data.last_name}`
            // Close dialog
          this.show_edit_dialog = false
        }
      }
    },

    async deleteAgent(){
      let data = await this.$store.dispatch(
        'user/deleteAgent', {
          contracting_code: this.agent.contracting_code,
          username: this.agent.username
        }
      )
      if (data === "ok"){
        this.$emit('agent-deleted')
      }
    },

    defaultSelectAllPermissions(){
      if (this.permissions.length === this.agentPermissions.length){
        return true
      }
      else {
        return false
      }
    },

    selectAllPermissions(){
      if (this.permissions.length === this.agentPermissions.length){
        this.permissions = []
      }
      else {
        this.permissions = this.agentPermissions
      }
    },

    selectAllEstablishments(){
      let all_agent_estabs = this.establishments.map(el=>el.AUX_agent_estab)
      if (this.agent_establishments.length === all_agent_estabs.length){
        this.agent_establishments = []
      }
      else{
        this.agent_establishments = all_agent_estabs
      }
    }
  },

  mounted() {
    this.permissions = this.agent.permissions
    // Add AUX_agent_estab in this.agent_establishments
    for (let key in this.establishments){
      let estab = this.establishments[key]
      if (this.agent.agent_establishments.some(el=>el.establishment===estab.AUX_agent_estab.establishment)){
        this.agent_establishments.push(estab.AUX_agent_estab)
      }
    }
    console.log(">>>>>>> this.agent_establishments: ", this.agent_establishments)
    this.first_name = this.agent.first_name
    this.last_name = this.agent.last_name
    this.email = this.agent.email
    this.status = String(this.agent.status)
    this.note = this.agent.note

    // Default value for access_all_permissions
    this.select_all_permissions = this.permissions.length === this.agentPermissions.length ? true : false

    // Default value for select_all_establishments
    let all_agent_estabs = this.establishments.map(el=>el.AUX_agent_estab)
    this.select_all_establishments = this.agent_establishments.length === all_agent_estabs.length ? true : false
  }
}
</script>
