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
            <!-- Active Users -->
            <v-text-field
              label="Active users limit"
              v-model="active_users_limit"
              :error-messages="activeUsersLimitErrors"
              required
              @blur="$v.active_users_limit.$touch()"
              class="mb-3"
            />
            <!-- Status -->
            <v-radio-group v-model="status" style="width: 25%;" label="Contracting Company Status" class="mb-3">
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
        <v-card-actions>
          <v-spacer />
          <v-btn class="blue--text darken-1" text @click="show_edit_dialog = false">Cancel</v-btn>
          <v-btn class="blue--text darken-1" text @click="updateContracting()">Save</v-btn>
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
  minValue,
  maxValue,
  integer
} from "vuelidate/lib/validators";
import { validationMixin } from "vuelidate";
export default {
  components: {
    "dots-menu-update-delete": require("@/components/dots-menu-update-delete.vue").default,
  },
  props: ['contracting'],
  mixins: [validationMixin],
  data: () => ({
    name: null,
    active_users_limit: null,
    status: null,
    note: null,
    show_edit_dialog: false,
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
            'organization/deleteContracting', 
            {contracting_code: this.contracting.contracting_code}
          )
          if (data === "ok"){
            this.$emit('contracting-deleted')
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
      "contracting_code",
      "active_users_limit",
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
    activeUsersLimitErrors() {
      const errors = [];
      if (!this.$v.active_users_limit.$dirty) return errors;
      !this.$v.active_users_limit.required && errors.push("This field is required.");
      !this.$v.active_users_limit.integer && errors.push("This value must be a integer.");
      !this.$v.active_users_limit.minValue && errors.push("This field cannot be less then 4.");
      !this.$v.active_users_limit.maxValue && errors.push("Make sure this value is less than or equal to 2147483647");
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
      //this.menu_items[id].click()  #will get errors, because of function click will no can access property with it's own 'this'
      this.menu_items[index].click.call(this) // will call the function but the function will use the Vue instance 'this' context.
    },
    async updateContracting(){
      // If update is successful, I update in the contracting prop
      try{
        let data = await this.$store.dispatch("organization/updateContracting", {
          contracting_code: this.contracting.contracting_code,
          name: this.name,
          active_users_limit: this.active_users_limit,
          status: this.status,
          note: this.note,

        })
        this.contracting.name = data.name
        this.contracting.active_users_limit = data.active_users_limit
        this.contracting.status = data.status
        this.contracting.note = data.note
      } catch(e){
        // error is being handled inside action
		}

    },
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
