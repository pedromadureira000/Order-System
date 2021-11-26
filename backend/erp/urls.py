"""erp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from erp.core.views import apiNotFound

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('erp.core.urls')),
    #  path('usuario/', include('django.contrib.auth.urls')),
    #  path('pedidos/', include('erp.orders.urls')),

    # REST URLS
    path('api/orders/', include('erp.orders.urls')),
    path('api/user/', include('erp.user.urls')),
    path('api/documents/', include('erp.documents.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [re_path(r'^api/.*$', apiNotFound )]  #if i call a wrong url, this is what i will get.
urlpatterns += [re_path(r'^.*$', TemplateView.as_view(template_name='index.html'))]  #if i call a wrong url, this is what i will get.
