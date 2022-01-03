import Vue from 'vue'
import Router from 'vue-router'
import { normalizeURL, decode } from 'ufo'
import { interopDefault } from './utils'
import scrollBehavior from './router.scrollBehavior.js'

const _4937e6c1 = () => interopDefault(import('../pages/About.vue' /* webpackChunkName: "pages/About" */))
const _cb41d4fa = () => interopDefault(import('../pages/Admin.vue' /* webpackChunkName: "pages/Admin" */))
const _08779492 = () => interopDefault(import('../pages/Admin/item/index.vue' /* webpackChunkName: "pages/Admin/item/index" */))
const _565bcda1 = () => interopDefault(import('../pages/Admin/item_category/index.vue' /* webpackChunkName: "pages/Admin/item_category/index" */))
const _212b6fcf = () => interopDefault(import('../pages/Admin/price_table/index.vue' /* webpackChunkName: "pages/Admin/price_table/index" */))
const _ce5d016c = () => interopDefault(import('../pages/Admin/user/index.vue' /* webpackChunkName: "pages/Admin/user/index" */))
const _6653e572 = () => interopDefault(import('../pages/Client.vue' /* webpackChunkName: "pages/Client" */))
const _55f3dafd = () => interopDefault(import('../pages/Client/Orders.vue' /* webpackChunkName: "pages/Client/Orders" */))
const _3d7d6fc0 = () => interopDefault(import('../pages/Client/Orders/index.vue' /* webpackChunkName: "pages/Client/Orders/index" */))
const _503cbed8 = () => interopDefault(import('../pages/Client/Orders/_order/index.vue' /* webpackChunkName: "pages/Client/Orders/_order/index" */))
const _5e95fe35 = () => interopDefault(import('../pages/Myaccount.vue' /* webpackChunkName: "pages/Myaccount" */))
const _f45f11b0 = () => interopDefault(import('../pages/PasswordReset.vue' /* webpackChunkName: "pages/PasswordReset" */))
const _6581561a = () => interopDefault(import('../pages/Reports.vue' /* webpackChunkName: "pages/Reports" */))
const _8b86d558 = () => interopDefault(import('../pages/password/reset/confirm/_uid/_token/index.vue' /* webpackChunkName: "pages/password/reset/confirm/_uid/_token/index" */))
const _1d04bcb4 = () => interopDefault(import('../pages/index.vue' /* webpackChunkName: "pages/index" */))

const emptyFn = () => {}

Vue.use(Router)

export const routerOptions = {
  mode: 'history',
  base: '/',
  linkActiveClass: 'nuxt-link-active',
  linkExactActiveClass: 'nuxt-link-exact-active',
  scrollBehavior,

  routes: [{
    path: "/About",
    component: _4937e6c1,
    name: "About"
  }, {
    path: "/Admin",
    component: _cb41d4fa,
    name: "Admin",
    children: [{
      path: "item",
      component: _08779492,
      name: "Admin-item"
    }, {
      path: "item_category",
      component: _565bcda1,
      name: "Admin-item_category"
    }, {
      path: "price_table",
      component: _212b6fcf,
      name: "Admin-price_table"
    }, {
      path: "user",
      component: _ce5d016c,
      name: "Admin-user"
    }]
  }, {
    path: "/Client",
    component: _6653e572,
    name: "Client",
    children: [{
      path: "Orders",
      component: _55f3dafd,
      children: [{
        path: "",
        component: _3d7d6fc0,
        name: "Client-Orders"
      }, {
        path: ":order",
        component: _503cbed8,
        name: "Client-Orders-order"
      }]
    }]
  }, {
    path: "/Myaccount",
    component: _5e95fe35,
    name: "Myaccount"
  }, {
    path: "/PasswordReset",
    component: _f45f11b0,
    name: "PasswordReset"
  }, {
    path: "/Reports",
    component: _6581561a,
    name: "Reports"
  }, {
    path: "/password/reset/confirm/:uid?/:token",
    component: _8b86d558,
    name: "password-reset-confirm-uid-token"
  }, {
    path: "/",
    component: _1d04bcb4,
    name: "index"
  }],

  fallback: false
}

export function createRouter (ssrContext, config) {
  const base = (config._app && config._app.basePath) || routerOptions.base
  const router = new Router({ ...routerOptions, base  })

  // TODO: remove in Nuxt 3
  const originalPush = router.push
  router.push = function push (location, onComplete = emptyFn, onAbort) {
    return originalPush.call(this, location, onComplete, onAbort)
  }

  const resolve = router.resolve.bind(router)
  router.resolve = (to, current, append) => {
    if (typeof to === 'string') {
      to = normalizeURL(to)
    }
    return resolve(to, current, append)
  }

  return router
}
