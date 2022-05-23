<template>
  <div class="ma-4">
    <h2 class="mb-2">{{$t('About the system')}}</h2>
    <p>{{$t('about_the_system__paragraph')}}</p>

    <div>
      <h2 class="mb-2">{{$t('System administration')}}</h2>
      <h3>{{$t('Types of user')}}</h3>
      <p>
        <b>{{$t('Admin_Agent')}}: </b>{{$t('system_administration__paragraph_1')}}<br>
        <b>{{$t('Agent')}}: </b>{{$t('system_administration__paragraph_2')}}<br>
        <b>{{$t('Client_User')}}: </b>{{$t('client_user__paragraph_1')}}<br>
        <b>{{'Obs: '}}</b>{{$t('system_administration__paragraph_obs')}}
      </p> 

      <h3>{{$t('Client')}}</h3>
      <p>{{$t('how_to_create_a_client__paragraph')}}<br>{{$t('how_to_create_a_client__paragraph_1')}} <u>{{$t('Client_establishments')}}</u>{{$t('how_to_create_a_client__paragraph_2')}} <u>{{$t('Client_establishments')}}</u> {{$t('how_to_create_a_client__paragraph_3')}}<br>
      {{$t('how_to_exclude_a_client__paragraph')}}</p>

      <h3>{{$t('Agent')}}</h3>
      <p>{{$t('how_to_create_an_agent__paragraph')}}<br>
     
      <h3>{{$t('Item')}}</h3>
      <p>{{$t('how_to_create_an_item__paragraph')}}<br>
      {{$t('how_to_create_an_item__paragraph_2')}}<br>
      {{$t('how_to_exclude_an_item__paragraph')}}</p>

      <h3>{{$t('Sales orders')}}</h3>
      <p><b>{{$t('Get orders')}}: </b>{{$t('how_to_get_orders__paragraph')}}<u>{{$t('View Orders')}}</u>{{$t('how_to_get_orders__paragraph_2')}}<u>{{$t('Search')}}</u>.<br>{{$t('how_to_get_orders__paragraph_3')}}<br>
      <b>{{$t('Edit Order')}}: </b>{{$t('how_to_update_orders__paragraph')}}<br>
      <b>Obs: </b>{{$t('how_to_update_orders__paragraph_OBS')}}</p>

      <h3>{{$t("About the representation of system elements by code and name.")}}</h3>
      <p>{{$t('representation_of_records_by_code')}}</p>
    </div>

    <div class="mb-5">
      <h2 class="mb-2">{{$t('Client pages')}}</h2>
      <!-- Client pages -->
      <h3>{{$t('Get orders')}}</h3>
      <p>
        {{$t('how_to_get_orders__paragraph')}}<u>{{$t('View Orders')}}</u>{{$t('how_to_get_orders__paragraph_2')}}<u>{{$t('Search')}}</u>.
        <br>{{$t('how_to_get_orders__paragraph_3')}}
      </p>

      <h3>{{$t('Make order')}}</h3>
      <p>{{$t('how_to_make_an_order__paragraph')}} <u>{{$t('Add')}}</u>{{$t('how_to_make_an_order__paragraph_2')}}<br><b>{{$t('Save')}}: </b>{{$t('how_to_make_an_order__paragraph_3')}}<br><b>{{$t('Typing')}}: </b>{{$t('how_to_make_an_order__paragraph_4')}}</p>
      <h3>{{$t('Update order')}}</h3>
      <p>{{$t('how_to_update_orders_by_client_user__paragraph')}}</p>
    </div>

  </div>
</template>
