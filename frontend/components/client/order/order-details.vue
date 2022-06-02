<template>
  <div v-if="order_details_fetched">
    <!-- ========= View Details Dialog ============ -->
    <v-dialog :retain-focus="false" :value="show_view_details_dialog" max-width="90%" persistent>
      <v-card class="pa-3">
        <!-- Close Butto -->
        <div style="text-align: right;"> 
          <v-icon @click="$emit('close-details-dialog')" large class="pt-2 mr-2">mdi-window-close</v-icon >
        </div>
        <v-row class="mb-1" style="padding-top: 0px;">
          <v-col style="display: flex; justify-content: center; padding-top: 0px;">
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
                            <td><b>{{$t('Order ID')}}</b></td>
                            <td>{{order.id}}</td>
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
                            <td><b>{{$t('Price_table')}}</b></td>
                            <!-- <td>{{order.price_table.description}} - {{order.price_table.table_code}}</td> -->
                            <td>{{order.price_table.table_code}} - {{order.price_table.description}}</td>
                          </tr>
                          <tr>
                            <td><b>{{$t('Invoice Date')}}</b></td>
                            <td>{{getLocaleDate(order.invoicing_date)}}</td>
                          </tr>
                          <tr>
                            <td><b>{{$t('Order Amount')}}</b></td>
                            <td>{{getRealMask(Number(order.order_amount))}}</td>
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
          <v-btn class="black--text darken-1" text @click="printOrder">{{$t('Print Order')}}</v-btn>
          <v-btn class="black--text darken-1" text @click="$emit('close-details-dialog')">{{$t('Close')}}</v-btn>
        </v-card-actions>
      </v-card>

      <!-- <p>=================================/These are the html templates to print order/==================================</p> -->
      <!-- This is being hidden by the margin-left -->
      <div style="z-index: -10000; position: fixed; margin-left: -2000px;"> 
        <div id="order_to_print" style="width: 1116px; height: 1578px; border-color: black; background-color: white;">
          <div style="padding: 50px 50px">
            <h3 class="ml-3 pt-3 mb-3" style="text-align:center">{{$t('Order Details') + ' ' + 'Nº ' + String(order.order_number)}}</h3>
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
                          <td><b>{{$t('Order ID')}}</b></td>
                          <td>{{order.id}}</td>
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
                          <td><b>{{$t('Price_table')}}</b></td>
                          <!-- <td>{{order.price_table.description}} - {{order.price_table.table_code}}</td> -->
                          <td>{{order.price_table.table_code}} - {{order.price_table.description}}</td>
                        </tr>
                        <tr>
                          <td><b>{{$t('Invoice Date')}}</b></td>
                          <td>{{getLocaleDate(order.invoicing_date)}}</td>
                        </tr>
                        <tr>
                          <td><b>{{$t('Order Amount')}}</b></td>
                          <td>{{getRealMask(Number(order.order_amount))}}</td>
                        </tr>
                        <tr>
                        </tr>
                      </tbody> 
                  </template>
                </v-simple-table>
              </v-col>
            </v-row>
            <!-- Ordered items Print -->
            <!-- <div style="height:1056px;"> -->
            <div style="height:1196px;">
              <h3 class="ml-3 pt-3 mb-3" style="text-align:center">{{$t('Order Items')}}</h3>
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th class="text-left">
                        Seq
                      </th>
                      <th class="text-left">
                        {{$t('Code')}}
                      </th>
                      <th class="text-left">
                        {{$t('Description')}}
                      </th>
                      <th class="text-left">
                        {{$t('Barcode')}}
                      </th>
                      <th class="text-right">
                        {{$t('Unit price')}}
                      </th>
                      <th class="text-right">
                        {{$t('Quantity')}}
                      </th>
                      <th class="text-left">
                        {{$t('Unit')}}
                      </th>
                      <th class="text-right">
                        Total
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="ordered_item in first_page_items " 
                      :key="ordered_item.item.item_compound_id"
                    >
                      <td>{{ordered_item.sequence_number}}</td>
                      <td>{{ordered_item.item.item_compound_id.split('*')[2]}}</td>
                      <td>{{ordered_item.item.description}}</td>
                      <td>{{ordered_item.item.barcode}}</td>
                      <td><span style="float: right;">{{getRealMask(Number(ordered_item.unit_price))}}</span></td>
                      <td><span style="float: right;">{{ordered_item.quantity}}</span></td>
                      <td>{{ordered_item.item.unit}}</td>
                      <td><span style="float: right;">{{getRealMask(ordered_item.quantity * ordered_item.unit_price)}}</span></td>
                    </tr>

                    <!-- <tr -->
                      <!-- v-for="x in first_page_items"  -->
                      <!-- :key="x.pk" -->
                    <!-- > -->
                      <!-- <td>{{x.pk}}</td> -->
                      <!-- <td>1111111111111</td> -->
                      <!-- <td>Item test Item test Item test Item test test Item test Itaaa</td> -->
                      <!-- <td>1111111111111</td> -->
                      <!-- <td><span style="float: right;">1000000</span></td> -->
                      <!-- <td><span style="float: right;">10000</span></td> -->
                      <!-- <td>uiua</td> -->
                      <!-- <td><span style="float: right;">1000000</span></td> -->
                    <!-- </tr> -->
                  </tbody>
                </template>
              </v-simple-table>
              <div id="note_with_order_total" v-if="order.ordered_items.length <= 17">
                <div class="ml-3 pt-3" style="text-align:right;">
                  <p style="margin-right: 15px"><b>Total: </b><span>{{getRealMask(getOrderTotal())}}</span></p>
                </div>
                <!-- Note -->
                <h4 class="ml-3">{{$t('Note')}}</h4>
                <p class="mt-2 ml-3">{{order.note}}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Print Other pages -->
        <div id="order_to_print_new_page" style="width: 1116px; height: 1578px; border-color: black; background-color: white;">
          <div style="padding: 50px 50px">
            <!-- Ordered items -->
            <div style="height:1196px;">
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th class="text-left">
                        Seq
                      </th>
                      <th class="text-left">
                        {{$t('Code')}}
                      </th>
                      <th class="text-left">
                        {{$t('Description')}}
                      </th>
                      <th class="text-left">
                        {{$t('Barcode')}}
                      </th>
                      <th class="text-right">
                        {{$t('Unit price')}}
                      </th>
                      <th class="text-right">
                        {{$t('Quantity')}}
                      </th>
                      <th class="text-left">
                        {{$t('Unit')}}
                      </th>
                      <th class="text-right">
                        Total
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="ordered_item in new_page_items" 
                      :key="ordered_item.item.item_compound_id"
                    >
                      <td>{{ordered_item.sequence_number}}</td>
                      <td>{{ordered_item.item.item_compound_id.split('*')[2]}}</td>
                      <td>{{ordered_item.item.description}}</td>
                      <td>{{ordered_item.item.barcode}}</td>
                      <td><span style="float: right;">{{getRealMask(Number(ordered_item.unit_price))}}</span></td>
                      <td><span style="float: right;">{{ordered_item.quantity}}</span></td>
                      <td>{{ordered_item.item.unit}}</td>
                      <td><span style="float: right;">{{getRealMask(ordered_item.quantity * ordered_item.unit_price)}}</span></td>
                    </tr>

                    <!-- <tr -->
                      <!-- v-for="x in new_page_items"  -->
                      <!-- :key="x.pk" -->
                    <!-- > -->
                      <!-- <td>{{x.pk}}</td> -->
                      <!-- <td>1111111111111111</td> -->
                      <!-- <td>aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa</td> -->
                      <!-- <td>111111111111111</td> -->
                      <!-- <td><span style="float: right;">1000000</span></td> -->
                      <!-- <td><span style="float: right;">10000</span></td> -->
                      <!-- <td>uiua</td> -->
                      <!-- <td><span style="float: right;">1000000</span></td> -->
                    <!-- </tr> -->
                  </tbody>
                </template>
              </v-simple-table>
              <div id="note_with_order_total_new_page" v-if="new_page_items.length <= 24">
                <div class="ml-3 pt-3" style="text-align:right;">
                  <p style="margin-right: 15px"><b>Total: </b><span>{{getRealMask(getOrderTotal())}}</span></p>
                </div>
                <!-- Note -->
                <h4 class="ml-3">{{$t('Note')}}</h4>
                <p class="mt-2 ml-3">{{order.note}}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </v-dialog>
  </div>
</template>

<script>
import { validationMixin } from "vuelidate"
import {money} from "~/helpers/validators"
import {VMoney} from 'v-money'

// -------------- PDF Libs
import { jsPDF } from "jspdf";
import html2canvas from 'html2canvas';

export default {
  mixins: [validationMixin],
  directives: {money: VMoney},
  props: ['order', 'show_view_details_dialog'],
  data() {
    return {
      /** ord_items: [{pk: 1}], */
      first_page_items: [],
      new_page_items: [],
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
      if (this.order_history.length === 0){
        let order_history = await this.$store.dispatch("order/fetchOrderHistory", this.order.id);
        if (order_history){
          this.order_history = order_history
        }
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
    },

    printOrder2(){
      var doc = new jsPDF();
      var name = "Doe, John"
      doc.setFontSize(12);
      doc.text(20,20,'Name: '+ name);
      doc.autoPrint();
      //This is a key for printing
      doc.output('dataurlnewwindow');
    },
    printOrder(){
      let filename = this.$t('Order') + 'Nº ' + String(this.order.order_number) + ' - ' + this.order.client.name + ".pdf"
      let ordered_items = this.order.ordered_items
      /** let ordered_items = this.ord_items */
      let new_page_items = this.new_page_items
      let nextTick = this.$nextTick

      html2canvas(document.querySelector('#order_to_print'),{
        allowTaint: true,
        useCORS: true,
        scale: 1
      }).then(async function(canvas) {
        /** document.body.appendChild(canvas); */
        const doc = new jsPDF({unit:'px'});
        doc.setFontSize(11)
        let img = canvas.toDataURL("image/png")
        /** doc.addImage({imageData:img, format:'PNG', x: 7, y:3, width: 190, height: 150, alias: 'aliasParam', compression:'FAST'}) */
        doc.addImage({imageData:img, width: 446, height: 631,format:'PNG', compression:'FAST'})
        // Add more pages if there are more than 17 items
        if (ordered_items.length > 17){
          // Calculate number of pages 
          let max_items_in_the_first_page = 21
          let max_items_per_additional_page = 29
          let number_of_the_last_item_from_the_first_additional_page =  max_items_in_the_first_page + max_items_per_additional_page 
          let note_size = 4.75
          let number_of_pages = Math.ceil((ordered_items.length + note_size - max_items_in_the_first_page) / max_items_per_additional_page) + 1
          // for each additional page
          for (let page = 2; page <= number_of_pages; page++){
            let new_doc = doc.insertPage(page)
            // Update additional page html
            new_page_items.splice(0, new_page_items.length) // empty the new_page_items array
            // add the sliced items
            let start = max_items_in_the_first_page + ((page - 2) * max_items_per_additional_page)
            let end = number_of_the_last_item_from_the_first_additional_page + ((page - 2) * max_items_per_additional_page)
            let sliced_array = ordered_items.slice(start, end)
            new_page_items.push(...sliced_array) 
            // Wait for the next tick, and add the image
            await nextTick()
            await html2canvas(document.querySelector('#order_to_print_new_page'),{
              allowTaint: true,
              useCORS: true,
              scale: 1
            }).then(function(canvas) {
              let new_page_img = canvas.toDataURL("image/png")
              new_doc.setFontSize(11)
              new_doc.addImage({imageData: new_page_img, width: 446, height: 631,format:'PNG', compression:'FAST'})
            })
          }
        }
        doc.setProperties({ title: filename })
        doc.autoPrint();
        //This is a key for printing
        doc.output('dataurlnewwindow');
        /** doc.save(filename) */
      });
    },

  },

  computed: {
    currentUserIsClientUser(){
      return this.$store.state.user.currentUser.roles.includes('client_user')
    },
  },
  watch: {
    order: {
      handler(obj){
        if (obj.ordered_items){
          // Fix ordered_items's sequence_number
          let aux_numb = 0
          this.order.ordered_items.forEach(el=> {
            aux_numb = aux_numb + 1
            el.sequence_number = aux_numb
          })
          this.order_details_fetched = true
          this.first_page_items = this.order.ordered_items.slice(0, 21) // // This is for order printing
        }
        else{
          this.order_details_fetched = false
        }
      },
      deep: true
    }
  },
  /** mounted(){ */
    /** for (let n = 2; n <= 17; n++){ */  // <- this is for test purposes
      /** this.ord_items.push({pk: n}) */
    /** } */
    /** console.log(">>>>>>> this.ord_items", this.ord_items) */
   
    /** this.first_page_items = this.ord_items.slice(0, 21) // // This is for order printing */
  /** } */
}
</script>
