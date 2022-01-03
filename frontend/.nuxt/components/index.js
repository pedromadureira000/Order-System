export { default as Footer } from '../../components/Footer.vue'
export { default as Welcome } from '../../components/Welcome.vue'
export { default as LoginDialog } from '../../components/login-dialog.vue'
export { default as SessionErrorDialog } from '../../components/session-error-dialog.vue'
export { default as AdminUserEditMenu } from '../../components/admin/user-edit-menu.vue'

// nuxt/nuxt.js#8607
function wrapFunctional(options) {
  if (!options || !options.functional) {
    return options
  }

  const propKeys = Array.isArray(options.props) ? options.props : Object.keys(options.props || {})

  return {
    render(h) {
      const attrs = {}
      const props = {}

      for (const key in this.$attrs) {
        if (propKeys.includes(key)) {
          props[key] = this.$attrs[key]
        } else {
          attrs[key] = this.$attrs[key]
        }
      }

      return h(options, {
        on: this.$listeners,
        attrs,
        props,
        scopedSlots: this.$scopedSlots,
      }, this.$slots.default)
    }
  }
}
