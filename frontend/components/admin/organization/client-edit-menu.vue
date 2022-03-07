<template>
  <p v-if="$fetchState.pending">Fetching data ...</p>
  <p v-else-if="$fetchState.error">An error occurred :(</p>
  <div v-else>
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
                label="Company"
                v-model="company.name"
                disabled
              />
              <v-text-field
                label="Price Table"
                v-model="company.price_table"
                disabled
              />
            </v-container>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-title>Assign Price Table</v-card-title>
          <v-card-text>
            <v-container fluid>
              <v-radio-group v-model="companyPriceTable" style="width: 25%;">
                <v-radio
                  v-for="(pricetable, key) in pricetables"
                  :key="key"
                  :label="pricetable.name"
                  :value="pricetable.table_code"
                ></v-radio>
                <v-radio
                  label="None"
                  value="None"
                ></v-radio>
              </v-radio-group>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn class="blue--text darken-1" text @click="show_edit_dialog = false">Cancel</v-btn>
            <v-btn class="blue--text darken-1" text @click="updateCompany()">Save</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </div>
</template>

<script>
export default {
		props: ['company'],
    data: () => ({
      show_edit_dialog: false,
      pricetables: [],
      companyPriceTable: 'None',
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
              'organization/deleteCompany', 
              {company_code: this.company.company_code}
            )
						if (data === "ok"){
							this.$emit('company-deleted')
						}
          }
        },
      ]
    }),
  async fetch(){
    let pricetables = await this.$store.dispatch("item/fetchPriceTables");
    for ( let key in pricetables){ 
      this.pricetables.push(pricetables[key])
    }
  },

    methods: {
      handleClick(index){
        //this.menu_items[id].click()  #will get erros, because of function click will no can access propertie with it's own 'this'
        this.menu_items[index].click.call(this) // will call the function but the function will use the vue instance 'this' context.
      },
      async updateCompany(){
        let data = await this.$store.dispatch("organization/updateCompany", {
          company_code: this.company.company_code,
          price_table: this.companyPriceTable
        })
        /** console.log(">>>>>>> ", data) */
        if (data){    //just reactivity
          if (this.companyPriceTable === 'None'){  
            this.company.price_table = null
          }else{
            this.company.price_table = this.companyPriceTable
          }
        }
      }
  },

  mounted() {
    if (this.company.price_table){
      this.companyPriceTable = this.company.price_table
    }

  }
}
</script>
