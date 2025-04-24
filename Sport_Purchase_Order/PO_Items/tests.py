from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.test import Client
from PO_Items.models import PurchaseOrder, SportsItem, Supplier


# Test Case for Login Functionality
class LoginTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.test_user = User.objects.create_user(username='Buyer', password='Nicolaecasian1')

    def test_successful_login(self):
        """Test that a user can log in with valid credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'Buyer',
            'password': 'Nicolaecasian1',
        })
        self.assertEqual(response.status_code, 302) 

    def test_login_with_invalid_credentials(self):
        """Test that login fails with invalid credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200) 
        self.assertContains(response, "Please enter a correct username and password.")

    def test_logout(self):
        """Test that a logged-in user can log out successfully."""
        self.client.login(username='Buyer', password='Nicolaecasian1')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout


class CreateOrderTest(TestCase):
    def setUp(self):
        User = get_user_model()
        # Create a buyer
        self.buyer = User.objects.create_user(
            username='Buyer', password='Nicolaecasian1', role='BUYER'
        )
        # Create a supplier and one sports item
        self.supplier = Supplier.objects.create(name='Default Supplier')
        self.item = SportsItem.objects.create(
            supplier=self.supplier,
            name='Test ',
            description='',
            unit_price=20.00
        )

        self.client = Client()
        self.url = reverse('PO_Items:create_order')

    def test_get_create_order_page(self):
        """Test that the create order page renders correctly."""
        self.client.login(username='Buyer', password='Nicolaecasian1')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Create Purchase Order')
        self.assertContains(resp, self.item.name)

    def test_post_creates_purchase_order_and_items(self):
        """Test that a purchase order and items are created successfully."""
        self.client.login(username='Buyer', password='Nicolaecasian1')

        # Adjust field names to match your form
        data = {
            'sports_item': [str(self.item.id)],  # Checkbox for selecting the item
            'quantity': '3',  # Quantity input field
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, 302)

        # Verify that exactly one PurchaseOrder is created
        self.assertEqual(PurchaseOrder.objects.count(), 1)
        po = PurchaseOrder.objects.first()
        self.assertEqual(po.created_by, self.buyer)

        # Verify that exactly one POItem is linked to the PurchaseOrder
        self.assertEqual(po.items.count(), 1)
        poi = po.items.first()
        self.assertEqual(poi.sports_item, self.item)
        self.assertEqual(poi.quantity, 3)
        # Verify that the price is calculated correctly
        self.assertEqual(poi.price, self.item.unit_price * 3)