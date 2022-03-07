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
  import {CRUDcontractingPermissions, CRUDcompanyPermissions, CRUDestablishmentPermissions, CRUDclientTablePermissions, CRUDclientPermissions} from '~/helpers/permissions'
  export default {
    middleware: ["authenticated"],
    data: () => ({ 
      // this will choose which will be the initial MenuItem.
      value: '',
      allMenuItems: [
        {permissions: CRUDcontractingPermissions, title: "Contracting", icon: "mdi-office-building", to: "/admin/organization/contracting"},
        {permissions: CRUDcompanyPermissions, title: "Company", icon: "mdi-office-building", to: "/admin/organization/company"},
        {permissions: CRUDestablishmentPermissions, title: "Establishment", icon: "mdi-office-building", to: "/admin/organization/establishment"},
        {permissions: CRUDclientTablePermissions, title: "Client Table", icon: "mdi-office-building", to: "/admin/organization/client_table"},
        {permissions: CRUDclientPermissions, title: "Client", icon: "mdi-office-building", to: "/admin/organization/client"},
      ],
    }),

    computed: {
      currentMenuItems() {
        let user = this.$store.state.user.currentUser;
        return this.allMenuItems.filter(MenuItem => {
          return MenuItem.permissions.some( permission => user.permissions.includes(permission))
        })
      },
    },
  }
</script>
<style scoped>
</style>
