from django.urls import path
from .views import (
    SearchPriceItemsToMakeOrder,
    OrderView,
    SpecificOrderView,
    fetchCategoriesToMakeOrder,
    fetchClientEstabsToCreateOrder,
    searchOnePriceItemToMakeOrder,
)

app_name = 'order'
urlpatterns = [
    path('get_price_item/<establishment_compound_id>/<item_code>', searchOnePriceItemToMakeOrder.as_view()),
    path('get_price_items/<establishment_compound_id>', SearchPriceItemsToMakeOrder.as_view()),
    path('fetch_categories_to_make_order/<establishment_compound_id>', fetchCategoriesToMakeOrder.as_view()),
    path('order', OrderView.as_view()),
    path('order/<establishment_compound_id>/<order_number>', SpecificOrderView.as_view()),
    path('establishments_to_make_order', fetchClientEstabsToCreateOrder.as_view()),
]
