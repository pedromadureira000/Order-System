<template>
  <div class="ma-3">
    <h3>Create User</h3>
    <form @submit.prevent="createCompany">
      <div class="mb-3">
        <v-text-field
          label="Name"
          v-model="name"
          :error-messages="nameErrors"
          required
          @blur="$v.name.$touch()"
        />
      </div>
      <div class="mb-3">
        <v-text-field
          label="CNPJ"
          v-model="cnpj"
          required
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
          label="Status"
          v-model="status"
          required
        />
      </div>
      <div class="mb-3">
        <v-text-field
          label="Company Type"
          v-model="company_type"
          required
        />
      </div>
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
      :items="companies"
      :items-per-page="10"
      class="elevation-1"
    >
      <template v-slot:item.actions="{ item }">
        <user-edit-menu :user="item" @user-deleted="deleteUser(item)" />
      </template>
    </v-data-table>
  </div>
</template>

<script>
import {
  required,
  minLength,
  maxLength,
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
      name: null,
      cnpj: null,
      company_code: null,
      status: null,
      company_type: null,
      loading: false,
      companies: [],
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'CNPJ', value: 'cnpj' },
        { text: 'Company code', value: 'company_code' },
        { text: 'Status', value: 'status' },
        { text: 'Company type', value: 'company_type' },
        { text: 'Actions', value: 'actions' },
      ]
    };
  },

  async fetch() {
    let companies = await this.$store.dispatch("auth/fetchCompanies");
    for (const company_index in companies){
      let company = companies[company_index]
      this.companies.push({name: company.name, cnpj: company.cnpj, company_code: company.company_code,
        status: company.status, company_type: company.company_type})
    }
  },

  validations: {
    name: { 
      required, 
      alphaNum, 
      maxLength: maxLength(12)
    },
    company_code: {
      required, 
      integer
    },
    companyInfoGroup: [
      "name",
      /** "cnpj", */
      "company_code",
      /** "status", */
      /** "company_type", */
      /** "company_code", */
    ],
  },

  methods: {
    async createCompany() {
      this.$v.companyInfoGroup.$touch();
      if (this.$v.companyInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: "Please fill the form correctly.", alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let data = await this.$store.dispatch("auth/createCompany", {
          name: this.name, 
          cnpj: this.cnpj,
          company_code: this.company_code,
          status: this.status,
          company_type: this.company_type
        });
        if (data) {
          this.companies.push(data);
        }
        this.loading = false;
      }
    },
    deleteUser(companyToDelete) {
      this.companies = this.companies.filter((company) => company.company_code != companyToDelete.company_code);
    },
  },

  computed: {
    nameErrors() {
      const errors = [];
      if (!this.$v.name.$dirty) return errors;
      !this.$v.name.alphaNum && errors.push("Must have only alphanumeric characters.");
      !this.$v.name.required && errors.push("Name is required");
      !this.$v.name.maxLength && errors.push("This field must have up to 12 characters.");
      return errors;
    },
    companyCodeErrors() {
      const errors = [];
      if (!this.$v.company_code.$dirty) return errors;
      !this.$v.company_code.integer && errors.push("Must be a integer");
      !this.$v.company_code.required && errors.push("Company code required");
      return errors;
    },
    /** cpfErrors() {  */
      /** const errors = []; */
      /** if (!this.$v.cpf.$dirty) return errors; */
      /** !this.$v.cpf.required && errors.push("CPF is required."); */
      /** !this.$v.cpf.maxLength && errors.push("This field must have up to 14 characters."); */
      /** return errors; */
    /** }, */
  },
};
</script>
<style scoped>
.v-application .mb-3 {
  margin-bottom: 0px !important;
}
</style>
