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
    PriceTableView, AssignPriceTableView,
    SpecificPriceTableView,

    #Item Price
    PriceItemView,
    SpecificPriceItemView

)

app_name = 'orders'
urlpatterns = [
    # Order
    path('order', OrderView.as_view(), name='api_order'),
    path('order/<code>', SpecificOrderView.as_view(), name='api_specific_order'),

    # Item
    path('item', ItemView.as_view(), name='api_item'),
    path('item/<code>', SpecificItemView.as_view(), name='api_specific_item'),

    # Category
    path('category', CategoryView.as_view(), name='api_category'),
    path('category/<code>', SpecificCategoryView.as_view(), name='api_specific_category'),

    # Price table
    path('pricetable', PriceTableView.as_view(), name='api_pricetable'),
    path('pricetable/<table_code>', SpecificPriceTableView.as_view(), name='api_pricetable'),
    path('assign_pricetable', AssignPriceTableView.as_view()),

    # Item Price
    path('priceitem/', PriceItemView.as_view()),
    path('priceitem/<item_code>/<table_code>', SpecificPriceItemView.as_view())
]
