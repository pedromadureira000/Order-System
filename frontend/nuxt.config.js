import colors from 'vuetify/es5/util/colors'
import {messages} from './messages'

const _isdev = process.env.DEV
const _apimock = process.env.API_MOCK 
const _apijs = _apimock ? 'apimock' : 'api'
// import pt from 'vuetify/es5/locale/pt'

export default {

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    titleTemplate: '%s - frontend',
    title: 'frontend',
    htmlAttrs: {
      lang: 'en'
    },
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' },
      { name: 'format-detection', content: 'telephone=no' }
    ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.jpg' }
    ]
  },

  loading: { color: '#fff' },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [
  ],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [
		// {src: '@/plugins/axios', ssr: false},
		// '@/plugins/axios',
    // '~/plugins/axios.js
		'@/plugins/vuetify',
		'~/plugins/formatStr',
  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    // https://go.nuxtjs.dev/typescript
    '@nuxt/typescript-build',
    // https://go.nuxtjs.dev/vuetify
    '@nuxtjs/vuetify',
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    '@nuxtjs/i18n',
    '@nuxtjs/proxy',
    // TODO Is it working?
  ],

  i18n: {
    locales: ['en', 'pt-BR'],
    strategy: 'prefix_except_default',
    defaultLocale: 'pt-BR',
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'lang',
      redirectOn: 'root',  // recommended
    },
    parsePages: false,   // Disable babel parsing. To use custom pages
    // If a custom path is missing for one of the locales, the defaultLocale custom path is used, if set.
    pages: {
      about: {
        en: '/about-us',
        'pt-BR': '/sobre-nos',
      },
      myaccount: {
        en: '/my-account',
        'pt-BR': '/minha-conta',
      },
      // Organization
      'admin/organization': {
        en: '/admin/organization',
        'pt-BR': '/admin/organizacao',
      },
      'admin/organization/contracting': {
        en: '/admin/organization/contracting',
        'pt-BR': '/admin/organizacao/contratante',
      },
      'admin/organization/company': {
        en: '/admin/organization/company',
        'pt-BR': '/admin/organizacao/empresa',
      },
      'admin/organization/establishment': {
        en: '/admin/organization/establishment',
        'pt-BR': '/admin/organizacao/estabelecimento',
      },
      'admin/organization/client_table': {
        en: '/admin/organization/client_table',
        'pt-BR': '/admin/organizacao/tabela_de_clientes',
      },
      'admin/organization/client': {
        en: '/admin/organization/client',
        'pt-BR': '/admin/organizacao/cliente',
      },
      // User
      'admin/user': {
        en: '/admin/user',
        'pt-BR': '/admin/usuario',
      },
      // 'admin/user/erp_user': {
        // en: '/admin/user/erp_user',
        // 'pt-BR': '/admin/usuario/usuario_erp',
      // },
      // 'admin/user/admin_agent': {
        // en: '/admin/user/admin_agent',
        // 'pt-BR': '/admin/usuario/agente_admin',
      // },
      // 'admin/user/agent': {
        // en: '/admin/user/agent',
        // 'pt-BR': '/admin/usuario/agente',
      // },
      // 'admin/user/client_user': {
        // en: '/admin/user/client_user',
        // 'pt-BR': '/admin/usuario/usuario_cliente',
      // },
      // Item
      'admin/item': {
        en: '/admin/item',
        'pt-BR': '/admin/item'
      },
      'admin/item/item': {
        en: '/admin/item/item',
        'pt-BR': '/admin/item/item'
      },
      'admin/item/item_category': {
        en: '/admin/item/item_category',
        'pt-BR': '/admin/item/item_category'
      },
      'admin/item/price_table': {
        en: '/admin/item/price_table',
        'pt-BR': '/admin/item/price_table'
      },
      // Order
      // 'client/client/price_table': {
        // en: '/admin/item/price_table',
        // 'pt-BR': '/admin/item/price_table'
      // },
    },
    vueI18n: {
      fallbackLocale: 'pt-BR',
      messages: messages
    }
  },

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
	axios: {
		// credentials: true,
    // timeout: 1000, TODO this is not working
	},

  // Vuetify module configuration: https://go.nuxtjs.dev/config-vuetify
  vuetify: {
    customVariables: ['~/assets/variables.scss'],
    theme: {
      // dark: true,
      dark: false,
      themes: {
        dark: {
          primary: colors.blue.darken2,
          accent: colors.grey.darken3,
          secondary: colors.amber.darken3,
          info: colors.teal.lighten1,
          warning: colors.amber.base,
          error: colors.deepOrange.accent4,
          success: colors.green.accent3
        }
      }
    },
    // lang: {
      // locales: { pt },
      // current: 'pt'
    // },
  },

	// Build Configuration: https://go.nuxtjs.dev/config-build
	build: {
		//You can extend webpack config here
		// loaders: {
			// sass: {
				// implementation: require('sass'),
			// },
		// },
		extend (config, ctx) {
			const home = config.resolve.alias['~']
			config.resolve.alias['~api'] = home + '/helpers/' + _apijs
		}
	},

	proxy: _isdev && !_apimock ? {
		'/api': 'http://127.0.0.1:8000/',
	} : null,

	transpileDependencies: [
		'vuetify'
	],

	env: {
		// test: process.env.test || 'test'
	},
	
  // router: {
    // middleware: ['fwdcookies', 'auth']
  // },
}
