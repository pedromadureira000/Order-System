<template>
  <p v-if="$fetchState.pending">{{$t('Fetching_data')}}</p>
  <p v-else-if="$fetchState.error">{{$t('Error_fetching_data')}}</p>
  <div v-else>
    <div class="ma-3">
      <v-expansion-panels>
        <v-expansion-panel>
          <v-expansion-panel-header>
            <h3>{{$t('Create Agent')}}</h3>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <form @submit.prevent="createUser">
              <!-- Username -->
              <v-text-field
                label="Username"
                v-model="username"
                :error-messages="usernameErrors"
                required
                @blur="$v.username.$touch()"
              />
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
                    ></v-checkbox>
                    <v-divider class="mt-2 mb-4"></v-divider>
                    <v-row
                      class="px-0 mb-2"
                      fluid
                      style="display: flex; justify-content: space-between;"
                    >
                      <v-checkbox 
                        v-for="(value, key) in agentPermissions"
                        :key="key"
                        v-model="permissions"
                        :value="value"
                        :label="$t(value)"
                        style="margin-right: 27px;"
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
              <!-- Submit Buttom -->
              <v-btn
                color="primary"
                type="submit"
                :loading="loading"
                :disabled="loading"
                >{{$t('Submit')}}</v-btn
              >
            </form>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>

      <div>
        <h3 class="mt-6">{{$t('Edit Agent')}}</h3>
        <v-data-table
          :headers="headers"
          :items="agents"
          :items-per-page="10"
          item-key="username"
          class="elevation-1 mt-3"
        >
          <template v-slot:top>
          </template>
          <template v-slot:item.actions="{ item }">
            <agent-edit-menu :agent="item" :establishments="establishments" @agent-deleted="deleteAgent(item)" />
          </template>
          <template v-slot:item.status="{ item }">
            <p>{{item.status === 1 ? $t('Active') : $t('Disabled')}}</p>
          </template>
          <template v-slot:item.note="{ item }">
            <p>{{$getNote(item.note)}}</p>
          </template>
        </v-data-table>
      </div>
    </div>
  </div>
</template>

<script>
import {
  required,
  sameAs,
  minLength,
  maxLength,
  email,
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
import {slugFieldValidator} from "~/helpers/validators"
 
export default {
  middleware: ["authenticated"],
  components: {
    "agent-edit-menu": require("@/components/admin/user/agent-edit-menu.vue").default,
  },
  mixins: [validationMixin],

  data() {
    return {
      username: null,
      client: null,
      first_name: null,
      last_name: null,
      email: null,
      password: null,
      password_confirm: null,
      note: "",
      agents: [],
      establishments: [],
      agent_establishments: [],
      loading: false,
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
      headers: [
        { text: 'Username', value: 'username' },
        { text: this.$t('Complete name'), value: 'complete_name' },
        { text: 'Email', value: 'email' },
        { text: 'Status', value: 'status'},
        { text: this.$t('Note'), value: 'note' },
        { text: this.$t('Actions'), value: 'actions' },
      ]
    };
  },

  async fetch() {
    // Fetch agents
    let agents = await this.$store.dispatch("user/fetchAgents");
    if (agents) {
      for (const user_index in agents){
        let user = agents[user_index]
        this.agents.push({...user, complete_name: `${user.first_name} ${user.last_name}`})
      }
    }
    // Fetch establishment option
    let establishments = await this.$store.dispatch("user/fetchEstablishmentsToCreateAgent");
    // Create AUX_agent_estab to user in agent-edit-menu
    if (establishments){
      for (let key in establishments) {
        let estab = establishments[key]
        estab.AUX_agent_estab = {establishment: estab.establishment_compound_id}
        this.establishments.push(estab)
      }
    }
  },

  validations: {
    username: { 
      required, 
      slugFieldValidator, 
      maxLength: maxLength(50)
    },
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
    password: {
      required,
      minLength: minLength(6),
      maxLength: maxLength(20),
    },
    password_confirm: {
      password_confirm: sameAs("password"),
    },
    userInfoGroup: [
      "username",
      "first_name",
      "last_name",
      "email",
      "note",
      "password",
      "password_confirm",
    ],
  },

  methods: {
    async createUser() {
      this.$v.userInfoGroup.$touch();
      if (this.$v.userInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let data = await this.$store.dispatch("user/createAgent", {
          agent_establishments: this.agent_establishments,
          permissions: this.permissions,
          username: this.username, 
          first_name: this.first_name,
          last_name: this.last_name,
          email: this.email,
          password: this.password,
          note: this.note,
          status: 1,
          note: this.note,
        });
        if (data) {
          this.agents.push({...data, complete_name: `${data.first_name} ${data.last_name}`})
          // Clearing fields
          this.$v.$reset()
          // this avoid "This field is required" errors by vuelidate
          this.agent_establishments = []
          this.permissions = []
          this.username = ""
          this.first_name = ""
          this.last_name = ""
          this.email = ""
          this.status = "1"
          this.password = ""
          this.password_confirm = ""
          this.note = ""
        }
        this.loading = false;
      }
    },

    deleteAgent(agentToDelete) {
      this.agents = this.agents.filter((agent) => agent.username != agentToDelete.username);
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

  computed: {
    usernameErrors() {
      const errors = [];
      if (!this.$v.username.$dirty) return errors;
      !this.$v.username.slugFieldValidator && errors.push(this.$t('SlugFieldErrorMessage'));
      !this.$v.username.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 50));
      !this.$v.username.required && errors.push(this.$t("This_field_is_required"));
      return errors;
    },
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
  },
};
</script>
<style scoped>
.v-application .mb-3 {
  margin-bottom: 0px !important;
}
</style>
