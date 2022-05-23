<template>
  <div>
    <dots-menu :menu_items="menu_items" :handleClick="handleClick"/>
    <order-details 
      :order="order" 
      :show_view_details_dialog="show_view_details_dialog"
      @close-details-dialog="show_view_details_dialog = false"
    />
    <edit-order 
      :order="order" 
      :show_edit_dialog="show_edit_dialog"
      @close-edit-dialog="show_edit_dialog = false"
    />
    <duplicate-order 
      :order="order" 
      :show_duplicate_order_dialog="show_duplicate_order_dialog"
      @close-duplicate-order-dialog="show_duplicate_order_dialog = false"
      @order-duplicated="$emit('order-duplicated', $event); show_duplicate_order_dialog = false"
    />
  </div>
</template>

<script>
export default {
  components: {
    "dots-menu": require("@/components/dots-menu.vue").default,
    "order-details": require("@/components/client/order/order-details.vue").default,
    "edit-order": require("@/components/client/order/edit-order.vue").default,
    "duplicate-order": require("@/components/client/order/duplicate-order.vue").default,
  },
  props: ['order'],
  data() {
    return {
      show_edit_dialog: false,
      show_view_details_dialog: false,
      show_duplicate_order_dialog: false,
      loading: false,
      menu_items: [
      ...(this.hasEditOrderPermission() && this.ifUserIsClientUserHeCanEdit() ? [{ 
          title: this.$t('Edit'),
          icon: 'mdi-pencil',
          async click(){
            this.show_edit_dialog = true
          }
        }] : [] ),
        ...(this.hasGetOrdersPermission() ? [{ 
          title: this.$t('View Details'),
          icon: 'mdi-text-box-search-outline',
          async click(){
            this.show_view_details_dialog = true
          }
        }] : []),
        ...(this.currentUserIsClientUser() ? [{ 
          title: this.$t('Duplicate Order'),
          icon: 'mdi-content-duplicate',
          async click(){
            this.show_duplicate_order_dialog = true
          }
        }] : []),
      ]
    }
  },

    methods: {
      handleClick(index){
        //this.menu_items[id].click()  #will get errors because the function click will not access properties with its own 'this'
        this.menu_items[index].click.call(this) // will call the function but the function will use the vue instance 'this' context.
      },

      ifUserIsClientUserHeCanEdit(){
        if (this.currentUserIsClientUser()){
          return this.order.status === 1
        }else{
          return true
        }
      },
      // Permission Functions
      hasEditOrderPermission(){
        let user = this.$store.state.user.currentUser;
        return user.permissions.includes("update_order_status") || user.permissions.includes("update_order_items")
      },
      hasGetOrdersPermission(){
        let user = this.$store.state.user.currentUser;
        return user.permissions.includes("get_orders")
      },
      currentUserIsClientUser(){
        return this.$store.state.user.currentUser.roles.includes('client_user')
      },
      // Fetch Order details
      async fetchOrderDetails(){
        let order_details = await this.$store.dispatch("order/fetchOrderDetails", this.order.id);
        if (order_details){
          // Add details to the order
          this.order.company= order_details.company
          this.order.establishment = order_details.establishment
          this.order.client = order_details.client
          this.order.client_user = order_details.client_user
          this.order.client_table = order_details.client_table
          this.order.price_table = order_details.price_table
          /** console.log(">>>>>>> order_details.ordered_items: ", order_details.ordered_items) */
          this.order.ordered_items = order_details.ordered_items.sort((a,b)=> a.sequence_number - b.sequence_number)
          this.order.note = order_details.note
          this.order.agent_note = order_details.agent_note
        }
      },
    },

  watch: {
    show_edit_dialog(newValue){
      if ( newValue === true){
        // Fetch details if it wasn't fetched yet
        if (!this.order.ordered_items){
          this.fetchOrderDetails()
        }
      }	
    },
    show_view_details_dialog(newValue){
      if ( newValue === true){
        // Fetch details if it wasn't fetched yet
        if (!this.order.ordered_items){
          this.fetchOrderDetails()
        }
      }	
    },
  }
}
</script>
