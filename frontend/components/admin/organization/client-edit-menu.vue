<template>
  <div>
    <dots-menu-update-delete :menu_items="menu_items" :handleClick="handleClick"/>

    <v-dialog v-model="show_edit_dialog" max-width="50%">
      <v-card>
        <v-card-title>{{$t('Edit')}}</v-card-title>
        <v-card-text>
          <v-container fluid>
            <!-- Client Table -->
            <v-row align="center">
              <v-col
                class="d-flex"
                cols="12"
                sm="6"
              >
                <v-select
                  disabled
                  v-model="client_table_from_client"
                  :label="$t('Client_Table')"
                  :items="client_tables"
                  :item-text="(x) => x.client_table_code"
                ></v-select>
              </v-col>
            </v-row>
            <!-- Name -->
            <v-text-field
              :label="$t('Name')"
              v-model="name"
              :error-messages="nameErrors"
              required
              @blur="$v.name.$touch()"
              class="mb-3"
            />
            <!-- CNPJ -->
            <v-text-field
              label="CNPJ"
              v-model="cnpj"
              v-mask="'##.###.###/####-##'"
              required
              :error-messages="cnpjError"
              @blur="$v.cnpj.$touch()"
              class="mb-3"
            />
            <!-- Client Status -->
            <v-radio-group v-model="status" style="width: 25%;" label='Status' class="mb-3">
              <v-radio
                :label="$t('Active')"
                value=1
              ></v-radio>
              <v-radio
                :label="$t('Disabled')"
                value=0
              ></v-radio>
            </v-radio-group>
            <!-- Vendor Code -->
            <v-text-field
              :label="$t('Vendor_Code')"
              v-model="vendor_code"
              :error-messages="vendorCodeErrors"
              @blur="$v.vendor_code.$touch()"
              class="mb-3"
            />

            <!-- Client Establishments -->
            <v-expansion-panels class="mb-5">
              <v-expansion-panel>
                <v-expansion-panel-header>{{$t('Client_Establishments')}}</v-expansion-panel-header>
                  <v-expansion-panel-content v-if="establishments.length > 0">
                    <v-container
                      v-for="establishment in establishments"
                      :key="establishment.establishment_compound_id"
                      class="grey lighten-5 mb-6"
                    >
                      <v-row align="center" class="ml-1 mt-0">
                        <v-col>
                          <!-- 'value' is a variable because 'value' is passed by reference. If a literal -->
                          <!-- was used, it will not be possible to update cli_estab.price_table -->
                          <v-checkbox
                            :label="establishment.establishment_code + ' - ' + establishment.name + ' (' + $t('Company') + ': ' + establishment.company + ')'"
                            v-model="client_establishments"
                            :value="establishment['AUX_cli_estab_' + client.client_compound_id]"
                            hide-details
                            class="shrink mr-2 mt-0"
                          ></v-checkbox>
                        </v-col>
                        <v-col>
                          <price-table-v-select 
                            :client_establishments='client_establishments' 
                            :establishment='establishment' 
                            :price_table_groups='price_table_groups'
                            :aux_cli_estab="establishment['AUX_cli_estab_' + client.client_compound_id]"
                            @update-price-table='updatePriceTable'
                            @update-price-table-groups='updatePriceTableGroups'
                          />
                        </v-col>
                      </v-row>
                      </v-container>
                  </v-expansion-panel-content>
              </v-expansion-panel>
            </v-expansion-panels>

            <!-- Note -->
            <v-textarea
              outlined
              :label="$t('Note')"
              v-model="note"
              :error-messages="noteErrors"
              @blur="$v.note.$touch()"
              class="mb-3"
            />
          </v-container>
        </v-card-text>
        <v-divider></v-divider>
        <!-- Submit Button -->
        <v-card-actions class="d-flex justify-space-around" style="width:100%;">
          <v-btn class="blue--text darken-1" text @click="show_edit_dialog = false">{{$t('Cancel')}}</v-btn>
          <v-btn 
            class="blue--text darken-1" 
            text 
            @click="updateClient()"
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
        <v-card-text class="d-flex justify-center">
          <v-card-actions class="d-flex justify-space-around" style="width:100%;">
            <v-btn class="black--text darken-1" text @click="show_delete_confirmation_dialog = false">{{$t('Cancel')}}</v-btn>
            <v-btn class="red--text darken-1" text @click="deleteClient()">{{$t('Delete')}}</v-btn>
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
import {cnpjFieldValidator} from "~/helpers/validators"
import {mask} from 'vue-the-mask'
export default {
  mixins: [validationMixin],
  components: {
    "dots-menu-update-delete": require("@/components/dots-menu-update-delete.vue").default,
    "price-table-v-select": require("@/components/admin/organization/price-table-v-select.vue").default,
  },
  directives: {mask},
  props: ['client', 'client_tables','establishment_groups', 'price_table_groups'],
  data() {
    return {
      client_table_from_client: null,
      show_edit_dialog: false,
      show_delete_confirmation_dialog: false,
      client_establishments: [],
      establishments: [],
      name: null,
      cnpj: null,
      status: null,
      vendor_code: null,
      note: null,
      loading: false,
      menu_items: [
      ...(this.hasUpdateClientPermission() ? [{ 
          title: this.$t('Edit'),
          icon: 'mdi-pencil',
          async click(){
            this.show_edit_dialog = true
          }
        }] : [] ),
        ...(this.hasDeleteClientPermission() ? [{ 
          title: this.$t('Delete'),
          icon: 'mdi-delete',
          async click(){
            this.show_delete_confirmation_dialog = true
          }
        }] : []),
      ]
    }
  },

  validations: {
    name: { 
      required, 
      minLength: minLength(3),
      maxLength: maxLength(60)
    },
    cnpj: {
      required, 
      cnpjFieldValidator,
    },
    vendor_code: {
      maxLength: maxLength(9)
    },
    note: {
      maxLength: maxLength(800)
    },
    clientInfoGroup: [
      "name",
      "cnpj",
      "vendor_code",
      "note",
    ],
  },

  computed: {
    nameErrors() {
      const errors = [];
      if (!this.$v.name.$dirty) return errors;
      !this.$v.name.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.name.minLength && errors.push(this.$formatStr(this.$t("This_field_must_have_at_least_X_characters"), 3));
      !this.$v.name.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 60));
      return errors;
    },
    cnpjError() { 
      const errors = [];
      if (!this.$v.cnpj.$dirty) return errors;
      !this.$v.cnpj.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.cnpj.cnpjFieldValidator && errors.push(this.$t("cnpjValidationError"));
      return errors;
    },
    vendorCodeErrors() {
      const errors = [];
      if (!this.$v.vendor_code.$dirty) return errors;
      !this.$v.vendor_code.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 9));
      return errors;
    },
    noteErrors() {
      const errors = [];
      if (!this.$v.note.$dirty) return errors;
      !this.$v.note.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 800));
      return errors;
    },
  },

  methods: {
    handleClick(index){
      //this.menu_items[id].click()  #will get errors because the function click will not access properties with its own 'this'
      this.menu_items[index].click.call(this) // will call the function but the function will use the vue instance 'this' context.
    },

    async fetchEstablishmentsToCreateClient(){
      // Check if establishment_group already exists. If it exist use it, otherwise, fetch establishments and add them to the establishment_group
      let establishment_group = this.establishment_groups.find(el=>el.group_id==this.client.client_table)
      if (establishment_group){
        var establishments = establishment_group.establishments
      }else{
        var establishments = await this.$store.dispatch("organization/fetchEstablishmentsToCreateClient", this.client.client_table);
        if (establishments){
          this.establishment_groups.push({group_id: this.client.client_table, establishments: [...establishments]})
        }
      }
      if (establishments){
        for (const establishment_index in establishments){
          let establishment = establishments[establishment_index]
          // This will be necessary for update clie_estab.price_table(added from a checkbox) from a v-select.
          // The client_establishments objects from this.client_establishments must be same objects as the AUX variables
          let cli_estab = this.client.client_establishments.find(el=>el.establishment == establishment.establishment_compound_id)
          if (cli_estab){
            establishment['AUX_cli_estab_' + this.client.client_compound_id] = cli_estab
            this.client_establishments.push(cli_estab)
            // If cli_estab exists for this client, fetch price_tables for this estab.company 
            let price_table_already_fetched = this.price_table_groups.find(el=>el.group_id === establishment.company)
            if (!price_table_already_fetched){
              let price_tables = await this.$store.dispatch("organization/fetchPriceTablesToCreateClient", establishment.company);
              if (price_tables){
                this.updatePriceTableGroups({group_id: establishment.company, price_tables: [{price_table_compound_id: null, 
                  description: 'default_null_value', table_code: 'default_null_value'}, ...price_tables]}) 
              }
            }
          }
          else{
            establishment['AUX_cli_estab_' + this.client.client_compound_id] = {establishment: establishment.establishment_compound_id,
              price_table: null}
          }
        }
        this.establishments.push(...establishments)
      }
    },

    async updateClient(){
      this.$v.clientInfoGroup.$touch();
      if (this.$v.clientInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
      } else {
          this.loading = true;
          let data = await this.$store.dispatch("organization/updateClient", {
            client_compound_id: this.client.client_compound_id,
            name: this.name,
            cnpj: this.cnpj,
            status: this.status,
            client_establishments: this.client_establishments,
            vendor_code: this.vendor_code,
            note: this.note,
          })
          this.loading = false;
          // Reactivity for Client list inside Client.vue 
          if (data){
            this.client.name = data.name
            this.client.cnpj = data.cnpj
            this.client.status = data.status
            this.client.client_establishments = data.client_establishments
            this.client.vendor_code = data.vendor_code
            this.client.note = data.note
              // Close dialog
            this.show_edit_dialog = false
          }
      }
    },
    updatePriceTable(estab, value){
      /** console.log(">>>>>>> VALUE:", value) */
      let cli_estab = this.client_establishments.find(el => el.establishment === estab.establishment_compound_id)
      cli_estab.price_table = value.price_table_compound_id
    },

    updatePriceTableGroups(payload){
      this.price_table_groups.push(payload)
    },

    async deleteClient(){
      let data = await this.$store.dispatch(
        'organization/deleteClient', 
        {client_compound_id: this.client.client_compound_id}
      )
      if (data === "ok"){
        this.$emit('client-deleted')
      }

    },

    hasUpdateClientPermission(){
      let user = this.$store.state.user.currentUser;
      return user.permissions.includes("update_client")
    },
    hasDeleteClientPermission(){
      let user = this.$store.state.user.currentUser;
      return user.permissions.includes("delete_client")
    },

  },

  watch: {
    show_edit_dialog(newValue, oldValue){
      if (newValue === true) {
        if (this.establishments.length == 0){
          this.fetchEstablishmentsToCreateClient()
        }
      }
    }	
  },

  mounted() {
    this.name = this.client.name
    this.cnpj = this.client.cnpj
    this.status = String(this.client.status)
    this.vendor_code = this.client.vendor_code
    this.note = this.client.note
    // Default client_table_from_client
    let cli_tab = this.client_tables.find(el=>el.client_table_compound_id === this.client.client_table)
    this.client_table_from_client = cli_tab
  }
}
</script>
