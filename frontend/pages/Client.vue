<template>
  <div>
    <v-bottom-navigation v-model="value">
      <v-btn value="user" to="/admin/user" nuxt>
        <span>User</span>
        <v-icon>mdi-account</v-icon>
      </v-btn>

      <v-btn value="item" to="/admin/item" nuxt>
        <span>Item</span>
        <v-icon>mdi-cart-variant</v-icon>
      </v-btn>

      <v-btn value="item category" to="/admin/item_category" nuxt>
        <span>Item Category</span>
        <v-icon>mdi-archive-edit-outline</v-icon>
      </v-btn>

      <v-btn value="price table" to="/admin/price_table" nuxt>
        <span>Price Table</span>
        <v-icon>mdi-table-large</v-icon>
      </v-btn>
    </v-bottom-navigation>
		<nuxt-child/>
  </div>
</template>

<script>
  export default {
    data: () => ({ value: 'user' }),
  }
</script>
<style scoped>
</style>
