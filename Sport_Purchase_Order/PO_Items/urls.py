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
     path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'), 
    path('delete_item/<int:item_id>/', views.delete_item, name='delete_item'),   
    path('delete_sports_item/<int:item_id>/', views.delete_sports_item, name='delete_sports_item'),   
    path('delete_supplier/<int:supplier_id>/', views.delete_supplier, name='delete_supplier'),  
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('edit_order/<int:order_id>/', views.edit_order, name='edit_order'),
]
