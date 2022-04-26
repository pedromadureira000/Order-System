<template>
  <p v-if="$fetchState.pending">{{$t('Fetching_data')}}</p>
  <p v-else-if="$fetchState.error">{{$t('Error_fetching_data')}}</p>
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
                    v-model="company"
                    :label="$t('Company')"
                    :items="companies"
                    :item-text="(x) => x.company_code + ' - ' + x.name"
                    return-object
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
                    :item-text="(x) => x.category_compound_id === null ? $t('All') : x.category_code + ' - ' + x.description"
                    :item-value="(x) => x.category_compound_id"
                  ></v-select>
                </v-col>
              </v-row>

              <!-- Item code -->
              <v-text-field
                :label="$t('Item code')"
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
                class="mb-3"
              />
              <!-- Client Status -->
              <v-radio-group v-model="status" style="width: 25%;" label='Status' class="mb-3">
                <v-radio
                  :label="$t('Active')"
                  value=1
                ></v-radio>
                <v-radio
                  :label="$t('Disabled')"
                  value=0
                ></v-radio>
              </v-radio-group>
              <!-- Image -->
              <v-row>
                <v-col>
                  <v-file-input
                    show-size
                    accept="image/*"
                    :label="$t('Image')"
                    prepend-icon="mdi-camera"
                    @change="onChange"
                  ></v-file-input>
                </v-col>
                <v-col>
                  <v-img
                    v-if="img_url"
                    contain
                    width="115px"
                    height="87px"
                    :src="img_url"
                  ></v-img>
                </v-col>
              </v-row>
              <!-- Technical Description -->
              <v-textarea
                outlined
                :label="$t('Technical description')"
                v-model.trim="technical_description"
                :error-messages="technicalDescriptionErrors"
                @blur="$v.technical_description.$touch()"
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
        <h3 class="mt-6 mb-7">{{$t('Edit Item')}}</h3>
        <!-- Search filters -->
        <v-card class="mb-6">
          <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Search filters')}}</v-card-title>
          <v-row class="ml-2">
            <v-col cols='3'>
                <v-select
                  v-model="filter__company"
                  :label="$t('Company')"
                  :items="companies"
                  :item-text="(x) => x.company_code + ' - ' + x.name"
                  return-object
                  @change="fetchCategoriesToSearchItems"
                ></v-select>
            </v-col>
            <v-col cols="3">
              <v-select
                v-model="filter__category"
                :label="$t('Category')"
                :items="category_filter_options"
                :item-text="(x) => x.category_compound_id === null ? $t(x.description) : x.category_compound_id.split('*')[2] + ' - ' + x.description"
                return-object
              ></v-select>
            </v-col>
            <v-col cols="2">
              <v-text-field
                :label="$t('Item code')"
                :error-messages="itemCodeToSearchItemsErrors"
                v-model.trim="filter__item_code"
                @keydown.enter.prevent="searchOnePriceItemToMakeOrder"
                @blur="$v.filter__item_code.$touch()"
              />
            </v-col>
            <v-col cols="3">
              <v-text-field
                :label="$t('Item description')"
                v-model.trim="filter__item_description"
                :error-messages="itemDescriptionToSearchItemsErrors"
                @blur="$v.filter__item_description.$touch()"
              />
            </v-col>
            <v-col cols="1" style="display: flex; justify-content: center; align-items: center;">
              <v-btn
                class="mr-4"
                style="width: 84%;"
                color="primary"
                :loading="loading"
                :disabled="loading"
                @click="options['page'] = 1; fetchItems()"
              >{{$t('Search')}}</v-btn>
            </v-col>
          </v-row>
        </v-card>

        <!-- Items list -->
        <v-data-table
          :headers="headers"
          :items="items"
          :items-per-page="10"
          item-key="item_compound_id"
          class="elevation-1 mt-3"
          @pagination="changePagination"
          :options.sync="options"
          :server-items-length="totalItems"
          :loading="loading_items"
          :footer-props="{'items-per-page-options': [5, 10, 15]}"
        >
          <template v-slot:item.description="{ item }">
            <p style="width: 240px;">{{item.description}}</p>
          </template>
          <template v-slot:item.image="{ item }">
            <v-img
              contain
              width="115px"
              height="87px"
              :lazy-src="$store.state.CDNBaseUrl + '/media/images/items/defaultimage.jpeg'"
              :src="getImageUrl(item.image)"
            ></v-img>
          </template>
          <template v-slot:item.actions="{ item }">
            <item-edit-menu :item="item" :companies="companies" :category_group="category_group" @item-deleted="deleteItem(item)" />
          </template>
          <template v-slot:item.category="{ item }">
            <p>{{item.category.split('*')[2]}}</p>
          </template>
          <template v-slot:item.status="{ item }">
            <p>{{item.status === 1 ? $t('Active') : $t('Disabled')}}</p>
          </template>
          <template v-slot:item.technical_description="{ item }">
            <p>{{$getNote(item.technical_description)}}</p>
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

let default_category_value = {category_compound_id: null, description: 'All'}
export default {
  middleware: ["authenticated"],
  components: {
    "item-edit-menu": require("@/components/admin/item/item-edit-menu.vue").default,
  },
  mixins: [validationMixin],

  data() {
    return {
      company: null,
      companies: [],
      category: null,
      item_code: null,
      description: null,
      technical_description: "",
      unit: null,
      barcode: "",
      status: "1",
      image: null,
      items: [],
      categories: [],
      category_group: [],
      img_url: '',
      loading: false,
      loading_items: false,
      options: {},
      totalItems: 0,
      filter__company: null,
      filter__item_description: '',
      filter__item_code: '',
      filter__category: default_category_value,
      category_filter_options: [default_category_value, ],
      headers: [
        { text: this.$t('Image'), value: 'image', sortable: false},
        { text: this.$t('Code'), value: 'item_code', sortable: false},
        { text: this.$t('Description'), value: 'description', sortable: false},
        { text: this.$t('Category'), value: 'category', sortable: false},
        { text: this.$t('Unit'), value: 'unit', sortable: false},
        { text: this.$t('Barcode'), value: 'barcode', sortable: false},
        { text: 'Status', value: 'status', sortable: false},
        { text: this.$t('Technical description'), value: 'technical_description', sortable: false },
        { text: this.$t('Actions'), value: 'actions', sortable: false},
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
        await this.fetchCategoriesToCreateItem()
        this.filter__company = this.companies[0]
        await this.fetchCategoriesToSearchItems()
      }
    }
  },

  methods: {
    async createItem(){
      this.$v.itemInfoGroup.$touch();
      if (this.$v.itemInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t('Please_fill_the_form_correctly'), alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        const formData = new FormData()
        formData.append('item_table', this.company.item_table)
        formData.append('item_code', this.item_code)
        formData.append('category', this.category)
        formData.append('description', this.description)
        formData.append('unit', this.unit)
        formData.append('barcode', this.barcode)
        formData.append('status', this.status)
        formData.append('technical_description', this.technical_description)
        if (this.image){
          formData.append('image', this.image, this.image.name)
        }
        let data = await this.$store.dispatch("item/createItem", formData);
        if (data) {
          if (this.filter__company.item_table === data.item_table){
            this.items.push(data)
          }
          // Clearing fields
          this.$v.$reset()
          // this avoid "This field is required" errors by vuelidate
          this.company = this.companies[0]
          this.category = this.categories[0].category_compound_id 
          this.item_code = ""
          this.description = ""
          this.unit = ""
          this.barcode = ""
          this.status = "1"
          this.technical_description = ""
          this.image = null
          this.img_url = ''
        }
        this.loading = false;
      }
    },

    async fetchItems(){
      this.loading_items = true
      const { sortBy, sortDesc, page, itemsPerPage } = this.options
      /** console.log(">>>>>>> sortBy: ", sortBy) */
      /** console.log(">>>>>>> sortDesc: ", sortDesc) */
      console.log(">>>>>>> page front: ", page)
      console.log(">>>>>>> itemsPerPage front: ", itemsPerPage)
      let query_strings = ""
      query_strings += `page=${page}&`
      query_strings += `items_per_page=${itemsPerPage}&`
      query_strings += `item_table=${this.filter__company.item_table}&`
      query_strings += this.filter__category.category_compound_id ? `category=${this.filter__category.category_compound_id}&` : ''
      query_strings += this.filter__item_code ? `item_code=${this.filter__item_code}&` : ''
      query_strings += this.filter__item_description ? `description=${this.filter__item_description}&` : ''
      if (query_strings !== "") {
        query_strings = query_strings.slice(0, -1) // remove the last '&' character
      }
      let {items, current_page, lastPage, total} = await this.$store.dispatch("item/fetchItems", query_strings);
      console.log(">>>>>>> items: ", items)
      console.log(">>>>>>> current_page: ", current_page)
      console.log(">>>>>>> lastPage: ", lastPage)
      console.log(">>>>>>> total: ", total)
      if (items) {
        this.items = items
        this.totalItems = total
      }
      this.loading_items = false
    },

    async fetchCategoriesToSearchItems(){
      let category_already_exists = this.category_group.find(el=>el.item_table == this.filter__company.item_table)
      if (category_already_exists){
        this.category_filter_options = [default_category_value, ...category_already_exists.categories]
        this.filter__category = default_category_value
      }
      else{
        let categories = await this.$store.dispatch("item/fetchCategoriesToCreateItem", this.filter__company.item_table); 
        if (categories){
          this.category_group.push({item_table: this.filter__company.item_table, categories: categories} )
          this.category_filter_options = [default_category_value, ...categories]
          this.filter__category = default_category_value
        }
      }
    },

    changePagination(event){
      /** console.log(">>>>>>>changePagination event: ", event) */
    },

    deleteItem(itemToDelete) {
      this.items = this.items.filter((item) => item.item_code != itemToDelete.item_code);
    },

    async fetchCategoriesToCreateItem(){
      let category_already_exists = this.category_group.find(el=>el.item_table == this.company.item_table)
      if (category_already_exists){
        this.categories = category_already_exists.categories
        if (this.categories.length > 0){
          this.category = this.categories[0].category_compound_id 
        }
      }
      else{
        let categories = await this.$store.dispatch("item/fetchCategoriesToCreateItem", this.company.item_table); 
        if (categories){
          this.category_group.push({item_table: this.company.item_table, categories: categories} )
          this.categories = categories
          if (this.categories.length > 0){
            this.category = this.categories[0].category_compound_id 
          }
        }
      }
    },

    // Image
    onChange (event) {
      /** console.log(">>>>>>> ", event) */
      this.image = event
      if (event === null){
        this.img_url = ''

      } else{
        this.img_url = URL.createObjectURL(this.image)
        /** console.log(">>>>>>> URL image: ", this.img_url) */

      }
    },
    // The backend return item url with base url "http://..." after create an item
    getImageUrl(image){
      if (image) {
        let url = image
        if (url.startsWith('http')){
          let url_fixed = url.split('/media/images/')[1]
          return this.$store.state.CDNBaseUrl + '/media/images/' + url_fixed
        }
        else {
          return this.$store.state.CDNBaseUrl + url
        }
      }
      else {
        return this.$store.state.CDNBaseUrl + '/media/images/items/defaultimage.jpeg'
      }
    },

    // Permissions 

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
      maxLength: maxLength(15)
    },
    technical_description: {
      maxLength: maxLength(800)
    },
    // Search items Filter
    filter__item_code: {
      slugFieldValidator, 
      maxLength: maxLength(15)
    },
    filter__item_description: { 
      maxLength: maxLength(60)
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
      !this.$v.barcode.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 15));
      return errors;
    },
    technicalDescriptionErrors() {
      const errors = [];
      if (!this.$v.technical_description.$dirty) return errors;
      !this.$v.technical_description.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 800));
      return errors;
    },
    // Search items filter
    itemCodeToSearchItemsErrors() {
      const errors = [];
      if (!this.$v.filter__item_code.$dirty) return errors;
      !this.$v.filter__item_code.slugFieldValidator && errors.push(this.$t('SlugFieldErrorMessage'));
      !this.$v.filter__item_code.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 15));
      return errors;
    },
    itemDescriptionToSearchItemsErrors() {
      const errors = [];
      if (!this.$v.description.$dirty) return errors;
      !this.$v.description.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 60));
      return errors;
    },
  },

  /** mounted() { */
    /** console.log('>>>>>>>>>>>>>>>>>> CDN url: ', this.cdn_url) */
  /** } */
  watch: {
    options: {
      handler () {
        this.fetchItems()
      },
      deep: true,
    },
  },
};
</script>
<style scoped>
.v-application .mb-3 {
  margin-bottom: 0px !important;
}
</style>
