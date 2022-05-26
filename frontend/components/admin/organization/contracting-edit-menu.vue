<template>
  <div>
    <dots-menu :menu_items="menu_items" :handleClick="handleClick"/>

    <v-dialog :retain-focus="false" v-model="show_edit_dialog" max-width="50%">
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
            <!-- Active Users -->
            <v-text-field
              :label="$t('Active_users_limit')"
              v-model="active_users_limit"
              :error-messages="activeUsersLimitErrors"
              required
              @blur="$v.active_users_limit.$touch()"
              class="mb-3"
            />
            <!-- Status -->
            <v-radio-group v-model="status" style="width: 25%;" :label="$t('Contracting_Company_Status')" class="mb-3">
              <v-radio
                :label="$t('Active')"
                value=1
              ></v-radio>
              <v-radio
                :label="$t('Disabled')"
                value=0
              ></v-radio>
            </v-radio-group>
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
            @click="updateContracting()"
            :loading="loading"
            :disabled="loading"
          >{{$t('Save')}}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <delete-confirmation-dialog 
      @delete-item="deleteContracting" 
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
  minValue,
  maxValue,
  integer
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
export default {
  components: {
    "dots-menu": require("@/components/dots-menu.vue").default,
    "delete-confirmation-dialog": require("@/components/delete-confirmation-dialog.vue").default,
  },
  props: ['contracting'],
  mixins: [validationMixin],
  data() { 
    return {
      name: null,
      active_users_limit: null,
      status: null,
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
    name: { 
      required, 
      minLength: minLength(3),
      maxLength: maxLength(60)
    },
    active_users_limit: {
      required, 
      integer,
      minValue: minValue(4),
      maxValue: maxValue(2147483647)
    },
    note: {
      maxLength: maxLength(800)
    },
    contractingInfoGroup: [
      "name",
      "active_users_limit",
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
    activeUsersLimitErrors() {
      const errors = [];
      if (!this.$v.active_users_limit.$dirty) return errors;
      !this.$v.active_users_limit.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.active_users_limit.integer && errors.push(this.$t("This_value_must_be_a_integer"));
      !this.$v.active_users_limit.minValue && errors.push(this.$formatStr(this.$t("This_value_must_be_greater_than_X"), 3 ));
      !this.$v.active_users_limit.maxValue && errors.push(this.$formatStr(this.$t("This_value_must_be_less_than_X"), 2147483648));
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
    async updateContracting(){
      // If update is successful, I update in the contracting prop
      this.$v.contractingInfoGroup.$touch();
      if (this.$v.contractingInfoGroup.$invalid) {
        this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
      } else {
        this.loading = true;
        let data = await this.$store.dispatch("organization/updateContracting", {
          contracting_code: this.contracting.contracting_code,
          name: this.name,
          active_users_limit: this.active_users_limit,
          status: this.status,
          note: this.note,
        })
        this.loading = false
        if (data){
          this.contracting.name = data.name
          this.contracting.active_users_limit = data.active_users_limit
          this.contracting.status = data.status
          this.contracting.note = data.note
            // Close dialog
          this.show_edit_dialog = false
        }
		  }
    },

    async deleteContracting(){
      let data = await this.$store.dispatch(
        'organization/deleteContracting', 
        {contracting_code: this.contracting.contracting_code}
      )
      if (data === "ok"){
        this.$emit('contracting-deleted')
      }

    }
  },
  // I can't add prop data to data property directly, this is why I'm doing this.
  mounted() {
    this.name = this.contracting.name
    this.active_users_limit = this.contracting.active_users_limit
    // If i don't convert to string, it will not mark the radio button
    this.status = String(this.contracting.status)
    this.note = this.contracting.note
  },
}
</script>
