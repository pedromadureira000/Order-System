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
              <!-- Item Table -->
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
                    :item-text="(x) => x.item_table_code + ' - ' + x.description"
                    :item-value="(x) => x.item_table_compound_id"
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
                    :item-text="(x) => x.category_code + ' - ' + x.description"
                    :item-value="(x) => x.category_compound_id"
                  ></v-select>
                </v-col>
              </v-row>

              <!-- Item code -->
              <v-text-field
                :label="$t('Item code')"
                v-model="item_code"
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

      <div v-if="hasGetItemsPermission()">
        <h3 class="mt-6">{{$t('Edit Item')}}</h3>
        <v-data-table
          :headers="headers"
          :items="items"
          :items-per-page="10"
          item-key="item_compound_id"
          class="elevation-1 mt-3"
        >
          <template v-slot:item.description="{ item }">
            <p style="width: 240px;">{{item.description}}</p>
          </template>
          <template v-slot:item.image="{ item }">
            <v-img
              contain
              width="115px"
              height="87px"
              :lazy-src="$store.state.CDNBaseUrl + '/media/images/items/defaultimage.jpeg'"
              :src="getImageUrl(item.image)"
            ></v-img>
          </template>
          <template v-slot:item.actions="{ item }">
            <item-edit-menu :item="item" :item_tables="item_tables" :category_group="category_group" @item-deleted="deleteItem(item)" />
          </template>
          <template v-slot:item.category="{ item }">
            <p>{{item.category.split('&')[2]}}</p>
          </template>
          <template v-slot:item.status="{ item }">
            <p>{{item.status === 1 ? $t('Active') : $t('Disabled')}}</p>
          </template>
          <template v-slot:item.technical_description="{ item }">
            <p>{{$getNote(item.technical_description)}}</p>
          </template>
        </v-data-table>
      </div>
    </div>
  </div>
</template>

<script>
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
    "item-edit-menu": require("@/components/admin/item/item-edit-menu.vue").default,
  },
  mixins: [validationMixin],

  data() {
    return {
      item_table: null,
      category: null,
      item_code: null,
      description: null,
      technical_description: "",
      unit: null,
      barcode: "",
      status: "1",
      image: null,
      items: [],
      categories: [],
      item_tables: [],
      category_group: [],
      /**EX:  category_group: [{item_table: '123$123', categories: [{categoryObj, categoryObj2 }]}] */
      img_url: '',
      loading: false,
      headers: [
        { text: this.$t('Image'), value: 'image' },
        { text: this.$t('Code'), value: 'item_code' },
        { text: this.$t('Description'), value: 'description' },
        { text: this.$t('Category'), value: 'category' },
        { text: this.$t('Unit'), value: 'unit' },
        { text: this.$t('Barcode'), value: 'barcode' },
        { text: 'Status', value: 'status' },
        { text: this.$t('Technical description'), value: 'technical_description' },
        { text: this.$t('Actions'), value: 'actions' },
      ]
    };
  },

  async fetch() {
    let items = await this.$store.dispatch("item/fetchItems");
    if (items){this.items.push(...items)}

    // Fetch ItemTables
    let item_tables = await this.$store.dispatch("item/fetchItemTablesToCreateItemOrCategoryOrPriceTable"); 
    if (item_tables){
      this.item_tables.push(...item_tables)
      if (this.item_tables.length > 0){
        this.item_table = this.item_tables[0].item_table_compound_id
        await this.fetchCategoriesToCreateItem()
      }
    }
  },

  methods: {
    async createItem(){
      this.$v.itemInfoGroup.$touch();
      if (this.$v.itemInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t('Please_fill_the_form_correctly'), alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        const formData = new FormData()
        formData.append('item_table', this.item_table)
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
          this.items.push(data);
          // Clearing fields
          this.$v.$reset()
          // this avoid "This field is required" errors by vuelidate
          this.item_table = this.item_tables[0].item_table_compound_id
          this.category = this.categories[0].category_compound_id 
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

    deleteItem(itemToDelete) {
      this.items = this.items.filter((item) => item.item_code != itemToDelete.item_code);
    },

    async fetchCategoriesToCreateItem(){
          let category_already_exists = this.category_group.find(el=>el.item_table == this.item_table)
          if (category_already_exists){
            this.categories = category_already_exists.categories
            if (this.categories.length > 0){
              this.category = this.categories[0].category_compound_id 
            }
          }
          else{
            let categories = await this.$store.dispatch("item/fetchCategoriesToCreateItem", this.item_table); 
            if (categories){
              this.category_group.push({item_table: this.item_table, categories: categories} )
              this.categories = categories
              if (this.categories.length > 0){
                this.category = this.categories[0].category_compound_id 
              }
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
    // The backend return item url with base url "http://..." after create an item
    getImageUrl(image){
      if (image) {
        let url = image
        if (url.startsWith('http')){
          let url_fixed = url.split('/media/images/')[1]
          return this.$store.state.CDNBaseUrl + '/media/images/' + url_fixed
        }
        else {
          return this.$store.state.CDNBaseUrl + url
        }
      }
      else {
        return this.$store.state.CDNBaseUrl + '/media/images/items/defaultimage.jpeg'
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
      maxLength: maxLength(13)
    },
    technical_description: {
      maxLength: maxLength(800)
    },
    itemInfoGroup: [
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
      !this.$v.barcode.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 13));
      return errors;
    },
    technicalDescriptionErrors() {
      const errors = [];
      if (!this.$v.technical_description.$dirty) return errors;
      !this.$v.technical_description.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 800));
      return errors;
    },
  },

  /** mounted() { */
    /** console.log('>>>>>>>>>>>>>>>>>> CDN url: ', this.cdn_url) */
  /** } */
};
</script>
<style scoped>
.v-application .mb-3 {
  margin-bottom: 0px !important;
}
</style>
