<template>
  <div>
    <dots-menu-update-delete :menu_items="menu_items" :handleClick="handleClick"/>

    <v-dialog v-model="show_edit_dialog" max-width="50%">
      <v-card>
        <v-card-title>{{$t('Edit')}}</v-card-title>
        <v-card-text>
          <v-container fluid>
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
                <v-expansion-panel @change="fetchItemsToUpdatePriceTable">
                  <v-expansion-panel-header>
                    <h4>{{$t('Add Price Items')}}</h4>
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
                            :label="item.item_code + ' - ' + item.description + ' ( ' + item.unit + ' )'"
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
    <v-dialog v-model="show_delete_confirmation_dialog" max-width="30%">
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
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
export default {
  mixins: [validationMixin],
  components: {
    "dots-menu-update-delete": require("@/components/dots-menu-update-delete.vue").default,
  },
  props: ['price_table', 'item_group'],
  data() {
    return {
      show_edit_dialog: false,
      show_delete_confirmation_dialog: false,
      price_items: [],
      items: [],
      description: null,
      note: null,
      loading: false,
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
            this.price_items = price_items
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
    itemCategoryInfoGroup: [
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
  },

  watch: {
    show_edit_dialog(newValue){
      if ( newValue === true) {
      }	
    }
  }
}
</script>
