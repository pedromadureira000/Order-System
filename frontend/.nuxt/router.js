import Vue from 'vue'
import Router from 'vue-router'
import { normalizeURL, decode } from 'ufo'
import { interopDefault } from './utils'
import scrollBehavior from './router.scrollBehavior.js'

const _4937e6c1 = () => interopDefault(import('../pages/About.vue' /* webpackChunkName: "pages/About" */))
const _5e95fe35 = () => interopDefault(import('../pages/Myaccount.vue' /* webpackChunkName: "pages/Myaccount" */))
const _f45f11b0 = () => interopDefault(import('../pages/PasswordReset.vue' /* webpackChunkName: "pages/PasswordReset" */))
const _6581561a = () => interopDefault(import('../pages/Reports.vue' /* webpackChunkName: "pages/Reports" */))
const _3d9e2d22 = () => interopDefault(import('../pages/Admin/Item.vue' /* webpackChunkName: "pages/Admin/Item" */))
const _66833e9c = () => interopDefault(import('../pages/Admin/Item/index.vue' /* webpackChunkName: "pages/Admin/Item/index" */))
const _48ccfc8a = () => interopDefault(import('../pages/Admin/Item/item_category.vue' /* webpackChunkName: "pages/Admin/Item/item_category" */))
const _08622438 = () => interopDefault(import('../pages/Admin/Item/price_table.vue' /* webpackChunkName: "pages/Admin/Item/price_table" */))
const _5d184b6a = () => interopDefault(import('../pages/Admin/User/index.vue' /* webpackChunkName: "pages/Admin/User/index" */))
const _55f3dafd = () => interopDefault(import('../pages/Client/Orders.vue' /* webpackChunkName: "pages/Client/Orders" */))
const _3d7d6fc0 = () => interopDefault(import('../pages/Client/Orders/index.vue' /* webpackChunkName: "pages/Client/Orders/index" */))
const _503cbed8 = () => interopDefault(import('../pages/Client/Orders/_order/index.vue' /* webpackChunkName: "pages/Client/Orders/_order/index" */))
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
    path: "/Admin/Item",
    component: _3d9e2d22,
    children: [{
      path: "",
      component: _66833e9c,
      name: "Admin-Item"
    }, {
      path: "item_category",
      component: _48ccfc8a,
      name: "Admin-Item-item_category"
    }, {
      path: "price_table",
      component: _08622438,
      name: "Admin-Item-price_table"
    }]
  }, {
    path: "/Admin/User",
    component: _5d184b6a,
    name: "Admin-User"
  }, {
    path: "/Client/Orders",
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
