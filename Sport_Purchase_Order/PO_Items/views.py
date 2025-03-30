from django.shortcuts import render, redirect, get_object_or_404
from .decorators import role_required
from .models import PurchaseOrder, POItem, SportsItem, Supplier, User
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.http import Http404
from django.forms import modelform_factory, modelformset_factory

@login_required
def dashboard(request):
    # Get the filter value from the request
    status_filter = request.GET.get('status', 'ALL')

    # Fetch orders based on the filter
    if status_filter == 'ALL':
        orders = PurchaseOrder.objects.all()  # Fetch all orders
    else:
        orders = PurchaseOrder.objects.filter(status=status_filter)  # Filter by status

    # Calculate the total price for each order
    for order in orders:
        order.total_price = sum(item.price * item.quantity for item in order.items.all())

    return render(request, 'PO_Items/index.html', {'orders': orders, 'status_filter': status_filter})

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

@login_required
@role_required(['ADMIN'])
def delete_order(request, order_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)
    order.delete()
    return redirect('PO_Items:PO_Items')  # Redirect to the dashboard after deletion

@login_required
@role_required(['ADMIN', 'BUYER'])
def delete_item(request, item_id):
    item = get_object_or_404(POItem, id=item_id)
    order_id = item.purchase_order.id

    # Debugging: Print item details before deletion
    print(f"Deleting item {item_id} from order {order_id}")

    item.delete()

    # Debugging: Print remaining items in the order
    remaining_items = POItem.objects.filter(purchase_order_id=order_id)
    print(f"Remaining items in order {order_id}: {remaining_items.count()}")

    return redirect('PO_Items:edit_order', order_id=order_id)

@login_required
@role_required(['ADMIN', 'INVENTORY_MANAGER'])
def delete_sports_item(request, item_id):
    try:
        item = SportsItem.objects.get(id=item_id)
        item.delete()
        return redirect('PO_Items:manage_items')  # Redirect to the manage items page after deletion
    except SportsItem.DoesNotExist:
        raise Http404("The sports item you are trying to delete does not exist.")
    
@login_required
@role_required(['ADMIN', 'INVENTORY_MANAGER'])
def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)

    # Check if the supplier has associated sports items
    if supplier.sportsitem_set.exists():
        # Redirect with an error message 
        return redirect('PO_Items:manage_suppliers')

    supplier.delete()
    return redirect('PO_Items:manage_suppliers')  

@login_required
@role_required(['ADMIN'])
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('PO_Items:manage_users') 

@login_required
@role_required(['ADMIN', 'BUYER'])
def edit_order(request, order_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)

    # Create a form for the PurchaseOrder model
    PurchaseOrderForm = modelform_factory(PurchaseOrder, fields=['order_number', 'status'])

    # Create a formset for the POItem model
    POItemFormSet = modelformset_factory(
        POItem,
        fields=['sports_item', 'quantity', 'price'],
        extra=0,  # Only show saved items
        can_delete=True
    )

    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=order)
        formset = POItemFormSet(request.POST, queryset=order.items.all().order_by('id'))

        if form.is_valid() and formset.is_valid():
            form.save()
            po_items = formset.save(commit=False)
            for item in po_items:
                item.purchase_order = order  # Associate each item with the current order
                item.save()
            formset.save_m2m()
            return redirect('PO_Items:edit_order', order_id=order.id)
        else:
            print("Form or Formset is invalid")
            print("Form errors:", form.errors)
            print("Formset errors:", formset.errors)
    else:
        form = PurchaseOrderForm(instance=order)
        formset = POItemFormSet(queryset=order.items.all().order_by('id'))

    return render(request, 'PO_Items/edit_order.html', {'form': form, 'formset': formset, 'order': order})