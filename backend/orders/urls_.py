from django.urls import path

from orders import views

app_name = 'orders'

urlpatterns = [
    path('criar-item/', views.create_item, name='create_item'),
    path('editar-itens/', views.edit_items, name='edit_items'),
    path('criar-tabela-preco/', views.create_price_table, name='create_price_table'),
    path('editar-tabelas-preco/', views.edit_price_table, name='edit_price_table'),
    path('criar-categoria/', views.create_category, name='create_category'),
    path('editar-categoria/', views.edit_category, name='edit_category'),



]
