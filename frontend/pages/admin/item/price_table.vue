<template>
  <p v-if="$fetchState.pending">{{$t('Fetching_data')}}</p>
  <p v-else-if="$fetchState.error">{{$t('Error_fetching_data')}}</p>
  <div v-else>
    <div class="ma-3">
      <v-expansion-panels v-if="hasCreatePriceTablePermission()">
        <v-expansion-panel>
          <v-expansion-panel-header>
            <h3>{{$t('Create Price Table')}}</h3>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <form @submit.prevent="createPriceTable">
              <!-- Company -->
              <v-row align="center">
                <v-col
                  class="d-flex"
                  cols="12"
                  sm="6"
                >
                  <v-select
                    v-model="company"
                    :label="$t('Company')"
                    :items="companies"
                    :item-text="(x) => x.company_code + ' - ' + x.name"
                    :item-value="(x) => x"
                    @change="fetchItemsToCreatePriceTable"
                  ></v-select>
                </v-col>
              </v-row>
              <!-- Price Table Code -->
              <v-text-field
                :label="$t('Price Table Code')"
                v-model="table_code"
                :error-messages="tableCodeErrors"
                required
                @blur="$v.table_code.$touch()"
                class="mb-3"
              />
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
                class="mb-3"
              />
              <!-- Price Items -->
              <v-expansion-panels>
                <v-expansion-panel>
                  <v-expansion-panel-header>
                    <h3>{{$t('Add Items')}}</h3>
                  </v-expansion-panel-header>
                  <v-expansion-panel-content>
                    <v-card outlined>
                      <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Table Items')}}</v-card-title>
                      <v-card-text>
                        <v-container fluid>
                          <v-text-field
                            v-for="v in $v.price_items.$each.$iter"
                            :key="v.item.$model"
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

              <!-- Submit -->
              <v-btn
                class="mt-3"
                color="primary"
                type="submit"
                :loading="loading"
                :disabled="loading"
              >{{$t('Submit')}}</v-btn>
            </form>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>

      <div v-if="hasGetPriceTablesPermission()">
        <h3 class="mt-6">{{$t('Edit Price Table')}}</h3>
        <v-data-table
          :headers="headers"
          :items="price_tables"
          :items-per-page="10"
          item-key="price_table_compound_id"
          class="elevation-1 mt-3"
        >
          <template v-slot:item.company="{ item }">
            <p>{{item.company.split('*')[1] + ' - ' + item.company_name}}</p>
          </template>
          <template v-slot:item.description="{ item }">
            <p style="width: 240px;">{{item.description}}</p>
          </template>
          <template v-slot:item.actions="{ item }">
            <price-table-edit-menu :price_table="item" :companies="companies" :item_group="item_group" @price-table-deleted="deletePriceTable(item)" />
          </template>
        <template v-slot:item.note="{ item }">
          <p>{{$getNote(item.note)}}</p>
        </template>
        </v-data-table>
      </div>
    </div>
  </div>
</template>

<script>
import {
  required,
  maxLength,
  minLength,
  minValue,
  maxValue,
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
import {slugFieldValidator, money} from "~/helpers/validators"
import {VMoney} from 'v-money'

export default {
  middleware: ["authenticated"],
  components: {
    "price-table-edit-menu": require("@/components/admin/item/price-table-edit-menu.vue").default,
  },
  mixins: [validationMixin],
  directives: {money: VMoney},
  data() {
    return {
      company: null,
      table_code: null,
      description: null,
      note: "",
      price_items: [],
      /**EX: [{item: '123$123$111111', unit_price: 1055.55}, masked_price: "R$ 1.055,55" , errors: []] */
      items: [],
      companies: [],
      item_group: [],
      /**EX:  item_group: [{item_table: '123$123', items: [{categoryObj, categoryObj2 }]}] */
      price_tables: [],
      loading: false,
      money: money,
      headers: [
        { text: this.$t('Company'), value: 'company' },
        { text: this.$t('Table_code'), value: 'table_code' },
        { text: this.$t('Description'), value: 'description' },
        { text: this.$t('Note'), value: 'note' },
        { text: this.$t('Actions'), value: 'actions' },
      ]
    };
  },

  async fetch() {
    let price_tables = await this.$store.dispatch("item/fetchPriceTables");
    if (price_tables){this.price_tables.push(...price_tables)}

    // Fetch Companies
    let companies = await this.$store.dispatch("item/fetchCompaniesToCreatePriceTable"); 
    if (companies){
      this.companies.push(...companies)
      if (this.companies.length > 0){
        this.company = this.companies[0]
        await this.fetchItemsToCreatePriceTable()
      }
    }
  },

  methods: {
    async createPriceTable() {
      this.$v.priceTableInfoGroup.$touch();
      if (this.$v.priceTableInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t('Please_fill_the_form_correctly'), alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let data = await this.$store.dispatch("item/createPriceTable", {
          company: this.company.company_compound_id,
          price_items: this.price_items,
          table_code: this.table_code,
          description: this.description,
          note: this.note,
        });
        if (data) {
          this.price_tables.push(data);
        }
        this.loading = false;
      }
    },
    deletePriceTable(itemToDelete) {
      this.price_tables = this.price_tables.filter((item) => item.price_table_compound_id != itemToDelete.price_table_compound_id);
    },

    async fetchItemsToCreatePriceTable(){
          let item_already_exists = this.item_group.find(el=>el.item_table == this.company.item_table)
          if (item_already_exists){
            this.items = item_already_exists.items
          }
          else{
            let items = await this.$store.dispatch("item/fetchItemsToCreatePriceTable", this.company.item_table); 
            if (items){
              this.item_group.push({item_table: this.company.item_table, items: items} )
              this.items = items
            }
          }
    },

    // Price Item Functions
    removeItem(item_compound_id){
      this.price_items = this.price_items.filter((obj)=> obj.item !== item_compound_id)
    },
    addItem(item){
      this.price_items = this.price_items.concat([{item: item.item_compound_id, unit_price: 0, masked_price: '', errors: []}])
    },
    itemDescription(item_compound_id){
      let item = this.items.filter((item)=> item.item_compound_id === item_compound_id)[0]
      return item.item_code + " - " + item.description + " ( " + item.unit + " )" 
    },

    // Permission Functions

    hasCreatePriceTablePermission(){
      let user = this.$store.state.user.currentUser;
      return user.permissions.includes("create_price_table")
    },
    hasGetPriceTablesPermission(){
      let user = this.$store.state.user.currentUser;
      return user.permissions.includes("get_price_tables")
    },

    // Validate item
    priceErrors(v) {
      const errors = [];
      /** if (!v.unit_price.$dirty){ */
      /** } */
      !v.unit_price.minValue && errors.push(this.$formatStr(this.$t("This_value_must_be_greater_than_X"), 'R$ 0,00'));
      !v.unit_price.maxValue && errors.push(this.$formatStr(this.$t("This_value_must_be_less_than_X"), 'R$ 999.999.999,99'));
      v.errors.$model = errors;
    },

    // masked_price: "R$ 1.000,00" is written over unit_price as "1000.00"
    writeUnmaskedValue(event, v){
      v.unit_price.$model = event.replace('R$ ', '').replace(/\./gi,'').replace(',','.')
      /** console.log(">>>>>>> unmasked value: ", v.unit_price.$model) */
    }
  },

  validations: {
    table_code: {
      required, 
      slugFieldValidator, 
      maxLength: maxLength(7)
    },
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
    priceTableInfoGroup: [
      "table_code",
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
    tableCodeErrors() {
      const errors = [];
      if (!this.$v.table_code.$dirty) return errors;
      !this.$v.table_code.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.table_code.slugFieldValidator && errors.push(this.$t('SlugFieldErrorMessage'));
      !this.$v.table_code.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 7));
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
