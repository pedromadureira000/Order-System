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
  import {CRUDerpUserPermissions, CRUDadminAgentPermissions, CRUDagentPermissions, CRUDclientUserPermissions} from '~/helpers/permissions'
  export default {
    middleware: ["authenticated"],
    data(){ 
      return {
        value: '',
        allMenuItems: [
          /** {permissions: CRUDerpUserPermissions, title: "ERP_User", icon: "mdi-account", to: "admin-user-erp_user"}, */
          /** {permissions: CRUDadminAgentPermissions, title: "Admin_Agent", icon: "mdi-account", to: "admin-user-admin_agent"}, */
          {permissions: CRUDagentPermissions, title: "Agent", icon: "mdi-account", to: "admin-user-agent"},
          {permissions: CRUDclientUserPermissions, title: "Client_User", icon: "mdi-account", to: "admin-user-client_user"},
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
