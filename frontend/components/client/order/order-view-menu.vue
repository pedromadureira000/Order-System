<template>
  <div>
    <dots-menu :menu_items="menu_items" :handleClick="handleClick"/>
    <order-details 
      :order="order" 
      :show_view_details_dialog="show_view_details_dialog"
      :order_details_fetched="order_details_fetched"
      @close-details-dialog="show_view_details_dialog = false"
    />
    <edit-order 
      :order="order" 
      :show_edit_dialog="show_edit_dialog"
      :order_details_fetched="order_details_fetched"
      @close-edit-dialog="show_edit_dialog = false"
    />
  </div>
</template>

<script>
export default {
  components: {
    "dots-menu": require("@/components/dots-menu.vue").default,
    "order-details": require("@/components/client/order/order-details.vue").default,
    "edit-order": require("@/components/client/order/edit-order.vue").default,
  },
  props: ['order'],
  data() {
    return {
      show_edit_dialog: false,
      show_view_details_dialog: false,
      order_details_fetched: false,
      loading: false,
      menu_items: [
      ...(this.hasEditOrderPermission() && this.ifUserIsClientUserHeCanEdit ? [{ 
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
      ]
    }
  },

    methods: {
      handleClick(index){
        //this.menu_items[id].click()  #will get errors because the function click will not access properties with its own 'this'
        this.menu_items[index].click.call(this) // will call the function but the function will use the vue instance 'this' context.
      },

      ifUserIsClientUserHeCanEdit(){
        if (this.currentUserIsClientUser){
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

      // Fetch Order details
      async fetchOrderDetails(){
        let order_details = await this.$store.dispatch("order/fetchOrderDetails", {client: this.order.client,
          establishment: this.order.establishment, order_number: this.order.order_number});
        if (order_details){
          // Add details to the order
          this.order.company= order_details.company
          this.order.establishment = order_details.establishment
          this.order.client = order_details.client
          this.order.client_user = order_details.client_user
          this.order.client_table = order_details.client_table
          this.order.price_table = order_details.price_table
          this.order.ordered_items = order_details.ordered_items
          // Show order after details are fetched
          this.order_details_fetched = true
        }
      },

      // Search Price Items
      async searchPriceItemsToMakeOrder(){
        let filter_parameters = {establishment: this.establishment.establishment_compound_id, category: this.filter__category.category_compound_id, 
          item_description: this.filter__item_description}
        let search_results = await this.$store.dispatch("order/searchPriceItemsToMakeOrder", filter_parameters);
        if (search_results){
          if (!this.item_compound_id_prefix){
            // TODO when i change the establishment it can change the item_table (clear this field in this case)
            let first_item = search_results[0]
            console.log(">>>>>>> first_item: ", first_item)
            if (first_item){
              this.item_compound_id_prefix = first_item.item.split('*')[0] + '*' + first_item.item.split('*')[1] + '*'
            }
          }
          this.search_results = search_results
        }
      },
    },

  computed: {
    currentUserIsClientUser(){
      return this.$store.state.user.currentUser.roles.includes('client_user')
    }
  },

  watch: {
    show_edit_dialog(newValue){
      if ( newValue === true){
        if (!this.order.ordered_items){
          this.fetchOrderDetails()
        }
      }	
    },
    show_view_details_dialog(newValue){
      if ( newValue === true){
        if (!this.order.ordered_items){
          this.fetchOrderDetails()
        }
      }	
    }
  }
}
</script>
