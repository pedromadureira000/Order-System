<template>
    <v-dialog :retain-focus="false" :value="show_delete_confirmation_dialog" max-width="30%" persistent>
      <v-card>
        <v-card-title>{{$t('Are_you_sure_you_want_to_delete')}}</v-card-title>
        <v-card-text>
          <v-card-actions class="d-flex justify-space-around" style="width:100%;">
            <v-btn class="black--text darken-1" text @click="$emit('cancel')">{{$t('Cancel')}}</v-btn>
            <v-btn class="red--text darken-1" text @click="$emit('delete-item')">{{$t('Delete')}}</v-btn>
          </v-card-actions>
        </v-card-text>
      </v-card>
    </v-dialog>
</template>

<script>
export default {
  props: ['show_delete_confirmation_dialog'],
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
