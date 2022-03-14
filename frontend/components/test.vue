<template>
  <div>
    <!-- MyComponent -->
  <v-text-field
    label="test!"
    @blur="$emit('some-event')"
    class="mb-3"
  />

  </div>
</template>

<script>
export default {
  data() {
    return {
       
    }
  },
  methods: {
      	
    }
}
</script>

<style>

</style>
