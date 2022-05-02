<template>
  <div v-if="order_details_fetched">
    <!-- ========= View Details Dialog ============ -->
    <v-dialog :retain-focus="false" :value="show_view_details_dialog" max-width="90%" persistent>
      <v-card class="pa-3">
        <v-row class="mb-1">
          <v-col style="display: flex; justify-content: center;">
            <h3 class="ml-3 pt-3">{{$t('Order Details')}}</h3>
          </v-col>
        </v-row>
        <v-row style="display: flex; justify-content: center;">
          <!-- Order Info -->
          <div style="display: flex; justify-content: center;">
            <div style="width: 90%">
              <v-row>
                <v-col>
                  <v-simple-table>
                    <template v-slot:default>
                        <tbody>
                          <tr>
                            <td><b>{{$t('Company')}}</b></td>
                            <td>{{order.company.company_code}} - {{order.company.name}}</td>
                          </tr>
                          <tr>
                            <td><b>{{$t('Client')}}</b></td>
                            <td>{{order.client.client_code}} - {{order.client.name}} ({{order.establishment.cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5")}})</td>
                          </tr>
                          <tr>
                            <td><b>{{$t('Order Number')}}</b></td>
                            <td>{{order.order_number}}</td>
                          </tr>
                          <tr>
                            <td><b>{{$t('Invoice Number')}}</b></td>
                            <td>{{order.invoice_number}}</td>
                          </tr>
                          <tr>
                            <td><b>Status</b></td>
                            <td>{{$t(status_options.filter(el=>el.value===String(order.status))[0].description)}}</td>
                          </tr>
                          <tr>
                            <td><b>{{$t('Price_table')}}</b></td>
                            <!-- <td>{{order.price_table.description}} - {{order.price_table.table_code}}</td> -->
                            <td>{{order.price_table.table_code}} - {{order.price_table.description}}</td>
                          </tr>
                          <tr>
                            <td><b>{{$t('Note')}}</b></td>
                            <td>{{order.note}}</td>
                          </tr>
                          <tr>
                          </tr>
                        </tbody> 
                    </template>
                  </v-simple-table>
                </v-col>

                <v-col>
                  <v-simple-table>
                    <template v-slot:default>
                        <tbody>
                          <tr>
                            <td><b>{{$t('Establishment')}}</b></td>
                            <td>{{order.establishment.establishment_code}} - {{order.establishment.name}} ({{order.establishment.cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5")}})</td>
                          </tr>
                          <tr>
                            <td><b>{{$t('Client_User')}}</b></td>
                            <td>{{order.client_user.first_name + ' ' + order.client_user.last_name }} ({{order.client_user.username}})</td>
                          </tr>
                          <tr>
                            <td><b>{{$t('Order Date')}}</b></td>
                            <td>{{getLocaleDate(order.order_date)}}</td>
                          </tr>
                          <tr>
                            <td><b>{{$t('Invoice Date')}}</b></td>
                            <td>{{getLocaleDate(order.invoice_date)}}</td>
                          </tr>
                          <tr>
                            <td><b>{{$t('Order Amount')}}</b></td>
                            <td>{{getRealMask(Number(order.order_amount))}}</td>
                          </tr>
                          <tr>
                            <td><b>{{$t('Order ID')}}</b></td>
                            <td>{{order.id}}</td>
                          </tr>
                          <tr v-if="!currentUserIsClientUser">
                            <td><b>{{$t('Agent Note')}}</b></td>
                            <td>{{order.agent_note}}</td>
                          </tr>
                          <tr>
                          </tr>
                          <tr>
                          </tr>
                        </tbody> 
                    </template>
                  </v-simple-table>
                </v-col>
              </v-row>
            </div>
          </div>
          <!-- Items -->
          <v-container fluid>
            <h4 class="mb-2 ml-13">{{$t('Items')}}</h4>
            <v-data-table
              :headers="view_details_ordered_items_headers"
              :items="order.ordered_items"
              class="elevation-1"
              sort-by="sequence_number"
              item-key="item.item_compound_id"
            >
              <template v-slot:item.image="{ item }">
                <v-img
                  contain
                  width="115px"
                  height="87px"
                  :lazy-src="$store.state.CDNBaseUrl + '/media/images/items/defaultimage.jpeg'"
                  :src="getImageUrl(item.item.image)"
                ></v-img>
                <!-- <p>Seq numb: {{item.sequence_number}}</p> -->
              </template>
              <template v-slot:item.item_code="{ item }">
                <p>{{item.item.item_compound_id.split('*')[2]}}</p>
              </template>
              <template v-slot:item.item_description="{ item }">
                <p>{{item.item.description}}</p>
              </template>
              <template v-slot:item.category="{ item }">
                <p>{{item.item.category}}</p>
              </template>
              <template v-slot:item.unit_price="{ item }">
                <p >{{getRealMask(Number(item.unit_price))}}</p>
              </template>
              <template v-slot:item.quantity="{ item }" >
                  <v-text-field
                    disabled
                    :value="item.quantity"
                    :label="$t('Quantity')"
                  />
              </template>
              <template v-slot:item.unit="{ item }">
                <p>{{item.item.unit}}</p>
              </template>
              <template v-slot:item.total="{ item }">
                <p >{{getRealMask(item.quantity * item.unit_price)}}</p>
              </template>
              <!-- Footer -->
              <template slot="body.append">
                  <tr class="black--text">
                      <th class="title">Total</th>
                      <th class="title"></th>
                      <th class="title"></th>
                      <th class="title"></th>
                      <th class="title"></th>
                      <th class="title"></th>
                      <th class="title">{{ getRealMask(getOrderTotal()) }}</th>
                  </tr>
              </template>
            </v-data-table>
          </v-container>
          <!-- Order History -->
          <v-expansion-panels class="ml-3">
            <v-expansion-panel @change="fetchOrderHistory">
              <v-expansion-panel-header>{{$t('Order History')}}</v-expansion-panel-header>
              <v-expansion-panel-content v-if="order_history.length > 0">
                <v-data-table
                  :headers="order_history_headers"
                  :items="order_history"
                  class="elevation-1"
                  sort-by="data"
                  item-key="data"
                  :items-per-page='-1'
                >
                  <template v-slot:item.date="{ item }">
                    <p>{{getLocaleDateAndTime(item.date)}}</p>
                  </template>
                  <template v-slot:item.user="{ item }">
                    <p>{{item.user}}</p>
                  </template>
                  <template v-slot:item.history_type="{ item }">
                    <p>{{$t(history_type_options.find(el=>el.value===item.history_type).description)}}</p>
                  </template>
                  <template v-slot:item.history_description="{ item }">
                    <p
                      v-for="(text, index) in parseHistoryDescription(item.history_description)"  
                      :key="index"
                      style="margin-bottom: 3px;"
                    >
                      <span v-if="text">{{text}}</span>
                    </p>
                  </template>
                  <template v-slot:item.agent_note="{ item }">
                    <p>{{item.agent_note}}</p>
                  </template>
                </v-data-table>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-row>
        <v-card-actions>
          <v-spacer />
          <v-btn class="black--text darken-1" text @click="$emit('close-details-dialog')">{{$t('Close')}}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { validationMixin } from "vuelidate";
import {money} from "~/helpers/validators"
import {VMoney} from 'v-money'

export default {
  mixins: [validationMixin],
  directives: {money: VMoney},
  props: ['order', 'show_view_details_dialog'],
  data() {
    return {
      note: null,
      loading: false,
      money: money,
      order_history: [],
      status_options: [
        {description: 'Canceled', value: '0'},
        {description: 'Typing', value: '1'},
        {description: 'Transferred', value: '2'},
        {description: 'Registered', value: '3'},
        {description: 'Invoiced', value: '4'},
        {description: 'Delivered', value: '5'},
      ],
      view_details_ordered_items_headers: [
        { text: this.$t('Image'), value: 'image', sortable: false },
        { text: this.$t('Code'), value: 'item_code', sortable: true },
        { text: this.$t('Description'), value: 'item_description', sortable: true },
        /** { text: this.$t('Category'), value: 'category' }, */
        { text: this.$t('Unit price'), value: 'unit_price', align: 'right', sortable: true },
        { text: this.$t('Quantity'), value: 'quantity', width: '15%', sortable: true},
        { text: this.$t('Unit'), value: 'unit', sortable: true },
        { text: 'Total', value: 'total', align: 'right', sortable: true },
      ],
      history_type_options: [
        {description: 'Inclusion', value: 'I'},
        {description: 'Alteration', value: 'A'},
        {description: 'Note', value: 'N'},
      ],
      order_history_headers: [
        { text: this.$t('Date'), value: 'date', sortable: true },
        { text: this.$t('User'), value: 'user', sortable: true },
        { text: this.$t('History type'), value: 'history_type', sortable: true },
        { text: this.$t('History description'), value: 'history_description', sortable: true },
        { text: this.$t('Agent_note'), value: 'agent_note', sortable: false },
      ],
      order_details_fetched: false,
    }
  },

  methods: {
    // Fetch Order details
    async fetchOrderHistory(){
      let order_history = await this.$store.dispatch("order/fetchOrderHistory", this.order.id);
      if (order_history){
        this.order_history = order_history
      }
    },

    // Mask
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
    getLocaleDateAndTime(value){
      if (value){
        return new Date(value).toLocaleDateString('pt-BR') + ' - ' + new Date(value).toLocaleTimeString('pt-BR') 
      }else{
        return ''
      }
    },
    parseHistoryDescription(text){
      let parsed_text = text.split('\n') 
      /** console.log(">>>>>>> parsed_text>>>>: ", parsed_text) */
      return parsed_text
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
    // Get order Total
    getOrderTotal(){
      /** console.log(">>>>>>>getOrderTotal -> this.order: ", this.order) */
      /** console.log(">>>>>>>order_details_fetched  ", this.order_details_fetched) */
      /** console.log(">>>>>>>show_view_details_dialog  ", this.show_view_details_dialog) */
      return this.order.ordered_items.reduce((previous, current)=>{
        return (typeof previous == 'number' ? previous : (previous.unit_price * previous.quantity)) + (current.unit_price * current.quantity)
      },0)
    }
  },

  computed: {
    currentUserIsClientUser(){
      return this.$store.state.user.currentUser.roles.includes('client_user')
    },
  },
  watch: {
    order: {
       handler(obj){
         /** console.log(">>>>>>>watch order: ", obj) */
         if (obj.ordered_items){
           this.order_details_fetched = true
         }
         else{
           this.order_details_fetched = false
         }
       },
       deep: true
    }
  }
}
</script>
