<template>
  <p v-if="$fetchState.pending">{{$t('Fetching_data')}}</p>
  <p v-else-if="$fetchState.error">{{$t('Error_fetching_data')}}</p>
  <div v-else>
    <div class="ma-3">
      <v-card>
        <!-- Search bar -->
        <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Search Orders')}}</v-card-title>
        <v-card-text class="mt-3">
          <v-container fluid>
            <v-row no-gutters>
              <!-- Company -->
              <v-col
                class="mr-3"
              >
                <v-select
                  v-model="company"
                  :label="$t('Company')"
                  :items="companies"
                  :item-text="(x) => x.company_compound_id ? x.company_code + ' - ' + x.name : $t('All')" 
                  return-object
                  @change="companyChanged"
                ></v-select>
              </v-col>
              <!-- Establishment -->
              <v-col
                class="mr-3"
              >
                <v-select
                  v-model="establishment"
                  :label="$t('Establishment')"
                  :items="establishments"
                  :item-text="(x) => x.establishment_compound_id ? x.establishment_code + ' - ' + x.name : $t('All')"
                  return-object
                ></v-select>
              </v-col>
              <!-- Client -->
              <v-col
                class="mr-3"
                v-if="!currentUserIsClientUser"
              >
                <v-select
                  v-model="client"
                  :label="$t('Client')"
                  :items="computed_clients"
                  :item-text="(x) => x.client_compound_id ? x.client_code + ' - ' + x.name : $t('All')"
                  return-object
                  @change="clientChanged"
                ></v-select>
              </v-col>
              <!-- Client User -->
              <v-col
                class="mr-3"
                v-if="!currentUserIsClientUser"
              >
                <v-select
                  v-model="client_user"
                  :label="$t('Client_user')"
                  :items="computed_client_users"
                  :item-text="(x) => x.user_code ? x.username + ' - ' + x.first_name + ' ' + x.last_name : $t('All')"
                  return-object
                ></v-select>
              </v-col>
            </v-row>
            <v-row no-gutters>
              <!-- Invoice Number -->
              <v-col cols="2">
                <v-text-field
                  :error-messages="invoiceNumberErrors"
                  :label="$t('Invoice Number')"
                  v-model.trim="invoice_number"
                  @keydown.enter.prevent=""
                  @blur="$v.invoice_number.$touch()"
                  class="mr-2"
                />
              </v-col>
              <!-- Order Number -->
              <v-col cols="2">
                <v-text-field
                  :error-messages="orderNumberErrors"
                  :label="$t('Order Number')"
                  v-model.trim="order_number"
                  @keydown.enter.prevent=""
                  @blur="$v.order_number.$touch()"
                  class="mr-2"
                />
              </v-col>
              <!-- Status -->
              <v-col
                class="d-flex"
                cols="3"
              >
                <v-select
                  v-model="status"
                  label="Status"
                  :items="status_options"
                  :item-text="(x) => $t(x.description)"
                  return-object
                ></v-select>
              </v-col>
              <!-- Period -->
              <v-col cols="3">
                <v-row>
                  <v-col class="ml-3">
                    <v-text-field
                      :label="$t('Initial Period')"
                      v-model.trim="initial_period"
                      class="mr-2"
                      outlined
                      dense
                      placeholder="dd/mm/yyyy"
                      persistent-placeholder
                      v-mask="'##/##/####'"
                      type="tel"
                    />
                  </v-col>
                  <v-col>
                    <v-text-field
                      :label="$t('Final Period')"
                      v-model.trim="final_period"
                      class="mr-2"
                      outlined
                      dense
                      placeholder="dd/mm/yyyy"
                      persistent-placeholder
                      v-mask="'##/##/####'"
                      type="tel"
                    />
                  </v-col>
                </v-row>
              </v-col>
              <!-- Submit -->
              <v-col cols="2" style="display: flex; justify-content: center;">
                <v-btn
                  class="mt-3 mr-0 ml-0"
                  color="primary"
                  :loading="loading_items"
                  :disabled="loading_items"
                  @click="options['page'] = 1; searchOrders()"
                >{{$t('Search')}}</v-btn>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <!-- Orders -->
        <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Orders')}}</v-card-title>
        <v-card-text>
          <v-container fluid>
            <v-data-table
              :headers="orders_headers"
              :items="orders"
              class="elevation-1"
              item-key="id"
              :options.sync="options"
              :server-items-length="totalItems"
              :loading="loading_items"
              :footer-props="{'items-per-page-options': [5, 10, 15]}"
            >
              <template v-slot:item.order_number="{ item }">
                <p>{{item.order_number}}</p>
              </template>
              <template v-slot:item.order_date="{ item }">
                <p>{{getLocaleDate(item.order_date)}}</p> 
              </template>
              <template v-slot:item.company="{ item }">
                <p>{{typeof item.company === 'string' ? item.company.split('*')[1] : item.company.company_code}}</p> 
              </template>
              <template v-slot:item.establishment="{ item }">
                <p>{{typeof item.establishment === 'string' ? item.establishment.split('*')[2] : item.establishment.establishment_code}}</p>
              </template>
              <template v-slot:item.status="{ item }">
                <div :style="{color: getColor(item.status)}">
                  <p>{{$t(status_options.filter(el=>el.value===String(item.status))[0].description)}}</p>
                </div>
              </template>
              <template v-slot:item.invoice_number="{ item }">
                <p>{{item.invoice_number}}</p>
              </template>
              <template v-slot:item.invoicing_date="{ item }">
                <p>{{getLocaleDate(item.invoicing_date)}}</p>
              </template>
              <template v-slot:item.order_amount="{ item }">
                <p style="float: right;">{{getRealMask(Number(item.order_amount))}}</p>
              </template>
              <template v-slot:item.actions="{ item }">
                <order-view-menu :order="item" @order-duplicated="orderDuplicated" :ref="'order_view_menu_' + item.id"/>
                <!-- <v-btn @click="testt(item)">testt</v-btn> -->
              </template>
            </v-data-table>
          </v-container>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script>
import {
  integer,
  maxLength,
  minValue,
} from "vuelidate/lib/validators";
import { validationMixin,  } from "vuelidate";
import {mask} from 'vue-the-mask'

let all_companies = {company_compound_id: null, establishments: [], client_table: null}
let all_establishments = {establishment_compound_id: null}
let all_clients = {client_compound_id: null, client_table: 'null'}
let all_client_users = {user_code: null, username: 'null'}
let all_status = {description: 'All', value: null}
let pending_status = {description: 'Pending', value: 'pending'}

export default {
  name: "ViewOrders",
  middleware: ["authenticated"],
  components: {
    "order-view-menu": require("@/components/client/order/order-view-menu.vue").default,
  },
  mixins: [validationMixin],
  directives: {mask},
  data() {
    return {
      orders: [],
      // Fields
      company: all_companies,
      establishment: all_establishments,
      client: all_clients,
      client_user: all_client_users,
      invoice_number: '',
      order_number: '',
      initial_period: '',
      final_period: '',
      status: pending_status,
      companies: [all_companies],
      clients: [all_clients],
      status_options: [
        all_status,
        pending_status,
        {description: 'Canceled', value: '0'},
        {description: 'Typing', value: '1'},
        {description: 'Transferred', value: '2'},
        {description: 'Registered', value: '3'},
        {description: 'Invoiced', value: '4'},
        {description: 'Delivered', value: '5'},
      ],
      // Fields
      orders_headers: [
        { text: this.$t('Order Number'), value: 'order_number', sortable: true},
        { text: this.$t('Order Date'), value: 'order_date', sortable: true},
        { text: this.$t('Company'), value: 'company', sortable: false},
        { text: this.$t('Establishment'), value: 'establishment', sortable: false},
        { text: 'Status', value: 'status', sortable: true },
        { text: this.$t('Invoice Number'), value: 'invoice_number', sortable: false},
        { text: this.$t('Invoice Date'), value: 'invoicing_date', sortable: false},
        { text: this.$t('Order Amount'), value: 'order_amount', sortable: true},
        { text: this.$t('Actions'), value: 'actions', sortable: false},
      ],
      // Pagination
      loading_items: false,
      options: {},
      totalItems: 0,
    };
  },

  async fetch() {
    // Fetch Companies with Establishments
    let data = await this.$store.dispatch("order/fetchDataToFillFilterSelectorsToSearchOrders"); 
    if (data){
      this.companies = [all_companies, ...data]
    }
    // Fetch Clients with client_users
    if (!this.currentUserIsClientUser){
      let clients = await this.$store.dispatch("order/fetchClientsToFillFilterSelectorToSearchOrders")
      if (clients) {
        this.clients = [all_clients, ...clients]
      }
    }
  },

  methods: {
    async searchOrders(){
      this.$v.clientInfoGroup.$touch();
      if (this.$v.clientInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
      } 
      else {
        this.loading_items = true
        const { sortBy, sortDesc, page, itemsPerPage } = this.options
        let query_strings = ""
        query_strings += sortBy[0] ? `sort_by=${sortBy[0]}&` : ''
        query_strings += sortDesc[0] ? `sort_desc=${sortDesc[0]}&` : ''
        query_strings += `page=${page}&`
        query_strings += `items_per_page=${itemsPerPage}&`
        query_strings += this.company.company_compound_id ? `company=${this.company.company_compound_id}&` : ''
        query_strings += this.establishment.establishment_compound_id ? `establishment=${this.establishment.establishment_compound_id}&` : ''
        query_strings += this.client.client_compound_id ? `client=${this.client.client_compound_id}&` : ''
        query_strings += this.client_user.user_code ? `client_user=${this.client_user.user_code}&` : ''
        query_strings += this.invoice_number ? `invoice_number=${this.invoice_number}&` : ''
        query_strings += this.order_number ? `order_number=${this.order_number}&` : ''
        query_strings += this.initial_period ? `initial_period=${this.fixPeriod(this.initial_period)}&` : ''
        query_strings += this.final_period ? `final_period=${this.fixPeriod(this.final_period)}&` : ''
        query_strings += this.status.value ? `status=${this.status.value}&` : ''
        if (query_strings !== "") {
          query_strings = query_strings.slice(0, -1) // remove the last '&' character
        }
        let data = await this.$store.dispatch("order/searchOrders", query_strings);
        if (data){
          let {orders, current_page, lastPage, total} = data
          this.orders = orders
          this.totalItems = total
        }
        this.loading_items = false
      }    
    },
 
    async companyChanged(){
      // Reset establishment field
      this.establishment = all_establishments
      // Reset client field
      if (this.client.client_table !== this.company.client_table){
        this.client = all_clients
      }
    },

    async clientChanged(){
      console.log(">>>>>>> ", this.client.client_compound_id)
      // Reset client_user field
      this.client_user = all_client_users
    },


    getRealMask(value){
      return value.toLocaleString('pt-br',{style: 'currency', currency: 'BRL'})
    },

    getLocaleDate(value){
      if (value){
        return new Date(value).toLocaleDateString('pt-BR')
      }
      else {
        return ""
      }
    },

    getColor(status){
      if (status === 0){return 'gray'}
      if (status === 1){return 'red'}
      if (status === 2){return 'green'}
      if (status === 3){return 'brown'}
      if (status === 4){return 'darkblue'}
      if (status === 5){return 'black'}
    },

    fixPeriod(value){
      let splited_date = value.split('/')
      let fixed_date = splited_date[2] + '-' + splited_date[1] + '-' + splited_date[0]
      return fixed_date
    },
    // Duplicate Order
    orderDuplicated(order){
      this.orders.push(order)
      // The v-data-table update is async
			setTimeout(() => {
        this.$refs['order_view_menu_' + order.id].show_edit_dialog = true
			}, 50);
    },

    /** testt(order){ */
    /** } */
  },

  validations: {
    invoice_number: {
      maxLength: maxLength(9)
    },
    order_number: {
      integer,
      minValue: minValue(1),
    },
    clientInfoGroup: [
      "invoice_number",
      "order_number",
    ],
  },

  computed: {
    currentUserIsClientUser(){
      return this.$store.state.user.currentUser.roles.includes('client_user')
    },
    establishments(){
      return [all_establishments, ...this.company.establishments]
    },
    computed_clients(){
      // If the company is not all_companies, then return only the clients from the company.client_table
      // otherwise return all clients
      return this.company.company_compound_id ? [all_clients, 
        ...this.clients.filter(el=>el.client_table===this.company.client_table)] : [all_clients, ...this.clients]  
    },
    computed_client_users(){
      // If the client is not all_clients, then return only the client users from this client
      // otherwise set all_client_users option
      return this.client.client_compound_id ? [all_client_users, ...this.client.client_users] : [all_client_users]  
    },
    // Vuelidate
    invoiceNumberErrors() {
      const errors = [];
      if (!this.$v.invoice_number.$dirty) return errors;
      !this.$v.invoice_number.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 9));
      return errors;
    },
    orderNumberErrors() {
      const errors = [];
      if (!this.$v.order_number.$dirty) return errors;
      !this.$v.order_number.integer && errors.push(this.$t("This_value_must_be_a_integer"));
      !this.$v.order_number.minValue && errors.push(this.$formatStr(this.$t("This_value_must_be_greater_than_X"), 1 ));
      return errors;
    },
  },

  /** mounted(){ */
    /** if (this.currentUserIsClientUser){ */
    /** } */
  /** } */

  watch: {
    options: {
      handler () {
        this.searchOrders()
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
/* This is for the price_items */
.container--fluid {
  margin-top: -20px;
} 
</style>
