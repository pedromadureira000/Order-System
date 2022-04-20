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
                ></v-select>
              </v-col>
            </v-row>
            <v-row no-gutters>
              <!-- Invoice Number -->
              <v-col cols="2">
                <v-text-field
                  :error-messages="invoiceNumberErrors"
                  :label="$t('Invoice Number')"
                  v-model="invoice_number"
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
                  v-model="order_number"
                  @keydown.enter.prevent=""
                  @blur="$v.order_number.$touch()"
                  class="mr-2"
                />
              </v-col>
              <!-- Period -->
              <v-col cols="3">
                <v-text-field
                  :label="$t('Period')"
                  v-model="period"
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
              <!-- Submit -->
              <v-col cols="2" style="display: flex; justify-content: center;">
                <v-btn
                  class="mt-3 mr-0 ml-0"
                  color="primary"
                  :loading="loading"
                  :disabled="loading"
                  @click="searchOrders"
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
              item-key="item"
            >
              <template v-slot:item.order_number="{ item }">
                <p>{{item.order_number}}</p>
              </template>
              <template v-slot:item.order_date="{ item }">
                <p>{{getLocaleDate(item.order_date)}}</p> 
              </template>
              <template v-slot:item.status="{ item }">
                <p>{{$t(status_options.filter(el=>el.value===String(item.status))[0].description)}}</p>
              </template>
              <template v-slot:item.invoice_number="{ item }">
                <p>{{item.invoice_number}}</p>
              </template>
              <template v-slot:item.invoice_date="{ item }">
                <p>{{item.invoice_date}}</p>
              </template>
              <template v-slot:item.order_amount="{ item }">
                <p>{{getRealMask(Number(item.order_amount))}}</p>
              </template>
              <template v-slot:item.actions="{ item }">
                <order-view-menu :order="item"/>
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
import {money} from "~/helpers/validators"
import {VMoney} from 'v-money'

let all_companies = {company_compound_id: null, establishments: [], client_table: null}
let all_establishments = {establishment_compound_id: null}
let all_clients = {client_compound_id: null, client_table: 'null'}
let all_status = {description: 'All', value: null}
let pending_status = {description: 'Pending', value: 'pending'}

export default {
  middleware: ["authenticated"],
  components: {
    "order-view-menu": require("@/components/client/order/order-view-menu.vue").default,
  },
  mixins: [validationMixin],
  directives: {money: VMoney},
  data() {
    return {
      orders: [],
      loading: false,
      money: money,
      // Fields
      company: all_companies,
      establishment: all_establishments,
      client: all_clients,
      invoice_number: '',
      order_number: '',
      period: '',
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
        { text: this.$t('Order Number'), value: 'order_number' },
        { text: this.$t('Order Date'), value: 'order_date' },
        { text: 'Status', value: 'status' },
        { text: this.$t('Invoice Number'), value: 'invoice_number' },
        { text: this.$t('Invoice Date'), value: 'invoice_date' },
        { text: this.$t('Order Amount'), value: 'order_amount' },
        { text: this.$t('Actions'), value: 'actions' },
      ]
    };
  },

  async fetch() {
    // Fetch Companies with Establishments
    let data = await this.$store.dispatch("order/fetchDataToFillFilterSelectorsToSearchOrders"); 
    if (data){
      this.companies = [all_companies, ...data]
      console.log(">>>>>>> this.companies: ", this.companies)
    }
    // Fetch Clients
    if (!this.currentUserIsClientUser){
      let clients = await this.$store.dispatch("order/fetchClientsToFillFilterSelectorToSearchOrders")
      if (clients) {
        this.clients = [all_clients, ...clients]
      }
    }
  },

  methods: {
    async searchOrders(){
      /** clientInfoGroup */
      let query_strings = ""
      query_strings += this.company.company_compound_id ? `company=${this.company.company_compound_id}&` : ''
      query_strings += this.establishment.establishment_compound_id ? `establishment=${this.establishment.establishment_compound_id}&` : ''
      query_strings += this.client.client_compound_id ? `client=${this.client.client_compound_id}&` : ''
      query_strings += this.invoice_number ? `invoice_number=${this.invoice_number}&` : ''
      query_strings += this.order_number ? `order_number=${this.order_number}&` : ''
      query_strings += this.period ? `period=${this.period}&` : ''
      query_strings += this.status.value ? `status=${this.status.value}&` : ''
      if (query_strings !== "") {
        query_strings = query_strings.slice(0, -1) // remove the last '&' character
      }
      let orders = await this.$store.dispatch("order/searchOrders", query_strings); 
      if (orders){
        this.orders = orders
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

    getRealMask(value){
      return value.toLocaleString('pt-br',{style: 'currency', currency: 'BRL'})
    },

    getLocaleDate(value){
      return new Date(value).toLocaleDateString('pt-BR')
    },
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
