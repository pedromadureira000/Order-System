<template>
  <div>
    <v-dialog :retain-focus="false" :value="show_duplicate_order_dialog" max-width="40%" persistent>
      <v-card v-if="comps_and_estabs_already_fetched">
        <v-card-title style="display: flex; justify-content: center;" class="mb-2">{{$t('Duplicate Order')}}</v-card-title>
        <form @submit.prevent="updateOrder" class="ml-3">
          <div style="display: flex; justify-content: center;">
            <div style="width: 80%">
              <v-row >
                <v-col>
                  <!-- Company -->
                  <div>
                    <v-select
                      v-model="company"
                      :label="$t('Company')"
                      :item-text="(x) => x.company_code + ' - ' + x.name"
                      :items="comps_and_estabs"
                    ></v-select>
                  </div>
                  <!-- Establishment -->
                  <div>
                    <v-select
                      v-model="establishment"
                      :label="$t('Establishment')"
                      :item-text="(x) =>  x.establishment_code + ' - ' + x.name"
                      :items="company.establishment_set"
                    ></v-select>
                  </div>
                <p>{{$t('areYouSureAboutDuplicateOrderMessage')}}</p>
                </v-col>
              </v-row>
            </div>
          </div>
          <!-- Submit Form -->
          <v-card-actions>
            <!-- Submit -->
            <v-spacer />
            <v-btn
              class="blue--text darken-1"
              text
              @click="duplicateOrder"
            >{{$t('Duplicate Order')}}</v-btn>
            <v-btn 
              class="black--text darken-1" 
              text 
              @click="$emit('close-duplicate-order-dialog')"
            >{{$t('Close')}}</v-btn>
          </v-card-actions>
        </form>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { validationMixin } from "vuelidate";
export default {
  mixins: [validationMixin],
  components: {
    "dots-menu": require("@/components/dots-menu.vue").default,
  },
  props: ['order', 'show_duplicate_order_dialog'],
  data() {
    return {
      comps_and_estabs: [],
      company: null,
      establishment: null,
      comps_and_estabs_already_fetched: false
    }
  },

  methods: {
    async fetchCompaniesAndEstabsToDuplicateOrder(){
      let comps_and_estabs = await this.$store.dispatch("order/fetchCompaniesAndEstabsToDuplicateOrder",
        this.order.id);
      if (comps_and_estabs){
        this.comps_and_estabs = comps_and_estabs
        if (comps_and_estabs.length > 0){
          this.company = comps_and_estabs[0]
          if (this.company.establishment_set.length > 0){
            this.establishment = comps_and_estabs[0].establishment_set[0]
            this.comps_and_estabs_already_fetched = true
          }else{
            this.$store.dispatch("setAlert", { message: this.$t('There is no establishments available.'), alertType: "warning" }, { root: true })
            this.$emit('close-duplicate-order-dialog')
          }
        }else{
          this.$store.dispatch("setAlert", { message: this.$t('There is no companies available.'), alertType: "warning" }, { root: true })
          this.$emit('close-duplicate-order-dialog')
        }
      }
      else {
        this.$emit('close-duplicate-order-dialog')
      }
    },
    async duplicateOrder(){
      let data = await this.$store.dispatch("order/duplicateOrder", this.order.id)
      if (data){
        if (data.some_items_were_not_copied === "True"){
          this.$store.dispatch("setAlert", { message: this.$t('some_items_were_not_copied'), alertType: "warning" }, { root: true })
        }
        /** console.log(">>>>>>> data.response_data: ", data.response_data) */
        this.$emit('order-duplicated', data.response_data)
      }
    }
  },

  watch: {
    show_duplicate_order_dialog(newValue){
      if (newValue === true){
        this.fetchCompaniesAndEstabsToDuplicateOrder()
      }
    },
  },

}
</script>
