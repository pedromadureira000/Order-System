from django.urls import path
from .views import (
    DuplicateOrder,
    OrderHistoryView,
    SearchPriceItemsToMakeOrder,
    OrderView,
    SpecificOrderView,
    fetchCategoriesToMakeOrderAndGetPriceTableInfo,
    fetchClientEstabsToCreateOrder,
    fetchClientsToFillFilterSelectorToSearchOrders,
    fetchCompaniesAndEstabsToDuplicateOrder,
    fetchDataToFillFilterSelectorsToSearchOrders,
    searchOnePriceItemToMakeOrder,
)

app_name = 'order'
urlpatterns = [
    path('get_price_item/<establishment_compound_id>/<item_code>', searchOnePriceItemToMakeOrder.as_view()),
    path('get_price_items/<establishment_compound_id>', SearchPriceItemsToMakeOrder.as_view()),
    path('fetch_categories_to_make_order_and_get_price_table_info/<establishment_compound_id>', fetchCategoriesToMakeOrderAndGetPriceTableInfo.as_view()),
    path('fetch_data_to_fill_filter_selectors_to_search_orders', fetchDataToFillFilterSelectorsToSearchOrders.as_view()), 
    path('fetch_clients_to_fill_filter_selector_to_search_orders', fetchClientsToFillFilterSelectorToSearchOrders.as_view()),  
    path('order', OrderView.as_view()),
    path('order/<id>', SpecificOrderView.as_view()),
    path('establishments_to_make_order', fetchClientEstabsToCreateOrder.as_view()),
    path('order_history/<order_id>', OrderHistoryView.as_view()),
    path('fetch_comps_and_estabs_to_duplicate_order/<order_id>', fetchCompaniesAndEstabsToDuplicateOrder.as_view()), 
    path('duplicate_order', DuplicateOrder.as_view()),
]
