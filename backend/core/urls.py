from django.urls import path
from django.urls.conf import include
#  from rest_framework.authtoken.views import obtain_auth_token
from core.views import (
    CheckAuthenticated, ContractingView, EstablishmentView, SpecificContracting, SpecificEstablishment, UpdateUserPassword, UserView, SpecificUser, CompanyView, SpecificCompany, Login, Logout, GetCSRFToken
)

urlpatterns = [
    path('user', UserView.as_view()),
    path('user/<username>/<company_code>', SpecificUser.as_view()),
    path('login', Login.as_view()),
    path('logout', Logout.as_view()),
    path('getcsrf', GetCSRFToken.as_view()),
    path('checkauth', CheckAuthenticated.as_view()),
    path('contracting', ContractingView.as_view()),
    path('contracting/<contracting_code>', SpecificContracting.as_view()),
    path('company', CompanyView.as_view()),
    path('company/<company_id>', SpecificCompany.as_view()),
    path('establishment', EstablishmentView.as_view()),
    path('establishment/<establishment_id>', SpecificEstablishment.as_view()),
    #  path('update_user_password', UpdateUserPassword.as_view()),
    #  path('gettoken', obtain_auth_token, name='gettoken'),
]
