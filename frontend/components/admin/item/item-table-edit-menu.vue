<template>
  <div>
    <dots-menu :menu_items="menu_items" :handleClick="handleClick"/>

    <v-dialog :retain-focus="false" v-model="show_edit_dialog" max-width="50%">
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
            <v-textarea
              outlined
              :label="$t('Note')"
              v-model="note"
              :error-messages="noteErrors"
              @blur="$v.note.$touch()"
              class="mb-3"
            />
          </v-container>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="d-flex justify-space-around" style="width:100%;">
          <v-btn class="blue--text darken-1" text @click="show_edit_dialog = false">{{$t('Cancel')}}</v-btn>
          <v-btn 
            class="blue--text darken-1" 
            text 
            @click="updateItemTable()"
            :loading="loading"
            :disabled="loading"
          >{{$t('Save')}}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <delete-confirmation-dialog 
      @delete-item="deleteItemTable" 
      @cancel="show_delete_confirmation_dialog = false" 
      :show_delete_confirmation_dialog="show_delete_confirmation_dialog"
    />
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
  components: {
    "dots-menu": require("@/components/dots-menu.vue").default,
    "delete-confirmation-dialog": require("@/components/delete-confirmation-dialog.vue").default,
  },
  props: ['item_table'],
  mixins: [validationMixin],
  data() { 
    return {
      description: null,
      note: null,
      show_edit_dialog: false,
      show_delete_confirmation_dialog: false,
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
    description: { 
      required, 
      minLength: minLength(3),
      maxLength: maxLength(60)
    },
    note: {
      maxLength: maxLength(800)
    },
    itemTableInfoGroup: [
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
    noteErrors() {
      const errors = [];
      if (!this.$v.note.$dirty) return errors;
      !this.$v.note.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 800));
      return errors;
    },
  },

  methods: {
    handleClick(index){
      //this.menu_items[id].click()  #will get errors, because of function click will no can access property with it's own 'this'
      this.menu_items[index].click.call(this) // will call the function but the function will use the Vue instance 'this' context.
    },
    async updateItemTable(){
      this.$v.itemTableInfoGroup.$touch();
      if (this.$v.itemTableInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
      } else {
        this.loading = true
      // If update is successful, I update in the item_table prop
        let data = await this.$store.dispatch("item/updateItemTable", {
          item_table_compound_id: this.item_table.item_table_compound_id,
          description: this.description,
          note: this.note,
        })
        this.loading = false
        if (data){
          this.item_table.description = data.description
          this.item_table.active_users_limit = data.active_users_limit
          this.item_table.status = data.status
          this.item_table.note = data.note
            // Close dialog
          this.show_edit_dialog = false
        }
		  }
    },

    async deleteItemTable(){
      let data = await this.$store.dispatch(
        'item/deleteItemTable', 
        {item_table_compound_id: this.item_table.item_table_compound_id}
      )
      if (data === "ok"){
        this.$emit('item-table-deleted')
      }

    }
  },
  // I can't add prop data to data property directly, this is why I'm doing this.
  mounted() {
    this.description = this.item_table.description
    this.active_users_limit = this.item_table.active_users_limit
    // If i don't convert to string, it will not mark the radio button
    this.status = String(this.item_table.status)
    this.note = this.item_table.note
  },
}
</script>
