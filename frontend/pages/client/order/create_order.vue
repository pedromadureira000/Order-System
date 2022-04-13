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
                  v-model="default_quantity"
                  @keydown.enter.prevent=""
                  @blur="$v.default_quantity.$touch()"
                  class="mr-2"
                />
              </v-col>
              <v-col cols="5">
                <v-text-field
                  :label="$t('Item code')"
                  v-model="item_code_to_search"
                  @keydown.enter.prevent="searchOnePriceItemToMakeOrder"
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
                <v-icon @click="show_search_dialog = true" large>
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
              item-key="item.$model"
            >
              <template v-slot:item.image="{ item }">
                <v-img
                  contain
                  width="115px"
                  height="87px"
                  :lazy-src="$store.state.CDNBaseUrl + '/media/images/items/defaultimage.jpeg'"
                  :src="getImageUrl(item.image.$model)"
                ></v-img>
              </template>
              <template v-slot:item.item_code="{ item }">
                <p>{{item.item.$model.split('*')[2]}}</p>
              </template>
              <template v-slot:item.item_description="{ item }">
                <p>{{item.item_description.$model}}</p>
              </template>
              <template v-slot:item.category="{ item }">
                <p>{{item.category.$model}}</p>
              </template>
              <template v-slot:item.unit="{ item }">
                <p>{{item.unit.$model}}</p>
              </template>
              <template v-slot:item.unit_price="{ item }">
                <p>{{getRealMask(Number(item.unit_price.$model))}}</p>
              </template>
              <template v-slot:item.quantity="{ item }">
                <v-text-field
                  v-model="item.quantity.$model"
                  :error-messages="item.errors.$model"
                  :label="$t('Quantity')"
                  @keydown.enter.prevent=""
                  @blur="quantityErrors(item)"
                />
              </template>
              <template v-slot:item.total="{ item }">
                <p>{{getRealMask(item.quantity.$model * item.unit_price.$model)}}</p>
              </template>
              <template v-slot:item.remove_item="{ item }">
                <div style="display:flex; align-items: center; justify-content: center;">
                  <v-icon @click="removeItem(item.item.$model)" color="red" large>
                    mdi-close-circle-outline
                  </v-icon >
                </div>
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
            @click="saveOrder"
          >{{$t('Save')}}</v-btn>
          <v-btn
            class="mt-3"
            color="primary"
            type="submit"
            :loading="loading"
            :disabled="loading"
            @click="saveOrderAndTransfer"
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
                :item-text="(x) => x.category_compound_id === 'all' ? $t(x.description) : x.category_compound_id + ' - ' + x.description"
                :item-value="(x) => x.category_compound_id"
              ></v-select>
              <v-text-field
                :label="$t('Item description')"
                v-model="filter__item_description"
              />
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn class="blue--text darken-1" text @click="searchPriceItemsToMakeOrder">{{$t('Search')}}</v-btn>
            <v-btn class="blue--text darken-1" text @click="show_search_dialog = false">{{$t('Close')}}</v-btn>
          </v-card-actions>

          <v-card-title style="font-size: 1.3rem; font-weight: 400; line-height: 1rem">{{$t('Search Results')}}</v-card-title>
          <v-card-text>
            <v-container fluid class="mt-2">
                <v-data-table
                  :headers="searched_items_headers"
                  :items="priceItemsToAdd"
                  class="elevation-1"
                  item-key="item"
                >
                  <template v-slot:item.image="{ item }">
                    <v-img
                      contain
                      width="115px"
                      height="87px"
                      :lazy-src="$store.state.CDNBaseUrl + '/media/images/items/defaultimage.jpeg'"
                      :src="getImageUrl(item.image)"
                    ></v-img>
                  </template>
                  <template v-slot:item.item_code="{ item }">
                    <p>{{item.item.split('*')[2]}}</p>
                  </template>
                  <template v-slot:item.item_description="{ item }">
                    <p>{{item.item_description}}</p>
                  </template>
                  <template v-slot:item.category="{ item }">
                    <p>{{item.category}}</p>
                  </template>
                  <template v-slot:item.unit="{ item }">
                    <p>{{item.unit}}</p>
                  </template>
                  <template v-slot:item.unit_price="{ item }">
                    <p>{{getRealMask(Number(item.unit_price))}}</p>
                  </template>
                  <template v-slot:item.add_item="{ item }">
                    <div style="display:flex; align-items: center; justify-content: center;">
                      <v-icon @click="addItem(item)" color="green" large>
                        mdi-plus
                      </v-icon >
                    </div>
                  </template>
                </v-data-table>
              <!-- ------------------------ -->
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
                    @change="show_select_establishment_dialog = false; fetchCategoriesToMakeOrderAndGetPriceTableInfo()"
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
          <v-card-title>{{'You have no establishments'}}</v-card-title>
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
    <v-btn label="Test" @click="gambiarra2"> test</v-btn>

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
import {money} from "~/helpers/validators"
import {VMoney} from 'v-money'
import {mask} from 'vue-the-mask'

let default_category_value = {category_compound_id: 'all', description: 'All'}
export default {
  middleware: ["authenticated"],
  components: {
    "price-table-edit-menu": require("@/components/admin/item/price-table-edit-menu.vue").default,
  },
  mixins: [validationMixin],
  directives: {money: VMoney, mask},
  data() {
    return {
    // Order Fields ---------
      establishment: null,
      note: "",
      ordered_items: [],
      // EX {item: '123$123$111111', item_description: "Nice Item", category: "Category asdf", unit_price: 1055.55, quantity: 5.33, errors: []} 
    // ---------
      search_results: [],
      // EX priceItemObj: {item: '123$123$111111', item_description: 'Nice Item', category: 'category 1', unit_price: 1055.55} 
      establishments: [],
      categories: [default_category_value, ],
      price_table: null,
      default_quantity: 1,
      item_code_to_search: "",
      filter__category: default_category_value,
      filter__item_description: "",
      loading: false,
      money: money,
      item_compound_id_prefix: "",
      show_select_establishment_dialog: false,
      show_you_have_no_establishments_to_buy_message: false,
      show_search_dialog: false,
      ordered_items_headers: [
        { text: this.$t('Image'), value: 'image' },
        { text: this.$t('Code'), value: 'item_code' },
        { text: this.$t('Description'), value: 'item_description' },
        { text: this.$t('Category'), value: 'category' },
        { text: this.$t('Unit'), value: 'unit' },
        { text: this.$t('Unit price'), value: 'unit_price' },
        { text: this.$t('Quantity'), value: 'quantity' },
        { text: 'Total', value: 'total' },
        { text: this.$t('Remove item'), value: 'remove_item' },
      ],
      searched_items_headers: [
        { text: this.$t('Image'), value: 'image' },
        { text: this.$t('Code'), value: 'item_code' },
        { text: this.$t('Description'), value: 'item_description' },
        { text: this.$t('Category'), value: 'category' },
        { text: this.$t('Unit'), value: 'unit' },
        { text: this.$t('Unit price'), value: 'unit_price' },
        { text: this.$t('Add item'), value: 'add_item' },
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
        this.fetchCategoriesToMakeOrderAndGetPriceTableInfo()
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
    async saveOrder(){
      this.$v.orderInfoGroup.$touch();
      if (this.$v.orderInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t('Please_fill_the_form_correctly'), alertType: "error" }, { root: true })
      } else {
        this.loading = true
        let response = await this.$store.dispatch("order/makeOrder", {
          establishment: this.establishment.establishment_compound_id,
          ordered_items: this.ordered_items,
          status: '1',
          note: this.note,
        })
        // Don't reset ordered_items and default_quantity if there is errors
        if (response === 'ok'){
          this.ordered_items = []
          this.default_quantity = 1
        }
      this.loading = false;
      }
    },

    async saveOrderAndTransfer(){
      this.$v.orderInfoGroup.$touch();
      if (this.$v.orderInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t('Please_fill_the_form_correctly'), alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let response = await this.$store.dispatch("order/makeOrder", {
          establishment: this.establishment.establishment_compound_id,
          ordered_items: this.ordered_items,
          status: '2',
          note: this.note,
        });
        // Don't reset ordered_items and default_quantity if there is errors
        if (response === 'ok'){
          this.ordered_items = []
          this.default_quantity = 1
        }
        this.loading = false;
      }
    },

    async searchOnePriceItemToMakeOrder(){
      if (this.ordered_items.some(el=>el.item === this.item_compound_id_prefix + this.item_code_to_search)){
        this.$store.dispatch("setAlert", { message: this.$t('This item is already added to the order.'), alertType: "warning" }, { root: true })
      }
      else{
        let search_result = await this.$store.dispatch("order/searchOnePriceItemToMakeOrder", 
          {establishment: this.establishment.establishment_compound_id, item_code: this.item_code_to_search}
        )
        if (search_result){
          if (!this.item_compound_id_prefix){
            this.item_compound_id_prefix = search_result.item.split('*')[0] + '*' + search_result.item.split('*')[1] + '*'
          }
          this.ordered_items.push({...search_result, quantity: this.default_quantity, errors: []})
        }
      }
    },

    async searchPriceItemsToMakeOrder(){
          /** let item_already_exists = this.item_group.find(el=>el.establishment === this.establishment.establishment_compound_id) */
          /** if (item_already_exists){ */
            /** this.items = item_already_exists.items */
          /** } */
          /** else{ */
          /** } */
      let filter_parameters = {establishment: this.establishment.establishment_compound_id, category: this.filter__category.category_compound_id, 
        item_description: this.filter__item_description}
      let search_results = await this.$store.dispatch("order/searchPriceItemsToMakeOrder", filter_parameters);
      if (search_results){
        if (!this.item_compound_id_prefix){
          // TODO when i change the establishment it can change the item_table (clear this field in this case)
          let first_item = search_results[0]
          console.log(">>>>>>> first_item: ", first_item)
          if (first_item){
            this.item_compound_id_prefix = first_item.item.split('*')[0] + '*' + first_item.item.split('*')[1] + '*'
          }
        }
        this.search_results = search_results
      }
    },

    async fetchCategoriesToMakeOrderAndGetPriceTableInfo(){
      // TODO add groups
      let {categories, price_table} = await this.$store.dispatch("order/fetchCategoriesToMakeOrderAndGetPriceTableInfo", this.establishment.establishment_compound_id);
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
      v.errors.$model = errors;
    },

    // masked_price: "R$ 1.000,00" is written over unit_price as "1000.00"
    /** getMaskedTotal(value){ */
      /** return value.replace('R$ ', '').replace(/\./gi,'').replace(',','.') */
    /** }, */

    getRealMask(value){
      return value.toLocaleString('pt-br',{style: 'currency', currency: 'BRL'})
    },

    // Add and remove item functions
    removeItem(item_compound_id){
      this.ordered_items = this.ordered_items.filter((obj)=> obj.item !== item_compound_id)
    },
    addItem(price_item){
      this.ordered_items.push({...price_item, quantity: this.default_quantity, errors: []})
    },
    // TEst
    gambiarra2(){
      /** return Array.from(this.$v.ordered_items.$each.$iter.entries()) */
      console.log(">>>>>>> array: ", Array.from(this.$v.ordered_items.$each.$iter))
      console.log(">>>>>>> array: ",  Object.values(this.$v.ordered_items.$each.$iter))
      console.log(">>>>>>> not array: ", this.$v.ordered_items.$each.$iter)
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

  },

  validations: {
    note: {
      maxLength: maxLength(800)
    },
    default_quantity: {
      required,
      decimal,
      maxValue: maxValue(999999999.99),
      minValue: minValue(0.01),

    },
    ordered_items: {
      $each: {
        item: {},
        item_description: {},
        category: {},
        quantity: {
          required,
          decimal,
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
      !this.$v.default_quantity.minValue && errors.push(this.$formatStr(this.$t("This_value_must_be_greater_than_X"), 0.01 ));
      !this.$v.default_quantity.maxValue && errors.push(this.$formatStr(this.$t("This_value_must_be_less_than_X"), 999999999.99));
      return errors;
    },
    // Price Items to Add
    priceItemsToAdd(){
      return this.search_results.filter((price_item)=> {
        let return_value = true
        let ordered_items = this.ordered_items
        for (const prop in ordered_items){
          if (ordered_items[prop].item === price_item.item){
            return_value = false
          }
        }
        return return_value
      })
    },
    ordered_items__array(){
      return Object.values(this.$v.ordered_items.$each.$iter)
    },
  },

  /** mounted() { */
    /** console.log('>>>>>>>>>>>>>>>>>>', this.item_compound_id_prefix) */
  /** } */
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
