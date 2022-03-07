<template>
  <p v-if="$fetchState.pending">Fetching data ...</p>
  <p v-else-if="$fetchState.error">An error occurred :(</p>
  <div v-else>
    <div class="ma-3">
      <h3>Create Company</h3>
      <form @submit.prevent="createCompany">
        <!-- Name -->
        <v-text-field
          label="Name"
          v-model="name"
          :error-messages="nameErrors"
          required
          @blur="$v.name.$touch()"
          class="mb-3"
        />
        <!-- Company Code -->
        <v-text-field
          label="Company code"
          v-model="company_code"
          :error-messages="companyCodeErrors"
          required
          @blur="$v.company_code.$touch()"
          class="mb-3"
        />
        <!-- Root of CNPJ -->
        <v-text-field
          label="Root of CNPJ"
          v-model="cnpj_root"
          required
          :error-messages="cnpjRootErrors"
          @blur="$v.cnpj_root.$touch()"
          class="mb-3"
        />
        <!-- Client table -->
        <v-radio-group v-model="client_table" style="width: 25%;" label="Client table" class="mb-3">
          <v-radio
            v-for="(client_table, key) in client_tables"
            :key="key"
            :label="client_table.description"
            :value="client_table.client_table_compound_id"
          ></v-radio>
          <v-radio
            label="None"
            value=""
          ></v-radio>
        </v-radio-group>
        <!-- Item table -->
        <v-radio-group v-model="item_table" style="width: 25%;" label="Item table" class="mb-3">
          <v-radio
            v-for="(item_table, key) in item_tables"
            :key="key"
            :label="item_table.description"
            :value="item_table.item_table_compound_id"
          ></v-radio>
          <v-radio
            label="None"
            value=""
          ></v-radio>
        </v-radio-group>
        <!-- Company Status -->
        <v-radio-group v-model="status" style="width: 25%;" label="Company Company Status" class="mb-3">
          <v-radio
            label="Active"
            value=1
          ></v-radio>
          <v-radio
            label="Disabled"
            value=0
          ></v-radio>
        </v-radio-group>
        <!-- Note -->
        <v-text-field
          label="Note"
          v-model="note"
          :error-messages="noteErrors"
          @blur="$v.note.$touch()"
          class="mb-3"
        />
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
          <company-edit-menu :company="item" :client_tables="client_tables" :item_tables="item_tables" @company-deleted="deleteCompany(item)" />
        </template>
      </v-data-table>
    </div>
  </div>
</template>

<script>
import {
  required,
  minLength,
  maxLength,
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
import {slugFieldValidator, raizcnpjFieldValidator} from "~/helpers/validators"

export default {
  components: {
    "company-edit-menu": require("@/components/admin/organization/company-edit-menu.vue").default,
  },
  middleware: ["authenticated"],
  mixins: [validationMixin],

  data() {
    return {
      name: null,
      company_code: null,
      cnpj_root: null,
      client_table: null,
      item_table: null,
      status: "1",
      note: null,
      loading: false,
      companies: [],
      client_tables: [],
      item_tables: [],
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'Company code', value: 'company_code' },
        { text: 'Raiz do CNPJ', value: 'cnpj_root' },
        { text: 'Client table', value: 'client_table' },
        { text: 'Item Table', value: 'item_table' },
        { text: 'Status', value: 'status' },
        { text: 'Note', value: 'note' },
        { text: 'Actions', value: 'actions' },
      ]
    };
  },

  async fetch() {
    // Fetch Companies to EDIT list
    let companies = await this.$store.dispatch("organization/fetchCompanies");
    for (const company_index in companies){
      let company = companies[company_index]
      this.companies.push(company)
    }
    // Fetch client_table options
    let client_tables = await this.$store.dispatch("organization/fetchClientTables");
    for (const client_table_index in client_tables){
      let client_table = client_tables[client_table_index]
      this.client_tables.push(client_table)
    }
    // Fetch item_table options
    let item_tables = await this.$store.dispatch("item/fetchItemTables");
    for (const item_table_index in item_tables){
      let item_table = item_tables[item_table_index]
      this.item_tables.push(item_table)
    }
  },

  validations: {
    name: { 
      required, 
      minLength: minLength(3),
      maxLength: maxLength(60)
    },
    company_code: {
      required, 
      slugFieldValidator, 
      maxLength: maxLength(3)
    },
    cnpj_root: {
      required, 
      raizcnpjFieldValidator,
    },
    note: {
      maxLength: maxLength(800)
    },
    companyInfoGroup: [
      "name",
      "company_code",
      "cnpj_root",
      "note",
    ],
  },

  computed: {
    nameErrors() {
      const errors = [];
      if (!this.$v.name.$dirty) return errors;
      !this.$v.name.required && errors.push("Name is required.");
      !this.$v.name.minLength && errors.push("This field must have at least 3 characters.");
      !this.$v.name.maxLength && errors.push("This field must have up to 60 characters.");
      return errors;
    },
    companyCodeErrors() {
      const errors = [];
      if (!this.$v.company_code.$dirty) return errors;
      !this.$v.company_code.required && errors.push("Company code required.");
      !this.$v.company_code.slugFieldValidator && errors.push("It must containing only letters, numbers, underscores or hyphens.");
      !this.$v.company_code.maxLength && errors.push("This field must have up to 3 characters.");
      return errors;
    },
    cnpjRootErrors() { 
      const errors = [];
      if (!this.$v.cnpj_root.$dirty) return errors;
      !this.$v.cnpj_root.required && errors.push("Root of CNPJ is required.");
      !this.$v.cnpj_root.raizcnpjFieldValidator && errors.push("This field must be in the format '99.999.999'");
      return errors;
    },
    noteErrors() {
      const errors = [];
      if (!this.$v.note.$dirty) return errors;
      !this.$v.note.maxLength && errors.push("This field must have up to 800 characters.");
      return errors;
    },
  },

  methods: {
    async createCompany() {
      this.$v.companyInfoGroup.$touch();
      if (this.$v.companyInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: "Please fill the form correctly.", alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let data = await this.$store.dispatch("organization/createCompany", {
          name: this.name, 
          company_code: this.company_code,
          cnpj_root: this.cnpj_root,
          client_table: this.client_table,
          item_table: this.item_table,
          status: this.status,
          note: this.note
        });
        if (data) {
          this.companies.push(data);
        }
        this.loading = false;
      }
    },
    deleteCompany(companyToDelete) {
      this.companies = this.companies.filter((company) => company.company_compound_id != companyToDelete.company_compound_id);
    },
  },
};
</script>
<style scoped>
.v-application .mb-3 {
  margin-bottom: 0px !important;
}
</style>
