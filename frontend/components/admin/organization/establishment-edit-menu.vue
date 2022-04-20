<template>
  <div>
    <dots-menu :menu_items="menu_items" :handleClick="handleClick"/>

    <v-dialog :retain-focus="false" v-model="show_edit_dialog" max-width="50%">
      <v-card>
        <v-card-title>{{$t('Edit')}}</v-card-title>
        <v-card-text>
          <v-container fluid>
            <!-- Company -->
            <v-row align="center">
              <v-col
                class="d-flex"
                cols="12"
                sm="6"
              >
                <v-select
                  disabled
                  v-model="companyFromEstab"
                  :label="$t('Company')"
                  :items="companies"
                  :item-text="(x) => x.company_code + ' - ' + x.name"
                  :item-value="(x) => x.company_compound_id"
                ></v-select>
              </v-col>
            </v-row>
            <!-- Name -->
            <v-text-field
              :label="$t('Name')"
              v-model="name"
              :error-messages="nameErrors"
              required
              @blur="$v.name.$touch()"
              class="mb-3"
            />
              <!-- CNPJ -->
              <v-text-field
                label="CNPJ"
                v-model="cnpj"
                v-mask="'##.###.###/####-##'"
                required
                :error-messages="cnpjError"
                @blur="$v.cnpj.$touch()"
                class="mb-3"
              />
            <!-- Establishment Status -->
            <v-radio-group v-model="status" style="width: 25%;" :label="$t('Establishment_Status')" class="mb-3">
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
              v-model="note"
              :label="$t('Note')"
              :error-messages="noteErrors"
              @blur="$v.note.$touch()"
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
              @click="updateEstablishment()"
              :loading="loading"
              :disabled="loading"
            >{{$t('Save')}}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- Delete Confirmation Dialog -->
    <v-dialog :retain-focus="false" v-model="show_delete_confirmation_dialog" max-width="30%">
      <v-card>
        <v-card-title>{{$t('Are_you_sure_you_want_to_delete')}}</v-card-title>
        <v-card-text>
          <v-card-actions class="d-flex justify-space-around" style="width:100%;">
            <v-btn class="black--text darken-1" text @click="show_delete_confirmation_dialog = false">{{$t('Cancel')}}</v-btn>
            <v-btn class="red--text darken-1" text @click="deleteEstablishment()">{{$t('Delete')}}</v-btn>
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
import {cnpjFieldValidator} from "~/helpers/validators"
import {mask} from 'vue-the-mask'
export default {
  mixins: [validationMixin],
  components: {
    "dots-menu": require("@/components/dots-menu.vue").default,
  },
  props: ['establishment', 'companies', 'companies_was_fetched'],
  directives: {mask},
  data() {
    return {
      show_edit_dialog: false,
      show_delete_confirmation_dialog: false,
      name: null,
      cnpj: null,
      status: null,
      note: null,
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
    cnpj: {
      required, 
      cnpjFieldValidator,
    },
    note: {
      maxLength: maxLength(800)
    },
    establishmentInfoGroup: [
      "name",
      "cnpj",
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
    cnpjError() { 
      const errors = [];
      if (!this.$v.cnpj.$dirty) return errors;
      !this.$v.cnpj.required && errors.push(this.$t("This_field_is_required"));
      !this.$v.cnpj.cnpjFieldValidator && errors.push(this.$t("cnpjValidationError"));
      return errors;
    },
    noteErrors() {
      const errors = [];
      if (!this.$v.note.$dirty) return errors;
      !this.$v.note.maxLength && errors.push(this.$formatStr(this.$t("This_field_must_have_up_to_X_characters"), 800));
      return errors;
    },
    /** Defaul value to company field */
    companyFromEstab(){
      return this.companies.find(el=>el.company_compound_id === this.establishment.company)
    }
  },

    methods: {
      handleClick(index){
        //this.menu_items[id].click()  #will get errors because the function click will not access properties with its own 'this'
        this.menu_items[index].click.call(this) // will call the function but the function will use the vue instance 'this' context.
      },
      async updateEstablishment(){
        this.$v.establishmentInfoGroup.$touch();
        if (this.$v.establishmentInfoGroup.$invalid) {
          this.$store.dispatch("setAlert", { message: this.$t("Please_fill_the_form_correctly"), alertType: "error" }, { root: true })
        } else {
            this.loading = true;
            let data = await this.$store.dispatch("organization/updateEstablishment", {
              establishment_compound_id: this.establishment.establishment_compound_id,
              name: this.name,
              cnpj: this.cnpj,
              status: this.status,
              note: this.note,
            })
            this.loading = false;
            if (data){
              // Reactivity for Establishment list inside Establishment.vue 
              this.establishment.name = data.name
              this.establishment.cnpj = data.cnpj
              this.establishment.status = data.status
              this.establishment.note = data.note
                // Close dialog
              this.show_edit_dialog = false
            }
          }
      },
      async deleteEstablishment(){
        let data = await this.$store.dispatch(
          'organization/deleteEstablishment', 
          {establishment_compound_id: this.establishment.establishment_compound_id}
        )
        if (data === "ok"){
          this.$emit('establishment-deleted')
        }
      }
  },

  mounted() {
    this.name = this.establishment.name
    this.cnpj = this.establishment.cnpj
    this.status = String(this.establishment.status)
    this.note = this.establishment.note
  },

  watch: {
    show_edit_dialog(newValue){
      if (newValue === true) {
        // fetch companies
        if (!this.companies_was_fetched) {
          this.$emit('fetch-companies')
        }	
      }
    },
  }
}
</script>
