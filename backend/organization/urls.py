from django.urls import path
from .views import (
    ClientTableView, ClientView, ContractingView, EstablishmentView, SpecificClient, SpecificClientTable, SpecificContracting, SpecificEstablishment, CompanyView, SpecificCompany
)

urlpatterns = [
    path('contracting', ContractingView.as_view()),
    path('contracting/<contracting_code>', SpecificContracting.as_view()),
    path('company', CompanyView.as_view()),
    path('company/<company_compound_id>', SpecificCompany.as_view()),
    path('establishment', EstablishmentView.as_view()),
    path('establishment/<establishment_compound_id>', SpecificEstablishment.as_view()),
    path('client_table', ClientTableView.as_view()),
    path('client_table/<client_table_compound_id>', SpecificClientTable.as_view()),
    path('client', ClientView.as_view()),
    path('client/<client_compound_id>', SpecificClient.as_view()),
]
