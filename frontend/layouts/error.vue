<template>
  <v-app dark>
    <div class="ma-4">
      <h1 v-if="error.statusCode === 404">
        <!-- You can't start a variable with a number -->
        {{ $t('_404_Not_Found') }}
      </h1>
      <h1 v-else>
        {{ $t('An_error_occurred') }}
      </h1>
      <NuxtLink to="/">
      {{$t('Home_Page')}}
      </NuxtLink>
    </div>
  </v-app>
</template>

<script>
export default {
  layout: 'empty',
  props: {
    error: {
      type: Object,
      default: null
    }
  },
  head () {
    const title =
      this.error.statusCode === 404 ? this.$t('_404_Not_Found') : this.$t('An_error_occurred')
    return {
      title
    }
  }
}
</script>

<style scoped>
h1 {
  font-size: 20px;
}
</style>
