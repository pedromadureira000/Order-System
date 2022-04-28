from django.urls import path
from .views import (
    ClientTableView, ClientView, ContractingView, EstablishmentView, GetClientsView, GetCompaniesToCreateClient, GetCompaniesToCreateEstablishment, GetEstablishmentsToCreateClient, GetPriceTablesToCreateClient, SpecificClient, SpecificClientTable, SpecificContracting, SpecificEstablishment, CompanyView, SpecificCompany
)

urlpatterns = [
    path('contracting', ContractingView.as_view()),
    path('contracting/<contracting_code>', SpecificContracting.as_view()),
    #Company
    path('company', CompanyView.as_view()),
    path('company/<company_compound_id>', SpecificCompany.as_view()),
    # Establishment
    path('establishment', EstablishmentView.as_view()),
    path('establishment/<establishment_compound_id>', SpecificEstablishment.as_view()),
    # Client table
    path('client_table', ClientTableView.as_view()),
    path('client_table/<client_table_compound_id>', SpecificClientTable.as_view()),
    # Client
    #  path('client_tables_to_create_client', GetClientTablesToCreateClient.as_view()),
    path('companies_to_create_client', GetCompaniesToCreateClient.as_view()), 
    path('establishments_to_create_client/<client_table_compound_id>', GetEstablishmentsToCreateClient.as_view()),
    path('price_tables_to_create_client/<company_compound_id>', GetPriceTablesToCreateClient.as_view()),
    path('get_clients/<client_table_compound_id>', GetClientsView.as_view()),
    path('client', ClientView.as_view()),
    path('client/<client_compound_id>', SpecificClient.as_view()),
    path('companies_to_create_establishment', GetCompaniesToCreateEstablishment.as_view()),

]
