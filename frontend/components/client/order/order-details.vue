<template>
  <div v-if="order_details_fetched">
    <!-- ========= View Details Dialog ============ -->
    <v-dialog :retain-focus="false" v-model="show_view_details_dialog" max-width="75%" persistent>
      <v-card class="pa-3">
        <v-row class="mb-1">
          <v-col style="display: flex; justify-content: center;">
            <h3 class="ml-3 pt-3">{{$t('Order Details')}}</h3>
          </v-col>
        </v-row>
        <v-row style="display: flex; justify-content: center;">
          <v-simple-table>
            <template v-slot:default>
                <tbody>
                  <tr>
                    <td><b>{{$t('Company')}}</b></td>
                    <td>{{order.company.company_code}} - {{order.company.name}}</td>
                  </tr>
                  <tr>
                    <td><b>{{$t('Establishment')}}</b></td>
                    <td>{{order.establishment.establishment_code}} - {{order.establishment.name}} ({{order.establishment.cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5")}})</td>
                  </tr>
                  <tr>
                    <td><b>{{$t('Client')}}</b></td>
                    <td>{{order.client.client_code}} - {{order.client.name}} ({{order.establishment.cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5")}})</td>
                  </tr>
                  <tr>
                    <td><b>{{$t('Client User')}}</b></td>
                    <td>{{order.client_user.username}}</td>
                  </tr>
                  <tr>
                    <td><b>{{$t('Price_table')}}</b></td>
                    <!-- <td>{{order.price_table.description}} - {{order.price_table.table_code}}</td> -->
                    <td>{{order.price_table.table_code}} - {{order.price_table.description}}</td>
                  </tr>
                  <tr>
                    <td><b>{{$t('Order Number')}}</b></td>
                    <td>{{order.order_number}}</td>
                  </tr>
                  <tr>
                    <td><b>{{$t('Order Date')}}</b></td>
                    <td>{{getLocaleDate(order.order_date)}}</td>
                  </tr>
                  <tr>
                    <td><b>Status</b></td>
                    <td>{{$t(status_options.filter(el=>el.value===String(order.status))[0].description)}}</td>
                  </tr>
                  <tr>
                    <td><b>{{$t('Invoice Number')}}</b></td>
                    <td>{{order.invoice_number}}</td>
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
                    <td><b>{{$t('Note')}}</b></td>
                    <td>{{order.note}}</td>
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
          <v-container fluid>
            <h4 class="mb-2">{{$t('Items')}}</h4>
            <v-data-table
              :headers="view_details_ordered_items_headers"
              :items="order.ordered_items"
              class="elevation-1"
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
              <template v-slot:item.unit="{ item }">
                <p>{{item.item.unit}}</p>
              </template>
              <template v-slot:item.unit_price="{ item }">
                <p>{{getRealMask(Number(item.unit_price))}}</p>
              </template>
              <template v-slot:item.quantity="{ item }">
                <v-text-field
                  disabled
                  :value="item.quantity"
                  :label="$t('Quantity')"
                />
              </template>
              <template v-slot:item.total="{ item }">
                <p>{{getRealMask(item.quantity * item.unit_price)}}</p>
              </template>
            </v-data-table>
          </v-container>
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
  props: ['order', 'show_view_details_dialog', 'order_details_fetched'],
  data() {
    return {
      note: null,
      loading: false,
      money: money,
      status_options: [
        {description: 'Canceled', value: '0'},
        {description: 'Typing', value: '1'},
        {description: 'Transferred', value: '2'},
        {description: 'Registered', value: '3'},
        {description: 'Invoiced', value: '4'},
        {description: 'Delivered', value: '5'},
      ],
      view_details_ordered_items_headers: [
        { text: this.$t('Image'), value: 'image' },
        { text: this.$t('Code'), value: 'item_code' },
        { text: this.$t('Description'), value: 'item_description' },
        { text: this.$t('Category'), value: 'category' },
        { text: this.$t('Unit'), value: 'unit' },
        { text: this.$t('Unit price'), value: 'unit_price' },
        { text: this.$t('Quantity'), value: 'quantity' },
        { text: 'Total', value: 'total' },
      ],
    }
  },

  methods: {
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

  computed: {
    currentUserIsClientUser(){
      return this.$store.state.user.currentUser.roles.includes('client_user')
    }
  }
}
</script>
