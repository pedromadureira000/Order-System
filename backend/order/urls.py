from django.urls import path
from .views import (
    OrderView,
    SpecificOrderView,
)

app_name = 'order'
urlpatterns = [
    path('order', OrderView.as_view()),
    path('order/<establishment_compound_id>/<order_number>', SpecificOrderView.as_view()),
]
