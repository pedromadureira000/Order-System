<template>
  <div>
    <v-menu
      bottom
      left
     >
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          icon
          v-bind="attrs"
          v-on="on"
        >
          <v-icon>mdi-dots-vertical</v-icon>
        </v-btn>
      </template>

      <v-list>
        <v-list-item
          v-for="(item, index) in menu_items"
          :key="index"
          @click="handleClick(index)"
        >
          <v-list-item-icon>
            <v-icon v-text="item.icon"></v-icon>
          </v-list-item-icon>
          <v-list-item-content>
              <v-list-item-title v-text="item.title"></v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-menu>

    <v-dialog v-model="show_edit_dialog" max-width="500px">
      <v-card>
        <v-card-title>Edit</v-card-title>
        <v-card-text>
          <v-container fluid>
            <v-text-field
              v-model="pricetable.name"
              label="Name"
              required
              type="text"
            ></v-text-field>
            <v-text-field
              v-model="pricetable.description"
              label="Description"
              required
              type="text"
            ></v-text-field>
          </v-container>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-title>Remove Items</v-card-title>
        <v-card-text>
          <v-container fluid>
            <v-text-field
              v-for="(price_item, key) in pricetable.price_items"
              :key="key"
              v-model="price_item.price_unit"
              :label="itemName(price_item.item)"
              type="number"
            >
              <template v-slot:append>
                <v-icon @click="removeItem(price_item)">
                  mdi-minus
                </v-icon >
              </template>
            </v-text-field>
          </v-container>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-title>Add Items</v-card-title>
        <v-card-text>
          <v-container fluid>
              <!-- @input="item.price_unit = $event" -->
            <v-text-field
              v-for="(item, key) in itemsToAdd"
              :key="key"
              v-model="item.price_unit"
              :label="item.name"
		          @keyup.enter="addItem(item)"
              type="number"
            >
              <template v-slot:append>
                <v-icon @click="addItem(item)" :disabled="item.price_unit == null">
                  mdi-plus
                </v-icon >
              </template>
            </v-text-field>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn class="blue--text darken-1" text @click="show_edit_dialog = false">Cancel</v-btn>
          <v-btn class="blue--text darken-1" text @click="updatePriceTable()" :loading="loading" :disabled="loading">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
		props: ['pricetable', 'items'],
    data(){
      return {
        show_edit_dialog: false,
        loading: false,
        menu_items: [
          { 
            title: 'Edit',
            icon: 'mdi-pencil',
            async click(){
              this.show_edit_dialog = true
            }
          },
          { 
            title: 'Delete',
            icon: 'mdi-delete',
            async click(){
              let data = await this.$store.dispatch(
                'item/deletePriceTable', 
                {table_code: this.pricetable.table_code}
              )
              if (data === "ok"){
                this.$emit('pricetable-deleted')
              }
            }
          },
        ]
      }
    },
    methods: {
      handleClick(index){
        //this.menu_items[item_code].click()  #will get erros, because of function click will no can access propertie with it's own 'this'
        this.menu_items[index].click.call(this) // will call the function but the function will use the vue instance 'this' context.
      },
      removeItem(item){
        this.pricetable.price_items = this.pricetable.price_items.filter((obj)=> obj !== item)
      },
      addItem(item){
        this.pricetable.price_items = this.pricetable.price_items.concat([{item: item.item_code, price_unit: item.price_unit}])
        item.price_unit = null
      },
      itemName(item_code){
        let item = this.items.filter((item)=> item.item_code === item_code)[0]
        return item.name
      },
      updatePriceTable(){
        this.$store.dispatch("item/updatePriceTable", this.pricetable)
      }
  },

  computed:{
    itemsToAdd(){
      return this.items.filter((item)=> {
        let return_value = true
        let price_items = this.pricetable.price_items
        for (const prop in price_items){
          if (price_items[prop].item === item.item_code){
            return_value = false
          }
        }
        return return_value
      })

    }
  },
}
</script>
