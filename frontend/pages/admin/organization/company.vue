<template>
  <p v-if="$fetchState.pending">{{$t('Fetching_data')}}</p>
  <p v-else-if="$fetchState.error">{{$t('Error_fetching_data')}}</p>
  <div v-else>
    <div class="ma-3">
      <v-expansion-panels>
        <v-expansion-panel>
          <v-expansion-panel-header>
            <h3>{{$t('Create_Company')}}</h3>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <form @submit.prevent="createCompany">
              <!-- Name -->
              <v-text-field
                :label="$t('Name')"
                v-model="name"
                :error-messages="nameErrors"
                required
                @blur="$v.name.$touch()"
                class="mb-3"
              />
              <!-- Company Code -->
              <v-text-field
                :label="$t('Company_code')"
                v-model="company_code"
                :error-messages="companyCodeErrors"
                required
                @blur="$v.company_code.$touch()"
                class="mb-3"
              />
              <!-- Root of CNPJ -->
              <v-text-field
                :label="$t('Root_of_CNPJ')"
                v-model="cnpj_root"
                v-mask="'##.###.###'"
                required
                :error-messages="cnpjRootErrors"
                @blur="$v.cnpj_root.$touch()"
                class="mb-3"
              />
              <!-- Client table -->
              <v-radio-group v-model="client_table" style="width: 25%;" :label="$t('Client_Table')" class="mb-3">
                <v-radio
                  v-for="(client_table, key) in client_tables"
                  :key="key"
                  :label="client_table.description"
                  :value="client_table.client_table_compound_id"
                ></v-radio>
                <v-radio
                  :label="$t('None')"
                  value=""
                ></v-radio>
              </v-radio-group>
              <!-- Item table -->
              <v-radio-group v-model="item_table" style="width: 25%;" :label="$t('Item_Table')" class="mb-3">
                <v-radio
                  v-for="(item_table, key) in item_tables"
                  :key="key"
                  :label="item_table.description"
                  :value="item_table.item_table_compound_id"
                ></v-radio>
                <v-radio
                  :label="$t('None')"
                  value=""
                ></v-radio>
              </v-radio-group>
              <!-- Company Status -->
              <v-radio-group v-model="status" style="width: 25%;" :label="$t('Company_Status')" class="mb-3">
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
              <v-btn
                color="primary"
                type="submit"
                :loading="loading"
                :disabled="loading"
                >{{$t('Submit')}}</v-btn>
            </form>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>

      <h3 class="mt-6">{{$t('Edit_Company')}}</h3>
      <v-data-table
        :headers="headers"
        :items="companies"
        :items-per-page="10"
        item-key="company_compound_id"
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
import {mask} from 'vue-the-mask'

export default {
  components: {
    "company-edit-menu": require("@/components/admin/organization/company-edit-menu.vue").default,
  },
  middleware: ["authenticated"],
  mixins: [validationMixin],
  directives: {mask},

  data() {
    return {
      name: null,
      company_code: null,
      cnpj_root: null,
      client_table: null,
      item_table: null,
      status: "1",
      note: "",
      loading: false,
      companies: [],
      client_tables: [],
      item_tables: [],
      headers: [
        { text: this.$t('Name'), value: 'name' },
        { text: this.$t('Company_code'), value: 'company_code' },
        { text: this.$t('CNPJ_Root'), value: 'cnpj_root' },
        { text: this.$t('Client_table'), value: 'client_table' },
        { text: this.$t('Item_Table'), value: 'item_table' },
        { text: 'Status', value: 'status' },
        { text: this.$t('Note'), value: 'note' },
        { text: this.$t('Actions'), value: 'actions' },
      ]
    };
  },

  async fetch() {
    // Fetch Companies to EDIT list
    let companies = await this.$store.dispatch("organization/fetchCompanies");
    this.companies.push(...companies)
    // Fetch client_table options
    let client_tables = await this.$store.dispatch("organization/fetchClientTables");
    this.client_tables.push(...client_tables)
    // Fetch item_table options
    let item_tables = await this.$store.dispatch("item/fetchItemTables");
    this.item_tables.push(...item_tables)
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
      !this.$v.name.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.name.minLength && errors.push(this.$formatStr(this.$t("This_field_must_have_at_least_X_characters"), 3));
      !this.$v.name.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 60));
      return errors;
    },
    companyCodeErrors() {
      const errors = [];
      if (!this.$v.company_code.$dirty) return errors;
      !this.$v.company_code.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.company_code.slugFieldValidator && errors.push(this.$t('SlugFieldErrorMessage'));
      !this.$v.company_code.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 3));
      return errors;
    },
    cnpjRootErrors() { 
      const errors = [];
      if (!this.$v.cnpj_root.$dirty) return errors;
      !this.$v.cnpj_root.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.cnpj_root.raizcnpjFieldValidator && errors.push(this.$t("cnpjRootValidationError"));
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
