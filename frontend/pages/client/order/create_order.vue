<template>
  <p v-if="$fetchState.pending">{{$t('Fetching_data')}}</p>
  <p v-else-if="$fetchState.error">{{$t('Error_fetching_data')}}</p>
  <div v-else>
    <div class="ma-3">
      <v-card outlined>
        <!-- Search bar -->
        <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Add item')}}</v-card-title>
        <v-card-text>
          <v-container fluid>
            <v-row>
              <v-text-field
                :error-messages="defaultQuantityErrors"
                :label="$t('Quantity')"
                v-model="default_quantitiy"
                @keydown.enter.prevent=""
                @blur="$v.default_quantitiy.$touch()"
              />
              <v-text-field
                :label="$t('Item code')"
                v-model="item_code_to_search"
                @keydown.enter.prevent=""
              />
              <v-btn
                class="mt-3"
                color="primary"
                :loading="loading"
                :disabled="loading"
                @click="searchOnePriceItemToMakeOrder"
              >{{$t('Add Item')}}</v-btn>
              <v-icon @click="show_search_dialog = true">
                mdi-magnify
              </v-icon >
            </v-row>
          </v-container>
        </v-card-text>

        <!-- Ordered items -->
        <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Ordered Items')}}</v-card-title>
        <v-card-text>
          <v-container fluid>
            <v-row
              v-for="(v, key) in $v.ordered_items.$each.$iter"
              :key="key"
            >
              <p>Cod. Item: {{v.item.$model.split('&')[2]}}</p>
              <p>Item Description: {{v.item_description.$model}}</p>
              <p>Item category: {{v.category.$model}}</p>
              <p>Unit Price: {{v.unit_price.$model}}</p>
              <v-text-field
                v-model="v.quantity.$model"
                :error-messages="v.errors.$model"
                :label="$t('Quantity')"
                @keydown.enter.prevent=""
                @blur="quantityErrors(v)"
              />
                <p>Total: {{$t('Currency_symbol')}} </p>
                <input 
                  disabled 
                  type="text" 
                  :value="v.quantity.$model * v.unit_price.$model" 
                  style="color: #000000DE; width: 130px"
                  v-money="money"
                />
              <v-icon @click="removeItem(v.item.$model)">
                mdi-minus
              </v-icon >
            </v-row>
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
      <v-dialog v-model="show_search_dialog" :retain-focus="false" max-width="500px">
        <v-card>
          <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Search Result')}}</v-card-title>
          <v-card-text>
            <v-container fluid>
              <v-select
                v-model="filter__category"
                :label="$t('Category')"
                :items="categories"
                :item-text="(x) => x === 'all' ? $t('All') : x.category_compound_id + ' - ' + x.description"
                :item-value="(x) => x === 'all' ? 'all' : x.category_compound_id"
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

          <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Search Results')}}</v-card-title>
          <v-card-text>
            <v-container fluid>
              <v-list-item-group>
                <div
                  v-for="(price_item, key) in priceItemsToAdd"
                  :key="key"
                >
                  <v-list-item>
                    <v-list-item-content>
                      /** price_item.item is a item_compound_id */
                      <v-list-item-title>{{price_item.item.split('&')[2] + ' - ' + price_item.item_description}}</v-list-item-title>
                    </v-list-item-content>

                    <v-list-item-action>
                      <v-icon @click="addItem(price_item)">
                        mdi-plus
                      </v-icon >
                    </v-list-item-action>
                  </v-list-item>
                  <v-divider
                    v-if="key < priceItemsToAdd.length - 1"
                    :key="key"
                  ></v-divider>
                </div>
              </v-list-item-group>
            </v-container>
          </v-card-text>
        </v-card>
      </v-dialog>

      <!-- Select Establishment Dialog -->
      <v-dialog :value="show_select_establishment_dialog" :retain-focus="false" max-width="500px" persistent>
        <v-card>
          <v-card-title>{{'Select an establishment'}}</v-card-title>
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
                    :item-text="(x) => x.establishment_compound_id + ' - ' + x.name"
                    :item-value="(x) => x"
                    @change="fetchCategoriesToMakeOrder"
                  ></v-select>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn class="blue--text darken-1" text @click="show_select_establishment_dialog = false">{{$t('Close')}}</v-btn>
          </v-card-actions>
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
            <v-btn class="blue--text darken-1" text @click="$router.push('/')">{{$t('Come back to home')}}</v-btn>
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
import {money} from "~/helpers/validators"
import {VMoney} from 'v-money'

export default {
  middleware: ["authenticated"],
  components: {
    "price-table-edit-menu": require("@/components/admin/item/price-table-edit-menu.vue").default,
  },
  mixins: [validationMixin],
  directives: {money: VMoney},
  data() {
    return {
    // Order Fields ---------
      establishment: null,
      note: "",
      ordered_items: [],
      // EX {item: '123$123$111111', item_description: "Nice Item", category: "Category asdf", unit_price: 1055.55, quantity: 5.33, errors: []} 
    // ---------
      search_result: [],
      // EX priceItemObj: {item: '123$123$111111', item_description: 'Nice Item', category: 'category 1', unit_price: 1055.55} 
      establishments: [],
      categories: ['all', ],
      default_quantitiy: 1,
      item_code_to_search: "",
      filter__category: 'all',
      filter__item_description: "",
      loading: false,
      money: money,
      item_compound_id_prefix: "",
      show_select_establishment_dialog: false,
      show_you_have_no_establishments_to_buy_message: false,
      show_search_dialog: false,
    };
  },

  async fetch() {
    // Fetch Client Establishments
    let establishments = await this.$store.dispatch("order/fetchClientEstabsToCreateOrder"); 
     /** EX: {"establishment_compound_id":"123&123&123","establishment_code":"123","name":"PHSW-estab", */
     /** "company":"123&123","company_name":"PHSW-comp"} */
    if (establishments){
      this.establishments = establishments
      console.log(">>>>>>> this.establishments: ", this.establishments)
      if (this.establishments.length === 1){
        this.establishment = this.establishments[0]
        this.fetchCategoriesToMakeOrder()
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
        await this.$store.dispatch("order/makeOrder", {
          establishment: this.establishment.establishment_compound_id,
          ordered_items: this.ordered_items,
          status: '1',
          note: this.note,
      })
      this.loading = false;
      }
    },

    async saveOrderAndTransfer(){
      this.$v.orderInfoGroup.$touch();
      if (this.$v.orderInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t('Please_fill_the_form_correctly'), alertType: "error" }, { root: true })
      } else {
        this.loading = true;
         await this.$store.dispatch("order/makeOrder", {
          establishment: this.establishment.establishment_compound_id,
          ordered_items: this.ordered_items,
          status: '2',
          note: this.note,
        });
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
            this.item_compound_id_prefix = search_result.item.split('&')[0] + '&' + search_result.item.split('&')[1] + '&'
          }
          this.ordered_items.push({item: search_result.item, item_description: search_result.item_description, 
            category: search_result.category, unit_price: search_result.unit_price, quantity: this.default_quantitiy, errors: []}) 
        // EX {item: '123$123$111111', item_description: 'Item 01', category: 'This category', unit_price: 1055.55, quantity: 1, errors: []} 
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
      let filter_parameters = {establishment: this.establishment.establishment_compound_id, category: this.filter__category, 
        item_description: this.filter__item_description}
      let search_result = await this.$store.dispatch("order/searchPriceItemsToMakeOrder", filter_parameters);
      if (search_result){
        if (!this.item_compound_id_prefix){
          // TODO when i change the establishment it can change the item_table (clear this field in this case)
          this.item_compound_id_prefix = search_result.item.split('&')[0] + '&' + search_result.item.split('&')[1] + '&'
        }
        this.search_result = search_result
      }
    },

    async fetchCategoriesToMakeOrder(){
      // TODO add groups
      let categories = await this.$store.dispatch("order/fetchCategoriesToMakeOrder", this.establishment.establishment_compound_id);
      if (categories){
        this.categories.push(...categories) 
      }
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

    // Add and remove item functions
    removeItem(item_compound_id){
      this.ordered_items = this.ordered_items.filter((obj)=> obj.item !== item_compound_id)
    },
    addItem(price_item){
      this.ordered_items = this.ordered_items.push({item: price_item.item, item_description: price_item.item_description, 
        category: price_item.category, unit_price: price_item.unit_price, quantity: this.default_quantitiy, errors: []})
    },
  },

  validations: {
    note: {
      maxLength: maxLength(800)
    },
    default_quantitiy: {
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
      if (!this.$v.default_quantitiy.$dirty) return errors;
      !this.$v.default_quantitiy.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.default_quantitiy.decimal && errors.push(this.$t("DecimalErrorMessage"));
      !this.$v.default_quantitiy.minValue && errors.push(this.$formatStr(this.$t("This_value_must_be_greater_than_X"), 0.01 ));
      !this.$v.default_quantitiy.maxValue && errors.push(this.$formatStr(this.$t("This_value_must_be_less_than_X"), 999999999.99));
      return errors;
    },
    // Price Items to Add
    priceItemsToAdd(){
      return this.search_result.filter((price_item)=> {
        let return_value = true
        let ordered_items = this.ordered_items
        for (const prop in ordered_items){
          if (ordered_items[prop].item === price_item.item){
            return_value = false
          }
        }
        return return_value
      })
    }
  },

  /** mounted() { */
    /** this.item_compound_id_prefix =  */
    /** console.log('>>>>>>>>>>>>>>>>>>', this.item_compound_id_prefix) */
    /** console.log('>>>>>>>>>>>>>>>>>>', this.) */
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
