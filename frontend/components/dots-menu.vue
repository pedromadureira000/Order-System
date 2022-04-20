<template>
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
</template>
<script>
export default {
  props: ['menu_items', 'handleClick'],
  /** mounted() { */
  /** } */
}

</script>
<style scoped>
.v-list-item {
  height: 0px;
}
</style>
