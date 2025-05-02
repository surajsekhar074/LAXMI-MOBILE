"""
URL configuration for HospitalManagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from hospital.views import *
from django.http import HttpResponse

from django.urls import path

from django.contrib.auth import views as auth_views










urlpatterns = [
    path('admin/', admin.site.urls),
    
    
    path('',index,name='home'),
    path('admin_login/', Login,name='login'),
    path('logout/', logout_Admin,name='logout'),
    path('store/<int:store_id>/stock/', store_stock_view, name='store_stock_view'),
    
    



   


    path('store_register/', register_store, name='register_store'),
    path('accounts/redirect/', redirect_to_store_stock, name='login_redirect'),
    path('', lambda request: HttpResponse("Hello This is LAXMI MOBILE")),
    
    path('login/', custom_login_view, name='login'),
     path('notifications/', notifications_view, name='notifications_view'),
    
    path('store/<int:store_id>/admin_add_user/', add_user_to_store, name='admin_add_user'),

    

    
    
    


    
    
    path('store/<int:store_id>/add_stock/', add_stock, name='add_stock'),
    
]
    



    



   


