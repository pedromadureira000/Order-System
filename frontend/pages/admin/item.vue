<template>
  <div>
    <v-bottom-navigation v-model="value">
      <v-btn v-for="item in currentMenuItems" :key="item.title" :value="item.title" :to="localePath(item.to)" nuxt>
        <span>{{$t(item.title)}}</span>
        <v-icon>{{item.icon}}</v-icon>
      </v-btn>
    </v-bottom-navigation>
		<nuxt-child/>
  </div>
</template>

<script>
  import {CRUDitemPermissions, CRUDpriceTablePerms, CRUDitemCategoryPerms } from '~/helpers/permissions'
  export default {
    middleware: ["authenticated"],
    data(){ 
      return {
        value: 'Item',
        allMenuItems: [
          {"permissions": CRUDitemPermissions, title: "Item", icon:"mdi-cart-variant", to: "admin-item"},
          {"permissions": CRUDitemCategoryPerms, title: "Item_Category", icon:"mdi-format-list-bulleted-type", to: "admin-item-item_category"},
          {"permissions": CRUDpriceTablePerms, title: "Price_Table", icon:"mdi-table-large", to: "admin-item-price_table"},
        ],
      }
    },

    computed: {
      currentMenuItems() {
        let user = this.$store.state.user.currentUser;
        return this.allMenuItems.filter(MenuItem => {
          return MenuItem.permissions.some(permission => user.permissions.includes(permission))
        })
      },
    },
  }
</script>
<style scoped>
</style>
