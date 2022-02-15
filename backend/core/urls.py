from django.urls import path
from django.urls.conf import include
#  from rest_framework.authtoken.views import obtain_auth_token
from core.views import (
    AdminAgentView, AgentView, ClientTableView, ClientUserView, ClientView, ContractingView, EstablishmentView, OwnProfileView, SpecificAdminAgent, SpecificAgent, SpecificClient, SpecificClientTable, SpecificClientUser, SpecificContracting, SpecificEstablishment, UpdateUserPassword, CompanyView, SpecificCompany, Login, Logout, GetCSRFToken
)

urlpatterns = [
    #Auth
    path('login', Login.as_view()),
    path('logout', Logout.as_view()),
    path('getcsrf', GetCSRFToken.as_view()),
    #Organization
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
    #User
    path('own_profile', OwnProfileView.as_view()),
    path('admin_agent', AdminAgentView.as_view()),
    path('admin_agent/<username>/<contracting_code>', SpecificAdminAgent.as_view()),
    path('agent', AgentView.as_view()),
    path('agent/<username>/<contracting_code>', SpecificAgent.as_view()),
    path('client_user', ClientUserView.as_view()),
    path('client_user/<username>/<contracting_code>', SpecificClientUser.as_view()),
    path('update_user_password', UpdateUserPassword.as_view()),
    #  path('gettoken', obtain_auth_token, name='gettoken'),
]
