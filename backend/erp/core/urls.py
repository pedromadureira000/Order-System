from django.urls import path
from erp.core import views

app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
]
