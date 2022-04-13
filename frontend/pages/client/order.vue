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
  let viewOrders = ['update_order_items', 'get_orders', 'update_order_status']
  export default {
    middleware: ["authenticated"],
    data(){
      return {
        value: 'User',
        allMenuItems: [
          {"permissions": ['create_order'], "title": "Create Order", "icon":"mdi-account", "to": "/client/order/create_order"},
          /** {"permissions": viewOrders, "title": "View Orders", "icon":"mdi-office-building", "to": "/client/order/view_orders"}, */
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
