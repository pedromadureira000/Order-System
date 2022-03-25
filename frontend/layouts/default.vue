<template>
  <v-app>
		<v-navigation-drawer v-model="drawer" app> 
      <!-- Test Button -->
      <v-card class="pa-3" color="blue-grey darken-4" tile>
        <nuxt-link :to="switchLocalePath('en')">English</nuxt-link>
        <nuxt-link :to="switchLocalePath('pt-BR')">Português</nuxt-link>
        <nuxt-link :to="localePath('admin-organization-company')">TEST</nuxt-link>
        <v-btn label="testF" @click="testF"/>
      </v-card>
      <!-- MenuItems composition -->
      <v-list nav dense>
        <v-list-item
          v-for="item in currentMenuItems"
          :key="item.to"
          :to="localePath(item.to)"
          link
        >
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>{{ $t(item.title) }}</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
    <!-- App bar -->
    <v-app-bar color="blue-grey darken-4" dark app>
      <v-app-bar-nav-icon
        @click="drawer = !drawer"
      ></v-app-bar-nav-icon>

      <v-toolbar-title>{{$t('Order_System')}}</v-toolbar-title>

      <v-spacer></v-spacer>
      <h5 v-if="logged_user">{{logged_user.first_name}} - {{logged_user.contracting_code}}</h5>

			<v-btn 
				v-if="!logged_user"
				text
				dark
				ripple
				class="ma-0 ml-5"
				depressed
				@click="open_login_dialog($event)"
			>Login</v-btn>

			<v-menu v-else offset-y>
				<template v-slot:activator="{ on }">
					<v-btn icon v-on="on" class="ma-0 ml-5">
						<v-avatar size="45px">
							<img src="~assets/images/default_user.jpg">
						</v-avatar>
					</v-btn>
				</template>
				<v-card class="no-padding">
					<v-list two-line>
						<v-list-item>
							<v-list-item-avatar>
								<v-avatar>
									<img src="~assets/images/default_user.jpg">
								</v-avatar>
							</v-list-item-avatar>
							<v-list-item-content>
								<v-list-item-title>{{logged_user.first_name}} {{logged_user.last_name}}</v-list-item-title>
								<v-list-item-subtitle>{{logged_user.email}}</v-list-item-subtitle>
							</v-list-item-content>
						</v-list-item>
					</v-list>

					<v-divider />
					
					<v-list>
            <v-list-item :to="localePath('myaccount')">
              <v-list-item-title>{{$t('My_Account')}}</v-list-item-title>
            </v-list-item>
            <v-list-item @click="logout">
              <v-list-item-title>{{$t('Logout')}}</v-list-item-title>
            </v-list-item>
					</v-list>
				</v-card>
			</v-menu>
    </v-app-bar>

    <v-main>
      <nuxt/>
    </v-main>

    <login-dialog ref="login_dialog"/>

    <session-error-dialog/>

    <problem-connecting-error-dialog/>

    <!-- Alert -->
    <div>
        <!-- dismissible -->
      <v-alert
        :value="$store.state.alert.showAlert"
        :type='$store.state.alert.alertType' 
        style="width: 50%;" 
        class="alert_message" 
      >
        <!-- ## dismissible get the same error as my custom v-btn ## -->
        <v-btn 
          @focus.prevent.self="$store.dispatch('removeAlert')"
          @click.prevent.self="" 
        >Close</v-btn>

        <!-- <v-btn  -->
          <!-- @focus.prevent.self="wtf" -->
          <!-- @click.prevent.self="wtf"  -->
        <!-- >Close</v-btn>  -->
        {{$store.state.alert.alertMessage}}
      </v-alert>
    </div>
		<le-footer/>
  </v-app>
</template>

<script>
import footer from '~/components/Footer.vue';
import loginDialog from '~/components/login-dialog.vue'
import sessionErrorDialog from '~/components/session-error-dialog.vue'
import problemConnectingErrorDialog from '~/components/problem-connecting-dialog.vue'
import {CRUDerpUserPermissions, CRUDadminAgentPermissions, CRUDagentPermissions, CRUDclientUserPermissions, CRUDcontractingPermissions, CRUDcompanyPermissions, CRUDestablishmentPermissions, CRUDclientTablePermissions, CRUDclientPermissions,CRUDitemTablePerms,CRUDitemPerms, CRUDitemCategoryPerms, CRUDpriceTablePerms, client_user} from '~/helpers/permissions'

let usersMenuPermissions = CRUDerpUserPermissions.concat(CRUDadminAgentPermissions, CRUDagentPermissions, CRUDclientUserPermissions)
let organizationPermissions = CRUDcontractingPermissions.concat(CRUDcompanyPermissions, CRUDestablishmentPermissions, CRUDclientTablePermissions, CRUDclientPermissions)
let itemsMenuPermissions = CRUDitemTablePerms.concat(CRUDitemPerms, CRUDitemCategoryPerms, CRUDpriceTablePerms)
let orderPermissions = client_user

/** import {handleError} from '~/helpers/functions' //TODO REmove it  */
/** import axios from '~/plugins/axios' */

export default {
	name: "default",
	middleware: ['fwdcookies', 'check_auth'],
  components: {
    loginDialog,
		sessionErrorDialog,
    problemConnectingErrorDialog,
    leFooter: footer
  },

  data() {
    return {
      drawer: null,
      defaultMenuItems: [
        { title: "Home", icon: "mdi-home", to: "index" },
        { title: "About", icon: "mdi-help-box", to: "about" },
      ],
      allMenuItems: [
        {permissions: organizationPermissions, title: "Organizations", icon: "mdi-clipboard-check-multiple", to: "admin-organization"},
        {permissions: usersMenuPermissions , title: "Users", icon: "mdi-account-group", to: "admin-user"},
        {permissions: itemsMenuPermissions, title: "Items", icon: "mdi-cart-variant", to: "admin-item"},
        {permissions: orderPermissions, title: "Orders", icon: "mdi-clipboard-check-multiple", to: "client-order"},
      ],
    }
  },
  methods: {
    /** TODO Remember who it works */
    open_login_dialog(evt) {
      this.$refs.login_dialog.open()
      evt.stopPropagation()
    },
    logout() {
			this.$store.dispatch('user/logout')
    },

    /** wtf(event){ */
      /** event.stopPropagation() */
      /** console.log(">>>>>>>JESUS!!!!!!: ", event) */
    /** }, */

    async testF(){
      /** this.$store.dispatch("setAlert", {message: "User deleted", alertType: "success"}, { root: true }) */
      this.$store.dispatch("setAlert", {message: "errorrr", alertType: "error"}, { root: true })

      /** this.$store.dispatch("switchConnectionError") */

        /** return await axios({  */
        /** method: "post", */
        /** data: { */
          /** "client_table": "123&11", */
          /** "client_code": "689", */
          /** "vendor_code": "string", */
          /** "name": "string", */
          /** "cnpj": "40.229.893/0001-66", */
          /** "status": 1, */
          /** "note": "string" */
        /** }, */
        /** url: `/api/organization/client`, */
          /** }).then((response) => { */
              /** console.log(">>>>>>> It worked", response) */
          /** }).catch(error => { */
            /** console.log(">>>>>>> ***********************", error.message) */
            /** handleError(error, this.$store.commit, this.$store.dispatch, this.$i18n, 'Error on the test' ) */
          /** }) */
    },
  },

  computed: {
		logged_user(){
			return this.$store.state.user.currentUser
		},
    /** Calculates which Menus the CurrentUser has access and return it concatenated with defaultMenuItems (between Home and About page). */
		currentMenuItems() {
			let user = this.$store.state.user.currentUser;
			if (user) {
        console.log(">>>>>>> ", user)
				return this.defaultMenuItems
					.slice(0, 1)
          .concat(this.allMenuItems.filter(MenuItem => {
            return MenuItem.permissions.some(permission => {
              return this.$store.state.user.currentUser.permissions.includes(permission)
            })
          }))
					.concat(this.defaultMenuItems.slice(1, 2));
			} else {
				return this.defaultMenuItems;
			}
		},
  },
  /** mounted() { */
    /** console.log('>>>>>>>>>>>>>>>>>>', this.localeRoute('/about')) */
    /** console.log('>>>>>>>>>>>>>>>>>>', this.getRouteBaseName('')) */
  /** } */

};
</script>

<style scoped>
.alert_message{
	position: fixed;
	left: 50%;
	top: 93%;
	transform: translate(-50%, -50%);
	z-index: 999;
}
.v-application .pa-3 {
	padding: 14px !important;
}
</style>
