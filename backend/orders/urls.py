from django.urls import path
from orders.views import (
    # Item
    ItemApi,
    SpecificItemApi,

    # Order
    OrderApi,
    SpecificOrderApi,

    # Category
    CategoryApi, SpecificCategoryApi, PriceTableApi, PriceItemApi,

)

app_name = 'orders'
urlpatterns = [
    # Order
    path('order', OrderApi.as_view(), name='api_order'),
    path('order/<code>', SpecificOrderApi.as_view(), name='api_specific_order'),

    # Item
    path('item', ItemApi.as_view(), name='api_item'),
    path('item/<code>', SpecificItemApi.as_view(), name='api_specific_item'),

    # Category
    path('category', CategoryApi.as_view(), name='api_category'),
    path('category/<code>', SpecificCategoryApi.as_view(), name='api_specific_category'),

    # Price list
    path('pricetable', PriceTableApi.as_view(), name='api_pricetable'),
    #  path('pricetable/<code>', SpecificPriceTableApi.as_view(), name='api_pricetable'),

    # Item Price
    path('priceitem/', PriceItemApi.as_view())
]
