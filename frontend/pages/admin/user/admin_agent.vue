<template>
  <p v-if="$fetchState.pending">{{$t('Fetching_data')}}</p>
  <p v-else-if="$fetchState.error">{{$t('Error_fetching_data')}}</p>
  <div v-else>
    <div class="ma-3">
      <v-expansion-panels>
        <v-expansion-panel>
          <v-expansion-panel-header>
            <h3>{{$t('Create Admin Agent')}}</h3>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <form @submit.prevent="createUser">
              <!-- Username -->
                <v-text-field
                  label="Username"
                  v-model.trim="username"
                  :error-messages="usernameErrors"
                  required
                  @blur="$v.username.$touch()"
                />
                <!-- First Name -->
                <v-text-field
                  :label="$t('First_name')"
                  v-model.trim="first_name"
                  :error-messages="firstNameErrors"
                  required
                  @blur="$v.first_name.$touch()"
                />
                <!-- Last name -->
                <v-text-field
                  :label="$t('Last_name')"
                  v-model.trim="last_name"
                  :error-messages="lastNameErrors"
                  required
                  @blur="$v.last_name.$touch()"
                />
                <!-- Email -->
                <v-text-field
                  label="Email"
                  type="email"
                  v-model.trim="email"
                  :error-messages="emailErrors"
                  required
                  @blur="$v.email.$touch()"
                />
                <!-- Password -->
                <v-text-field
                  type="password"
                  :label="$t('Password')"
                  v-model.trim="password"
                  :error-messages="passwordErrors"
                  required
                  @blur="$v.password.$touch()"
                />
                <!-- Password Confirm -->
                <v-text-field
                  type="password"
                  :label="$t('Password_Confirm')"
                  v-model.trim="password_confirm"
                  :error-messages="passConfirmErrors"
                  required
                  @blur="$v.password_confirm.$touch()"
                />
                <!-- Note -->
                <v-textarea
                  outlined
                  :label="$t('Note')"
                  v-model.trim="note"
                  :error-messages="noteErrors"
                  @blur="$v.note.$touch()"
                  class="mb-3"
                />
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
        <h3 class="mt-6">{{$t('Edit Admin Agent')}}</h3>
        <v-data-table
          :headers="headers"
          :items="admin_agents"
          :items-per-page="10"
          item-key="username"
          class="elevation-1 mt-3"
        >
          <template v-slot:item.actions="{ item }">
            <admin-agent-edit-menu :admin_agent="item" @admin-agent-deleted="deleteAdminAgent(item)" />
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
    "admin-agent-edit-menu": require("@/components/admin/user/admin-agent-edit-menu.vue").default,
  },
  mixins: [validationMixin],

  data() {
    return {
      username: null,
      first_name: null,
      last_name: null,
      email: null,
      password: null,
      password_confirm: null,
      note: "",
      admin_agents: [],
      contracting_companies: [],
      loading: false,
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
    // Fetch admin_agents
    let admin_agents = await this.$store.dispatch("user/fetchAdminAgents");
    if (admin_agents) {
      for (const user_index in admin_agents){
        let user = admin_agents[user_index]
        this.admin_agents.push({...user, complete_name: `${user.first_name} ${user.last_name}`})
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
        let data = await this.$store.dispatch("user/createAdminAgent", {
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
          this.admin_agents.push({...data, complete_name: `${data.first_name} ${data.last_name}`})
          // Clearing fields
          this.$v.$reset()
          // this avoid "This field is required" errors by vuelidate
          this.username = ""
          this.first_name = ""
          this.last_name = ""
          this.email = ""
          this.status = "1"
          this.note = ""
          this.password = ""
          this.password_confirm = ""
        }
        this.loading = false;
      }
    },
    deleteAdminAgent(agentToDelete) {
      this.admin_agents = this.admin_agents.filter((user) => user.username != agentToDelete.username);
    },

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
