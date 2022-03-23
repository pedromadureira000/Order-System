<template>
  <p v-if="$fetchState.pending">{{$t('Fetching_data')}}</p>
  <p v-else-if="$fetchState.error">{{$t('Error_fetching_data')}}</p>
  <div v-else>
    <div class="ma-3">
      <v-expansion-panels>
        <v-expansion-panel>
          <v-expansion-panel-header>
            <h3>{{$t('Create_Establishment')}}</h3>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <form @submit.prevent="createEstablishment">
              <!-- Name -->
              <v-text-field
                :label="$t('Name')"
                v-model="name"
                :error-messages="nameErrors"
                required
                @blur="$v.name.$touch()"
                class="mb-3"
              />
              <!-- Establishment Code -->
              <v-text-field
                :label="$t('Establishment_code')"
                v-model="establishment_code"
                :error-messages="establishmentCodeErrors"
                required
                @blur="$v.establishment_code.$touch()"
                class="mb-3"
              />
              <!-- Company -->
              <v-row align="center">
                <v-col
                  class="d-flex"
                  cols="12"
                  sm="6"
                >
                  <v-select
                    v-model="company"
                    :label="$t('Company')"
                    :items="companies"
                    :item-text="(x) => x.company_code + ' - ' + x.name"
                    :item-value="(x) => x.company_compound_id"
                  ></v-select>
                </v-col>
              </v-row>
              <!-- CNPJ -->
              <v-text-field
                label="CNPJ"
                v-model="cnpj"
                v-mask="'##.###.###/####-##'"
                required
                :error-messages="cnpjError"
                @blur="$v.cnpj.$touch()"
                class="mb-3"
              />
              <!-- Establishment Status -->
              <v-radio-group v-model="status" style="width: 25%;" :label="$t('Establishment_Status')" class="mb-3">
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

      <h3 class="mt-6">{{$t('Edit_Establishment')}}</h3>
      <v-data-table
        :headers="headers"
        :items="establishments"
        :items-per-page="10"
        item-key="establishment_compound_id"
        class="elevation-1"
      >
        <template v-slot:item.actions="{ item }">
          <establishment-edit-menu :establishment="item" @establishment-deleted="deleteEstablishment(item)" />
        </template>
        <template v-slot:item.cnpj_with_mask="{ item }">
          <input type="text" v-mask="'##.###.###/####-##'" :value="item.cnpj" disabled style="color: #000000DE;"/>
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
import {slugFieldValidator, cnpjFieldValidator} from "~/helpers/validators"
import {mask} from 'vue-the-mask'

export default {
  components: {
    "establishment-edit-menu": require("@/components/admin/organization/establishment-edit-menu.vue").default,
  },
  middleware: ["authenticated"],
  mixins: [validationMixin],
  directives: {mask},

  data() {
    return {
      name: null,
      establishment_code: null,
      company: null,
      cnpj: null,
      status: "1",
      note: "",
      loading: false,
      establishments: [],
      companies: [],
      headers: [
        { text: this.$t('Name'), value: 'name' },
        { text: this.$t('Establishment_code'), value: 'establishment_code' },
        { text: this.$t('Company'), value: 'company' },
        { text: 'CNPJ', value: 'cnpj_with_mask' },
        { text: 'Status', value: 'status' },
        { text: this.$t('Note'), value: 'note' },
        { text: this.$t('Actions'), value: 'actions' },
      ]
    };
  },

  async fetch() {
    // Fetch Establishments to EDIT list
    let establishments = await this.$store.dispatch("organization/fetchEstablishments");
    if (establishments){this.establishments.push(...establishments)}
    // Fetch company options
    let companies = await this.$store.dispatch("organization/fetchCompaniesToCreateEstablishment");
    if (companies) {this.companies.push(...companies)}
    
  },

  validations: {
    name: { 
      required, 
      minLength: minLength(3),
      maxLength: maxLength(60)
    },
    establishment_code: {
      required, 
      slugFieldValidator, 
      maxLength: maxLength(3)
    },
    cnpj: {
      required, 
      cnpjFieldValidator,
    },
    note: {
      maxLength: maxLength(800)
    },
    establishmentInfoGroup: [
      "name",
      "establishment_code",
      "cnpj",
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
    establishmentCodeErrors() {
      const errors = [];
      if (!this.$v.establishment_code.$dirty) return errors;
      !this.$v.establishment_code.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.establishment_code.slugFieldValidator && errors.push(this.$t('SlugFieldErrorMessage'));
      !this.$v.establishment_code.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 3));
      return errors;
    },
    cnpjError() { 
      const errors = [];
      if (!this.$v.cnpj.$dirty) return errors;
      !this.$v.cnpj.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.cnpj.cnpjFieldValidator && errors.push(this.$t("cnpjValidationError"));
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
    async createEstablishment() {
      this.$v.establishmentInfoGroup.$touch();
      if (this.$v.establishmentInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let data = await this.$store.dispatch("organization/createEstablishment", {
          name: this.name, 
          establishment_code: this.establishment_code,
          cnpj: this.cnpj,
          company: this.company,
          status: this.status,
          note: this.note
        });
        if (data) {
          this.establishments.push(data);
        }
        this.loading = false;
      }
    },
    deleteEstablishment(establishmentToDelete) {
      this.establishments = this.establishments.filter((establishment) => establishment.establishment_compound_id != 
        establishmentToDelete.establishment_compound_id);
    },
  },
};
</script>
<style scoped>
.v-application .mb-3 {
  margin-bottom: 0px !important;
}
</style>
