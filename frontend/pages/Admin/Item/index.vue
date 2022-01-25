<template>
  <p v-if="$fetchState.pending">Fetching mountains...</p>
  <p v-else-if="$fetchState.error">An error occurred :(</p>
  <div v-else>
    <div class="ma-3">
      <h3>Create Item</h3>
      <form @submit.prevent="createItem">
        <div class="mb-3">
          <v-text-field
            label="Name"
            v-model="name"
            required
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="Item code"
            v-model="item_code"
            required
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="Description"
            v-model="description"
            required
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="Unit"
            v-model="unit"
            required
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="Barcode"
            v-model="barcode"
            required
          />
        </div>
        <div class="mb-3">
          <h5>Item Category</h5>
          <v-radio-group v-model="category" style="width: 25%;">
            <v-radio
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            ></v-radio>
          </v-radio-group>
        </div>
        <div class="mb-3">
          <v-checkbox 
            v-model="active"
            label="Active"
          ></v-checkbox>
        </div>
        <div class="mb-3">
          image_
        </div>
        <v-btn
          color="primary"
          type="submit"
          :loading="loading"
          :disabled="loading"
          >Submit</v-btn
        >
      </form>

      <h3 class="mt-6">Edit Item</h3>
      <v-data-table
        :headers="headers"
        :items="items"
        :items-per-page="10"
        class="elevation-1"
      >
        <template v-slot:item.actions="{ item }">
          <!-- <user-edit-menu :user="item" @user-deleted="deleteUser(item)" /> -->
        </template>
      </v-data-table>
    </div>
  </div>
</template>

<script>
/** import { */
  /** required, */
  /** maxLength, */
  /** alphaNum, */
  /** integer */
/** } from "vuelidate/lib/validators"; */
/** import { validationMixin } from "vuelidate"; */

export default {
  middleware: ["authenticated", "admin"],
  components: {
    "user-edit-menu": require("@/components/admin/user-edit-menu.vue").default,
  },
  /** mixins: [validationMixin], */

  data() {
    return {
      name: null,
      item_code: null,
      description: null,
      category: "default",
      categories: [],
      unit: null,
      barcode: null,
      active: true,
      image: null,
      loading: false,
      items: [],
      headers: [
        { text: 'Image', value: 'image' },
        { text: 'Name', value: 'name' },
        { text: 'Item code', value: 'item_code' },
        { text: 'Description', value: 'description' },
        { text: 'Category', value: 'category' },
        { text: 'Unit', value: 'unit' },
        { text: 'Barcode', value: 'barcode' },
        { text: 'Active', value: 'active' },
        { text: 'Actions', value: 'actions' },
      ]
    };
  },

  async fetch() {
    let items = await this.$store.dispatch("orders/fetchItems");
    /** for (const item_index in items){ */
      /** let item = items[item_index] */
      /** this.items.push({name: item.name, item_code: item.item_code, description: item.description, */
        /** category: item.category, unit: item.unit, barcode: item.barcode, active: item.active, image: item.image}) */
    /** } */
    for (const item_index in items){
      let item = items[item_index]
      this.items.push(item)
    }
    this.categories = await this.$store.dispatch("orders/fetchCategories"); 
    console.log(this.categories)
  },

  /** validations: { */
    /** name: {  */
      /** required,  */
      /** alphaNum,  */
      /** maxLength: maxLength(12) */
    /** }, */
    /** company_code: { */
      /** required,  */
      /** integer */
    /** }, */
    /** companyInfoGroup: [ */
      /** "name", */
      /** "company_code", */
    /** ], */
  /** }, */

  methods: {
    async createItem() {
      /** this.$v.companyInfoGroup.$touch(); */
      /** if (this.$v.companyInfoGroup.$invalid) { */
        /** this.$store.dispatch("setAlert", { message: "Please fill the form correctly.", alertType: "error" }, { root: true }) */
      /** } else { */
        this.loading = true;
        let data = await this.$store.dispatch("orders/createItem", {
          name: this.name, 
          item_code: this.item_code,
          description: this.description,
          category: this.category, 
          unit: this.unit, 
          barcode: this.barcode, 
          active: this.active,
          image: this.image
        });
        if (data) {
          this.items.push(data);
        }
        this.loading = false;
      /** } */
    },
    deleteItem(itemToDelete) {
      this.items = this.items.filter((item) => item.item_code != itemToDelete.item_code);
    },
  },

  /** computed: { */
    /** nameErrors() { */
      /** const errors = []; */
      /** if (!this.$v.name.$dirty) return errors; */
      /** !this.$v.name.alphaNum && errors.push("Must have only alphanumeric characters."); */
      /** !this.$v.name.required && errors.push("Name is required"); */
      /** !this.$v.name.maxLength && errors.push("This field must have up to 12 characters."); */
      /** return errors; */
    /** }, */
    /** companyCodeErrors() { */
      /** const errors = []; */
      /** if (!this.$v.company_code.$dirty) return errors; */
      /** !this.$v.company_code.integer && errors.push("Must be a integer"); */
      /** !this.$v.company_code.required && errors.push("Company code required"); */
      /** return errors; */
    /** }, */
    /** cpfErrors() {  */
      /** const errors = []; */
      /** if (!this.$v.cpf.$dirty) return errors; */
      /** !this.$v.cpf.required && errors.push("CPF is required."); */
      /** !this.$v.cpf.maxLength && errors.push("This field must have up to 14 characters."); */
      /** return errors; */
    /** }, */
  /** }, */
};
</script>
<style scoped>
.v-application .mb-3 {
  margin-bottom: 0px !important;
}
</style>
