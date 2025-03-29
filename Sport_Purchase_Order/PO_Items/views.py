from django.shortcuts import render,redirect

# Create your views here.
from .models import PurchaseOrder ,POItem, SportsItem
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string


@login_required
def dashboard(request):
    orders = PurchaseOrder.objects.filter(created_by=request.user)
    for order in orders:
        # Calculate the total price for the order
        order.total_price = sum(item.price * item.quantity for item in order.items.all())
    return render(request, 'PO_Items/index.html', {'orders': orders})

@login_required
def create_order(request):
    if request.method == "POST":
        # Generate a unique order number
        order_number = get_random_string(length=10).upper()

        # Create a new PurchaseOrder instance
        purchase_order = PurchaseOrder.objects.create(
            order_number=order_number,
            created_by=request.user
        )

        # Get selected sports items and their quantities from the form
        sports_item_ids = request.POST.getlist('sports_item')
        quantities = request.POST.getlist('quantity')

        # Add each selected sports item to the purchase order
        for item_id, quantity in zip(sports_item_ids, quantities):
            sports_item = SportsItem.objects.get(id=item_id)
            POItem.objects.create(
                purchase_order=purchase_order,
                sports_item=sports_item,
                quantity=int(quantity),
                price=sports_item.unit_price  # Set the price per item
            )

        # Redirect to the dashboard after saving
        return redirect('PO_Items:PO_Items')

    # Pass available sports items to the template
    sports_items = SportsItem.objects.all()
    return render(request, 'PO_Items/create_order.html', {'sports_items': sports_items})