<template>
  <p v-if="$fetchState.pending">{{$t('Fetching_data')}}</p>
  <p v-else-if="$fetchState.error">{{$t('Error_fetching_data')}}</p>
  <div v-else>
    <div class="ma-3">
      <v-expansion-panels v-if="hasCreateItemPermission()">
        <v-expansion-panel>
          <v-expansion-panel-header>
            <h3>{{$t('Create Item')}}</h3>
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <form @submit.prevent="createItem">
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
                    return-object
                    @change="fetchCategoriesToCreateItem"
                  ></v-select>
                </v-col>
              </v-row>
              <!-- Category -->
              <v-row align="center">
                <v-col
                  class="d-flex"
                  cols="12"
                  sm="6"
                >
                  <v-select
                    v-model="category"
                    :label="$t('Category')"
                    :items="categories"
                    :item-text="(x) => x.category_compound_id === null ? $t('All') : x.category_code + ' - ' + x.description"
                    :item-value="(x) => x.category_compound_id"
                    :error-messages="categoryErrors"
                  ></v-select>
                </v-col>
              </v-row>

              <!-- Item code -->
              <v-text-field
                :label="$t('Item code')"
                v-model.trim="item_code"
                :error-messages="itemCodeErrors"
                required
                @blur="$v.item_code.$touch()"
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
              <!-- Unit -->
              <v-text-field
                :label="$t('Unit')"
                v-model.trim="unit"
                :error-messages="unitErrors"
                @blur="$v.unit.$touch()"
                required
                class="mb-3"
              />
              <!-- Barcode -->
              <v-text-field
                :label="$t('Barcode')"
                v-model.trim="barcode"
                :error-messages="barcodeErrors"
                @blur="$v.barcode.$touch()"
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
              <!-- Image -->
              <v-row>
                <v-col>
                  <v-file-input
                    show-size
                    accept="image/*"
                    :label="$t('Image')"
                    prepend-icon="mdi-camera"
                    @change="onChange"
                  ></v-file-input>
                </v-col>
                <v-col>
                  <v-img
                    v-if="img_url"
                    contain
                    width="115px"
                    height="87px"
                    :src="img_url"
                  ></v-img>
                </v-col>
              </v-row>
              <!-- Technical Description -->
              <v-textarea
                outlined
                :label="$t('Technical description')"
                v-model.trim="technical_description"
                :error-messages="technicalDescriptionErrors"
                @blur="$v.technical_description.$touch()"
                class="mb-3"
              />
              <!-- Submit -->
              <v-btn
                color="primary"
                type="submit"
                :loading="loading"
                :disabled="loading"
              >{{$t('Submit')}}</v-btn>
            </form>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>

      <h3 class="mt-6 mb-7">{{$t('Edit Item')}}</h3>
      <search-items
        ref="search_items"
        v-if="hasGetItemsPermission()"
        :category_group="category_group"
        :companies="companies"
        :itsForAdminItemPage="true"
        :itsForPriceItems="false"
      />
    </div>
  </div>
</template>

<script>
// XXX I tried to use the 'not' builtin-validator from Vuelidate but it doesn't worked
const notSame = (compareTo) => {
	return (val, vm) => val != vm[compareTo]
}
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
    "seach-items": require("@/components/search-items.vue").default,
  },
  mixins: [validationMixin],

  data() {
    return {
      company: null,
      companies: [],
      category: null,
      item_code: null,
      description: null,
      technical_description: "",
      unit: null,
      barcode: "",
      status: "1",
      image: null,
      categories: [],
      category_group: [],
      img_url: '',
      loading: false,
    };
  },

  async fetch() {
    // Fetch Companies
    let companies = await this.$store.dispatch("item/fetchCompaniesToCreatePriceTable"); 
    if (companies){
      this.companies.push(...companies)
      if (this.companies.length > 0){
        this.company = this.companies[0]
        await this.fetchCategoriesToCreateItem()
      }
    }
  },

  methods: {
    async createItem(){
      this.$v.itemInfoGroup.$touch();
      if (this.$v.itemInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t('Please_fill_the_form_correctly'), alertType: "error" }, { root: true })
      } 
      else {
        this.loading = true;
        const formData = new FormData()
        formData.append('item_table', this.company.item_table)
        formData.append('item_code', this.item_code)
        formData.append('category', this.category)
        formData.append('description', this.description)
        formData.append('unit', this.unit)
        formData.append('barcode', this.barcode)
        formData.append('status', this.status)
        formData.append('technical_description', this.technical_description)
        if (this.image){
          formData.append('image', this.image, this.image.name)
        }
        let data = await this.$store.dispatch("item/createItem", formData);
        if (data) {
          // Clearing fields
          this.$v.$reset()
          // this avoid "This field is required" errors by vuelidate
          this.company = this.companies[0]
          this.item_code = ""
          this.description = ""
          this.unit = ""
          this.barcode = ""
          this.status = "1"
          this.technical_description = ""
          this.image = null
          this.img_url = ''
        }
        this.loading = false;
      }
    },

    async fetchCategoriesToCreateItem(){
      let category_already_exists = this.category_group.find(el=>el.item_table == this.company.item_table)
      if (category_already_exists){
        this.categories = category_already_exists.categories
      }
      else{
        let categories = await this.$store.dispatch("item/fetchCategoriesToCreateItem", this.company.item_table); 
        if (categories){
          this.category_group.push({item_table: this.company.item_table, categories: categories} )
          this.categories = categories
        }
      }
    },

    // Image
    onChange (event) {
      /** console.log(">>>>>>> ", event) */
      this.image = event
      if (event === null){
        this.img_url = ''
      } else{
        this.img_url = URL.createObjectURL(this.image)
        /** console.log(">>>>>>> URL image: ", this.img_url) */
      }
    },

    // Permissions 
    hasCreateItemPermission(){
      let user = this.$store.state.user.currentUser;
      return user.permissions.includes("create_item")
    },
    hasGetItemsPermission(){
      let user = this.$store.state.user.currentUser;
      return user.permissions.includes("get_items")
    },
  },

  validations: {
    category: {
      isDifferent: notSame(null)
    },
    description: { 
      required, 
      minLength: minLength(3),
      maxLength: maxLength(60)
    },
    item_code: {
      required, 
      slugFieldValidator, 
      maxLength: maxLength(15)
    },
    unit: { 
      required, 
      maxLength: maxLength(10)
    },
    barcode: { 
      maxLength: maxLength(15)
    },
    technical_description: {
      maxLength: maxLength(800)
    },
    itemInfoGroup: [
      "category",
      "item_code",
      "description",
      "unit",
      "barcode",
      "technical_description",
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
    itemCodeErrors() {
      const errors = [];
      if (!this.$v.item_code.$dirty) return errors;
      !this.$v.item_code.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.item_code.slugFieldValidator && errors.push(this.$t('SlugFieldErrorMessage'));
      !this.$v.item_code.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 15));
      return errors;
    },
    unitErrors() {
      const errors = [];
      if (!this.$v.unit.$dirty) return errors;
      !this.$v.unit.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.unit.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 10));
      return errors;
    },
    barcodeErrors() {
      const errors = [];
      if (!this.$v.barcode.$dirty) return errors;
      !this.$v.barcode.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 15));
      return errors;
    },
    technicalDescriptionErrors() {
      const errors = [];
      if (!this.$v.technical_description.$dirty) return errors;
      !this.$v.technical_description.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 800));
      return errors;
    },
    categoryErrors() {
      const errors = [];
      if (!this.$v.category.$dirty) return errors;
      !this.$v.category.isDifferent && errors.push(this.$t("You must select a category"))
      return errors;
    },
    
  },

};
</script>
<style scoped>
.v-application .mb-3 {
  margin-bottom: 0px !important;
}
</style>
