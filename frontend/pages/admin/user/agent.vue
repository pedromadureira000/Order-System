<template>
  <p v-if="$fetchState.pending">{{$t('Fetching_data')}}</p>
  <p v-else-if="$fetchState.error">{{$t('Error_fetching_data')}}</p>
  <div v-else>
    <div class="ma-3">
      <h3>{{$t('Create User')}}</h3>
      <form @submit.prevent="createUser">
        <!-- Agent Permissions -->
        <v-container
          class="px-0"
          style="display: flex;"
          fluid
        >
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
            label="First Name"
            v-model="first_name"
            :error-messages="firstNameErrors"
            required
            @blur="$v.first_name.$touch()"
          />
          <!-- Last name -->
          <v-text-field
            label="Last Name"
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
          <!-- Note -->
          <v-text-field
            :label="$t('Note')"
            v-model="note"
            :error-messages="noteErrors"
            @blur="$v.note.$touch()"
            class="mb-3"
          />
          <!-- Password -->
          <v-text-field
            type="password"
            label="Password"
            v-model="password"
            :error-messages="passwordErrors"
            required
            @blur="$v.password.$touch()"
          />
          <!-- Password Confirm -->
          <v-text-field
            type="password"
            label="Password Confirm"
            v-model="password_confirm"
            :error-messages="passConfirmErrors"
            required
            @blur="$v.password_confirm.$touch()"
          />
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
        item-key="username"
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
  middleware: ["authenticated"],
  components: {
    "user-edit-menu": require("@/components/admin/user/user-edit-menu.vue").default,
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
      loading: false,
      note: "",
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
      companies: [],
      headers: [
        { text: 'Username', value: 'username' },
        { text: 'Complete name', value: 'complete_name' },
        { text: 'Email', value: 'email' },
        { text: 'Note', value: 'note' },
        { text: 'Actions', value: 'actions' },
      ]
    };
  },

  async fetch() {
    // Fetch users
    let users = await this.$store.dispatch("user/fetchUsersByAdmin");
    for (const user_index in users){
      let user = users[user_index]
      this.users.push({...user, complete_name: `${user.first_name} ${user.last_name}`, role:user.roles[0]})
    }

    // Fetch client option
    /** let clients = await this.$store.dispatch("organization/fetchClientsToCreateClientUser"); */
    /** this.clients.push(...clients) */
  },

  validations: {
    username: { 
      required, 
      alphaNum, 
      maxLength: maxLength(12)
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
      "password",
      "note",
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
        let data = await this.$store.dispatch("user/createUser", {
          username: this.username, 
          first_name: this.first_name,
          last_name: this.last_name,
          email: this.email,
          status: 1,
          password: this.password,
          role: "",
          agentPermissions: this.agentPermissions
        });
        if (data) {
          this.users.push({...data, complete_name: `${data.first_name} ${data.last_name}`, role: data.roles[0]})
        }
        this.loading = false;
      }
    },
    deleteUser(userToDelete) {
      this.users = this.users.filter((user) => user.user_code != 
        userToDelete.user_code);
    },
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
    noteErrors() {
      const errors = [];
      if (!this.$v.note.$dirty) return errors;
      !this.$v.note.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 800));
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
