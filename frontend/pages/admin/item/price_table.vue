<template>
  <p v-if="$fetchState.pending">Fetching data ...</p>
  <p v-else-if="$fetchState.error">An error occurred :(</p>
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
              <v-text-field
                :label="$t('Note')"
                v-model.trim="note"
                :error-messages="noteErrors"
                @blur="$v.note.$touch()"
                required
                class="mb-3"
              />
              <!-- Price Items -->
              <v-expansion-panels>
                <v-expansion-panel>
                  <v-expansion-panel-header>
                    <h3>{{$t('Add Price Items')}}</h3>
                  </v-expansion-panel-header>
                  <v-expansion-panel-content>
                    <v-card>
                      <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Remove Items')}}</v-card-title>
                      <v-card-text>
                        <v-container fluid>
                          <v-text-field
                            v-for="(price_item, key) in price_items"
                            :key="key"
                            v-model="price_item.unit_price"
                            :label="itemDescription(price_item.item)"
                            type="number"
                            @keydown.enter.prevent=""
                          >
                            <template v-slot:append>
                              <v-icon @click="removeItem(price_item)">
                                mdi-minus
                              </v-icon >
                            </template>
                          </v-text-field>
                        </v-container>
                      </v-card-text>

                      <v-divider></v-divider>

                      <v-card-title style="font-size: 1rem; font-weight: 400; line-height: 1rem">{{$t('Add Items')}}</v-card-title>
                      <v-card-text>
                        <v-container fluid>
                            <!-- @input="item.unit_price = $event" -->
                          <v-text-field
                            v-for="(item, key) in itemsToAdd"
                            :key="key"
                            v-model="item.unit_price"
                            :label="item.item_code + ' - ' + item.description"
                            @keydown.enter.prevent="addItem(item)"
                            type="number"
                          >
                            <template v-slot:append>
                              <v-icon @click="addItem(item)" :disabled="item.unit_price == null">
                                mdi-plus
                              </v-icon >
                            </template>
                          </v-text-field>
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
          class="elevation-1"
        >
          <template v-slot:item.actions="{ item }">
            <price-table-edit-menu :price_table="item" :item_group="item_group" @price-table-deleted="deletePriceTable(item)" />
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
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
import {slugFieldValidator} from "~/helpers/validators"

export default {
  middleware: ["authenticated"],
  components: {
    "price-table-edit-menu": require("@/components/admin/item/price-table-edit-menu.vue").default,
  },
  mixins: [validationMixin],

  data() {
    return {
      company: null,
      table_code: null,
      description: null,
      note: "",
      price_items: [],
      items: [],
      companies: [],
      /**EX:  item_group: [{item_table: '123$123', items: [{categoryObj, categoryObj2 }]}] */
      item_group: [],
      price_tables: [],
      loading: false,
      headers: [
        { text: this.$t('Company'), value: 'company' },
        { text: this.$t('Description'), value: 'description' },
        { text: this.$t('Price table code'), value: 'table_code' },
        { text: this.$t('Note'), value: 'note' },
        { text: this.$t('Actions'), value: 'actions' },
      ]
    };
  },

  async fetch() {
    let price_tables = await this.$store.dispatch("item/fetchPriceTables");
    if (price_tables){this.price_tables.push(...price_tables)}

    // Fetch Companies
    let companies = await this.$store.dispatch("item/fetchCompaniesToCreateItemOrCategoryOrPriceTable"); 
    if (companies){this.companies.push(...companies)}
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
    removeItem(item){
      this.price_items = this.price_items.filter((obj)=> obj !== item)
    },
    addItem(item){
      this.price_items = this.price_items.concat([{item: item.item_compound_id, unit_price: item.unit_price}])
      item.unit_price = null
    },
    itemDescription(item_compound_id){
      let item = this.items.filter((item)=> item.item_compound_id === item_compound_id)[0]
      return item.item_code + " - " + item.description 
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
    priceTableInfoGroup: [
      "table_code",
      "description",
      "note",
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
