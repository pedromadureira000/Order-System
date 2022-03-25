<template>
  <p v-if="$fetchState.pending">{{$t('Fetching_data')}}</p>
  <p v-else-if="$fetchState.error">{{$t('Error_fetching_data')}}</p>
  <div v-else>
    <div class="ma-3">
      <v-expansion-panels>
        <v-expansion-panel>
          <v-expansion-panel-header>
            <h3>{{$t('Create Item Table')}}</h3>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <form @submit.prevent="createItemTable">
              <!-- NAME -->
              <v-text-field
                :label="$t('Description')"
                v-model.trim="description"
                :error-messages="descriptionErrors"
                @blur="$v.description.$touch()"
                required
                class="mb-3"
              />
              <!-- Item Table Code -->
              <v-text-field
                :label="$t('Item Table Code')"
                v-model="item_table_code"
                :error-messages="itemTableCodeErrors"
                required
                @blur="$v.item_table_code.$touch()"
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

      <h3 class="mt-6">{{$t('Edit Item Table')}}</h3>
      <v-data-table
        :headers="headers"
        :items="item_tables"
        :items-per-page="10"
        item-key="item_table_compound_id"
        class="elevation-1"
      >
        <template v-slot:item.actions="{ item }">
          <item-table-edit-menu
            :item_table="item" 
            @item-table-deleted="deleteItemTable(item)" 
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
    "item-table-edit-menu": require("@/components/admin/item/item-table-edit-menu.vue").default,
  },
  mixins: [validationMixin],

  data() {
    return {
      description: null,
      item_table_code: null,
      // If it wasn't a string, the radio button will not be marked
      status: "1",
      active_users_limit: 5,
      note: "",
      loading: false,
      item_tables: [],
      headers: [
        { text: this.$t('Item Table Code'), value: 'item_table_code' },
        { text: this.$t('Description'), value: 'description' },
        { text: this.$t('Note'), value: 'note' },
        { text: this.$t('Actions'), value: 'actions' },
      ]
    };
  },

  async fetch() {
    let item_tables = await this.$store.dispatch("item/fetchItemTables");
    if (item_tables){
      this.item_tables.push(...item_tables)
    }
  },

  validations: {
    description: { 
      required, 
      minLength: minLength(3),
      maxLength: maxLength(60)
    },
    item_table_code: {
      required, 
      slugFieldValidator, 
      maxLength: maxLength(3)
    },
    note: {
      maxLength: maxLength(800)
    },
    itemTableInfoGroup: [
      "description",
      "item_table_code",
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
    itemTableCodeErrors() {
      const errors = [];
      if (!this.$v.item_table_code.$dirty) return errors;
      !this.$v.item_table_code.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.item_table_code.slugFieldValidator && errors.push(this.$t("It_must_containing_only_letters_numbers_underscores_or_hyphens"));
      !this.$v.item_table_code.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 3));
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
    async createItemTable() {
      this.$v.itemTableInfoGroup.$touch();
      if (this.$v.itemTableInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let data = await this.$store.dispatch("item/createItemTable", {
          description: this.description, 
          item_table_code: this.item_table_code,
          note: this.note
        });
        if (data) {
          this.item_tables.push(data);
        }
        this.loading = false;
      }
    },
    deleteItemTable(itemTableToDelete) {
      this.item_tables = this.item_tables.filter((item_table) => item_table.item_table_compound_id != itemTableToDelete.item_table_compound_id);
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
