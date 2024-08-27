"""fraud_detection URL Configuration

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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from myapp.views import *
urlpatterns = [
    path('admin/', admin.site.urls),
    path('create-user/', create_custom_user, name='create_custom_user'),
    path('users/list/', list_custom_users, name='list_users'),
    path('users/detail/<int:user_id>/', retrieve_custom_user, name='retrieve-custom-user'), 
    path('user/update/<int:user_id>/', update_custom_user, name='customuser-update'),
    path('user/delete/<int:user_id>/', delete_custom_user, name='customuser-delete'),
    path('login/', login_user, name='login'),


    path('bankaccounts/create/<int:user_id>/', create_bank_account, name='bankaccount-create'),
    path('bankaccounts/<int:user_id>/', list_bank_accounts, name='bankaccount-list'),
    path('bankaccount/upadate/<int:user_id>/<int:account_id>/', update_bank_account, name='bankaccount-update'),
    path('bankaccount/detail/<int:pk>/', bank_account_detail, name='bankaccount-detail'),


    path('transaction/create/', create_transaction, name='create_transaction'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
