from django.urls import path
from orders.views import (
    # Item
    ItemView,
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
    # Item
    path('item', ItemView.as_view()),
    path('item/<code>', SpecificItemView.as_view()),
    # Category
    path('category', CategoryView.as_view()),
    path('category/<code>', SpecificCategoryView.as_view()),
    # Price table
    path('pricetable', PriceTableView.as_view()),
    path('pricetable/<table_code>', SpecificPriceTableView.as_view()),
    #  path('assign_pricetable', AssignPriceTableView.as_view()),
    # Item Price
    #  path('priceitem/', PriceItemView.as_view()),
    #  path('priceitem/<item_code>/<table_code>', SpecificPriceItemView.as_view()),
    # Order
    path('order', OrderView.as_view()),
    path('order/<code>', SpecificOrderView.as_view()),
]
