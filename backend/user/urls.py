from django.urls import path
#  from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    AdminAgentView, AgentView, ClientUserView, ERPUserView, OwnProfileView, SpecificAdminAgent, SpecificAgent, SpecificClientUser, SpecificERPUser, UpdateUserPassword, Login, Logout, GetCSRFToken
)

urlpatterns = [
    #Auth
    path('login', Login.as_view()),
    path('logout', Logout.as_view()),
    path('getcsrf', GetCSRFToken.as_view()),
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
