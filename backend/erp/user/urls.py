from django.urls import path
#  from rest_framework.authtoken.views import obtain_auth_token

from erp.user.views import (
    CheckAuthenticatedView, SignupView, LoginView, LogoutView, GetCSRFToken
)

app_name = 'user'
urlpatterns = [
    #  path('', UserView.as_view()),
    path('register', SignupView.as_view()),
    path('login', LoginView.as_view()),
    path('logout', LogoutView.as_view()),
    path('getcsrf', GetCSRFToken.as_view()),
    path('checkauth', CheckAuthenticatedView.as_view()),
    #  path('gettoken', obtain_auth_token, name='gettoken'),
    #  path('delete', DeleteAccountView.as_view(), name='deleteAccount'),
    #  path('test', test_view, name='teste'),
]
