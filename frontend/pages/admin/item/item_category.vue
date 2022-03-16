<template>
  <div class="ma-3">
    <h3>Create Item Category</h3>
    <form @submit.prevent="createCategory">
      <div class="mb-3">
        <v-text-field
          label="Name"
          v-model="name"
          required
        />
      </div>
      <div class="mb-3">
        <v-text-field
          label="Category code"
          v-model="category_code"
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

    <h3 class="mt-6">Edit Item Category</h3>
    <v-data-table
      :headers="headers"
      :items="categories"
      :items-per-page="10"
      item-key="category_compound_id"
      class="elevation-1"
    >
      <template v-slot:item.actions="{ item }">
        <!-- <user-edit-menu :user="item" @user-deleted="deleteUser(item)" /> -->
      </template>
    </v-data-table>
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
  middleware: ["authenticated"],
  components: {
    /** "user-edit-menu": require("@/components/admin/item/user-edit-menu.vue").default, */
  },
  /** mixins: [validationMixin], */

  data() {
    return {
      name: null,
      category_code: null,
      description: null,
      categories: [],
      loading: false,
      headers: [
        { text: 'Name', value: 'name' },
        { text: 'Category code', value: 'category_code' },
        { text: 'Description', value: 'description' },
        { text: 'Actions', value: 'actions' },
      ]
    };
  },

  async fetch() {
    let categories = await this.$store.dispatch("item/fetchCategories");
    for (const item_index in categories){
      let category = categories[item_index]
      this.categories.push(category)
    }
    this.categories = await this.$store.dispatch("item/fetchCategories"); 
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
    async createCategory() {
      /** this.$v.companyInfoGroup.$touch(); */
      /** if (this.$v.companyInfoGroup.$invalid) { */
        /** this.$store.dispatch("setAlert", { message: "Please fill the form correctly.", alertType: "error" }, { root: true }) */
      /** } else { */
        this.loading = true;
        let data = await this.$store.dispatch("item/createCategory", {
          name: this.name, 
          category_code: this.category_code,
          description: this.description,
        });
        if (data) {
          this.categories.push(data);
        }
        this.loading = false;
      /** } */
    },
    deleteItem(categoryToDelete) {
      this.categories = this.categories.filter((category) => category.category_code != categoryToDelete.category_code);
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
