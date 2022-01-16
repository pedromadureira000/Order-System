<template>
  <p v-if="$fetchState.pending">Fetching mountains...</p>
  <p v-else-if="$fetchState.error">An error occurred :(</p>
  <div v-else>
    <div class="ma-3">
      <h3>Create User</h3>
      <form @submit.prevent="createUser">
        <div class="mb-3">
          <v-text-field
            label="Username"
            v-model="username"
            :error-messages="usernameErrors"
            required
            @blur="$v.username.$touch()"
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="Company code"
            v-model="company_code"
            :error-messages="companyCodeErrors"
            required
            @blur="$v.company_code.$touch()"
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="First Name"
            v-model="first_name"
            :error-messages="firstNameErrors"
            required
            @blur="$v.first_name.$touch()"
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="Last Name"
            v-model="last_name"
            :error-messages="lastNameErrors"
            required
            @blur="$v.last_name.$touch()"
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="Email"
            type="email"
            v-model="email"
            :error-messages="emailErrors"
            required
            @blur="$v.email.$touch()"
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="CPF"
            v-model="cpf"
            :error-messages="cpfErrors"
            required
            @blur="$v.cpf.$touch()"
          />
        </div>
        <div class="mb-3">
          <v-text-field
            type="password"
            label="Password"
            v-model="password"
            :error-messages="passwordErrors"
            required
            @blur="$v.password.$touch()"
          />
        </div>
        <div class="mb-3">
          <v-text-field
            type="password"
            label="Password Confirm"
            v-model="password_confirm"
            :error-messages="passConfirmErrors"
            required
            @blur="$v.password_confirm.$touch()"
          />
        </div>
        <h4>User role</h4>
        <v-container
          class="px-0"
          style="display: flex;"
          fluid
        >
          <v-radio-group v-model="userRole" style="width: 25%;">
            <v-radio
              v-if="isAdmin() || isAdminAgent() || haveCreateClientPermissions()"
              label="Client"
              value="client"
            ></v-radio>
            <v-radio
              v-if="isAdmin() || isAdminAgent()"
              label="Agent"
              value="agent"
            ></v-radio>
            <v-radio
              v-if="isAdmin()"
              label="Admin Agent"
              value="admin_agent"
            ></v-radio>
          </v-radio-group>
          <v-container
            class="px-0"
            fluid
            v-if="userRole === 'agent'" 
            style="width: 85%; display: flex; justify-content: space-between;"
          >
            <v-row >
              <v-checkbox 
                v-for="(value, perm) in agentPermissions"
                :key="perm"
                v-model="agentPermissions[perm]"
                :label="perm"
                style="margin-right: 27px;"
              ></v-checkbox>
            </v-row>
          </v-container>
        </v-container>
        <v-btn
          color="primary"
          type="submit"
          :loading="loading"
          :disabled="loading"
          >Submit</v-btn
        >
      </form>

      <h3 class="mt-6">Edit User</h3>
      <v-data-table
        :headers="headers"
        :items="users"
        :items-per-page="10"
        class="elevation-1"
      >
        <template v-slot:top>
        </template>
        <template v-slot:item.actions="{ item }">
          <user-edit-menu :user="item" @user-deleted="deleteUser(item)" />
        </template>
      </v-data-table>
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
  alphaNum,
  integer
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
 
export default {
  middleware: ["authenticated", "admin"],
  components: {
    "user-edit-menu": require("@/components/admin/user-edit-menu.vue").default,
  },
  mixins: [validationMixin],

  data() {
    return {
      username: null,
      company_code: null,
      first_name: null,
      last_name: null,
      email: null,
			cpf: null,
      password: null,
      password_confirm: null,
      loading: false,
      userRole: "client",
      agentPermissions: {
          create_client: false,
          get_clients: false,
          update_client: false,
          delete_client: false,
          create_item: false,
          get_items: false,
          update_item: false,
          delete_item: false,
          create_item_category: false,
          get_item_category: false,
          update_item_category: false,
          delete_item_category: false,
          create_price_table: false,
          get_price_tables: false,
          update_price_table: false,
          delete_price_table: false
      },
      users: [],
      headers: [
        { text: 'Username', value: 'username' },
        { text: 'Complete name', value: 'complete_name' },
        { text: 'Email', value: 'email' },
        { text: 'CPF', value: 'cpf' },
        { text: 'Company', value: 'company' },
        { text: 'Actions', value: 'actions' },
      ]
    };
  },

  async fetch() {
    let users = await this.$store.dispatch("auth/fetchUsersByAdmin");
    for (const user_index in users){
      let user = users[user_index]
      this.users.push({username: user.username, complete_name: `${user.first_name} ${user.last_name}`, 
        email: user.email, cpf: user.cpf, company: user.company.name, company_code: user.company.company_code})
    }
  },

  validations: {
    username: { 
      required, 
      alphaNum, 
      maxLength: maxLength(12)
    },
    company_code: {
      required, 
      integer
    },
    first_name: {
      required,
      maxLength: maxLength(10),
    },
    last_name: {
      required,
      maxLength: maxLength(10),
    },
    email: {
      required,
      email,
    },
    cpf: {  
      required,
      maxLength: maxLength(14),
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
      "company_code",
      "first_name",
      "last_name",
      "email",
      "cpf",
      "password",
      "password_confirm",
    ],
  },

  methods: {
    async createUser() {
      this.$v.userInfoGroup.$touch();
      if (this.$v.userInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: "Please fill the form correctly.", alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let data = await this.$store.dispatch("auth/createUser", {
          username: this.username, 
          company_code: this.company_code,
          first_name: this.first_name,
          last_name: this.last_name,
          email: this.email,
          cpf: this.cpf,
          password: this.password,
          role: this.userRole,
          agentPermissions: this.agentPermissions
        });
        if (data) {
          this.users.push({username: data.username, complete_name: `${data.first_name} ${data.last_name}`, 
            email: data.email, cpf: data.cpf, company: data.company.name, company_code: data.company.company_code})
        }
        this.loading = false;
      }
    },
    deleteUser(userToDelete) {
      this.users = this.users.filter((user) => user.username + "#" + userToDelete.company_code != 
        userToDelete.username + "#" + userToDelete.company_code);
    },
    haveCreateClientPermissions(){
			let user = this.$store.state.auth.currentUser;
      if (user.permissions.includes("create_client" )){return true}
    },
    isAdmin(){
			let user = this.$store.state.auth.currentUser;
      if (user.roles.includes("admin")) {return true}
    },
    isAdminAgent(){
			let user = this.$store.state.auth.currentUser;
      if (user.roles.includes("admin_agent")) {return true}
    }
  },

  computed: {
    usernameErrors() {
      const errors = [];
      if (!this.$v.username.$dirty) return errors;
      !this.$v.username.alphaNum && errors.push("Must have only alphanumeric characters.");
      !this.$v.username.required && errors.push("Username is required");
      !this.$v.username.maxLength && errors.push("This field must have up to 12 characters.");
      return errors;
    },
    companyCodeErrors() {
      const errors = [];
      if (!this.$v.company_code.$dirty) return errors;
      !this.$v.company_code.integer && errors.push("Must be a integer");
      !this.$v.company_code.required && errors.push("Company required");
      return errors;
    },
    firstNameErrors() {
      const errors = [];
      if (!this.$v.first_name.$dirty) return errors;
      !this.$v.first_name.required && errors.push("First name is required.");
      !this.$v.first_name.maxLength &&
        errors.push("This field must have up to 10 characters.");
      return errors;
    },
    lastNameErrors() {
      const errors = [];
      if (!this.$v.last_name.$dirty) return errors;
      !this.$v.last_name.required && errors.push("Last name is required.");
      !this.$v.last_name.maxLength &&
        errors.push("This field must have up to 10 characters.");
      return errors;
    },
    emailErrors() {
      const errors = [];
      if (!this.$v.email.$dirty) return errors;
      !this.$v.email.email && errors.push("Must be valid e-mail");
      !this.$v.email.required && errors.push("E-mail is required");
      return errors;
    },
    cpfErrors() { 
      const errors = [];
      if (!this.$v.cpf.$dirty) return errors;
      !this.$v.cpf.required && errors.push("CPF is required.");
      !this.$v.cpf.maxLength && errors.push("This field must have up to 14 characters.");
      return errors;
    },
    passwordErrors() {
      const errors = [];
      if (!this.$v.password.$dirty) return errors;
      !this.$v.password.required && errors.push("Password is required.");
      !this.$v.password.maxLength &&
        errors.push("This field must have up to 20 characters.");
      !this.$v.password.minLength &&
        errors.push("This field must have at least 6 characters.");
      this.password === this.current_password &&
        errors.push(
          "The password should not be equal to the current password."
        );
      return errors;
    },
    passConfirmErrors() {
      const errors = [];
      if (!this.$v.password_confirm.$dirty) return errors;
      !this.$v.password_confirm.password_confirm &&
        errors.push("Password must be iqual.");
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
