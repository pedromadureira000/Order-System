<template>
  <div>
    <dots-menu :menu_items="menu_items" :handleClick="handleClick"/>

    <v-dialog :retain-focus="false" v-model="show_edit_dialog" max-width="95%">
      <v-card>
        <v-card-title>{{$t('Edit')}}</v-card-title>
        <v-card-text>
          <v-container fluid>
              <!-- Company -->
              <v-row align="center">
                <v-col
                  class="d-flex"
                  cols="12"
                  sm="6"
                >
                  <v-select
                    disabled
                    v-model="company_from_price_table"
                    :label="$t('Company')"
                    :items="companies"
                    :item-text="(x) => x.company_code + ' - ' + x.name"
                  ></v-select>
                </v-col>
              </v-row>
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
              <v-expansion-panels>
                <v-expansion-panel @change="fetchPriceItemsFromThePriceTable">
                  <v-expansion-panel-header>
                    <h3>{{$t('Edit Items')}}</h3>
                  </v-expansion-panel-header>
                  <v-expansion-panel-content>
                    <v-card outlined>
                      <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Table Items')}}</v-card-title>
                      <v-card-text>
                        <v-container fluid>
                          <v-simple-table>
                            <template v-slot:default>
                              <thead>
                                <tr>
                                  <th class="text-left">
                                    Item
                                  </th>
                                  <th class="text-left">
                                    {{$t('Unit price')}}
                                  </th>
                                  <th class="text-left">
                                    {{$t('Unit')}}
                                  </th>
                                  <th class="text-left">
                                    {{$t('Remove item')}}
                                  </th>
                                </tr>
                              </thead>
                              <tbody>
                                <tr
                                  v-for="v in $v.price_items.$each.$iter"
                                  :key="v.item.$model.item_compound_id"
                                >
                                  <td>
                                    <p>{{v.item.$model.item_compound_id.split('*')[2] + ' - ' + v.item.$model.description}}</p>
                                  </td>
                                  <td>
                                    <v-text-field
                                      :error-messages="v.errors.$model"
                                      v-model="v.masked_price.$model"
                                      @keydown.enter.prevent=""
                                      @blur="priceErrors(v)"
                                      @input="writeUnmaskedValue($event, v)"
                                      v-money="money"
                                    ></v-text-field>
                                  </td>
                                  <td>
                                    <p>{{v.item.$model.unit}}</p>
                                  </td>
                                  <td class="text-center">
                                    <v-icon @click="removeItem(v.item.$model.item_compound_id)" color="red">
                                      mdi-close-circle-outline
                                    </v-icon >
                                  </td>
                                </tr>
                              </tbody>
                            </template>
                          </v-simple-table>
                        </v-container>
                      </v-card-text>

                      <v-divider></v-divider>

                      <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Search Items')}}</v-card-title>
                      <v-card-text>
                        <v-container fluid>
                          <v-list-item-group>
                            <search-items
                              ref="search_items"
                              :category_group="category_group"
                              :companies="companies"
                              :price_table="price_table"
                              :price_items="price_items"
                              :itsForAdminItemPage="false"
                              :itsForPriceItems="true"
                              @add-item="addItem"
                            />
                            <!-- <div -->
                              <!-- v-for="(item, key) in itemsToAdd" -->
                              <!-- :key="item.item_code" -->
                            <!-- > -->
                              <!-- <v-list-item> -->
                                <!-- <v-list-item-content> -->
                                  <!-- <v-list-item-title>{{item.item_code + ' - ' + item.description + ' ( ' + item.unit + ' )'}}</v-list-item-title> -->
                                <!-- </v-list-item-content> -->

                                <!-- <v-list-item-action> -->
                                  <!-- <v-icon @click="addItem(item)"> -->
                                    <!-- mdi-plus -->
                                  <!-- </v-icon > -->
                                <!-- </v-list-item-action> -->
                              <!-- </v-list-item> -->
                              <!-- <v-divider -->
                                <!-- v-if="key < itemsToAdd.length - 1" -->
                              <!-- ></v-divider> -->
                            <!-- </div> -->
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
    "dots-menu": require("@/components/dots-menu.vue").default,
  },
  directives: {money: VMoney},
  props: ['price_table',  'companies','item_group'],
  data() {
    return {
      show_edit_dialog: false,
      show_delete_confirmation_dialog: false,
      price_items: [],
      price_items_already_fetched: false,
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
      ],
      category_group: [],
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
          // Fix price_items (item field should have item_compound_id as value)
          let price_items_fixed = this.price_items.map(el=>{
            let element = JSON.parse(JSON.stringify(el))
            // This is doing a Deep copy
            element.item = element.item.item_compound_id
            return element
          })
          let data = await this.$store.dispatch("item/updatePriceTable", {
            price_table_compound_id: this.price_table.price_table_compound_id,
            price_items: price_items_fixed,
            description: this.description,
            note: this.note,
          })
          // Reactivity for PriceTable list inside PriceTable.vue 
          this.loading = false;
          if (data) {
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

      /** async fetchItemsToUpdatePriceTable(){ */
          /** let items = await this.$store.dispatch("item/fetchItemsToCreatePriceTable", this.price_table.item_table);  */
          /** if (items){ */
            /** this.items = items */
          /** } */
      /** }, */

      async fetchPriceItemsFromThePriceTable(){
        // it jill run every time the v-expansion-panel emit @change 
        if (!this.price_items_already_fetched) {
          let price_items = await this.$store.dispatch("item/fetchPriceItemsFromThePriceTable", this.price_table.price_table_compound_id); 
          if (price_items){
            for (let index in price_items){
              let price_item = price_items[index]
              price_item['errors'] = []
              price_item['masked_price'] = price_item.unit_price.toLocaleString('pt-br',{style: 'currency', currency: 'BRL'})
            }
            this.price_items = price_items
            this.price_items_already_fetched = true
            console.log(">>>>>>> this.price_items: ", this.price_items)
          }
        }
      },

      // Price Item Functions
      removeItem(item_compound_id){
        this.price_items = this.price_items.filter((obj)=> obj.item.item_compound_id !== item_compound_id)
      },
      addItem(item){
        item.unit_price = null
        this.price_items.push({item: {item_compound_id: item.item_compound_id, description: item.description, unit: item.unit}, 
          unit_price: 0, masked_price: '', errors: []})
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

<style scoped>
</style>
