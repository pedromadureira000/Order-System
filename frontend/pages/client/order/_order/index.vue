<template>
  <div>
    <dots-menu-update-delete :menu_items="menu_items" :handleClick="handleClick"/>

    <v-dialog :retain-focus="false" v-model="show_edit_dialog" max-width="50%">
      <v-card>
        <v-card-title>{{$t('Edit')}}</v-card-title>
        <v-card-text>
          <v-container fluid>
              <!-- Ordered items -->
              <v-card>
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
              <!-- Description -->
              <v-text-field
                :label="$t('Description')"
                v-model.trim="description"
                :error-messages="descriptionErrors"
                @blur="$v.description.$touch()"
                required
                class="mb-3"
              />
              <!-- Note -->
              <v-textarea
                outlined
                :label="$t('Note')"
                v-model.trim="note"
                :error-messages="noteErrors"
                @blur="$v.note.$touch()"
                required
                class="mb-3"
              />
              <!-- Price Items -->
              <!-- <v-expansion-panels> -->
                <!-- <v-expansion-panel @change="fetchItemsToUpdatePriceTable"> -->
                  <!-- <v-expansion-panel-header> -->
                    <!-- <h4>{{$t('Add Price Items')}}</h4> -->
                  <!-- </v-expansion-panel-header> -->
                  <!-- <v-expansion-panel-content> -->
                    <!-- <v-card> -->
                      <!-- <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Remove Items')}}</v-card-title> -->
                      <!-- <v-card-text> -->
                        <!-- <v-container fluid> -->
                          <!-- <v-text-field -->
                            <!-- v-for="(price_item, key) in price_items" -->
                            <!-- :key="key" -->
                            <!-- v-model="price_item.unit_price" -->
                            <!-- :label="itemDescription(price_item.item)" -->
                            <!-- type="number" -->
                            <!-- @keydown.enter.prevent="" -->
                          <!-- > -->
                            <!-- <template v-slot:append> -->
                              <!-- <v-icon @click="removeItem(price_item)"> -->
                                <!-- mdi-minus -->
                              <!-- </v-icon > -->
                            <!-- </template> -->
                          <!-- </v-text-field> -->
                        <!-- </v-container> -->
                      <!-- </v-card-text> -->

                      <!-- <v-divider></v-divider> -->

                      <!-- <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Add Items')}}</v-card-title> -->
                      <!-- <v-card-text> -->
                        <!-- <v-container fluid> -->
                          <!-- <v-text-field -->
                            <!-- v-for="(item, key) in itemsToAdd" -->
                            <!-- :key="key" -->
                            <!-- v-model="item.unit_price" -->
                            <!-- :label="item.item_code + ' - ' + item.description + ' ( ' + item.unit + ' )'" -->
                            <!-- @keydown.enter.prevent="addItem(item)" -->
                            <!-- type="number" -->
                          <!-- > -->
                            <!-- <template v-slot:append> -->
                              <!-- <v-icon @click="addItem(item)" :disabled="item.unit_price == null"> -->
                                <!-- mdi-plus -->
                              <!-- </v-icon > -->
                            <!-- </template> -->
                          <!-- </v-text-field> -->
                        <!-- </v-container> -->
                      <!-- </v-card-text> -->
                    <!-- </v-card> -->
                  <!-- </v-expansion-panel-content> -->
                <!-- </v-expansion-panel> -->
              <!-- </v-expansion-panels> -->

              <v-expansion-panels>
                <v-expansion-panel @change="fetchItemsToUpdatePriceTable">
                  <v-expansion-panel-header>
                    <h3>{{$t('Edit Items')}}</h3>
                  </v-expansion-panel-header>
                  <v-expansion-panel-content>
                    <v-card outlined>
                      <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Table Items')}}</v-card-title>
                      <v-card-text>
                        <v-container fluid>
                          <v-text-field
                            v-for="(v, key) in $v.price_items.$each.$iter"
                            :key="key"
                            :error-messages="v.errors.$model"
                            :label="itemDescription(v.item.$model)"
                            v-model="v.masked_price.$model"
                            @keydown.enter.prevent=""
                            @blur="priceErrors(v)"
                            @input="writeUnmaskedValue($event, v)"
                            v-money="money"
                          >
                            <template v-slot:append>
                              <v-icon @click="removeItem(v.item.$model)">
                                mdi-minus
                              </v-icon >
                            </template>
                          </v-text-field>
                        </v-container>
                      </v-card-text>

                      <v-divider></v-divider>

                      <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Available Items')}}</v-card-title>
                      <v-card-text>
                        <v-container fluid>
                          <v-list-item-group>
                            <div
                              v-for="(item, key) in itemsToAdd"
                              :key="key"
                            >
                              <v-list-item>
                                <v-list-item-content>
                                  <v-list-item-title>{{item.item_code + ' - ' + item.description + ' ( ' + item.unit + ' )'}}</v-list-item-title>
                                </v-list-item-content>

                                <v-list-item-action>
                                  <v-icon @click="addItem(item)">
                                    mdi-plus
                                  </v-icon >
                                </v-list-item-action>
                              </v-list-item>
                              <v-divider
                                v-if="key < itemsToAdd.length - 1"
                                :key="key"
                              ></v-divider>
                            </div>
                          </v-list-item-group>
                        </v-container>
                      </v-card-text>
                    </v-card>
                  </v-expansion-panel-content>
                </v-expansion-panel>
              </v-expansion-panels>


          </v-container>
        </v-card-text>
        <v-divider></v-divider>
        <!-- Submit Button -->
        <v-card-actions class="d-flex justify-space-around" style="width:100%;">
          <v-btn class="blue--text darken-1" text @click="show_edit_dialog = false">{{$t('Cancel')}}</v-btn>
          <v-btn 
            class="blue--text darken-1" 
            text 
            @click="updatePriceTable()"
            :loading="loading"
            :disabled="loading"
          >{{$t('Save')}}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- Delete Confirmation Dialog -->
    <v-dialog :retain-focus="false" v-model="show_delete_confirmation_dialog" max-width="30%">
      <v-card>
        <v-card-title>{{$t('Are_you_sure_you_want_to_delete')}}</v-card-title>
        <v-card-text>
          <v-card-actions class="d-flex justify-space-around" style="width:100%;">
            <v-btn class="black--text darken-1" text @click="show_delete_confirmation_dialog = false">{{$t('Cancel')}}</v-btn>
            <v-btn class="red--text darken-1" text @click="deletePriceTable()">{{$t('Delete')}}</v-btn>
          </v-card-actions>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import {
  required,
  minLength,
  maxLength,
  minValue,
  maxValue,
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
import {money} from "~/helpers/validators"
import {VMoney} from 'v-money'

export default {
  mixins: [validationMixin],
  components: {
    "dots-menu-update-delete": require("@/components/dots-menu-update-delete.vue").default,
  },
  directives: {money: VMoney},
  props: ['price_table',  'companies','item_group'],
  data() {
    return {
      show_edit_dialog: false,
      show_delete_confirmation_dialog: false,
      price_items: [],
      items: [],
      description: null,
      note: null,
      loading: false,
      money: money,
      company_from_price_table: "",
      menu_items: [
      ...(this.hasUpdatePriceTablePermission() ? [{ 
          title: this.$t('Edit'),
          icon: 'mdi-pencil',
          async click(){
            this.show_edit_dialog = true
          }
        }] : [] ),
        ...(this.hasDeletePriceTablePermission() ? [{ 
          title: this.$t('Delete'),
          icon: 'mdi-delete',
          async click(){
            this.show_delete_confirmation_dialog = true
          }
        }] : []),
      ]
    }
  },

    methods: {
      handleClick(index){
        //this.menu_items[id].click()  #will get errors because the function click will not access properties with its own 'this'
        this.menu_items[index].click.call(this) // will call the function but the function will use the vue instance 'this' context.
      },

      async updatePriceTable(){
        this.$v.itemCategoryInfoGroup.$touch();
        if (this.$v.itemCategoryInfoGroup.$invalid) {
          this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
        } else {
          this.loading = true;
          let data = await this.$store.dispatch("item/updatePriceTable", {
            price_table_compound_id: this.price_table.price_table_compound_id,
            price_items: this.price_items,
            description: this.description,
            note: this.note,
          })
          // Reactivity for PriceTable list inside PriceTable.vue 
          this.loading = false;
          if (data) {
            this.price_table.price_items = this.price_items,
            this.price_table.description = data.description
            this.price_table.note = data.note
              // Close dialog
            this.show_edit_dialog = false
          }
        }
      },
      async deletePriceTable(){
        let data = await this.$store.dispatch(
          'item/deletePriceTable', 
          {price_table_compound_id: this.price_table.price_table_compound_id}
        )
        if (data === "ok"){
          this.$emit('price-table-deleted')
        }
      },

      // TODO : it would be better if it have only one query
      async fetchItemsToUpdatePriceTable(){
        // it would run every time the v-expansion-panel emited @change if in didn't add this if
        if (this.items.length === 0) {
          /** console.log(">>>>>>> $$$$$$$$$$$$$$ this.price_table.item_table: ", this.price_table.item_table) */
          /** console.log(">>>>>>> $$$$$$$$$$$$$$ this.item_group: ", this.item_group) */
          let item_group_already_exists = this.item_group.find(el=>el.item_table===this.price_table.item_table)
          if (item_group_already_exists){
            this.items = item_group_already_exists.items
          } 
          else {
            let items = await this.$store.dispatch("item/fetchItemsToCreatePriceTable", this.price_table.item_table); 
            if (items){
              this.item_group.push({item_table: this.price_table.item_table, items: items} )
              this.items = items
              /** console.log(">>>>>>> !!!!!!!!!!! what is going on? ", this.item_group) */
            }
          }
          // Fetch price items after fetch items
          //TODO it could receive price_items from the parent component (when you have just created a price_table for ex)
          this.fetchPriceItemsFromThePriceTable()
        }
      },

      async fetchPriceItemsFromThePriceTable(){
          let price_items = await this.$store.dispatch("item/fetchPriceItemsFromThePriceTable", this.price_table.price_table_compound_id); 
          if (price_items){
            for (let index in price_items){
              let price_item = price_items[index]
              price_item['errors'] = []
              price_item['masked_price'] = price_item.unit_price.toLocaleString('pt-br',{style: 'currency', currency: 'BRL'})
            }
            this.price_items = price_items
        }
      },

      // Price Item Functions
      removeItem(item_compound_id){
        this.price_items = this.price_items.filter((obj)=> obj.item !== item_compound_id)
      },
      addItem(item){
        this.price_items = this.price_items.concat([{item: item.item_compound_id, unit_price: 0, masked_price: '', errors: []}])
        item.unit_price = null
      },
      itemDescription(item_compound_id){
        let item = this.items.filter((item)=> item.item_compound_id === item_compound_id)[0]
        return item.item_code + " - " + item.description + " ( " + item.unit + " )" 
      },

      // Permission Functions
      hasUpdatePriceTablePermission(){
        let user = this.$store.state.user.currentUser;
        return user.permissions.includes("update_price_table")
      },

      hasDeletePriceTablePermission(){
        let user = this.$store.state.user.currentUser;
        return user.permissions.includes("delete_price_table")
      },

      // Validate item
      priceErrors(v) {
        const errors = [];
        !v.unit_price.minValue && errors.push(this.$formatStr(this.$t("This_value_must_be_greater_than_X"), 'R$ 0,00'));
        !v.unit_price.maxValue && errors.push(this.$formatStr(this.$t("This_value_must_be_less_than_X"), 'R$ 999.999.999,99'));
        v.errors.$model = errors;
      },

      // masked_price: "R$ 1.000,00" is written over unit_price as "1000.00"
      writeUnmaskedValue(event, v){
        v.unit_price.$model = event.replace('R$ ', '').replace(/\./gi,'').replace(',','.')
        /** console.log(">>>>>>> unmasked value: ", v.unit_price.$model) */
      },
    },

  validations: {
    description: { 
      required, 
      minLength: minLength(3),
      maxLength: maxLength(60)
    },
    note: {
      maxLength: maxLength(800)
    },
    price_items: {
      $each: {
        unit_price: {
          maxValue: maxValue(999999999.99),
          minValue: minValue(0.01),
        },
        item: {},
        errors: {},
        masked_price: {}
      }
    },
    itemCategoryInfoGroup: [
      "description",
      "note",
      "price_items"
    ],
  },

  computed: {
    descriptionErrors() {
      const errors = [];
      if (!this.$v.description.$dirty) return errors;
      !this.$v.description.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.description.minLength && errors.push(this.$formatStr(this.$t("This_field_must_have_at_least_X_characters"), 3));
      !this.$v.description.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 60));
      return errors;
    },
    noteErrors() {
      const errors = [];
      if (!this.$v.note.$dirty) return errors;
      !this.$v.note.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 800));
      return errors;
    },

    // Item Price
    itemsToAdd(){
      return this.items.filter((item)=> {
        let return_value = true
        let price_items = this.price_items
        for (const prop in price_items){
          if (price_items[prop].item === item.item_compound_id){
            return_value = false
          }
        }
        return return_value
      })
    }
  },

  mounted() {
    this.description = this.price_table.description
    this.note = this.price_table.note
    // Default value for company_from_price_table
    this.company_from_price_table = this.companies.find(el=>el.company_compound_id === this.price_table.company)
  },

  /** watch: { */
    /** show_edit_dialog(newValue){ */
      /** if ( newValue === true) { */
      /** }	 */
    /** } */
  /** } */
}
</script>
