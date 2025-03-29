from django.urls import path
from . import views

app_name = "PO_Items"

urlpatterns = [
    path('', views.dashboard, name='PO_Items' ),
    # Add paths for creating, editing, and approving orders
]
