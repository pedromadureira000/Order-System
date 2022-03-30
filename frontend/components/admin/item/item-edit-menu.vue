<template>
  <div>
    <dots-menu-update-delete :menu_items="menu_items" :handleClick="handleClick"/>

    <v-dialog v-model="show_edit_dialog" max-width="50%">
      <v-card>
        <v-card-title>{{$t('Edit')}}</v-card-title>
        <v-card-text>
          <v-container fluid>
              <!-- Item Table -->
              <v-row align="center">
                <v-col
                  class="d-flex"
                  cols="12"
                  sm="6"
                >
                  <v-select
                    disabled
                    v-model="item_table_from_item"
                    :label="$t('Item_Table')"
                    :items="item_tables"
                    :item-text="(x) => x.item_table_code + ' - ' + x.description"
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
          </v-container>
        </v-card-text>
        <v-divider></v-divider>
        <!-- Submit Button -->
        <v-card-actions class="d-flex justify-space-around" style="width:100%;">
          <v-btn class="blue--text darken-1" text @click="show_edit_dialog = false">{{$t('Cancel')}}</v-btn>
          <v-btn 
            class="blue--text darken-1" 
            text 
            @click="updateItem()"
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
            <v-btn class="red--text darken-1" text @click="deleteItem()">{{$t('Delete')}}</v-btn>
          </v-card-actions>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from '~/plugins/axios'
import {
  required,
  minLength,
  maxLength,
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
export default {
  mixins: [validationMixin],
  components: {
    "dots-menu-update-delete": require("@/components/dots-menu-update-delete.vue").default,
  },
  props: ['item', 'item_tables', 'category_group'],
  data() {
    return {
      item_table_from_item: null,
      show_edit_dialog: false,
      show_delete_confirmation_dialog: false,
      category: null,
      categories: [],
      description: null,
      technical_description: null,
      unit: null,
      barcode: null,
      status: "1",
      image: null,
      img_url: '',
      loading: false,
      menu_items: [
      ...(this.hasUpdateItemPermission() ? [{ 
          title: this.$t('Edit'),
          icon: 'mdi-pencil',
          async click(){
            this.show_edit_dialog = true
          }
        }] : [] ),
        ...(this.hasDeleteItemPermission() ? [{ 
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
    description: { 
      required, 
      minLength: minLength(3),
      maxLength: maxLength(60)
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

    methods: {
      handleClick(index){
        //this.menu_items[id].click()  #will get errors because the function click will not access properties with its own 'this'
        this.menu_items[index].click.call(this) // will call the function but the function will use the vue instance 'this' context.
      },

      async fetchCategoriesToCreateItem(){
          let categories = await this.$store.dispatch("item/fetchCategoriesToCreateItem", this.item.item_table); 
          if (categories){
            this.category_group.push({item_table: this.item.item_table, categories: categories} )
            this.categories = categories
          }
      },

      async updateItem(){
        this.$v.itemInfoGroup.$touch();
        if (this.$v.itemInfoGroup.$invalid) {
          this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
        } else {
          this.loading = true;
          //
          const formData = new FormData()
          formData.append('item_compound_id', this.item.item_compound_id)
          formData.append('category', this.category)
          formData.append('description', this.description)
          formData.append('unit', this.unit)
          formData.append('barcode', this.barcode)
          formData.append('status', this.status)
          formData.append('technical_description', this.technical_description)
          if (this.image){
            formData.append('image', this.image, this.image.name)
          }
          let data = await this.$store.dispatch("item/updateItem", formData);
          // Reactivity for Item list inside Item.vue 
          this.loading = false;
          if (data) {
            this.item.category = data.category
            this.item.description = data.description
            this.item.unit = data.unit
            this.item.barcode = data.barcode
            this.item.status = data.status
            this.item.technical_description = data.technical_description
            this.item.image = this.getImageUrl(data.image) 
              // Close dialog
            this.show_edit_dialog = false
          }
        }
      },
      async deleteItem(){
        let data = await this.$store.dispatch(
          'item/deleteItem', 
          {item_compound_id: this.item.item_compound_id}
        )
        if (data === "ok"){
          this.$emit('item-deleted')
        }
      },

      // Permissions
      hasUpdateItemPermission(){
        let user = this.$store.state.user.currentUser;
        return user.permissions.includes("update_item")
      },

      hasDeleteItemPermission(){
        let user = this.$store.state.user.currentUser;
        return user.permissions.includes("delete_item")
      },

      //Image

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
  },

  mounted() {
    this.category = this.item.category
    this.description = this.item.description
    this.unit = this.item.unit
    this.barcode = this.item.barcode
    this.status = this.item.status
    this.technical_description = this.item.technical_description
    this.img_url = this.getImageUrl(this.item.image)
    // Default value for item_table_from_item
    let item_table = this.item_tables.find(el=>el.item_table_compound_id === this.item.item_table)
    this.item_table_from_item = item_table
  },

  watch: {
    show_edit_dialog(newValue){
      if ( newValue === true) {
        let category_already_exists = this.category_group.find(el=>el.item_table===this.item.item_table)
        if (category_already_exists){
          this.categories = category_already_exists.categories
        } else {
          this.fetchCategoriesToCreateItem()
        }
      }	
    }
  },
}
</script>
