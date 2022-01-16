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
              label="Username"
              v-model="user.username"
              disabled
            />
          </v-container>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-title>Assign Price Table</v-card-title>
        <v-card-text>
          <v-container fluid>
            <!-- <v-text-field -->
              <!-- v-for="(price_table, key) in pricetables" -->
              <!-- :key="key" -->
              <!-- v-model="price_table.price_unit" -->
              <!-- :label="itemName(price_table.item)" -->
              <!-- type="number" -->
            <!-- > -->
              <!-- <template v-slot:append> -->
                <!-- <v-icon @click="removeItem(price_table)"> -->
                  <!-- mdi-minus -->
                <!-- </v-icon > -->
              <!-- </template> -->
            <!-- </v-text-field> -->
          </v-container>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-title>Add Items</v-card-title>
        <v-card-text>
          <v-container fluid>
              <!-- @input="item.price_unit = $event" -->
            <!-- <v-text-field -->
              <!-- v-for="(item, key) in itemsToAdd" -->
              <!-- :key="key" -->
              <!-- v-model="item.price_unit" -->
              <!-- :label="item.name" -->
							<!-- @keyup.enter="addItem(item)" -->
              <!-- type="number" -->
            <!-- > -->
              <!-- <template v-slot:append> -->
                <!-- <v-icon @click="addItem(item)" :disabled="item.price_unit == null"> -->
                  <!-- mdi-plus -->
                <!-- </v-icon > -->
              <!-- </template> -->
            <!-- </v-text-field> -->
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn class="blue--text darken-1" text @click="show_edit_dialog = false">Cancel</v-btn>
          <v-btn class="blue--text darken-1" text @click="updateUser()" >Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
export default {
		props: ['user'],
    data: () => ({
      show_edit_dialog: false,
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
              'auth/deleteUserByAdmin', 
              {username: this.user.username, company_code: this.user.company_code}
            )
						if (data === "ok"){
							this.$emit('user-deleted')
						}
          }
        },
      ]
    }),
    methods: {
      handleClick(index){
        //this.menu_items[id].click()  #will get erros, because of function click will no can access propertie with it's own 'this'
        this.menu_items[index].click.call(this) // will call the function but the function will use the vue instance 'this' context.
      },
      updateUser(){
        this.$store.dispatch("orders/updateUser", this.user)
      }
  },
}
</script>
