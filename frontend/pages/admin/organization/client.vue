<template>
  <p v-if="$fetchState.pending">{{$t('Fetching_data')}}</p>
  <p v-else-if="$fetchState.error">{{$t('Error_fetching_data')}}</p>
  <div v-else>
    <div class="ma-3">
      <v-expansion-panels v-if="hasCreateClientPermission()">
        <v-expansion-panel>
          <v-expansion-panel-header>
            <h3>{{$t('Create_Client')}}</h3>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <form @submit.prevent="createClient" class="ml-3">
              <!-- Client Table -->
              <v-row align="center">
                <v-col
                  class="d-flex"
                  cols="12"
                  sm="6"
                >
                  <v-select
                    v-model="client_table"
                    :label="$t('Client_Table')"
                    :items="client_tables"
                    :item-text="(x) => x.client_table_code"
                    :item-value="(x) => x.client_table_compound_id"
                    @change="fetchEstablishmentsToCreateClient"
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
              <!-- Client Code -->
              <v-text-field
                :label="$t('Client_code')"
                v-model="client_code"
                :error-messages="clientCodeErrors"
                required
                @blur="$v.client_code.$touch()"
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
              <!-- Note -->
              <v-textarea
                outlined
                :label="$t('Note')"
                v-model="note"
                :error-messages="noteErrors"
                @blur="$v.note.$touch()"
                class="mb-3"
              />
              <!-- Client Establishments -->
              <v-expansion-panels class="mb-5">
                <v-expansion-panel @change="fetchEstablishmentsToCreateClient">
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
                              :value='establishment.AUX_cli_estab'
                              hide-details
                              class="shrink mr-2 mt-0"
                            ></v-checkbox>
                          </v-col>
                          <v-col>
                            <price-table-v-select 
                              :client_establishments='client_establishments' 
                              :establishment='establishment' 
                              :price_table_groups='price_table_groups'
                              :aux_cli_estab="establishment['AUX_cli_estab']"
                              @update-price-table='updatePriceTable'
                              @update-price-table-groups='updatePriceTableGroups'
                            />
                          </v-col>
                        </v-row>
                      </v-container>
                    </v-expansion-panel-content>
                </v-expansion-panel>
              </v-expansion-panels>
              <v-btn
                color="primary"
                type="submit"
                :loading="loading"
                :disabled="loading"
                >{{$t('Submit')}}</v-btn
              >
            </form>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>

      <div v-if="hasGetClientPermission()">
        <h3 class="mt-6">{{$t('Edit_Client')}}</h3>
        <v-data-table
          :headers="headers"
          :items="clients"
          :items-per-page="10"
          item-key="client_compound_id"
          class="elevation-1 mt-3"
        >
          <!-- <template v-slot:item.actions="{ item }"> -->
          <template v-slot:[`item.actions`]="{ item }">
            <client-edit-menu 
              :client="item" 
              :client_tables="client_tables"
              :establishment_groups="establishment_groups" 
              :price_table_groups="price_table_groups" 
              @client-deleted="deleteClient(item)" 
            />
          </template>
          <template v-slot:item.cnpj_with_mask="{ item }">
            <input type="text" v-mask="'##.###.###/####-##'" :value="item.cnpj" disabled style="color: #000000DE; width: 130px"/>
          </template>
          <template v-slot:item.client_table="{ item }">
            <p>{{item.client_table.split("&")[1]}}</p>
          </template>
          <template v-slot:item.status="{ item }">
            <p>{{item.status === 1 ? $t('Active') : $t('Disabled')}}</p>
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
  minLength,
  maxLength,
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
import {slugFieldValidator, cnpjFieldValidator } from "~/helpers/validators"
import {mask} from 'vue-the-mask'

export default {
  components: {
    "client-edit-menu": require("@/components/admin/organization/client-edit-menu.vue").default,
    "price-table-v-select": require("@/components/admin/organization/price-table-v-select.vue").default,
  },
  middleware: ["authenticated"],
  mixins: [validationMixin],
  directives: {mask},
  data() {
    return {
      client_table: null,
      client_tables: [],
      establishments: [],
      clients: [],
      client_establishments: [],
      price_table_groups: [],
      client_code: null,
      name: null,
      cnpj: null,
      status: "1",
      vendor_code: "",
      note: "",
      establishment_groups: [],
      loading: false,
      headers: [
        { text: this.$t('Client_code'), value: 'client_code' },
        { text: this.$t('Name'), value: 'name' },
        { text: 'CNPJ', value: 'cnpj_with_mask' },
        { text: this.$t('Vendor_Code'), value: 'vendor_code' },
        { text: this.$t('Client_Table'), value: 'client_table' },
        { text: 'Status', value: 'status' },
        { text: this.$t('Note'), value: 'note' },
        { text: this.$t('Actions'), value: 'actions' },
      ]
    };
  },

  async fetch() {
    // Fetch Clients to EDIT list
    let clients = await this.$store.dispatch("organization/fetchClients");
    if (clients) {this.clients.push(...clients)}
    // Fetch client table options
    let client_tables = await this.$store.dispatch("organization/fetchClientTablesToCreateClient");
    if (client_tables) {
      this.client_tables.push(...client_tables)
      if (this.client_tables.length > 0){
        this.client_table = this.client_tables[0].client_table_compound_id
      }
    }
  },

  validations: {
    name: { 
      required, 
      minLength: minLength(3),
      maxLength: maxLength(60)
    },
    client_code: {
      required, 
      slugFieldValidator, 
      maxLength: maxLength(9)
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
      "client_code",
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
    clientCodeErrors() {
      const errors = [];
      if (!this.$v.client_code.$dirty) return errors;
      !this.$v.client_code.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.client_code.slugFieldValidator && errors.push(this.$t('SlugFieldErrorMessage'));
      !this.$v.client_code.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 9));
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
    async createClient() {
      this.$v.clientInfoGroup.$touch();
      if (this.$v.clientInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t('Please_fill_the_form_correctly'), alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let data = await this.$store.dispatch("organization/createClient", {
          client_table: this.client_table,
          client_establishments: this.client_establishments,
          client_code: this.client_code,
          name: this.name, 
          cnpj: this.cnpj,
          vendor_code: this.vendor_code,
          status: this.status,
          note: this.note
        });
        if (data) {
          this.clients.push(data);
          // Clearing fields
          this.$v.$reset()
          // this avoid "This field is required" errors by vuelidate
          this.client_table = this.client_tables[0].client_table_compound_id
          this.client_establishments = []
          this.client_code = ""
          this.name = ""
          this.cnpj = ""
          this.vendor_code = ""
          this.status = "1"
          this.note = ""
        }
        this.loading = false;
      }
    },
    deleteClient(clientToDelete) {
      /** console.log(">>>>>>> clientToDelete", clientToDelete) */
      this.clients = this.clients.filter((client) => client.client_compound_id != clientToDelete.client_compound_id);
    },

    async fetchEstablishmentsToCreateClient(){
      let establishment_group = this.establishment_groups.find(el=>el.group_id==this.client_table)
      if (establishment_group){
        this.establishments = establishment_group.establishments
      }
      else{
        let establishments = await this.$store.dispatch("organization/fetchEstablishmentsToCreateClient", this.client_table)
        if (establishments) {
          for (const establishment_index in establishments){
            let establishment = establishments[establishment_index]
            // This will be necessary for update clie_estab.price_table(added from a checkbox) from a v-select.
            establishment.AUX_cli_estab = {establishment: establishment.establishment_compound_id, price_table: null}
            this.establishments.push(establishment)
          }
          this.establishment_groups = [{group_id: this.client_table, establishments: [...establishments]}]
        }
      }
    },

    updatePriceTable(estab, value){
      let cli_estab = this.client_establishments.find(el => el.establishment === estab.establishment_compound_id)
      cli_estab.price_table = value.price_table_compound_id
    },

    updatePriceTableGroups(payload){
      this.price_table_groups.push(payload)
    },
    hasCreateClientPermission(){
      let user = this.$store.state.user.currentUser;
      return user.permissions.includes("create_client")
    },
    hasGetClientPermission(){
      let user = this.$store.state.user.currentUser;
      return user.permissions.includes("get_clients")
    },
  },

  /** mounted() { */
    /** console.log('>>>>>>>>>>>>>>>>>>estabs', this.establishments) */
  /** } */

};
</script>
<style scoped>
.v-application .mb-3 {
  margin-bottom: 0px !important;
}
</style>
