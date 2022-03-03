from django.urls import path
from orders.views import (
    # Item
    ItemTableView,
    ItemView,
    PriceItemForAgentsView,
    GetPriceItemByClientUserView,
    SpecificItemTable,
    SpecificItemView,

    # Order
    OrderView,
    SpecificOrderView,

    # Category
    CategoryView, SpecificCategoryView, 

    #Price Table
    PriceTableView,
    SpecificPriceItemView,
    SpecificPriceTableView,

    #Item Price
    #  PriceItemView,
    #  SpecificPriceItemView

)

app_name = 'orders'
urlpatterns = [
    path('item_table', ItemTableView.as_view()),
    path('item_table/<item_table_compound_id>', SpecificItemTable.as_view()),
    path('category', CategoryView.as_view()),
    path('category/<category_compound_id>', SpecificCategoryView.as_view()),
    path('item', ItemView.as_view()),
    path('item/<item_compound_id>', SpecificItemView.as_view()),
    path('pricetable', PriceTableView.as_view()),
    path('pricetable/<price_table_compound_id>', SpecificPriceTableView.as_view()),
    path('get_price_items/<establishment_compound_id>', GetPriceItemByClientUserView.as_view()),
    path('get_price_items_for_agents/<price_table_compound_id>', PriceItemForAgentsView.as_view()),
    path('priceitem/<price_table_compound_id>/<item_compound_id>', SpecificPriceItemView.as_view()),
    path('order', OrderView.as_view()),
    path('order/<establishment_compound_id>/<order_number>', SpecificOrderView.as_view()),
]
