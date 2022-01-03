from django.urls import path
from documents.views import gen_boleto

app_name = "boleto"
urlpatterns = [
    path('boleto/', gen_boleto, name="gen_boleto")
]
