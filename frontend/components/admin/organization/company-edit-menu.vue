<template>
  <div>
    <dots-menu-update-delete :menu_items="menu_items" :handleClick="handleClick"/>

    <v-dialog v-model="show_edit_dialog" max-width="500px">
      <v-card>
        <v-card-title>Edit</v-card-title>
        <v-card-text>
          <v-container fluid>
            <!-- Name -->
              <v-text-field
                label="Name"
                v-model="name"
                :error-messages="nameErrors"
                required
                @blur="$v.name.$touch()"
                class="mb-3"
              />
            <!-- Root of CNPJ -->
              <v-text-field
                label="Root of CNPJ"
                v-model="cnpj_root"
                required
                :error-messages="cnpjRootErrors"
                @blur="$v.cnpj_root.$touch()"
                class="mb-3"
              />
            <!-- Client table -->
            <v-radio-group v-model="client_table" style="width: 25%;" label="Client table" class="mb-3">
              <v-radio
                v-for="(client_table, key) in client_tables"
                :key="key"
                :label="client_table.description"
                :value="client_table.client_table_compound_id"
              ></v-radio>
              <v-radio
                label="None"
                value=""
              ></v-radio>
            </v-radio-group>
            <!-- Item table -->
            <v-radio-group v-model="item_table" style="width: 25%;" label="Item table" class="mb-3">
              <v-radio
                v-for="(item_table, key) in item_tables"
                :key="key"
                :label="item_table.description"
                :value="item_table.item_table_compound_id"
              ></v-radio>
              <v-radio
                label="None"
                value=""
              ></v-radio>
            </v-radio-group>
            <!-- Company Status -->
            <v-radio-group v-model="status" style="width: 25%;" label="Company Company Status" class="mb-3">
              <v-radio
                label="Active"
                value=1
              ></v-radio>
              <v-radio
                label="Disabled"
                value=0
              ></v-radio>
            </v-radio-group>
            <!-- Note -->
              <v-text-field
                label="Note"
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
          <v-btn class="blue--text darken-1" text @click="show_edit_dialog = false">Cancel</v-btn>
          <v-btn class="blue--text darken-1" text @click="updateCompany()">Save</v-btn>
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
  props: ['company', 'client_tables', 'item_tables'],
  data: () => ({
    show_edit_dialog: false,
    name: null,
    cnpj_root: null,
    client_table: null,
    item_table: null,
    status: null,
    note: null,
    loading: false,
    menu_items: [
      { 
        title: 'Edit',
        icon: 'mdi-pencil',
        async click(){
          this.show_edit_dialog = true
        }
      },
      { 
        title: 'Delete',
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
  }),

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
      !this.$v.name.required && errors.push("Name is required.");
      !this.$v.name.minLength && errors.push("This field must have at least 3 characters.");
      !this.$v.name.maxLength && errors.push("This field must have up to 60 characters.");
      return errors;
    },
    cnpjRootErrors() { 
      const errors = [];
      if (!this.$v.cnpj_root.$dirty) return errors;
      !this.$v.cnpj_root.required && errors.push("Root of CNPJ is required.");
      !this.$v.cnpj_root.raizcnpjFieldValidator && errors.push("This field must be in the format '99.999.999'");
      return errors;
    },
    noteErrors() {
      const errors = [];
      if (!this.$v.note.$dirty) return errors;
      !this.$v.note.maxLength && errors.push("This field must have up to 800 characters.");
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
