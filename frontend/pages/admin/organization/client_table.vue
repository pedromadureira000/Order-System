<template>
  <p v-if="$fetchState.pending">{{$t('Fetching_data')}}</p>
  <p v-else-if="$fetchState.error">{{$t('Error_fetching_data')}}</p>
  <div v-else>
    <div class="ma-3">
      <v-expansion-panels>
        <v-expansion-panel>
          <v-expansion-panel-header>
            <h3>{{$t('Create Client Table')}}</h3>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <form @submit.prevent="createClientTable">
              <!-- NAME -->
              <v-text-field
                :label="$t('Description')"
                v-model.trim="description"
                :error-messages="descriptionErrors"
                @blur="$v.description.$touch()"
                required
                class="mb-3"
              />
              <!-- Client Table Code -->
              <v-text-field
                :label="$t('Client Table Code')"
                v-model="client_table_code"
                :error-messages="clientTableCodeErrors"
                required
                @blur="$v.client_table_code.$touch()"
                class="mb-3"
              />
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

          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>

      <h3 class="mt-6">{{$t('Edit Client Table')}}</h3>
      <v-data-table
        :headers="headers"
        :items="client_tables"
        :items-per-page="10"
        item-key="client_table_compound_id"
        class="elevation-1"
      >
        <template v-slot:item.actions="{ item }">
          <client-table-edit-menu
            :client_table="item" 
            @client-table-deleted="deleteClientTable(item)" 
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
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
import {slugFieldValidator} from "~/helpers/validators"

export default {
  middleware: ["authenticated"],
  components: {
    "client-table-edit-menu": require("@/components/admin/organization/client-table-edit-menu.vue").default,
  },
  mixins: [validationMixin],

  data() {
    return {
      description: null,
      client_table_code: null,
      // If it wasn't a string, the radio button will not be marked
      status: "1",
      active_users_limit: 5,
      note: "",
      loading: false,
      client_tables: [],
      headers: [
        { text: this.$t('Description'), value: 'description' },
        { text: this.$t('Client Table Code'), value: 'client_table_code' },
        { text: this.$t('Note'), value: 'note' },
        { text: this.$t('Actions'), value: 'actions' },
      ]
    };
  },

  async fetch() {
    let client_tables = await this.$store.dispatch("organization/fetchClientTables");
    if (client_tables){
      this.client_tables.push(...client_tables)
    }
  },

  validations: {
    description: { 
      required, 
      minLength: minLength(3),
      maxLength: maxLength(60)
    },
    client_table_code: {
      required, 
      slugFieldValidator, 
      maxLength: maxLength(2)
    },
    note: {
      maxLength: maxLength(800)
    },
    clientTableInfoGroup: [
      "description",
      "client_table_code",
      "note",
    ],
  },

  computed: {
    descriptionErrors() {
      const errors = [];
      if (!this.$v.description.$dirty) return errors;
      !this.$v.description.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.description.minLength && errors.push(this.$formatStr(this.$t("This_field_must_have_at_least_X_characters"), 3));
      !this.$v.description.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 60));
      return errors;
    },
    clientTableCodeErrors() {
      const errors = [];
      if (!this.$v.client_table_code.$dirty) return errors;
      !this.$v.client_table_code.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.client_table_code.slugFieldValidator && errors.push(this.$t("It_must_containing_only_letters_numbers_underscores_or_hyphens"));
      !this.$v.client_table_code.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 2));
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
    async createClientTable() {
      this.$v.clientTableInfoGroup.$touch();
      if (this.$v.clientTableInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let data = await this.$store.dispatch("organization/createClientTable", {
          description: this.description, 
          client_table_code: this.client_table_code,
          note: this.note
        });
        if (data) {
          this.client_tables.push(data);
        }
        this.loading = false;
      }
    },
    deleteClientTable(clientTableToDelete) {
      this.client_tables = this.client_tables.filter((client_table) => client_table.client_table_compound_id != clientTableToDelete.client_table_compound_id);
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
