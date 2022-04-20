<template>
  <div v-if="order_details_fetched">
    <!-- ========= Edit Order Dialog ============ -->
    <v-dialog :retain-focus="false" v-model="show_edit_dialog" max-width="85%" persistent>
      <v-card>
        <v-card-title>{{$t('Edit Order')}}</v-card-title>
        <!-- Company -->
        <form @submit.prevent="updateOrder" class="ml-3">
          <div style="width: 25%;">
            <v-select
              disabled
              :value="order.company"
              :label="$t('Company')"
              :item-text="(x) => x.company_code + ' - ' + x.name"
              :items="[order.company]"
            ></v-select>
          </div>
        <!-- Establishment -->
          <div style="width: 25%;">
            <v-select
              disabled
              :value="order.establishment"
              :label="$t('Establishment')"
              :item-text="(x) =>  x.establishment_code + ' - ' + x.name"
              :items="[order.establishment]"
            ></v-select>
          </div>
        <!-- Client -->
          <div style="width: 25%;">
            <v-select
              disabled
              :value="order.client"
              :label="$t('Client')"
              :item-text="(x) => x.client_code + ' - ' + x.name"
              :items="[order.client]"
            ></v-select>
          </div>
        <!-- Client user -->
          <div style="width: 25%;">
            <v-select
              disabled
              :value="order.client_user"
              :label="$t('Client User')"
              :item-text="(x) => x.first_name + ' ' + x.last_name + '('+ x.username + ')'"
              :items="[order.client_user]"
            ></v-select>
          </div>
        <!-- Price table -->
          <div style="width: 25%;">
            <v-select
              disabled
              :value="order.price_table"
              :label="$t('Price_Table')"
              :item-text="(x) => x.table_code + ' - ' + x.description"
              :items="[order.price_table]"
            ></v-select>
          </div>
          <!-- Order Number -->
          <v-text-field
            disabled
            style="width: 25%;"
            :label="$t('Order Number')"
            :value="order.order_number"
            class="mb-3"
          />
          <!-- Order Date -->
          <v-text-field
            disabled
            style="width: 25%;"
            :label="$t('Order Date')"
            :value="getLocaleDate(order.order_date)"
            class="mb-3"
          />
          <!-- Invoice Number -->
          <v-text-field
            disabled
            style="width: 25%;"
            :label="$t('Invoice Number')"
            :value="order.invoice_number"
            class="mb-3"
          />
          <!-- Invoice Date -->
          <v-text-field
            disabled
            style="width: 25%;"
            :label="$t('Invoice Date')"
            :value="getLocaleDate(order.invoice_date)"
            class="mb-3"
          />
          <!-- Order Amount -->
          <v-text-field
            disabled
            style="width: 25%;"
            :label="$t('Order Amount')"
            :value="getRealMask(Number(order.order_amount))"
            class="mb-3"
          />
          <!-- Order Status -->
          <div style="width: 25%;">
            <v-select
              :disabled="statusIsDisabled"
              v-model="status"
              label="Status"
              :items="status_options_computed"
              :item-text="(x) => $t(x.description)"
              :item-value="(x) => x.value"
            ></v-select>
          </div>
          <!-- Note -->
          <v-textarea
            :disabled="!currentUserIsClientUserAndCanEditTheOrder"
            outlined
            :label="$t('Note')"
            v-model.trim="order.note"
            :error-messages="noteErrors"
            @blur="$v.note.$touch()"
            class="mb-3"
            style="width: 55%"
          />
          <!-- Agent Note -->
          <v-textarea
            v-if="!currentUserIsClientUser"
            outlined
            :label="$t('Agent Note')"
            v-model.trim="order.agent_note"
            :error-messages="agentNoteErrors"
            @blur="$v.agent_note.$touch()"
            class="mb-3"
            style="width: 55%"
          />
          <!-- Ordered items -->
          <v-expansion-panels class="mb-5">
            <v-expansion-panel>
              <v-expansion-panel-header>{{$t('Ordered Items')}}</v-expansion-panel-header>
                <v-expansion-panel-content>
                  <v-container fluid>
                    <!-- Search bar -->
                    <div v-if="currentUserIsClientUserAndCanEditTheOrder">
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
                                type="number"
                              />
                            </v-col>
                            <v-col cols="5">
                              <v-text-field
                                :label="$t('Item code')"
                                v-model.trim="item_code_to_search"
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
                    </div>
                    <!-- Ordered Items -->
                    <v-data-table
                      :headers="edit_ordered_items_headers"
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
                        <!-- <p>{{item.item.$model.category}}</p> -->
                      <!-- </template> -->
                      <template v-slot:item.unit="{ item }">
                        <p>{{item.item.$model.unit}}</p>
                      </template>
                      <template v-slot:item.unit_price="{ item }">
                        <p>{{getRealMask(Number(item.unit_price.$model))}}</p>
                      </template>
                      <template v-slot:item.quantity="{ item }">
                        <v-text-field
                          :disabled="!currentUserIsClientUserAndCanEditTheOrder"
                          :error-messages="item.errors.$model"
                          :label="$t('Quantity')"
                          v-model="item.quantity.$model"
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
                      <template v-slot:item.remove_item="{ item }" v-if="currentUserIsClientUserAndCanEditTheOrder">
                        <div style="display:flex; align-items: center; justify-content: center;">
                          <v-icon @click="removeItem(item.item.$model.item_compound_id)" color="red" large>
                            mdi-close-circle-outline
                          </v-icon >
                        </div>
                      </template>
                    </v-data-table>
                  </v-container>
                </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>  

          <!-- Submit Form -->
          <v-card-actions>
            <!-- Submit -->
            <v-spacer />
            <v-btn
              class="blue--text darken-1"
              type="submit"
              text
              :loading="loading"
              :disabled="loading"
            >{{$t('Save')}}</v-btn>
            <v-btn 
              class="black--text darken-1" 
              text 
              @click="$emit('close-edit-dialog')"
            >{{$t('Close')}}</v-btn>
          </v-card-actions>
        </form>
      </v-card>
    </v-dialog>

    <!-- Cancel Confirmation Dialog -->
    <v-dialog :retain-focus="false" v-model="show_cancel_dialog" max-width="30%">
      <v-card>
        <v-card-title>{{$t('Are_you_sure_you_want_to_delete')}}</v-card-title>
        <v-card-text>
          <v-card-actions class="d-flex justify-space-around" style="width:100%;">
            <v-btn class="black--text darken-1" text @click="show_cancel_dialog = false">{{$t('Cancel')}}</v-btn>
            <v-btn class="red--text darken-1" text @click="deletePriceTable()">{{$t('Delete')}}</v-btn>
          </v-card-actions>
        </v-card-text>
      </v-card>
    </v-dialog>

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
              v-model.trim="filter__item_description"
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
                item-key="item.item_compound_id"
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
                    <v-icon @click="addItem(item)" color="green" large>
                      mdi-plus
                    </v-icon >
                  </div>
                </template>
              </v-data-table>
          </v-container>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import {
  decimal,
  required,
  maxLength,
  minValue,
  maxValue,
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
import {decimal_only_2places} from "~/helpers/validators"
let default_category_value = {category_compound_id: 'all', description: 'All'}
export default {
  mixins: [validationMixin],
  components: {
    "dots-menu": require("@/components/dots-menu.vue").default,
  },
  props: ['order', 'show_edit_dialog', 'order_details_fetched'],
  data() {
    return {
      show_cancel_dialog: false,
      show_search_dialog: false,
      note: '',
      agent_note: '',
      status: '',
      ordered_items: [],
      default_quantity: 1,
      categories: [default_category_value, ],
      price_table: null,
      item_code_to_search: "",
      filter__category: default_category_value,
      filter__item_description: "",
      search_results: [],
      loading: false,
      status_options: [
        {description: 'Canceled', value: 0},
        {description: 'Typing', value: 1},
        {description: 'Transferred', value: 2},
        {description: 'Registered', value: 3},
        {description: 'Invoiced', value: 4},
        {description: 'Delivered', value: 5},
      ],
      edit_ordered_items_headers: [
        { text: this.$t('Image'), value: 'image' },
        { text: this.$t('Code'), value: 'item_code' },
        { text: this.$t('Description'), value: 'item_description' },
        /** { text: this.$t('Category'), value: 'category' }, */
        { text: this.$t('Unit'), value: 'unit' },
        { text: this.$t('Unit price'), value: 'unit_price' },
        { text: this.$t('Quantity'), value: 'quantity' },
        { text: 'Total', value: 'total' },
        ],
      searched_items_headers: [
        { text: this.$t('Image'), value: 'image' },
        { text: this.$t('Code'), value: 'item_code' },
        { text: this.$t('Description'), value: 'item_description' },
        /** { text: this.$t('Category'), value: 'category' }, */
        { text: this.$t('Unit'), value: 'unit' },
        { text: this.$t('Unit price'), value: 'unit_price' },
        { text: this.$t('Add item'), value: 'add_item' },
      ]
    }
  },

  methods: {
    async fetchCategoriesToMakeOrderAndGetPriceTableInfo(){
      let {categories, price_table} = await this.$store.dispatch("order/fetchCategoriesToMakeOrderAndGetPriceTableInfo",
        this.order.establishment.establishment_compound_id);
      if (categories){
        this.categories.push(...categories) 
      }
    },
    // Validate item
    quantityErrors(v) {
      const errors = [];
      !v.quantity.required && errors.push(this.$t("This_field_is_required"));
      !v.quantity.decimal && errors.push(this.$t("DecimalErrorMessage"));
      !v.quantity.minValue && errors.push(this.$formatStr(this.$t("This_value_must_be_greater_than_X"), "0.01"));
      !v.quantity.maxValue && errors.push(this.$formatStr(this.$t("This_value_must_be_less_than_X"), "999999999.99"));
      !v.quantity.decimal_only_2places && errors.push(this.$t("DecimalErrorMessage2Places"));
      v.errors.$model = errors;
    },

    // Save Orders
    async updateOrder(){
      this.$v.orderInfoGroup.$touch();
      if (this.$v.orderInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t('Please_fill_the_form_correctly'), alertType: "error" }, { root: true })
      } else {
        this.loading = true
        // The API to update order must receive item_compound_id as value for the item field.
        let ordered_items_fixed = this.ordered_items.map(el=>{
          // The below code leads to problems since it does not copy the object
          /** let element = el */
          /** element.item = el.item.item_compound_id */
          /** return element */
          let element = JSON.parse(JSON.stringify(el))
          // This is doing a Deep copy
          element.item = element.item.item_compound_id
          return element
        })
        let payload = {
          client: this.order.client.client_compound_id,
          establishment: this.order.establishment.establishment_compound_id,
          order_number: this.order.order_number,
          ordered_items: ordered_items_fixed,
          status: this.status,
        }
        if (this.note){payload['note'] = this.note}
        if (this.agent_note){payload['agent_note'] = this.agent_note}
        let response = await this.$store.dispatch("order/updateOrder", payload)
        if (response) {
          this.order.order_amount = response.order_amount
          this.order.status = response.status
          this.order.note = response.note
          this.order.agent_note = response.agent_note
          console.log(">>>>>>> response: ", response)
          this.$emit('close-edit-dialog')
        }
        this.loading = false;
      }
    },

    // Search Price Item
    async searchOnePriceItemToMakeOrder(){
      if (!this.item_code_to_search){
        this.$store.dispatch("setAlert", { message: this.$t('Plese fill the item code field.'), alertType: "warning" }, { root: true })
      }
      if (this.ordered_items.some(el=>el.item.item_compound_id.split('*')[2] === this.item_code_to_search)){
        this.$store.dispatch("setAlert", { message: this.$t('This item is already added to the order.'), alertType: "warning" }, { root: true })
      }
      else{
        let search_result = await this.$store.dispatch("order/searchOnePriceItemToMakeOrder", 
          {establishment: this.order.establishment.establishment_compound_id, item_code: this.item_code_to_search}
        )
        if (search_result){
          this.ordered_items.push({...search_result, quantity: this.default_quantity, errors: []})
        }
      }
    },

    // Search Price Items
    async searchPriceItemsToMakeOrder(){
      let filter_parameters = {establishment: this.order.establishment.establishment_compound_id, 
        category: this.filter__category.category_compound_id, item_description: this.filter__item_description}
      let search_results = await this.$store.dispatch("order/searchPriceItemsToMakeOrder", filter_parameters);
      if (search_results){
        this.search_results = search_results
      }
    },

    getRealMask(value){
      return value.toLocaleString('pt-br',{style: 'currency', currency: 'BRL'})
    },
    getLocaleDate(value){
      if (value){
        return new Date(value).toLocaleDateString('pt-BR')
      }else{
        return ''
      }
    },

    // Add and remove item
    removeItem(item_compound_id){
      console.log(">>>>>>> ", item_compound_id)
      this.ordered_items = this.ordered_items.filter((obj)=> obj.item.item_compound_id !== item_compound_id)
    },
    addItem(price_item){
      console.log(">>>>>>> addItem(price_item){  :", price_item)
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
  },

  validations: {
    agent_note: {
      maxLength: maxLength(800)
    },
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
    ordered_items: {
      $each: {
        item: {},
        quantity: {
          required,
          decimal,
          decimal_only_2places,
          maxValue: maxValue(999999999.99),
          minValue: minValue(0.01),
        },
        unit_price: {},
        errors: {},
      }
    },
    orderInfoGroup: [
      "note",
      "agent_note",
      "ordered_items"
    ],
  },

  computed: {
    currentUserIsClientUser(){
      return this.$store.state.user.currentUser.roles.includes('client_user')
    },
    currentUserIsClientUserAndCanEditTheOrder(){
      return this.currentUserIsClientUser && this.order.status === 1
    },  
    //Vuelidate
    agentNoteErrors() {
      const errors = [];
      if (!this.$v.agent_note.$dirty) return errors;
      !this.$v.agent_note.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 800));
      return errors;
    },
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
    // Price Items to Add
    priceItemsToAdd(){
      return this.search_results.filter((price_item)=> {
        let return_value = true
        let ordered_items = this.ordered_items
        for (const prop in ordered_items){
          if (ordered_items[prop].item.item_compound_id === price_item.item.item_compound_id){
            return_value = false
          }
        }
        return return_value
      })
    },
    ordered_items__array(){
      return Object.values(this.$v.ordered_items.$each.$iter)
    },
    //
    status_options_computed(){
      if (this.currentUserIsClientUser){
        if (this.order.status === 1){return this.status_options.filter(el=>el.value === 2 || el.value === 0 || el.value === 1)}
        else {return this.status_options.filter(el=>el.value === this.order.status)}
      }
      else{
        if (this.order.status === 1){return this.status_options.filter(el=>el.value === 0 || el.value === 1)}
        if (this.order.status === 2){return this.status_options.filter(el=>el.value === 0 || el.value === 2)}
        if (this.order.status === 3){return this.status_options.filter(el=>el.value === 0 || el.value === 4 || el.value === 3)}
        if (this.order.status === 4){return this.status_options.filter(el=>el.value === 0 || el.value === 3 || el.value === 5 || el.value === 4)}
        if (this.order.status === 5){return this.status_options.filter(el=>el.value === 0 || el.value === 4 || el.value === 5)} 
      }
    },
    statusIsDisabled(){
      if (this.order.status === 0){return true}
      if (this.currentUserIsClientUser && this.order.status !== 1){return true}
      else {return false}
    },
  },

  watch: {
    order_details_fetched(newValue){
      if (newValue === true){
        this.ordered_items = this.order.ordered_items.map(el=>{
          el.errors = []
          return el
        })
        this.status = this.order.status
        if (this.currentUserIsClientUserAndCanEditTheOrder) { 
          this.edit_ordered_items_headers.push({ text: this.$t('Remove item'), value: 'remove_item' })
          this.fetchCategoriesToMakeOrderAndGetPriceTableInfo()
        }
      }
    }	
  },
}
</script>
