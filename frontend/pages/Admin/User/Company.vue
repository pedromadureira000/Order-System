<template>
  <p v-if="$fetchState.pending">Fetching mountains...</p>
  <p v-else-if="$fetchState.error">An error occurred :(</p>
  <div v-else>
    <div class="ma-3">
      <h3>Create Company</h3>
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
            label="Client code"
            v-model="client_code"
            required
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="Vendor code"
            v-model="vendor_code"
            required
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="Note"
            v-model="note"
          />
        </div>
        <h5>Status da empresa</h5>
        <v-radio-group v-model="status" style="width: 25%;">
          <v-radio
            label="Ativado"
            value="A"
          ></v-radio>
          <v-radio
            label="Desativado"
            value="D"
          ></v-radio>
          <v-radio
            label="Bloqueado"
            value="B"
          ></v-radio>
        </v-radio-group>
        <h5>Tipo de empresa</h5>
        <v-radio-group v-model="company_type" style="width: 25%;">
          <v-radio
            v-if="isAdmin()"
            label="Contratante"
            value="C"
          ></v-radio>
          <v-radio
            v-if="isAdmin() || isAdminAgent() || haveCreateClientPermissions()"
            label="Distribuidora"
            value="D"
          ></v-radio>
          <v-radio
            v-if="isAdmin() || isAdminAgent() || haveCreateClientPermissions()"
            label="Logista"
            value="L"
          ></v-radio>
          <v-radio
            v-if="isAdmin() || isAdminAgent() || haveCreateClientPermissions()"
            label="Outros"
            value="O"
          ></v-radio>
        </v-radio-group>
        <v-btn
          color="primary"
          type="submit"
          :loading="loading"
          :disabled="loading"
          >Submit</v-btn
        >
      </form>

      <h3 class="mt-6">Edit Company</h3>
      <v-data-table
        :headers="headers"
        :items="companies"
        :items-per-page="10"
        class="elevation-1"
      >
        <template v-slot:item.actions="{ item }">
          <company-edit-menu :company="item" @company-deleted="deleteComapany(item)" />
        </template>
      </v-data-table>
    </div>
  </div>
</template>

<script>
import {
  required,
  maxLength,
  alphaNum,
  integer
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";

export default {
  middleware: ["authenticated", "admin"],
  components: {
    "company-edit-menu": require("@/components/admin/company-edit-menu.vue").default,
  },
  mixins: [validationMixin],

  data() {
    return {
      name: null,
      cnpj: null,
      company_code: null,
      status: null,
      company_type: null,
      client_code: null,
      vendor_code: null,
      note: null,
      loading: false,
      companies: [],
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'CNPJ', value: 'cnpj' },
        { text: 'Company code', value: 'company_code' },
        { text: 'Status', value: 'status' },
        { text: 'Company type', value: 'company_type' },
        { text: 'Price Table', value: 'price_table' },
        { text: 'Client code', value: 'client_code' },
        { text: 'Vendor code', value: 'vendor_code' },
        { text: 'Note', value: 'note' },
        { text: 'Actions', value: 'actions' },
      ]
    };
  },

  async fetch() {
    let companies = await this.$store.dispatch("auth/fetchCompanies");
    for (const company_index in companies){
      let company = companies[company_index]
      /** this.companies.push({name: company.name, cnpj: company.cnpj, company_code: company.company_code, */
        /** status: company.status, company_type: company.company_type, price_table: company.price_table}) */
    /** } */
      this.companies.push(company)
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
          company_type: this.company_type,
          client_code: this.client_code,
          vendor_code: this.vendor_code,
          note: this.note
        });
        if (data) {
          this.companies.push(data);
        }
        this.loading = false;
      }
    },
    deleteComapany(companyToDelete) {
      this.companies = this.companies.filter((company) => company.company_code != companyToDelete.company_code);
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
