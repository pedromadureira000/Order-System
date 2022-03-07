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
  import {admin, adminAgent, agent} from '~/helpers/permissions'
  /** let usersSubMenuPermissions = adminAgent.concat(admin).concat(agent) */
  export default {
    middleware: ["authenticated"],
    data: () => ({ 
      value: 'User',
      /** allMenuItems: [ */
        /** {"permissions": usersSubMenuPermissions, "title": "User", "icon":"mdi-account", "to": "/admin/user"}, */
        /** {"permissions": company, "title": "Company", "icon":"mdi-office-building", "to": "/admin/user/company"}, */
      /** ], */
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
