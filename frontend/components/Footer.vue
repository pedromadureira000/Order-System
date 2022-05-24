<template>
  <v-footer color="blue-grey darken-4" class="white--text">
		<div class="col">
			<address>
          {{$config.phone_number}}
					<br/>
          <a :href="'mailto:' + $config.email" class="white--text">{{$config.email}}</a>
			</address>
		</div>
		<v-spacer />
      <div v-if="$config.company_name">
        <span>{{$config.company_name}}</span>
        <span>- {{date.getFullYear()}}</span><br/>
      </div>
  </v-footer>
</template>

<script>
export default {
	data() {
		return {
			date: new Date,
		}
	},
}
</script>
<style scoped>
.v-footer {
  z-index: 7;
} 
</style>
