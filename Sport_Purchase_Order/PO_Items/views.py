from django.shortcuts import render,redirect,get_object_or_404
from .decorators import role_required
# Create your views here.
from .models import PurchaseOrder ,POItem, SportsItem, Supplier, User
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
@role_required(['ADMIN', 'BUYER'])
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

@role_required(['ADMIN', 'APPROVER'])
@login_required
def change_status(request, order_id):
    # Get the purchase order by ID
    order = get_object_or_404(PurchaseOrder, id=order_id)

    # Get all items associated with the purchase order
    items = POItem.objects.filter(purchase_order=order)

    if request.method == "POST":
        # Update the status based on the submitted form
        new_status = request.POST.get("status")
        if new_status in dict(PurchaseOrder.ORDER_STATUS_CHOICES):
            order.status = new_status
            order.save()
            return redirect('PO_Items:PO_Items')

    # Render the change_status template
    return render(request, 'PO_Items/change_status.html', {'order': order, 'items': items})

@role_required(['ADMIN', 'INVENTORY_MANAGER'])
@login_required
def manage_items(request):
    if request.method == "POST":
        # Handle form submission to create a new item
        name = request.POST.get("name")
        description = request.POST.get("description")
        unit_price = request.POST.get("unit_price")
        supplier_id = request.POST.get("supplier")

        # Get the supplier object
        supplier = Supplier.objects.get(id=supplier_id)

        # Create the new SportsItem
        SportsItem.objects.create(
            name=name,
            description=description,
            unit_price=unit_price,
            supplier=supplier
        )
        return redirect('PO_Items:manage_items') 

    # Fetch all existing items and suppliers
    items = SportsItem.objects.all()
    suppliers = Supplier.objects.all()
    return render(request, 'PO_Items/manage_items.html', {'items': items, 'suppliers': suppliers})

@role_required(['ADMIN', 'INVENTORY_MANAGER'])
@login_required
def manage_suppliers(request):
    if request.method == "POST":
        # Handle form submission to create a new supplier
        name = request.POST.get("name")
        contact_info = request.POST.get("contact_info")

        # Create the new Supplier
        Supplier.objects.create(
            name=name,
            contact_info=contact_info
        )
        return redirect('PO_Items:manage_suppliers')  

    # Fetch all existing suppliers
    suppliers = Supplier.objects.all()
    return render(request, 'PO_Items/manage_suppliers.html', {'suppliers': suppliers})

@login_required
@role_required(['ADMIN'])
def manage_users(request):
    if request.method == "POST":
        if "username" in request.POST:  # Adding a new user
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            role = request.POST.get("role")

            # Create the new user
            user = User.objects.create_user(username=username, email=email, password=password)
            user.role = role
            user.save()
        elif "user_id" in request.POST:  # Updating an existing user's role
            user_id = request.POST.get("user_id")
            new_role = request.POST.get("role")
            user = User.objects.get(id=user_id)
            if new_role in dict(User.ROLE_CHOICES):
                user.role = new_role
                user.save()

        return redirect('PO_Items:manage_users')  

    users = User.objects.all()
    return render(request, 'PO_Items/manage_users.html', {'users': users})