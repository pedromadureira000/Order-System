<template>
  <div>
    <dots-menu-update-delete :menu_items="menu_items" :handleClick="handleClick"/>

    <v-dialog v-model="show_edit_dialog" max-width="500px">
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
            <!-- CNPJ -->
            <v-text-field
              label="CNPJ"
              v-model="cnpj"
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
            <v-text-field
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
        <v-card-actions>
          <v-spacer />
          <v-btn class="blue--text darken-1" text @click="show_edit_dialog = false">{{$t('Cancel')}}</v-btn>
          <v-btn class="blue--text darken-1" text @click="updateCompany()">{{$t('Save')}}</v-btn>
        </v-card-actions>
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
export default {
  mixins: [validationMixin],
  components: {
    "dots-menu-update-delete": require("@/components/dots-menu-update-delete.vue").default,
  },
  props: ['client'],
  data() {
    return {
      show_edit_dialog: false,
      client_establishments: [],
          /** establishments: [], */
              /** price_tables: [], */
      name: null,
      cnpj: null,
      status: null,
      vendor_code: null,
      note: null,
      loading: false,
      enabled: false,
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
            let data = await this.$store.dispatch(
              'organization/deleteCompany', 
              {company_compound_id: this.company.company_compound_id}
            )
            if (data === "ok"){
              this.$emit('company-deleted')
            }
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
        //this.menu_items[id].click()  #will get erros, because of function click will no can access propertie with it's own 'this'
        this.menu_items[index].click.call(this) // will call the function but the function will use the vue instance 'this' context.
      },
      async updateCompany(){
        try {
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
          this.company.name = data.name
          this.company.cnpj_root = data.cnpj_root
          this.company.client_table = data.client_table
          this.company.item_table = data.item_table
          this.company.status = data.status
          this.company.note = data.note
        } catch(e){
        // error is being handled inside action
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
