<template>
  <div>
    <v-bottom-navigation v-model="value">
      <v-btn v-for="item in currentMenuItems" :key="item.title" :value="item.title" :to="item.to" nuxt>
        <span>{{item.title}}</span>
        <v-icon>{{item.icon}}</v-icon>
      </v-btn>
    </v-bottom-navigation>
		<nuxt-child/>
  </div>
</template>

<script>
  import {itemPermissions, priceTablePermissions, categoryPermissions } from '~/helpers/permissions'
  export default {
    middleware: ["authenticated", "admin"],
    data: () => ({ 
      value: 'user',
      allMenuItems: [
        {"permissions": itemPermissions, "title": "Item", "icon":"mdi-cart-variant", "to": "/admin/item"},
        {"permissions": categoryPermissions, "title": "Item Category", "icon":"mdi-format-list-bulleted-type", "to": "/admin/item/item_category"},
        {"permissions": priceTablePermissions, "title": "Price table", "icon":"mdi-table-large", "to": "/admin/item/price_table"},
        /** {"permissions": orderPermissions, "title": "Orders", "icon":"mdi-clipboard-check-multiple", "to": "/client/orders"}, */
        /** {"permission": "client", "title": "Reports", "icon":"mdi-clipboard-list-outline", "to": "/reports"}, */
      ],
    }),

    computed: {
      currentMenuItems() {
        let user = this.$store.state.auth.currentUser;
        return this.allMenuItems.filter(MenuItem => {
          let addItem = false
          MenuItem.permissions.forEach(permission => {
            if (user.permissions.includes(permission)){addItem = true; return;}
          })
          return addItem
        })
      },
    },
  }
</script>
<style scoped>
</style>
