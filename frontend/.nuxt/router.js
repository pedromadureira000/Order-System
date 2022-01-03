import Vue from 'vue'
import Router from 'vue-router'
import { normalizeURL, decode } from 'ufo'
import { interopDefault } from './utils'
import scrollBehavior from './router.scrollBehavior.js'

const _4937e6c1 = () => interopDefault(import('../pages/About.vue' /* webpackChunkName: "pages/About" */))
const _cb41d4fa = () => interopDefault(import('../pages/Admin.vue' /* webpackChunkName: "pages/Admin" */))
const _1f982dc6 = () => interopDefault(import('../pages/Admin/index.vue' /* webpackChunkName: "pages/Admin/index" */))
const _ce5d016c = () => interopDefault(import('../pages/Admin/user/index.vue' /* webpackChunkName: "pages/Admin/user/index" */))
const _5e95fe35 = () => interopDefault(import('../pages/Myaccount.vue' /* webpackChunkName: "pages/Myaccount" */))
const _8d7d413e = () => interopDefault(import('../pages/Orders.vue' /* webpackChunkName: "pages/Orders" */))
const _d8f1cdb8 = () => interopDefault(import('../pages/Orders/index.vue' /* webpackChunkName: "pages/Orders/index" */))
const _df6542a0 = () => interopDefault(import('../pages/Orders/_order/index.vue' /* webpackChunkName: "pages/Orders/_order/index" */))
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
    children: [{
      path: "",
      component: _1f982dc6,
      name: "Admin"
    }, {
      path: "user",
      component: _ce5d016c,
      name: "Admin-user"
    }]
  }, {
    path: "/Myaccount",
    component: _5e95fe35,
    name: "Myaccount"
  }, {
    path: "/Orders",
    component: _8d7d413e,
    children: [{
      path: "",
      component: _d8f1cdb8,
      name: "Orders"
    }, {
      path: ":order",
      component: _df6542a0,
      name: "Orders-order"
    }]
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
