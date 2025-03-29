from django.urls import path
from . import views

app_name = "PO_Items"

urlpatterns = [
    path('', views.dashboard, name='PO_Items' ),
    path('create_order/', views.create_order, name='create_order'),
]
