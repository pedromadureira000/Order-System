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
                class="d-flex"
                cols="12"
              >
                <v-select
                  v-model="company"
                  :label="$t('Company')"
                  :items="companies"
                  :item-text="(x) => x.company_compound_id ? x.company_code + ' - ' + x.name : $t('All')" 
                  :item-value="(x) => x.company_compound_id"
                  @change="fetchClientsToFillFilterSelectorToSearchOrders"
                ></v-select>
              </v-col>
              <!-- Establishment -->
              <v-col
                class="d-flex"
                sm="6"
              >
                <v-select
                  v-model="establishment"
                  :label="$t('Establishment')"
                  :items="establishments"
                  :item-text="(x) => x.establishment_compound_id ? x.establishment_code + ' - ' + x.name : $t('All')"
                  :item-value="(x) => x.establishment_compound_id"
                ></v-select>
              </v-col>
              <!-- Client -->
              <v-col
                class="d-flex"
                cols="12"
                sm="6"
              >
                <v-select
                  v-model="client"
                  :label="$t('Client')"
                  :items="clients"
                  :item-text="(x) => x.client_compound_id ? x.client_code + ' - ' + x.name : $t('All')"
                  :item-value="(x) => x.client_compound_id"
                ></v-select>
              </v-col>
              <!-- Invoice Number -->
              <v-col cols="3">
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
              <v-col cols="3">
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
                cols="12"
                sm="6"
              >
                <v-select
                  v-model="status"
                  :label="$t('Status')"
                  :items="status_options"
                  :item-text="(x) => x.description"
                  :item-value="(x) => $t(x.value)"
                ></v-select>
              </v-col>
              <!-- Submit -->
              <v-col cols="3" style="display: flex; justify-content: center;">
                <v-btn
                  class="mt-3"
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
                <p>{{item.order_date}}</p>
              </template>
              <template v-slot:item.status="{ item }">
                <p>{{item.status}}</p>
              </template>
              <template v-slot:item.invoice_number="{ item }">
                <p>{{item.invoice_number}}</p>
              </template>
              <template v-slot:item.invoice_date="{ item }">
                <p>{{item.invoice_date}}</p>
              </template>
              <template v-slot:item.order_amount="{ item }">
                <p>{{getRealMask(item.order_amount)}}</p>
              </template>
              <template v-slot:item.actions="{ item }">
                <order-edit-menu :order="item"/>
              </template>
            </v-data-table>
          </v-container>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import {money} from "~/helpers/validators"
import {VMoney} from 'v-money'

let all_companies = {company_compound_id: null}
let all_establishments = {establishment_compound_id: null}
let all_clients = {client_compound_id: null}
let all_status = {description: 'All', value: null}

export default {
  middleware: ["authenticated"],
  components: {
    "price-table-edit-menu": require("@/components/admin/item/price-table-edit-menu.vue").default,
  },
  mixins: [validationMixin],
  directives: {money: VMoney},
  data() {
    return {
      orders: [],
      loading: false,
      money: money,
      // Fields
      company: null,
      establishment: null,
      client: null,
      invoice_number: '',
      order_number: '',
      period: '',
      status: '',
      companies: [all_companies],
      clients: [all_clients],
      client_groups: [],
      status_options: [
        all_status,
        {description: 'Pending', value: 'pending'},
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
        /** { text: this.$t('Company'), value: 'company' }, */
        /** { text: this.$t('Establishment'), value: 'establishment' }, */
        /** { text: this.$t('Client'), value: 'client' }, */
        /** { text: this.$t('Client User'), value: 'client_user' }, */
        /** { text: this.$t('Price Table'), value: 'price_table' }, */
        { text: this.$t('Order Date'), value: 'order_date' },
        { text: this.$t('Status'), value: 'status' },
        { text: this.$t('Invoice Number'), value: 'invoice_number' },
        { text: this.$t('Invoice Date'), value: 'invoice_date' },
        { text: this.$t('Order Amount'), value: 'order_amount' },
        { text: this.$t('Actions'), value: 'actions' },
      ]
    };
  },

  async fetch() {
    /** Fetch Companies with Establishments */
    let data = await this.$store.dispatch("order/fetchDataToFillFilterSelectorsToSearchOrders"); 
    if (data){
      this.companies = [all_companies, ...data]
      console.log(">>>>>>> this.companies: ", this.companies)
    }
  },

  methods: {
    async searchOrders(){
      let query_strings = ""
      query_strings += this.company ? `company=${this.company}&` : ''
      query_strings += this.establishment ? `establishment=${this.establishment}&` : ''
      query_strings += this.client ? `client=${this.client}&` : ''
      query_strings += this.invoice_number ? `invoice_number=${this.invoice_number}&` : ''
      query_strings += this.order_number ? `order_number=${this.order_number}&` : ''
      query_strings += this.period ? `period=${this.period}&` : ''
      query_strings += this.status ? `status=${this.status}&` : ''
      if (query_strings !== "") {
        query_strings = query_strings.slice(0, -1) // remove the last '&' character
      }
      let orders = await this.$store.dispatch("order/searchOrders", query_strings); 
      if (orders){
        this.orders = orders
      }
    },
 
    async fetchClientsToFillFilterSelectorToSearchOrders(){
      if (this.company === all_companies){
        this.clients = [all_clients]
        this.client = null
        this.establishments = [all_establishments]

      }
      else {
        let client_table_id = this.company.client_table
        let client_group = this.client_groups.find(el=>el.group_id===client_table_id)
        if (client_group){
          this.clients = [all_clients, ...client_group.clients]
        }
        else{
          let clients = await this.$store.dispatch("organization/fetchClientsToFillFilterSelectorToSearchOrders", client_table_id)
          if (clients) {
            this.clients = [all_clients, ...clients]
            this.client_groups.push({group_id: client_table_id, clients: clients})
          }
        }
      }
    },

    getRealMask(value){
      return value.toLocaleString('pt-br',{style: 'currency', currency: 'BRL'})
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
      return [all_establishments,...this.company.establishments]
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
