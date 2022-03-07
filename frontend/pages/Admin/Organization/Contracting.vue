<template>
  <p v-if="$fetchState.pending">Fetching contracting companies ...</p>
  <p v-else-if="$fetchState.error">An error occurred :(</p>
  <div v-else>
    <div class="ma-3">
      <h3>Create Contracting</h3>
      <form @submit.prevent="createContracting">
        <!-- NAME -->
        <v-text-field
          label="Name"
          v-model.trim="name"
          :error-messages="nameErrors"
          @blur="$v.name.$touch()"
          required
          class="mb-3"
        />
        <!-- Contracting Code -->
        <v-text-field
          label="Contracting code"
          v-model="contracting_code"
          :error-messages="contractingCodeErrors"
          required
          @blur="$v.contracting_code.$touch()"
          class="mb-3"
        />
        <!-- Active Users limit -->
        <v-text-field
          label="Active users limit"
          v-model="active_users_limit"
          :error-messages="activeUsersLimitErrors"
          required
          @blur="$v.active_users_limit.$touch()"
          class="mb-3"
        />
        <!-- Contracting Status -->
        <v-radio-group v-model="status" style="width: 25%;" label="Contracting Company Status" class="mb-3">
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
        <!-- Submit Button -->
        <v-btn
          color="primary"
          type="submit"
          :loading="loading"
          :disabled="loading"
          >Submit</v-btn
        >
      </form>

      <h3 class="mt-6">Edit Contracting</h3>
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
      note: null,
      loading: false,
      contracting_companies: [],
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'Contracting code', value: 'contracting_code' },
        { text: 'Status', value: 'status' },
        { text: 'Active users limit', value: 'active_users_limit' },
        { text: 'Note', value: 'note' },
        { text: 'Actions', value: 'actions' },
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
      !this.$v.name.required && errors.push("Name is required.");
      !this.$v.name.minLength && errors.push("This field must have at least 3 characters.");
      !this.$v.name.maxLength && errors.push("This field must have up to 60 characters.");
      return errors;
    },
    contractingCodeErrors() {
      const errors = [];
      if (!this.$v.contracting_code.$dirty) return errors;
      !this.$v.contracting_code.required && errors.push("Contracting code required.");
      !this.$v.contracting_code.slugFieldValidator && errors.push("It must containing only letters, numbers, underscores or hyphens.");
      !this.$v.contracting_code.maxLength && errors.push("This field must have up to 3 characters.");
      return errors;
    },
    activeUsersLimitErrors() {
      const errors = [];
      if (!this.$v.active_users_limit.$dirty) return errors;
      !this.$v.active_users_limit.required && errors.push("This field is required.");
      !this.$v.active_users_limit.integer && errors.push("This value must be a integer.");
      !this.$v.active_users_limit.minValue && errors.push("This field cannot be less then 4.");
      !this.$v.active_users_limit.maxValue && errors.push("Make sure this value is less than or equal to 2147483647");
      /** Certifique-se de que este valor seja inferior ou igual a 2147483647. */
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
    async createContracting() {
      this.$v.contractingInfoGroup.$touch();
      if (this.$v.contractingInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: "Please fill the form correctly.", alertType: "error" }, { root: true })
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
};
</script>
<style scoped>
.v-application .mb-3 {
  margin-bottom: 0px !important;
}
</style>
