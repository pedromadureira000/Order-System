<template>
  <div v-if="order_details_fetched">
    <!-- ========= Edit Order Dialog ============ -->
    <v-dialog :retain-focus="false" v-model="show_edit_dialog" max-width="90%" persistent>
      <v-card>
        <v-card-title style="display: flex; justify-content: center;" class="mb-2">{{$t('Edit Order')}}</v-card-title>
        <form @submit.prevent="updateOrder" class="ml-3">
          <div style="display: flex; justify-content: center;">
            <div style="width: 80%">
              <v-row >
                <v-col>
                  <!-- Company -->
                  <div>
                    <v-select
                      disabled
                      :value="order.company"
                      :label="$t('Company')"
                      :item-text="(x) => x.company_code + ' - ' + x.name"
                      :items="[order.company]"
                    ></v-select>
                  </div>
                  <!-- Client -->
                    <div >
                      <v-select
                        disabled
                        :value="order.client"
                        :label="$t('Client')"
                        :item-text="(x) => x.client_code + ' - ' + x.name"
                        :items="[order.client]"
                      ></v-select>
                    </div>
                    <!-- Order Number -->
                    <v-text-field
                      disabled
                      :label="$t('Order Number')"
                      :value="order.order_number"
                      class="mb-3"
                    />
                    <!-- Order ID -->
                    <v-text-field
                      disabled
                      :label="$t('Order ID')"
                      :value="order.id"
                      class="mb-3"
                    />
                    <!-- Invoice Number -->
                    <v-text-field
                      disabled
                      :label="$t('Invoice Number')"
                      :value="order.invoice_number"
                      class="mb-3"
                    />
                    <!-- Price table -->
                    <div>
                      <v-select
                        disabled
                        :value="order.price_table"
                        :label="$t('Price_Table')"
                        :item-text="(x) => x.table_code + ' - ' + x.description"
                        :items="[order.price_table]"
                      ></v-select>
                    </div>
                    <!-- Note -->
                    <v-textarea
                      :disabled="!currentUserIsClientUserAndCanEditTheOrder"
                      outlined
                      :label="$t('Note')"
                      v-model.trim="note"
                      :error-messages="noteErrors"
                      @blur="$v.note.$touch()"
                      class="mb-3"
                    />
                </v-col>

                <v-col>
                  <!-- Establishment -->
                    <div>
                      <v-select
                        disabled
                        :value="order.establishment"
                        :label="$t('Establishment')"
                        :item-text="(x) =>  x.establishment_code + ' - ' + x.name"
                        :items="[order.establishment]"
                      ></v-select>
                    </div>
                    <!-- Client user -->
                    <div>
                      <v-select
                        disabled
                        :value="order.client_user"
                        :label="$t('Client_User')"
                        :item-text="(x) => x.first_name + ' ' + x.last_name + '('+ x.username + ')'"
                        :items="[order.client_user]"
                      ></v-select>
                    </div>
                    <!-- Order Date -->
                    <v-text-field
                      disabled
                      :label="$t('Order Date')"
                      :value="getLocaleDate(order.order_date)"
                      class="mb-3"
                    />
                    <!-- Order Amount -->
                    <v-text-field
                      disabled
                      :label="$t('Order Amount')"
                      :value="getRealMask(Number(order.order_amount))"
                      class="mb-3"
                    />
                    <!-- Invoice Date -->
                    <v-text-field
                      disabled
                      :label="$t('Invoice Date')"
                      :value="getLocaleDate(order.invoice_date)"
                      class="mb-3"
                    />
                    <!-- Order Status -->
                    <div>
                      <v-select
                        :disabled="statusIsDisabled"
                        v-model="status"
                        label="Status"
                        :items="status_options_computed"
                        :item-text="(x) => $t(x.description)"
                        :item-value="(x) => x.value"
                      ></v-select>
                    </div>
                    <!-- Agent Note -->
                    <v-textarea
                      v-if="!currentUserIsClientUser"
                      outlined
                      :label="$t('Agent Note')"
                      v-model.trim="agent_note"
                      :error-messages="agentNoteErrors"
                      @blur="$v.agent_note.$touch()"
                      class="mb-3"
                    />
                </v-col>
              </v-row>
            </div>
          </div>
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
                    </div>
                    <!-- Ordered Items -->
                    <v-data-table
                      :headers="edit_ordered_items_headers"
                      :items="ordered_items__array"
                      class="elevation-1"
                      sort-by="sequence_number.$model"
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
                        <!-- <p>Seq numb: {{item.sequence_number.$model}}</p> -->
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
                        <p >{{getRealMask(item.quantity.$model * item.unit_price.$model)}}</p>
                      </template>
                      <template v-slot:item.remove_item="{ item }" v-if="currentUserIsClientUserAndCanEditTheOrder">
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
          <v-btn class="blue--text darken-1" text @click="options['page'] = 1; searchPriceItemsToMakeOrder()">{{$t('Search')}}</v-btn>
          <v-btn class="blue--text darken-1" text @click="show_search_dialog = false">{{$t('Close')}}</v-btn>
        </v-card-actions>

        <v-card-title style="font-size: 1.3rem; font-weight: 400; line-height: 1rem">{{$t('Search Results')}}</v-card-title>
        <v-card-text>
          <v-container fluid class="mt-2">
              <v-data-table
                :headers="searched_items_headers"
                :items="search_results"
                class="elevation-1"
                item-key="item.item_compound_id"
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
import {decimal_only_2places, slugFieldValidator} from "~/helpers/validators"
let default_category_value = {category_compound_id: null, description: 'All'}
export default {
  mixins: [validationMixin],
  components: {
    "dots-menu": require("@/components/dots-menu.vue").default,
  },
  props: ['order', 'show_edit_dialog'],
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
        { text: this.$t('Image'), value: 'image', align: 'center', sortable: false },
        { text: this.$t('Code'), value: 'item_code', align: 'center', sortable: false },
        { text: this.$t('Description'), value: 'item_description', align: 'left', width: '80%', sortable: false },
        /** { text: this.$t('Category'), value: 'category' }, */
        { text: this.$t('Unit price'), value: 'unit_price', align: 'right', sortable: false },
        { text: this.$t('Quantity'), value: 'quantity', align: 'center', width: '25%', sortable: false},
        { text: this.$t('Unit'), value: 'unit', align: 'center', sortable: false },
        { text: 'Total', value: 'total', align: 'right', sortable: false },
      ],
      searched_items_headers: [
        { text: this.$t('Image'), value: 'image', sortable: false },
        { text: this.$t('Code'), value: 'item_code', sortable: true },
        { text: this.$t('Description'), value: 'item_description', sortable: true },
        /** { text: this.$t('Category'), value: 'category' }, */
        { text: this.$t('Unit'), value: 'unit', sortable: false },
        { text: this.$t('Unit price'), value: 'unit_price', sortable: true },
        { text: this.$t('Add item'), value: 'add_item', sortable: false },
      ],
      // Pagination
      search_dialog_was_already_open: false,
      search_dialog_was_already_open: false,
      options: {},
      totalItems: 0,
      loading_items: false,
      // util
      order_details_fetched: false
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
          id: this.order.id,
          client: this.order.client.client_compound_id,
          establishment: this.order.establishment.establishment_compound_id,
          order_number: this.order.order_number,
          ordered_items: ordered_items_fixed,
          status: this.status,
        }
        if (this.note && this.currentUserIsClientUser){payload['note'] = this.note}
        if (this.agent_note && !this.currentUserIsClientUser){payload['agent_note'] = this.agent_note}
        let response = await this.$store.dispatch("order/updateOrder", payload)
        if (response == 'ok') {
          this.order.order_amount = this.getOrderTotal()
          this.order.status = this.status
          this.$emit('close-edit-dialog')
        }
        this.loading = false;
      }
    },

    // Search Price Item
    async searchOnePriceItemToMakeOrder(){
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
            {establishment: this.order.establishment.establishment_compound_id, item_code: this.item_code_to_search}
          )
          if (search_result){
            this.ordered_items.push({...search_result, quantity: this.default_quantity, sequence_number: this.getSequenceNumber(),errors: []})
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
        {establishment: this.order.establishment.establishment_compound_id, query_strings: query_strings });
      if (price_items){
        this.search_results = price_items
        this.totalItems = total
      }
      this.loading_items = false
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
      this.ordered_items = this.ordered_items.filter((obj)=> obj.item.item_compound_id !== item_compound_id)
    },
    addItem(price_item){
      this.ordered_items.push({...price_item, quantity: this.default_quantity, sequence_number: this.getSequenceNumber(), errors: []})
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
    // Sequence Number
    getSequenceNumber(){
      return this.ordered_items.reduce((previous, current)=>{
        return Math.max(typeof previous == 'number' ? previous : previous.sequence_number, current.sequence_number);
      }, 0) + 1
    },
    // Check if can add item to order
    itemIsAlreadyInTheOrder(item_compound_id){
      return this.ordered_items.some(el=>el.item.item_compound_id === item_compound_id)
    },
    // Get order Total
    getOrderTotal(){
      return this.ordered_items.reduce((previous, current)=>{
        return (typeof previous == 'number' ? previous : (previous.unit_price * previous.quantity)) + (current.unit_price * current.quantity)
      }, 0)
    },
    searchIconFunction(){
      this.show_search_dialog = true
      this.search_dialog_was_already_open = true
      if (this.categories.length == 1){
        this.fetchCategoriesToMakeOrderAndGetPriceTableInfo()
      }
    }

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
    item_code_to_search: {
      required, 
      slugFieldValidator, 
      maxLength: maxLength(15)
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
        sequence_number: {},
        errors: {},
      }
    },
    orderInfoGroup: [
      "note",
      "agent_note",
      "ordered_items"
    ],
    defaultQuantity: ["default_quantity", "item_code_to_search"]
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
    itemCodeToSearchErrors() {
      const errors = [];
      if (!this.$v.item_code_to_search.$dirty) return errors;
      !this.$v.item_code_to_search.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.item_code_to_search.slugFieldValidator && errors.push(this.$t('SlugFieldErrorMessage'));
      !this.$v.item_code_to_search.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 15));
      return errors;
    },
    // Price Items to Add
    /** priceItemsToAdd(){ */
      /** return this.search_results.filter((price_item)=> { */
        /** let return_value = true */
        /** let ordered_items = this.ordered_items */
        /** for (const prop in ordered_items){ */
          /** if (ordered_items[prop].item.item_compound_id === price_item.item.item_compound_id){ */
            /** return_value = false */
          /** } */
        /** } */
        /** return return_value */
      /** }) */
    /** }, */
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
        if (this.order.status === 2){return this.status_options.filter(el=>el.value === 0 || el.value === 2 || el.value === 3)}
        // Agent can't change order status from registred to invoiced
        if (this.order.status === 3){return this.status_options.filter(el=>el.value === 0 || el.value === 3)} 
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
    order: {
      handler(obj){
        /** console.log(">>>>>>> INSIDE ORDER WATCHER") */
        if (obj.ordered_items){
          // Run this code only once after fetch order details (since updating order will update some fields of this.order)
          if (!this.order_details_fetched){
            this.order_details_fetched = true
            this.ordered_items = this.order.ordered_items.map(el=>{
              // This will avoid changes in the edit-order-component from alterate ordered_items in the order-details-component 
              let element = JSON.parse(JSON.stringify(el))
              element.errors = []
              return element
            })
            /** console.log(">>>>>>> where is the note? ", this.order) */
            this.note = this.order.note
            this.agent_note = this.order.agent_note
            this.status = this.order.status
            if (this.currentUserIsClientUserAndCanEditTheOrder) { 
              this.edit_ordered_items_headers.push({ text: this.$t('Remove item'), value: 'remove_item', sortable: false})
              /** this.fetchCategoriesToMakeOrderAndGetPriceTableInfo() */
            }
          }
        }
        else{
          this.order_details_fetched = false
        }
      },
      deep: true
    },
    options: {
      handler () {
        if (this.search_dialog_was_already_open){
          this.searchPriceItemsToMakeOrder()
        }
      },
      deep: true,
    },
  },

}
</script>
