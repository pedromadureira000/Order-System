<template>
	<div>
		<p>Order ID: {{order_id}}</p>
	</div>
</template>

<script>
export default {
	validate({params}){
		return /^\d+$/.test(params.order) //accept only numbers
	},
	data() {
		return {
			order_id: this.$route.params.order,
		}
	},
	methods: {
		
		}
}
</script>

<style>

</style>
