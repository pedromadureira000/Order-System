from django.urls import path
#  from rest_framework.authtoken.views import obtain_auth_token
from core.views import (
    AdminAgentView, AgentView, ClientTableView, ClientUserView, ClientView, ContractingView, ERPUserView, EstablishmentView, OwnProfileView, SpecificAdminAgent, SpecificAgent, SpecificClient, SpecificClientTable, SpecificClientUser, SpecificContracting, SpecificERPUser, SpecificEstablishment, UpdateUserPassword, CompanyView, SpecificCompany, Login, Logout, GetCSRFToken
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
    path('erp_user', ERPUserView.as_view()),
    path('erp_user/<contracting_code>/<username>', SpecificERPUser.as_view()),
    path('admin_agent', AdminAgentView.as_view()),
    path('admin_agent/<contracting_code>/<username>', SpecificAdminAgent.as_view()),
    path('agent', AgentView.as_view()),
    path('agent/<contracting_code>/<username>', SpecificAgent.as_view()),
    path('client_user', ClientUserView.as_view()),
    path('client_user/<contracting_code>/<username>', SpecificClientUser.as_view()),
    path('update_user_password', UpdateUserPassword.as_view()),
    #  path('gettoken', obtain_auth_token, name='gettoken'),
]
