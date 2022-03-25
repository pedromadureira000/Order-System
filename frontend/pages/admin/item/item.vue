<template>
  <p v-if="$fetchState.pending">Fetching data ...</p>
  <p v-else-if="$fetchState.error">An error occurred :(</p>
  <div v-else>
    <div class="ma-3">
      <v-expansion-panels v-if="hasCreateItemPermission()">
        <v-expansion-panel>
          <v-expansion-panel-header>
            <h3>{{$t('Create Item')}}</h3>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <form @submit.prevent="createItem">
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
                    @change="fetchCategoriesToCreateItem"
                  ></v-select>
                </v-col>
              </v-row>

              <!-- Category -->
              <v-row align="center">
                <v-col
                  class="d-flex"
                  cols="12"
                  sm="6"
                >
                  <v-select
                    v-model="category"
                    :label="$t('Category')"
                    :items="categories"
                    :item-text="(x) => x.category_code + ' - ' + x.description"
                    :item-value="(x) => x.category_compound_id"
                  ></v-select>
                </v-col>
              </v-row>

              <!-- Item Code -->
              <v-text-field
                :label="$t('Item Code')"
                v-model="item_code"
                :error-messages="itemCodeErrors"
                required
                @blur="$v.item_code.$touch()"
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
              <!-- Unit -->
              <v-text-field
                :label="$t('Unit')"
                v-model.trim="unit"
                :error-messages="unitErrors"
                @blur="$v.unit.$touch()"
                required
                class="mb-3"
              />
              <!-- Barcode -->
              <v-text-field
                :label="$t('Barcode')"
                v-model.trim="barcode"
                :error-messages="barcodeErrors"
                @blur="$v.barcode.$touch()"
                required
                class="mb-3"
              />
              <!-- Technical Description -->
              <v-text-field
                :label="$t('Technical description')"
                v-model.trim="technical_description"
                :error-messages="technicalDescriptionErrors"
                @blur="$v.technical_description.$touch()"
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

      <div v-if="hasGetItemsPermission()">
        <h3 class="mt-6">{{$t('Edit Item')}}</h3>
        <v-data-table
          :headers="headers"
          :items="items"
          :items-per-page="10"
          item-key="item_compound_id"
          class="elevation-1"
        >
          <template v-slot:item.actions="{ item }">
            <item-edit-menu :item="item" :category_group="category_group" @item-deleted="deleteItem(item)" />
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
    "item-edit-menu": require("@/components/admin/item/item-edit-menu.vue").default,
  },
  mixins: [validationMixin],

  data() {
    return {
      item_table: null,
      category: null,
      item_code: null,
      description: null,
      technical_description: null,
      unit: null,
      barcode: null,
      status: "1",
      image: null,
      items: [],
      categories: [],
      companies: [],
      category_group: [],
      /**EX:  category_group: [{item_table: '123$123', categories: [{categoryObj, categoryObj2 }]}] */
      loading: false,
      headers: [
        { text: this.$t('Image'), value: 'image' },
        { text: this.$t('Description'), value: 'description' },
        { text: this.$t('Item code'), value: 'item_code' },
        { text: this.$t('Category'), value: 'category' },
        { text: this.$t('Unit'), value: 'unit' },
        { text: this.$t('Barcode'), value: 'barcode' },
        { text: 'Status', value: 'status' },
        { text: this.$t('Actions'), value: 'actions' },
      ]
    };
  },

  async fetch() {
    let items = await this.$store.dispatch("item/fetchItems");
    if (items){this.items.push(...items)}

    // Fetch Companies
    let companies = await this.$store.dispatch("item/fetchCompaniesToCreateItemOrCategoryOrPriceTable"); 
    if (companies){this.companies.push(...companies)}
  },

  methods: {
    async createItem() {
      this.$v.itemInfoGroup.$touch();
      if (this.$v.itemInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t('Please_fill_the_form_correctly'), alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let data = await this.$store.dispatch("item/createItem", {
          item_table: this.item_table,
          item_code: this.item_code,
          category: this.category, 
          description: this.description,
          unit: this.unit, 
          barcode: this.barcode, 
          status: this.status,
          technical_description: this.technical_description,
          /** image: this.image */
        });
        if (data) {
          this.items.push(data);
        }
        this.loading = false;
      }
    },
    deleteItem(itemToDelete) {
      this.items = this.items.filter((item) => item.item_code != itemToDelete.item_code);
    },

    async fetchCategoriesToCreateItem(){
          let category_already_exists = this.category_group.find(el=>el.item_table == this.item_table)
          if (category_already_exists){
            this.categories = category_already_exists.categories
          }
          else{
            let categories = await this.$store.dispatch("item/fetchCategoriesToCreateItem", this.item_table); 
            if (categories){
              this.category_group.push({item_table: this.item_table, categories: categories} )
              this.categories = categories
            }
          }
    },

    hasCreateItemPermission(){
      let user = this.$store.state.user.currentUser;
      return user.permissions.includes("create_item")
    },
    hasGetItemsPermission(){
      let user = this.$store.state.user.currentUser;
      return user.permissions.includes("get_items")
    },
  },

  validations: {
    description: { 
      required, 
      minLength: minLength(3),
      maxLength: maxLength(60)
    },
    item_code: {
      required, 
      slugFieldValidator, 
      maxLength: maxLength(15)
    },
    unit: { 
      required, 
      maxLength: maxLength(10)
    },
    barcode: { 
      maxLength: maxLength(13)
    },
    technical_description: {
      maxLength: maxLength(800)
    },
    itemInfoGroup: [
      "item_code",
      "description",
      "unit",
      "barcode",
      "technical_description",
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
    itemCodeErrors() {
      const errors = [];
      if (!this.$v.item_code.$dirty) return errors;
      !this.$v.item_code.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.item_code.slugFieldValidator && errors.push(this.$t('SlugFieldErrorMessage'));
      !this.$v.item_code.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 15));
      return errors;
    },
    unitErrors() {
      const errors = [];
      if (!this.$v.unit.$dirty) return errors;
      !this.$v.unit.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.unit.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 10));
      return errors;
    },
    barcodeErrors() {
      const errors = [];
      if (!this.$v.barcode.$dirty) return errors;
      !this.$v.barcode.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 13));
      return errors;
    },
    technicalDescriptionErrors() {
      const errors = [];
      if (!this.$v.technical_description.$dirty) return errors;
      !this.$v.technical_description.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 800));
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
