<template>
    <div>
      <!-- Search filters -->
      <v-card class="mb-6">
        <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Search filters')}}</v-card-title>
        <v-row class="ml-2">
          <v-col cols='3'>
              <v-select
                :disabled="itsForPriceItems"
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
              :loading="loading_items"
              :disabled="loading_items"
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
          <item-edit-menu 
            v-if="itsForAdminItemPage"
            :item="item" 
            :companies="companies" 
            :category_group="category_group" 
            :item_company="filter__company" 
            @item-deleted="deleteItem(item)" 
          />
          <div style="display:flex; align-items: center; justify-content: center;" v-if="itsForPriceItems">
            <v-icon @click="$emit('add-item', item)" color="green" large v-if="!itemIsAlreadyAdded(item.item_compound_id)">
              mdi-plus
            </v-icon >
          </div>
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
</template>

<script>
import {
  maxLength,
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
import {slugFieldValidator} from "~/helpers/validators"

let default_category_value = {category_compound_id: null, description: 'All'}
export default {
  mixins: [validationMixin],
  components: {
    "item-edit-menu": require("@/components/admin/item/item-edit-menu.vue").default,
  },
  props: ['companies', 'category_group', 'price_table', 'price_items', 'itsForAdminItemPage', 'itsForPriceItems'],
  data() {
    return {
      items: [],
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
        { text: this.$t('Code'), value: 'item_code', sortable: true},
        { text: this.$t('Description'), value: 'description', sortable: true},
        { text: this.$t('Category'), value: 'category', sortable: false},
        { text: this.$t('Unit'), value: 'unit', sortable: false},
        { text: this.$t('Barcode'), value: 'barcode', sortable: false},
        { text: 'Status', value: 'status', sortable: false},
        ...(this.itsForAdminItemPage ? [{text: this.$t('Technical description'), value: 'technical_description', sortable: false }] : []),
        { text: this.$t('Actions'), value: 'actions', sortable: false},
      ]
    }
  },
  methods: {
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
    async fetchItems(){
      this.loading_items = true
      const { sortBy, sortDesc, page, itemsPerPage } = this.options
      /** console.log(">>>>>>> sortBy: ", sortBy) */
      /** console.log(">>>>>>> sortDesc: ", sortDesc) */
      /** console.log(">>>>>>> page front: ", page) */
      /** console.log(">>>>>>> itemsPerPage front: ", itemsPerPage) */
      let query_strings = ""
      query_strings += sortBy[0] ? `sort_by=${sortBy[0]}&` : ''
      query_strings += sortDesc[0] ? `sort_desc=${sortDesc[0]}&` : ''
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
      /** console.log(">>>>>>> items: ", items) */
      /** console.log(">>>>>>> current_page: ", current_page) */
      /** console.log(">>>>>>> lastPage: ", lastPage) */
      /** console.log(">>>>>>> total: ", total) */
      if (items) {
        this.items = items
        this.totalItems = total
      }
      this.loading_items = false
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

    // List functions
    deleteItem(itemToDelete) {
      this.items = this.items.filter((item) => item.item_code != itemToDelete.item_code);
    },
    //Prite Item Functions

    itemIsAlreadyAdded(item_compound_id){
      return this.price_items.some(el=>el.item.item_compound_id === item_compound_id)
    },
  },

  validations: {
    // Search items Filter
    filter__item_code: {
      slugFieldValidator, 
      maxLength: maxLength(15)
    },
    filter__item_description: { 
      maxLength: maxLength(60)
    },
  },

  computed:{
    itemCodeToSearchItemsErrors() {
      const errors = [];
      if (!this.$v.filter__item_code.$dirty) return errors;
      !this.$v.filter__item_code.slugFieldValidator && errors.push(this.$t('SlugFieldErrorMessage'));
      !this.$v.filter__item_code.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 15));
      return errors;
    },
    itemDescriptionToSearchItemsErrors() {
      const errors = [];
      if (!this.$v.filter__item_description.$dirty) return errors;
      !this.$v.filter__item_description.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 60));
      return errors;
    },

  },

  watch: {
    options: {
      handler () {
        /** console.log(">>>>>>> $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$") */
        this.fetchItems()
      },
      deep: true,
    },
  },

  mounted() {
    /** console.log('>>>>>>>>>>>>>>>>>> CDN url: ', this.cdn_url) */
    if (this.itsForAdminItemPage){
      this.filter__company = this.companies[0]
    }
    else if (this.itsForPriceItems){
      this.filter__company = this.companies.find(el=>el.company_compound_id === this.price_table.company.company_compound_id)
    }
    // The function below will not run another api call. It's just for set the default filter values
    this.fetchCategoriesToSearchItems() 
  }
}
</script>

<style>

</style>
