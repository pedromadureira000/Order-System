<template>
  <p v-if="$fetchState.pending">{{$t('Fetching_data')}}</p>
  <p v-else-if="$fetchState.error">{{$t('Error_fetching_data')}}</p>
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
                    v-model="company"
                    :label="$t('Company')"
                    :items="companies"
                    :item-text="(x) => x.company_code + ' - ' + x.name"
                    return-object
                  ></v-select>
                </v-col>
              </v-row>
              <!-- Item Category Code -->
              <v-text-field
                :label="$t('Category code')"
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
              <v-textarea
                outlined
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
        <h3 class="mt-6 mb-7">{{$t('Edit Category')}}</h3>
        <!-- Select company -->
        <v-card class="mb-6">
          <v-row>
            <v-col cols='3'>
              <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Select company')}}</v-card-title>
            </v-col>
            <v-col cols='3'>
                <v-select
                  v-model="company_to_fetch_categories"
                  :label="$t('Company')"
                  :items="companies"
                  :item-text="(x) => x.company_code + ' - ' + x.name"
                  return-object
                ></v-select>
            </v-col>
            <v-col cols="6"></v-col>
          </v-row>
        </v-card>
        <v-data-table
          :headers="headers"
          :items="categories"
          :items-per-page="10"
          item-key="category_compound_id"
          class="elevation-1 mt-3"
        >
          <template v-slot:item.description="{ item }">
            <p style="width: 240px;">{{item.description}}</p>
          </template>
          <template v-slot:item.actions="{ item }">
            <item-category-edit-menu :category="item" :companies="companies" @item-category-deleted="deleteItemCategory(item)" />
          </template>
          <template v-slot:item.note="{ item }">
            <p>{{$getNote(item.note)}}</p>
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
      company: null,
      companies: [],
      category_code: null,
      description: null,
      note: null,
      company_to_fetch_categories: null,
      categories: [],
      category_group: [],
      loading: false,
      headers: [
        { text: this.$t('Category code'), value: 'category_code' },
        { text: this.$t('Description'), value: 'description' },
        { text: this.$t('Note'), value: 'note' },
        { text: this.$t('Actions'), value: 'actions' },
      ]
    };
  },

  async fetch() {
    // Fetch Companies
    let companies = await this.$store.dispatch("item/fetchCompaniesToCreatePriceTable"); 
    if (companies){
      this.companies.push(...companies)
      if (this.companies.length > 0){
        this.company = this.companies[0]
        // this will lead to call fetchCategories function
        this.company_to_fetch_categories = this.companies[0]
      }
    }
  },

  methods: {
    async fetchCategories(){
      console.log(">>>>>>> inside fetchCategories()")
      let category_group = this.category_group.find(el=>el.group_id===this.company_to_fetch_categories.item_table)
      if (category_group){
        console.log(">>>>>>> inside fetchCategories(): category_group found")
        this.categories = category_group.categories
      }
      else{
        console.log(">>>>>>> inside fetchCategories(): category_group was not found")
        let categories = await this.$store.dispatch("item/fetchCategories", this.company_to_fetch_categories.item_table);
        if (categories){
          this.categories.push(...categories)
          this.category_group.push({group_id: this.company_to_fetch_categories.item_table, categories: [...categories]})
        }
      }
    },

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

  watch: {
    company_to_fetch_categories(newValue, oldValue){
      console.log(">>>>>>> newValue: ", newValue)
      console.log(">>>>>>> OldValue:", oldValue)
      if (newValue.item_table !== (oldValue === null ? null : oldValue.item_table)) {
        this.fetchCategories()
      }
    }	
  },
};
</script>
<style scoped>
.v-application .mb-3 {
  margin-bottom: 0px !important;
}
</style>
