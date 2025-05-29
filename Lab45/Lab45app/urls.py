from django.urls import path
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('login'), permanent=False), name='index'),
    # Auth
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_page, name='logout'),
    path('dashboard/', views.dashboard_page, name='dashboard'),

    # User Management (Admin Only)
    path('users/', views.users_list, name='users_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),

    # Role Management (Admin Only)
    path('roles/', views.roles_list, name='roles_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<int:role_id>/edit/', views.role_edit, name='role_edit'),
    path('roles/<int:role_id>/delete/', views.role_delete, name='role_delete'),

    # Found Items
    path('items-found/', views.items_found_list, name='items_found_list'),
    path('items-found/create/', views.item_found_create, name='item_found_create'),
    path('items-found/<int:item_id>/edit/', views.item_found_edit, name='item_found_edit'),
    path('items-found/<int:item_id>/delete/', views.item_found_delete, name='item_found_delete'),

    # Lost Items
    path('items-lost/', views.items_lost_list, name='items_lost_list'),
    path('items-lost/create/', views.lost_item_create, name='lost_item_create'),
    path('items-lost/<int:item_id>/edit/', views.lost_item_edit, name='lost_item_edit'),
    path('items-lost/<int:item_id>/delete/', views.lost_item_delete, name='lost_item_delete'),
]
