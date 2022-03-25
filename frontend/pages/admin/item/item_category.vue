<template>
  <p v-if="$fetchState.pending">Fetching data ...</p>
  <p v-else-if="$fetchState.error">An error occurred :(</p>
  <div v-else>
    <div class="ma-3">
      <v-expansion-panels v-if="hasCreateItemCategoryPermission()">
        <v-expansion-panel>
          <v-expansion-panel-header>
            <h3>{{$t('Create Category')}}</h3>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <form @submit.prevent="createItemCategory">
              <!-- Company -->
              <v-row align="center">
                <v-col
                  class="d-flex"
                  cols="12"
                  sm="6"
                >
                  <v-select
                    v-model="item_table"
                    :label="$t('Company')"
                    :items="companies"
                    :item-text="(x) => x.company_code + ' - ' + x.name"
                    :item-value="(x) => x.item_table"
                  ></v-select>
                </v-col>
              </v-row>
              <!-- Item Category Code -->
              <v-text-field
                :label="$t('Item Category Code')"
                v-model="category_code"
                :error-messages="itemCategoryCodeErrors"
                required
                @blur="$v.category_code.$touch()"
                class="mb-3"
              />
              <!-- Description -->
              <v-text-field
                :label="$t('Description')"
                v-model.trim="description"
                :error-messages="descriptionErrors"
                @blur="$v.description.$touch()"
                required
                class="mb-3"
              />
              <!-- Note -->
              <v-text-field
                :label="$t('Note')"
                v-model.trim="note"
                :error-messages="noteErrors"
                @blur="$v.note.$touch()"
                required
                class="mb-3"
              />
              <!-- Submit -->
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

      <div v-if="hasGetItemCategoriesPermission()">
        <h3 class="mt-6">{{$t('Edit Category')}}</h3>
        <v-data-table
          :headers="headers"
          :items="categories"
          :items-per-page="10"
          item-key="category_compound_id"
          class="elevation-1"
        >
          <template v-slot:item.actions="{ item }">
            <item-category-edit-menu :category="item" @item-category-deleted="deleteItemCategory(item)" />
          </template>
        </v-data-table>
      </div>
    </div>
  </div>
</template>

<script>
import {
  required,
  maxLength,
  minLength,
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
import {slugFieldValidator} from "~/helpers/validators"

export default {
  middleware: ["authenticated"],
  components: {
    "item-category-edit-menu": require("@/components/admin/item/item-category-edit-menu.vue").default,
  },
  mixins: [validationMixin],

  data() {
    return {
      item_table: null,
      category_code: null,
      description: null,
      note: null,
      categories: [],
      companies: [],
      loading: false,
      headers: [
        { text: this.$t('Description'), value: 'description' },
        { text: this.$t('Category code'), value: 'category_code' },
        { text: this.$t('Note'), value: 'note' },
        { text: this.$t('Actions'), value: 'actions' },
      ]
    };
  },

  async fetch() {
    let categories = await this.$store.dispatch("item/fetchCategories");
    if (categories){this.categories.push(...categories)}

    // Fetch Companies
    let companies = await this.$store.dispatch("item/fetchCompaniesToCreateItemOrCategoryOrPriceTable"); 
    if (companies){this.companies.push(...companies)}
  },

  methods: {
    async createItemCategory() {
      this.$v.itemInfoGroup.$touch();
      if (this.$v.itemInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t('Please_fill_the_form_correctly'), alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let data = await this.$store.dispatch("item/createCategory", {
          item_table: this.item_table,
          category_code: this.category_code,
          description: this.description,
          note: this.note,
        });
        if (data) {
          this.categories.push(data);
        }
        this.loading = false;
      }
    },
    deleteItemCategory(itemToDelete) {
      this.categories = this.categories.filter((item) => item.category_code != itemToDelete.category_code);
    },

    hasCreateItemCategoryPermission(){
      let user = this.$store.state.user.currentUser;
      return user.permissions.includes("create_item_category")
    },
    hasGetItemCategoriesPermission(){
      let user = this.$store.state.user.currentUser;
      return user.permissions.includes("get_item_category")
    },
  },

  validations: {
    description: { 
      required, 
      minLength: minLength(3),
      maxLength: maxLength(60)
    },
    category_code: {
      required, 
      slugFieldValidator, 
      maxLength: maxLength(8)
    },
    note: {
      maxLength: maxLength(800)
    },
    itemInfoGroup: [
      "category_code",
      "description",
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
    itemCategoryCodeErrors() {
      const errors = [];
      if (!this.$v.category_code.$dirty) return errors;
      !this.$v.category_code.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.category_code.slugFieldValidator && errors.push(this.$t('SlugFieldErrorMessage'));
      !this.$v.category_code.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 8));
      return errors;
    },
    noteErrors() {
      const errors = [];
      if (!this.$v.note.$dirty) return errors;
      !this.$v.note.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 800));
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
