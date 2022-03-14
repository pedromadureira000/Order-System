<template>
  <v-select
    :disabled="loading == true ? true : disabled"
    :label="$t('Price_Table')"
    :items="price_tables"
    :item-text="(x) => x.description == 'default_null_value' && x.table_code == 'default_null_value' ? 'Null' : x.table_code + ' - ' + x.description"
    :item-value="(x) => x.price_table_compound_id"
    @change="updatePriceTable(establishment, $event)"
    :loading="loading"
    clearable
    shaped
    outlined
  ></v-select>
</template>

<script>
export default {
  props: ['client_establishments', 'establishment'],
  data() {
    return {
      price_tables: [{price_table_compound_id: null, description: 'default_null_value', table_code: 'default_null_value'}],
      loading: false,
    }
  },

  methods: {
    updatePriceTable(establishment, event){
      this.$emit('update-price-table', establishment, event)
    },

    async fetchPriceTables(){
      this.loading = true
      let price_tables = await this.$store.dispatch("item/fetchPriceTables");
      for (const price_table_index in price_tables){
        let price_table = price_tables[price_table_index]
        this.price_tables.push(price_table)
      }
      this.loading = false
    },
  },

  computed: {
    disabled(){
      return !this.client_establishments.some((obj) => obj.establishment === this.establishment.establishment_compound_id)
    }
  },
  watch: {
    disabled(newValue){
      if (newValue == false) {
        if (this.price_tables.length == 1) {
          this.fetchPriceTables()
        }
      }	
    }
  }
}
</script>

<style>

</style>
