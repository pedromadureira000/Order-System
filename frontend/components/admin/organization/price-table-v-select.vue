<template>
  <v-select
    :disabled="loading == true ? true : disabled"
    :label="$t('Price_Table')"
    :items="price_tables"
    :item-text="el => el.description == 'default_null_value' && el.table_code == 'default_null_value' ? $t('Empty') : el.table_code + ' - ' + el.description"
    :item-value="el => el"
    @change="updatePriceTable(establishment, $event)"
    :loading="loading"
    v-model="price_table"
    shaped
    outlined
  ></v-select>
</template>

<script>
const default_value = {price_table_compound_id: null, description: 'default_null_value', table_code: 'default_null_value'}
export default {
  props: ['client_establishments', 'establishment', 'price_table_groups', 'aux_cli_estab'],
  data() {
    return {
      price_tables: [default_value],
      price_table: default_value,
      loading: false,
    }
  },

  methods: {
    updatePriceTable(establishment, event){
      this.$emit('update-price-table', establishment, event)
    },

    async fetchPriceTables(){
      let price_table_already_fetched = this.price_table_groups.find(el=>el.group_id === this.establishment.company)
      if (price_table_already_fetched){
        /** console.log(">>>>>>> I GOT IT $$$$$$$$$$$$$$$$$", price_table_already_fetched) */
        // price_table_already_fetched comes with 'default_null_value'
        this.price_tables = price_table_already_fetched.price_tables
      }else{
        /** console.log(">>>>>>> I fetch IT $$$$$$$$$$$$$$$$$") */
        this.loading = true
        let price_tables = await this.$store.dispatch("organization/fetchPriceTablesToCreateClient", this.establishment.company);
        this.loading = false
        if (price_tables) {
          this.price_tables.push(...price_tables)
          this.$emit('update-price-table-groups', {group_id: this.establishment.company, price_tables: this.price_tables})
        }
      }
    },
  },

  computed: {
    disabled(){
      return !this.client_establishments.some((obj) => obj.establishment === this.establishment.establishment_compound_id)
    }
  },

  watch: {
    // Price_Table fetch if checkbox is marked
    disabled(newValue){
      if (newValue == false) {
        if (this.price_tables.length == 1) {
          this.fetchPriceTables()
        }
      }	
    }
  },
  mounted() {
    /** console.log('>>>>>>>>>>>>>>>>>>: ???????? It is disabled?', this.disabled) */
    // Initial price_tables fetch for if cli_estab exists
    if (!this.disabled){
      this.fetchPriceTables()
    }
    // cli_estab.price_table exists and is different from 'null'.
    let preselected_price_table = this.price_tables.find(el=>el.price_table_compound_id==this.aux_cli_estab.price_table && this.aux_cli_estab.price_table !==null)
    if (preselected_price_table){
      /** console.log('>>>>>>>>>>>>>>>>>>: preselected_price_table: ', preselected_price_table) */
      this.price_table = preselected_price_table
    } 
  }
}
</script>

<style>

</style>
