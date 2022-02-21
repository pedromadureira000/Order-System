from django.urls import path
from orders.views import (
    # Item
    ItemTableView,
    ItemView,
    SpecificItemTable,
    SpecificItemView,

    # Order
    OrderView,
    SpecificOrderView,

    # Category
    CategoryView, SpecificCategoryView, 

    #Price Table
    PriceTableView,
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
    path('pricetable/<pricetable_compound_id>', SpecificPriceTableView.as_view()),
    #  path('assign_pricetable', AssignPriceTableView.as_view()),
    # Item Price
    #  path('priceitem/', PriceItemView.as_view()),
    #  path('priceitem/<item_code>/<table_code>', SpecificPriceItemView.as_view()),
    # Order
    path('order', OrderView.as_view()),
    path('order/<code>', SpecificOrderView.as_view()),
]
