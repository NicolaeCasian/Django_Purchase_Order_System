from django.urls import path
from . import views

app_name = "PO_Items"

urlpatterns = [
    path('', views.dashboard, name='PO_Items' ),
    path('create_order/', views.create_order, name='create_order'),
     path('change_status/<int:order_id>/', views.change_status, name='change_status'),
    path('manage_items/', views.manage_items, name='manage_items'),
    path('manage_suppliers/', views.manage_suppliers, name='manage_suppliers'),
    path('manage_users/', views.manage_users, name='manage_users'),
]
