from django.shortcuts import render,redirect

# Create your views here.
from .models import PurchaseOrder
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    # Display purchase orders for the logged in user
    orders = PurchaseOrder.objects.filter(created_by=request.user)
    return render(request, 'PO_Items/index.html', {'orders': orders})
