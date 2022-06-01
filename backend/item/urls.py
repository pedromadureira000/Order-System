from django.urls import path
from item.views import (
    # Item
    GetCategoriesView,
    ItemTableView,
    ItemView,
    PriceItemForAgentsView,
    SpecificItemTable,
    SpecificItemView,

    # Category
    CategoryView, SpecificCategoryView, 

    #Price Table
    PriceTableView,
    SpecificPriceItemView,
    SpecificPriceTableView,
    fetchCategoriesToCreateItem,
    fetchCompaniesToCreatePriceTable,
    fetchItemTablesToCreateItemOrCategoryOrPriceTable,
)

app_name = 'item'
urlpatterns = [
    path('item_table', ItemTableView.as_view()),
    path('item_table/<item_table_compound_id>', SpecificItemTable.as_view()),
    path('item_tables_to_create_item_category_or_pricetable', fetchItemTablesToCreateItemOrCategoryOrPriceTable.as_view()),
    path('get_categories/<item_table_compound_id>', GetCategoriesView.as_view()),
    path('category', CategoryView.as_view()),
    path('category/<category_compound_id>', SpecificCategoryView.as_view()),
    path('categories_to_create_item/<item_table_compound_id>', fetchCategoriesToCreateItem.as_view()),
    path('item', ItemView.as_view()),
    path('item/<item_compound_id>', SpecificItemView.as_view()),
    path('companies_to_create_price_table', fetchCompaniesToCreatePriceTable.as_view()),
    #  path('items_to_create_price_table/<item_table_compound_id>', fetchItemsToCreatePriceTable.as_view()),
    path('pricetable', PriceTableView.as_view()),
    path('pricetable/<price_table_compound_id>', SpecificPriceTableView.as_view()),
    path('get_price_items_for_agents/<price_table_compound_id>', PriceItemForAgentsView.as_view()),
    path('priceitem/<price_table_compound_id>/<item_compound_id>', SpecificPriceItemView.as_view()),
]
