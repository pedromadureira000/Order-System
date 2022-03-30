<template>
  <div>
    <dots-menu-update-delete :menu_items="menu_items" :handleClick="handleClick"/>

    <v-dialog v-model="show_edit_dialog" max-width="50%">
      <v-card>
        <v-card-title>{{$t('Edit')}}</v-card-title>
        <v-card-text>
          <v-container fluid>
            <!-- Name -->
            <v-text-field
              :label="$t('Name')"
              v-model="name"
              :error-messages="nameErrors"
              required
              @blur="$v.name.$touch()"
              class="mb-3"
            />
            <!-- Root of CNPJ -->
            <v-text-field
              :label="$t('Root_of_CNPJ')"
              v-model="cnpj_root"
              v-mask="'##.###.###'"
              required
              :error-messages="cnpjRootErrors"
              @blur="$v.cnpj_root.$touch()"
              class="mb-3"
            />
            <!-- Client table -->
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
                    :item-text="(x) => x.client_table_compound_id === null ? $t('Empty') : x.client_table_code + ' - ' + x.description"
                    :item-value="(x) => x.client_table_compound_id"
                  ></v-select>
                </v-col>
              </v-row>
            <!-- Item table -->
              <v-row align="center">
                <v-col
                  class="d-flex"
                  cols="12"
                  sm="6"
                >
                  <v-select
                    v-model="item_table"
                    :label="$t('Item_Table')"
                    :items="item_tables"
                    :item-text="(x) => x.item_table_compound_id === null ? $t('Empty') : x.item_table_code + ' - ' + x.description"
                    :item-value="(x) => x.item_table_compound_id"
                  ></v-select>
                </v-col>
              </v-row>
            <!-- Company Status -->
            <v-radio-group v-model="status" style="width: 25%;" :label="$t('Company_Status')" class="mb-3">
              <v-radio
                :label="$t('Active')"
                value=1
              ></v-radio>
              <v-radio
                :label="$t('Disabled')"
                value=0
              ></v-radio>
            </v-radio-group>
            <!-- Note -->
            <v-textarea
              outlined
              v-model="note"
              :label="$t('Note')"
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
            @click="updateCompany()"
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
            <v-btn class="red--text darken-1" text @click="deleteCompany()">{{$t('Delete')}}</v-btn>
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
import {raizcnpjFieldValidator} from "~/helpers/validators"
import {mask} from 'vue-the-mask'
export default {
  mixins: [validationMixin],
  components: {
    "dots-menu-update-delete": require("@/components/dots-menu-update-delete.vue").default,
  },
  props: ['company', 'client_tables', 'item_tables'],
  directives: {mask},
  data() {
    return {
      show_edit_dialog: false,
      show_delete_confirmation_dialog: false,
      name: null,
      cnpj_root: null,
      client_table: null,
      item_table: null,
      status: null,
      note: null,
      loading: false,
      menu_items: [
        { 
          title: this.$t('Edit'),
          icon: 'mdi-pencil',
          async click(){
            this.show_edit_dialog = true
          }
        },
        { 
          title: this.$t('Delete'),
          icon: 'mdi-delete',
          async click(){
            this.show_delete_confirmation_dialog = true
          }
        },
      ]
    }
  },

  validations: {
    name: { 
      required, 
      minLength: minLength(3),
      maxLength: maxLength(60)
    },
    cnpj_root: {
      required, 
      raizcnpjFieldValidator,
    },
    note: {
      maxLength: maxLength(800)
    },
    companyInfoGroup: [
      "name",
      "cnpj_root",
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
    cnpjRootErrors() { 
      const errors = [];
      if (!this.$v.cnpj_root.$dirty) return errors;
      !this.$v.cnpj_root.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.cnpj_root.raizcnpjFieldValidator && errors.push(this.$t("cnpjRootValidationError"));
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
      async updateCompany(){
        this.$v.companyInfoGroup.$touch();
        if (this.$v.companyInfoGroup.$invalid) {
          this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
        } else {
          this.loading = true;
          let data = await this.$store.dispatch("organization/updateCompany", {
            company_compound_id: this.company.company_compound_id,
            name: this.name,
            cnpj_root: this.cnpj_root,
            client_table: this.client_table,
            item_table: this.item_table,
            status: this.status,
            note: this.note,
          })
          // Reactivity for Company list inside Company.vue 
          this.loading = false;
          if (data) {
            this.company.name = data.name
            this.company.cnpj_root = data.cnpj_root
            this.company.client_table = data.client_table
            this.company.item_table = data.item_table
            this.company.status = data.status
            this.company.note = data.note
            // Close dialog
            this.show_edit_dialog = false
          }
        }
      },
      async deleteCompany(){
        let data = await this.$store.dispatch(
          'organization/deleteCompany', 
          {company_compound_id: this.company.company_compound_id}
        )
        if (data === "ok"){
          this.$emit('company-deleted')
        }
      }
  },

  mounted() {
    this.name = this.company.name
    this.cnpj_root = this.company.cnpj_root
    this.client_table = this.company.client_table
    this.item_table = this.company.item_table
    this.status = String(this.company.status)
    this.note = this.company.note
  }
}
</script>
