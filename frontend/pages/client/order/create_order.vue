<template>
  <p v-if="$fetchState.pending">{{$t('Fetching_data')}}</p>
  <p v-else-if="$fetchState.error">{{$t('Error_fetching_data')}}</p>
  <div v-else>
    <div class="ma-3">
      <v-row v-if="establishment && price_table" class="ma-1">
        <v-col cols="3">
          <p><b>{{$t('Company')}}</b>: {{establishment.company_name}} - {{establishment.company.split('*')[1]}}</p>
        </v-col>
        <v-col cols="4">
          <p><b>{{$t('Establishment')}}</b>: {{establishment.name}} - {{establishment.establishment_code}} - {{establishment.cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5")}}</p> 
        </v-col>
        <v-col cols="2">
          <p><b>{{$t('Client')}}</b>: {{$store.state.user.currentUser.client_name}} - {{$store.state.user.currentUser.client.split('*')[2]}}</p>
        </v-col>
        <v-col cols="3">
          <p><b>{{$t('Price_table')}}</b>: {{price_table.description}} - {{price_table.table_code}}</p>
        </v-col>
      </v-row>
      <v-card outlined>
        <!-- Search bar -->
        <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Add item')}}</v-card-title>
        <v-card-text class="mt-3">
          <v-container fluid>
            <v-row no-gutters>
              <v-col cols="3">
                <v-text-field
                  :error-messages="defaultQuantityErrors"
                  :label="$t('Quantity')"
                  v-model.trim="default_quantity"
                  @keydown.enter.prevent=""
                  @blur="$v.default_quantity.$touch()"
                  class="mr-2"
                />
              </v-col>
              <v-col cols="5">
                <v-text-field
                  :label="$t('Item code')"
                  :error-messages="itemCodeToSearchErrors"
                  v-model.trim="item_code_to_search"
                  @keydown.enter.prevent="searchOnePriceItemToMakeOrder"
                  @blur="$v.item_code_to_search.$touch()"
                />
              </v-col>
              <v-col cols="3" style="display: flex; justify-content: center;">
                <v-btn
                  class="mt-3"
                  color="primary"
                  :loading="loading"
                  :disabled="loading"
                  @click="searchOnePriceItemToMakeOrder"
                >{{$t('Add')}}</v-btn>
              </v-col>
              <v-col cols="1" style="display: flex; align-items: center;">
                <v-icon @click="searchIconFunction" large>
                  mdi-magnify
                </v-icon >
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>

        <!-- Ordered items -->
        <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Ordered Items')}}</v-card-title>
        <v-card-text>
          <v-container fluid>
            <v-data-table
              :headers="ordered_items_headers"
              :items="ordered_items__array"
              class="elevation-1"
              item-key="item.$model.item_compound_id"
            >
              <template v-slot:item.image="{ item }">
                <v-img
                  contain
                  width="115px"
                  height="87px"
                  :lazy-src="$store.state.CDNBaseUrl + '/media/images/items/defaultimage.jpeg'"
                  :src="getImageUrl(item.item.$model.image)"
                ></v-img>
              </template>
              <template v-slot:item.item_code="{ item }">
                <p>{{item.item.$model.item_compound_id.split('*')[2]}}</p>
              </template>
              <template v-slot:item.item_description="{ item }">
                <p>{{item.item.$model.description}}</p>
              </template>
              <!-- <template v-slot:item.category="{ item }"> -->
                <!-- <p>{{item.category.$model}}</p> -->
              <!-- </template> -->
              <template v-slot:item.unit="{ item }">
                <p>{{item.item.$model.unit}}</p>
              </template>
              <template v-slot:item.unit_price="{ item }">
                <p>{{getRealMask(Number(item.unit_price.$model))}}</p>
              </template>
              <template v-slot:item.quantity="{ item }">
                <v-text-field
                  v-model.trim="item.quantity.$model"
                  :error-messages="item.errors.$model"
                  :label="$t('Quantity')"
                  @keydown.enter.prevent=""
                  @blur="quantityErrors(item)"
                  type="number"
                  step="0.01"
                  min="0.01"
                  max="999999999.99"
                />
              </template>
              <template v-slot:item.total="{ item }">
                <p>{{getRealMask(item.quantity.$model * item.unit_price.$model)}}</p>
              </template>
              <template v-slot:item.remove_item="{ item }">
                <div style="display:flex; align-items: center; justify-content: center;">
                  <v-icon @click="removeItem(item.item.$model.item_compound_id)" color="red" large>
                    mdi-close-circle-outline
                  </v-icon >
                </div>
              </template>
              <!-- Footer -->
              <template slot="body.append">
                  <tr class="black--text">
                      <th class="title">Total:</th>
                      <th class="title"></th>
                      <th class="title"></th>
                      <th class="title"></th>
                      <th class="title"></th>
                      <th class="title"></th>
                      <th class="title"> {{ getRealMask(getOrderTotal()) }}</th>
                  </tr>
              </template>
            </v-data-table>
          </v-container>
        </v-card-text>
      </v-card>
      <!-- Submit Form -->
      <v-card
        class="mx-auto"
      >
        <v-card-text>
          <!-- Note -->
          <v-textarea
            outlined
            :label="$t('Note')"
            v-model.trim="note"
            :error-messages="noteErrors"
            @blur="$v.note.$touch()"
            class="mb-3"
          />
          <!-- Submit -->
          <v-btn
            class="mt-3"
            color="primary"
            type="submit"
            :loading="loading"
            :disabled="loading"
            @click="makeOrder('1')"
          >{{$t('Save')}}</v-btn>
          <v-btn
            class="mt-3"
            color="primary"
            type="submit"
            :loading="loading"
            :disabled="loading"
            @click="makeOrder('2')"
          >{{$t('Transfer')}}</v-btn>
        </v-card-text>
      </v-card>

      <!-- Search Items Dialog -->
      <v-dialog v-model="show_search_dialog" :retain-focus="false" max-width="75%">
        <v-card>
          <v-card-title style="font-size: 1.3rem; font-weight: 400; line-height: 1rem">{{$t('Search Items')}}</v-card-title>
          <v-card-text class="mt-2">
            <v-container fluid>
              <v-select
                v-model="filter__category"
                :label="$t('Category')"
                :items="categories"
                :item-text="(x) => x.category_compound_id ? x.category_compound_id.split('*')[2] + ' - ' + x.description : $t(x.description)"
                return-object
              ></v-select>
              <v-text-field
                :label="$t('Item description')"
                v-model.trim="filter__item_description"
              />
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn 
              class="blue--text darken-1" 
              text 
              @click="options['page'] = 1; searchPriceItemsToMakeOrder()"
              :loading="loading_items"
              :disabled="loading_items"
            >{{$t('Search')}}</v-btn>
            <v-btn class="blue--text darken-1" text @click="show_search_dialog = false">{{$t('Close')}}</v-btn>
          </v-card-actions>

          <v-card-title style="font-size: 1.3rem; font-weight: 400; line-height: 1rem">{{$t('Search Results')}}</v-card-title>
          <v-card-text>
            <v-container fluid class="mt-2">
                <v-data-table
                  :headers="searched_items_headers"
                  :items="search_results"
                  class="elevation-1"
                  item-key="item.item.item_compound_id"
                  :options.sync="options"
                  :server-items-length="totalItems"
                  :loading="loading_items"
                  :footer-props="{'items-per-page-options': [5, 10, 15]}"
                >
                  <template v-slot:item.image="{ item }">
                    <v-img
                      contain
                      width="115px"
                      height="87px"
                      :lazy-src="$store.state.CDNBaseUrl + '/media/images/items/defaultimage.jpeg'"
                      :src="getImageUrl(item.item.image)"
                    ></v-img>
                  </template>
                  <template v-slot:item.item_code="{ item }">
                    <p>{{item.item.item_compound_id.split('*')[2]}}</p>
                  </template>
                  <template v-slot:item.item_description="{ item }">
                    <p>{{item.item.description}}</p>
                  </template>
                  <!-- <template v-slot:item.category="{ item }"> -->
                    <!-- <p>{{item.category}}</p> -->
                  <!-- </template> -->
                  <template v-slot:item.unit_price="{ item }">
                    <p>{{getRealMask(Number(item.unit_price))}}</p>
                  </template>
                  <template v-slot:item.unit="{ item }">
                    <p>{{item.item.unit}}</p>
                  </template>
                  <template v-slot:item.add_item="{ item }">
                    <div style="display:flex; align-items: center; justify-content: center;">
                      <v-icon @click="addItem(item)" color="green" large v-if="!itemIsAlreadyInTheOrder(item.item.item_compound_id)">
                        mdi-plus
                      </v-icon >
                    </div>
                  </template>
                </v-data-table>
            </v-container>
          </v-card-text>
        </v-card>
      </v-dialog>

      <!-- Select Establishment Dialog -->
      <v-dialog :value="show_select_establishment_dialog" :retain-focus="false" max-width="500px" persistent>
        <v-card>
          <v-card-title>{{$t('Select an establishment')}}</v-card-title>
          <v-card-text>
            <v-container fluid>
              <!-- Establishment -->
              <v-row align="center">
                <v-col
                  class="d-flex"
                  cols="12"
                  sm="6"
                >
                  <v-select
                    v-model="establishment"
                    :label="$t('Establishment')"
                    :items="establishments"
                    :item-text="(x) => x.establishment_compound_id.split('*')[2] + ' - ' + x.name + ' (' + $t('Company') + ': '  + x.company + ' - ' + x.company_name + ')'"
                    :item-value="(x) => x"
                    @change="show_select_establishment_dialog = false"
                  ></v-select>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <!-- <v-card-actions> -->
            <!-- <v-spacer /> -->
            <!-- <v-btn class="blue--text darken-1" text @click="show_select_establishment_dialog = false">{{$t('Close')}}</v-btn> -->
          <!-- </v-card-actions> -->
        </v-card>
      </v-dialog>

      <!-- Show 'You have no establishments to buy' message -->
      <v-dialog :value="show_you_have_no_establishments_to_buy_message" :retain-focus="false" max-width="500px" persistent>
        <v-card>
          <v-card-title>{{$t('You have no establishments')}}</v-card-title>
          <v-card-text>
            <v-container fluid>
              <p>{{$t('It seems that you have no establishments which you can buy at this moment.')}}</p>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn class="blue--text darken-1" text @click="$router.push('/')">{{$t('Come back to Homepage')}}</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

    </div>
  </div>
</template>

<script>
import {
  required,
  decimal,
  maxLength,
  minValue,
  maxValue,
} from "vuelidate/lib/validators";
import {validationMixin} from "vuelidate";
import {decimal_only_2places, slugFieldValidator} from "~/helpers/validators"
import {mask} from 'vue-the-mask'

let default_category_value = {category_compound_id: null, description: 'All'}
export default {
  name: "CreateOrder",
  middleware: ["authenticated"],
  components: {
    "price-table-edit-menu": require("@/components/admin/item/price-table-edit-menu.vue").default,
  },
  mixins: [validationMixin],
  directives: {mask},
  data() {
    return {
    // Order Fields ---------
      establishment: null,
      note: "",
      ordered_items: [],
    // ---------
      search_results: [],
      establishments: [],
      categories: [default_category_value, ],
      price_table: null,
      default_quantity: 1,
      // ---
      search_dialog_was_already_open: false,
      options: {},
      totalItems: 0,
      loading_items: false,
      item_code_to_search: "",
      filter__category: default_category_value,
      filter__item_description: "",
      loading: false,
      show_select_establishment_dialog: false,
      show_you_have_no_establishments_to_buy_message: false,
      show_search_dialog: false,
      ordered_items_headers: [
        { text: this.$t('Image'), value: 'image', sortable: false },
        { text: this.$t('Code'), value: 'item_code', sortable: false },
        { text: this.$t('Description'), value: 'item_description', width: '100%', sortable: false },
        /** { text: this.$t('Category'), value: 'category' }, */
        { text: this.$t('Unit price'), value: 'unit_price', align: 'right', sortable: false },
        { text: this.$t('Quantity'), value: 'quantity', width: '10%', sortable: false},
        { text: this.$t('Unit'), value: 'unit', sortable: false },
        { text: 'Total', value: 'total', align: 'right', sortable: false },
        { text: this.$t('Remove item'), value: 'remove_item', sortable: false },
      ],
      searched_items_headers: [
        { text: this.$t('Image'), value: 'image', sortable: false,  },
        { text: this.$t('Code'), value: 'item_code', sortable: true },
        { text: this.$t('Description'), value: 'item_description', sortable: true },
        /** { text: this.$t('Category'), value: 'category' }, */
        { text: this.$t('Unit'), value: 'unit', sortable: false },
        { text: this.$t('Unit price'), value: 'unit_price', sortable: true },
        { text: this.$t('Add item'), value: 'add_item', sortable: false },
      ]
    };
  },

  async fetch() {
    // Fetch Client Establishments
    let establishments = await this.$store.dispatch("order/fetchClientEstabsToCreateOrder"); 
     /** EX: {"establishment_compound_id":"123*123*123","establishment_code":"123","name":"PHSW-estab", */
     /** "company":"123*123","company_name":"PHSW-comp"} */
    if (establishments){
      this.establishments = establishments
      /** console.log(">>>>>>> this.establishments: ", this.establishments) */
      if (this.establishments.length === 1){
        this.establishment = this.establishments[0]
      }
      else if (this.establishments.length > 1){
        this.show_select_establishment_dialog = true
      }
      else if (this.establishments.length === 0){
        this.show_you_have_no_establishments_to_buy_message = true
      }
    }
  },

  methods: {
    async makeOrder(status){
      this.$v.orderInfoGroup.$touch();
      if (this.$v.orderInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t('Please_fill_the_form_correctly'), alertType: "error" }, { root: true })
      } else {
        this.loading = true
        // The API to make order must receive item_compound_id as value for the item field.
        let ordered_items_fixed = this.ordered_items.map(el=>{
          let element = JSON.parse(JSON.stringify(el)) // This is doing a Deep copy 
          element.item = element.item.item_compound_id
          return element
        })
        let response = await this.$store.dispatch("order/makeOrder", {
          establishment: this.establishment.establishment_compound_id,
          ordered_items: ordered_items_fixed,
          status: status,
          note: this.note,
        })
        // Don't reset ordered_items and default_quantity if there is errors
        if (response === 'ok'){
          this.ordered_items = []
          this.default_quantity = 1
          this.note = ""
        }
      this.loading = false;
      }
    },

    async searchOnePriceItemToMakeOrder(){
      /** if (!this.item_code_to_search){ */
        /** this.$store.dispatch("setAlert", { message: this.$t('Plese fill the item code field.'), alertType: "warning" }, { root: true }) */
      /** } */
      this.$v.defaultQuantity.$touch();
      if (this.$v.defaultQuantity.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
      } 
      else {
        this.loading = true
        if (this.ordered_items.some(el=>el.item.item_compound_id.split('*')[2] === this.item_code_to_search)){
          this.$store.dispatch("setAlert", { message: this.$t('This item is already added to the order.'), alertType: "warning" }, { root: true })
        }
        else{
          let search_result = await this.$store.dispatch("order/searchOnePriceItemToMakeOrder", 
            {establishment: this.establishment.establishment_compound_id, item_code: this.item_code_to_search}
          )
          if (search_result){
            this.ordered_items.push({...search_result, quantity: this.default_quantity, errors: []})
          }
        }
        this.loading = false
      }
    },

    async searchPriceItemsToMakeOrder(){
      this.loading_items = true
      const { sortBy, sortDesc, page, itemsPerPage } = this.options
      let query_strings = ""
      query_strings += sortBy[0] ? `sort_by=${sortBy[0]}&` : ''
      query_strings += sortDesc[0] ? `sort_desc=${sortDesc[0]}&` : ''
      query_strings += `page=${page}&`
      query_strings += `items_per_page=${itemsPerPage}&`
      query_strings += this.filter__category.category_compound_id ? `category=${this.filter__category.category_compound_id}&` : ''
      query_strings += this.filter__item_description ? `item_description=${this.filter__item_description}&` : ''
      if (query_strings !== "") {
        query_strings = query_strings.slice(0, -1) // remove the last '&' character
      }
      let {price_items, current_page, lastPage, total} = await this.$store.dispatch("order/searchPriceItemsToMakeOrder", 
        {establishment: this.establishment.establishment_compound_id, query_strings: query_strings });
      if (price_items){
        this.search_results = price_items
        this.totalItems = total
      }
      this.loading_items = false
    },

    async fetchCategoriesToMakeOrderAndGetPriceTableInfo(){
      let data = await this.$store.dispatch("order/fetchCategoriesToMakeOrderAndGetPriceTableInfo",
        this.establishment.establishment_compound_id);
      let {categories, price_table} = data
      if (categories){
        this.categories.push(...categories) 
      }
      this.price_table = price_table
    },

    // Validate item
    quantityErrors(v) {
      const errors = [];
      /** if (!v.unit_price.$dirty){ */
      /** } */
      !v.quantity.required && errors.push(this.$t("This_field_is_required"));
      !v.quantity.decimal && errors.push(this.$t("DecimalErrorMessage"));
      !v.quantity.minValue && errors.push(this.$formatStr(this.$t("This_value_must_be_greater_than_X"), 0.01));
      !v.quantity.maxValue && errors.push(this.$formatStr(this.$t("This_value_must_be_less_than_X"), 999999999.99));
      !v.quantity.decimal_only_2places && errors.push(this.$t("DecimalErrorMessage2Places"));
      v.errors.$model = errors;
    },

    // masked_price: "R$ 1.000,00" is written over unit_price as "1000.00"
    /** getMaskedTotal(value){ */
      /** return value.replace('R$ ', '').replace(/\./gi,'').replace(',','.') */
    /** }, */

    getRealMask(value){
      return value.toLocaleString('pt-br',{style: 'currency', currency: 'BRL'})
    },
    // Get order Total
    getOrderTotal(){
      return this.ordered_items.reduce((previous, current)=>{
        return (typeof previous == 'number' ? previous : (previous.unit_price * previous.quantity)) + (current.unit_price * current.quantity)
      }, 0)
    },
    // Add and remove item functions
    removeItem(item_compound_id){
      this.ordered_items = this.ordered_items.filter((obj)=> obj.item.item_compound_id !== item_compound_id)
    },
    addItem(price_item){
      this.ordered_items.push({...price_item, quantity: this.default_quantity, errors: []})
    },
    // Image
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
    // Check if can add item to order
    itemIsAlreadyInTheOrder(item_compound_id){
      return this.ordered_items.some(el=>el.item.item_compound_id === item_compound_id)
    },

    searchIconFunction(){
      this.show_search_dialog = true
      this.search_dialog_was_already_open = true
      // This will happen if the client user click the search icon for the first tame and the user has only one establishment
      if (this.categories.length == 1){
        this.fetchCategoriesToMakeOrderAndGetPriceTableInfo()
      }
    }
  },

  validations: {
    note: {
      maxLength: maxLength(800)
    },
    default_quantity: {
      required,
      decimal,
      decimal_only_2places,
      maxValue: maxValue(999999999.99),
      minValue: minValue(0.01),
    },
    item_code_to_search: {
      required, 
      slugFieldValidator, 
      maxLength: maxLength(15)
    },
    ordered_items: {
      $each: {
        item: {},
        item_description: {},
        category: {},
        quantity: {
          required,
          decimal,
          decimal_only_2places,
          maxValue: maxValue(999999999.99),
          minValue: minValue(0.01),
        },
        unit_price: {},
        unit: {},
        image: {},
        errors: {},
      }
    },
    orderInfoGroup: [
      "note",
      "ordered_items"
    ],
    defaultQuantity: ["default_quantity", "item_code_to_search"]
  },

  computed: {
    noteErrors() {
      const errors = [];
      if (!this.$v.note.$dirty) return errors;
      !this.$v.note.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 800));
      return errors;
    },
    defaultQuantityErrors() {
      const errors = [];
      if (!this.$v.default_quantity.$dirty) return errors;
      !this.$v.default_quantity.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.default_quantity.decimal && errors.push(this.$t("DecimalErrorMessage"));
      !this.$v.default_quantity.decimal_only_2places && errors.push(this.$t("DecimalErrorMessage2Places"));
      !this.$v.default_quantity.minValue && errors.push(this.$formatStr(this.$t("This_value_must_be_greater_than_X"), 0.01 ));
      !this.$v.default_quantity.maxValue && errors.push(this.$formatStr(this.$t("This_value_must_be_less_than_X"), 999999999.99));
      return errors;
    },
    itemCodeToSearchErrors() {
      const errors = [];
      if (!this.$v.item_code_to_search.$dirty) return errors;
      !this.$v.item_code_to_search.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.item_code_to_search.slugFieldValidator && errors.push(this.$t('SlugFieldErrorMessage'));
      !this.$v.item_code_to_search.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 15));
      return errors;
    },
    ordered_items__array(){
      return Object.values(this.$v.ordered_items.$each.$iter)
    },
  },

  /** mounted() { */
  /** }, */

  watch: {
    options: {
      handler () {
        if (this.search_dialog_was_already_open){
          this.searchPriceItemsToMakeOrder()
        }
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
/* This is for the ordered_items */
.container--fluid {
  margin-top: -20px;
} 
</style>
