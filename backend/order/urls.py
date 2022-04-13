from django.urls import path
from .views import (
    SearchPriceItemsToMakeOrder,
    OrderView,
    SpecificOrderView,
    fetchCategoriesToMakeOrderAndGetPriceTableInfo,
    fetchClientEstabsToCreateOrder,
    fetchClientsToFillFilterSelectorToSearchOrders,
    fetchDataToFillFilterSelectorsToSearchOrders,
    searchOnePriceItemToMakeOrder,
)

app_name = 'order'
urlpatterns = [
    path('get_price_item/<establishment_compound_id>/<item_code>', searchOnePriceItemToMakeOrder.as_view()),
    path('get_price_items/<establishment_compound_id>/<category_compound_id>/<item_description>', SearchPriceItemsToMakeOrder.as_view()),
    path('fetch_categories_to_make_order_and_get_price_table_info/<establishment_compound_id>', fetchCategoriesToMakeOrderAndGetPriceTableInfo.as_view()),
    path('fetch_data_to_fill_filter_selectors_to_search_orders', fetchDataToFillFilterSelectorsToSearchOrders.as_view()), 
    path('fetch_clients_to_fill_filter_selector_to_search_orders', fetchClientsToFillFilterSelectorToSearchOrders.as_view()), 
    path('order', OrderView.as_view()),
    path('order/<establishment_compound_id>/<order_number>', SpecificOrderView.as_view()),
    path('establishments_to_make_order', fetchClientEstabsToCreateOrder.as_view()),
]
