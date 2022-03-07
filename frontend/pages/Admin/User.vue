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
  import {CRUDerpUserPermissions, CRUDadminAgentPermissions, CRUDagentPermissions, CRUDclientUserPermissions} from '~/helpers/permissions'
  export default {
    middleware: ["authenticated"],
    data: () => ({ 
      value: '',
      allMenuItems: [
        {permissions: CRUDerpUserPermissions, title: "ERP User", icon: "mdi-account", to: "/admin/user/erp_user"},
        {permissions: CRUDadminAgentPermissions, title: "Admin Agent", icon: "mdi-account", to: "/admin/user/admin_agent"},
        {permissions: CRUDagentPermissions, title: "Agent", icon: "mdi-account", to: "/admin/user/agent"},
        {permissions: CRUDclientUserPermissions, title: "Client User", icon: "mdi-account", to: "/admin/user/client_user"},
      ],
    }),

    computed: {
      currentMenuItems() {
        let user = this.$store.state.auth.currentUser;
        return this.allMenuItems.filter(MenuItem => {
          return MenuItem.permissions.some(permission => user.permissions.includes(permission))
        })
      },
    },
  }
</script>
<style scoped>
</style>
