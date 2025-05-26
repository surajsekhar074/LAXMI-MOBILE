from django.contrib import admin
from django.urls import path
from hospital.views import *
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home
    path('', index, name='home'),

    # Authentication
    path('login/', custom_login_view, name='login'),
    path('logout/', logout_Admin, name='logout'),


    # Store and Stock
    path('store/<int:store_id>/stock/', store_stock_view, name='store_stock_view'),
    path('store/<int:store_id>/add_stock/', add_stock, name='add_stock'),
    path('store_register/', register_store, name='register_store'),
    path('accounts/redirect/', redirect_to_store_stock, name='login_redirect'),
    path('add-staff/', add_staff, name='add_staff'),


    # Admin user management
    path('store/<int:store_id>/admin_add_user/', add_user_to_store, name='admin_add_user'),
    path('all-users/', all_users_view, name='all_users'),
    path('reset-password/<int:user_id>/', reset_password_view, name='reset_password'),
    path('edit-user/<int:user_id>/', edit_user_view, name='edit_user'),
    path('delete-user/<int:user_id>/', delete_user_view, name='delete_user'),

    # Notifications
    path('notifications/', notifications_view, name='notifications_view'),
    path('all-staff/', all_staff, name='all_staff'),  # 👈 New route
    path('edit-staff/<int:user_id>/', edit_staff, name='edit_staff'),
    path('delete-staff/<int:user_id>/', delete_staff, name='delete_staff'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
