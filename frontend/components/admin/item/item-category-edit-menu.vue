<template>
  <div>
    <dots-menu-update-delete :menu_items="menu_items" :handleClick="handleClick"/>

    <v-dialog v-model="show_edit_dialog" max-width="50%">
      <v-card>
        <v-card-title>{{$t('Edit')}}</v-card-title>
        <v-card-text>
          <v-container fluid>
              <!-- Description -->
              <v-text-field
                :label="$t('Description')"
                v-model.trim="description"
                :error-messages="descriptionErrors"
                @blur="$v.description.$touch()"
                required
                class="mb-3"
              />
              <!-- Note -->
              <v-text-field
                :label="$t('Note')"
                v-model.trim="note"
                :error-messages="technicalDescriptionErrors"
                @blur="$v.note.$touch()"
                required
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
            @click="updateCategory()"
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
            <v-btn class="red--text darken-1" text @click="deleteCategory()">{{$t('Delete')}}</v-btn>
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
export default {
  mixins: [validationMixin],
  components: {
    "dots-menu-update-delete": require("@/components/dots-menu-update-delete.vue").default,
  },
  props: ['category'],
  data() {
    return {
      show_edit_dialog: false,
      show_delete_confirmation_dialog: false,
      description: null,
      note: null,
      loading: false,
      menu_items: [
      ...(this.hasUpdateItemCategoryPermission() ? [{ 
          title: this.$t('Edit'),
          icon: 'mdi-pencil',
          async click(){
            this.show_edit_dialog = true
          }
        }] : [] ),
        ...(this.hasDeleteItemCategoryPermission() ? [{ 
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
    note: {
      maxLength: maxLength(800)
    },
    itemCategoryInfoGroup: [
      "description",
      "note",
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

      async updateCategory(){
        this.$v.itemCategoryInfoGroup.$touch();
        if (this.$v.itemCategoryInfoGroup.$invalid) {
          this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
        } else {
          this.loading = true;
          let data = await this.$store.dispatch("item/updateCategory", {
            category_compound_id: this.category.category_compound_id,
            description: this.description,
            note: this.note,
          })
          // Reactivity for ItemCategory list inside ItemCategory.vue 
          this.loading = false;
          if (data) {
            this.category.description = data.description
            this.category.note = data.note
          }
        }
      },
      async deleteCategory(){
        let data = await this.$store.dispatch(
          'item/deleteCategory', 
          {category_compound_id: this.category.category_compound_id}
        )
        if (data === "ok"){
          this.$emit('item-category-deleted')
        }
      },

      hasUpdateItemCategoryPermission(){
        let user = this.$store.state.user.currentUser;
        return user.permissions.includes("update_item_category")
      },

      hasDeleteItemCategoryPermission(){
        let user = this.$store.state.user.currentUser;
        return user.permissions.includes("delete_item_category")
      },
  },

  mounted() {
    this.description = this.category.description
    this.note = this.category.note
  },
}
</script>
