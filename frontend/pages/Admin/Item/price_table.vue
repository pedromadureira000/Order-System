<template>
  <p v-if="$fetchState.pending">Fetching mountains...</p>
  <p v-else-if="$fetchState.error">An error occurred :(</p>
  <div v-else>
    <div class="ma-3">
      <h3>Create Price Table</h3>
      <form @submit.prevent="createPriceTable">
        <div class="mb-3">
          <v-text-field
            label="Name"
            v-model="verbose_name"
            required
          />
        </div>
        <div class="mb-3">
          <v-text-field
            label="Table code"
            v-model="table_code"
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
        <v-btn
          color="primary"
          type="submit"
          :loading="loading"
          :disabled="loading"
          >Submit</v-btn
        >
      </form>

      <h3 class="mt-6">Edit Price Table</h3>
      <v-data-table
        :headers="headers"
        :items="pricetables"
        :items-per-page="10"
        class="elevation-1"
      >
        <template v-slot:item.actions="{ item }">
          <pricetable-edit-menu :pricetable="item" :items="items" @pricetable-deleted="deletePriceTable(item)" />
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
    "pricetable-edit-menu": require("@/components/admin/pricetable-edit-menu.vue").default,
  },
  /** mixins: [validationMixin], */

  data() {
    return {
      verbose_name: null,
      table_code: null,
      description: null,
      price_items: [],
      pricetables: [],
      items: [],
      loading: false,
      headers: [
        { text: 'Name', value: 'verbose_name' },
        { text: 'Table code', value: 'table_code' },
        { text: 'Description', value: 'description' },
        { text: 'Actions', value: 'actions' },
      ]
    };
  },

  async fetch() {
    let pricetables = await this.$store.dispatch("orders/fetchPriceTables");
    for (const item_index in pricetables){
      let pricetable = pricetables[item_index]
      this.pricetables.push(pricetable)
    }
    console.log(this.pricetables)
    let items = await this.$store.dispatch("orders/fetchItems");
    items.forEach((item)=> item["price_unit"] = null)  //Gambiarra: i don't fugure out a way to receve input value without use v-model
    this.items =  items
/** items[key]['price_unit'] */
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
    async createPriceTable() {
      /** this.$v.companyInfoGroup.$touch(); */
      /** if (this.$v.companyInfoGroup.$invalid) { */
        /** this.$store.dispatch("setAlert", { message: "Please fill the form correctly.", alertType: "error" }, { root: true }) */
      /** } else { */
        this.loading = true;
        let data = await this.$store.dispatch("orders/createPriceTable", {
          verbose_name: this.verbose_name, 
          table_code: this.table_code,
          description: this.description,
          price_items: this.price_items
        });
        if (data) {
          this.pricetables.push(data);
        }
        this.loading = false;
      /** } */
    },
    deletePriceTable(priceTableToDelete) {
      this.pricetables = this.pricetables.filter((pricetable) => pricetable.table_code != priceTableToDelete.table_code);
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
