<template>
  <p v-if="$fetchState.pending">{{$t('Fetching_contracting_companies')}}</p>
  <p v-else-if="$fetchState.error">{{$t('Fetching_contracting_companies_ERROR')}}</p>
  <div v-else>
    <div class="ma-3">
      <h3>{{$t('Create_Contracting')}}</h3>
      <form @submit.prevent="createContracting">
        <!-- NAME -->
        <v-text-field
          :label="$t('Name')"
          v-model.trim="name"
          :error-messages="nameErrors"
          @blur="$v.name.$touch()"
          required
          class="mb-3"
        />
        <!-- Contracting Code -->
        <v-text-field
          :label="$t('Contracting_code')"
          v-model="contracting_code"
          :error-messages="contractingCodeErrors"
          required
          @blur="$v.contracting_code.$touch()"
          class="mb-3"
        />
        <!-- Active Users limit -->
        <v-text-field
          :label="$t('Active_users_limit')"
          v-model="active_users_limit"
          :error-messages="activeUsersLimitErrors"
          required
          @blur="$v.active_users_limit.$touch()"
          class="mb-3"
        />
        <!-- Contracting Status -->
        <v-radio-group v-model="status" style="width: 25%;" :label="$t('Contracting_Company_Status')" class="mb-3">
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
        <!-- Submit Button -->
        <v-btn
          color="primary"
          type="submit"
          :loading="loading"
          :disabled="loading"
          >{{$t('Submit')}}</v-btn
        >
      </form>

      <h3 class="mt-6">{{$t('Edit_Contracting')}}</h3>
      <v-data-table
        :headers="headers"
        :items="contracting_companies"
        :items-per-page="10"
        class="elevation-1"
      >
        <template v-slot:item.actions="{ item }">
          <contracting-edit-menu
            :contracting="item" 
            @contracting-deleted="deleteContracting(item)" 
          />
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
  minValue,
  maxValue,
  integer
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
import {slugFieldValidator} from "~/helpers/validators"

export default {
  middleware: ["authenticated"],
  components: {
    "contracting-edit-menu": require("@/components/admin/organization/contracting-edit-menu.vue").default,
  },
  mixins: [validationMixin],

  data() {
    return {
      name: null,
      contracting_code: null,
      // If it wasn't a string, the radio button will not be marked
      status: "1",
      active_users_limit: 5,
      note: "",
      loading: false,
      contracting_companies: [],
      headers: [
        { text: this.$t('Name'), value: 'name' },
        { text: this.$t('Contracting_code'), value: 'contracting_code' },
        { text: 'Status', value: 'status' },
        { text: this.$t('Active_users_limit'), value: 'active_users_limit' },
        { text: this.$t('Note'), value: 'note' },
        { text: this.$t('Actions'), value: 'actions' },
      ]
    };
  },

  async fetch() {
    let contracting_companies = await this.$store.dispatch("organization/fetchContractingCompanies");
    for (const contracting_index in contracting_companies){
      let contracting = contracting_companies[contracting_index]
      this.contracting_companies.push(contracting)
    }
  },

  validations: {
    name: { 
      required, 
      minLength: minLength(3),
      maxLength: maxLength(60)
    },
    contracting_code: {
      required, 
      slugFieldValidator, 
      maxLength: maxLength(3)
    },
    active_users_limit: {
      required, 
      integer,
      minValue: minValue(4),
      maxValue: maxValue(2147483647)
    },
    note: {
      maxLength: maxLength(800)
    },
    contractingInfoGroup: [
      "name",
      "contracting_code",
      "active_users_limit",
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
    contractingCodeErrors() {
      const errors = [];
      if (!this.$v.contracting_code.$dirty) return errors;
      !this.$v.contracting_code.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.contracting_code.slugFieldValidator && errors.push(this.$t("It_must_containing_only_letters_numbers_underscores_or_hyphens"));
      !this.$v.contracting_code.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 3));
      return errors;
    },
    activeUsersLimitErrors() {
      const errors = [];
      if (!this.$v.active_users_limit.$dirty) return errors;
      !this.$v.active_users_limit.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.active_users_limit.integer && errors.push(this.$t("This_value_must_be_a_integer"));
      !this.$v.active_users_limit.minValue && errors.push(this.$formatStr(this.$t("This_value_must_be_greater_than_X"), 3 ));
      !this.$v.active_users_limit.maxValue && errors.push(this.$formatStr(this.$t("This_value_must_be_less_than_X"), 2147483648));
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
    async createContracting() {
      this.$v.contractingInfoGroup.$touch();
      if (this.$v.contractingInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let data = await this.$store.dispatch("organization/createContracting", {
          name: this.name, 
          contracting_code: this.contracting_code,
          status: this.status,
          active_users_limit: this.active_users_limit,
          note: this.note
        });
        if (data) {
          this.contracting_companies.push(data);
        }
        this.loading = false;
      }
    },
    deleteContracting(contractingToDelete) {
      this.contracting_companies = this.contracting_companies.filter((contracting) => contracting.contracting_code != contractingToDelete.contracting_code);
    },
  },
  /** mounted() { */
  /** }     */
};
</script>
<style scoped>
.v-application .mb-3 {
  margin-bottom: 0px !important;
}
</style>
