from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


#Test Case for the login functionality
class LoginTest(TestCase):
    # Test setup method to create a test user
    def setUp(self):
        User = get_user_model() 
        self.test_user = User.objects.create_user(username='Buyer', password='Nicolaecasian1')

    # Test method to test successful login
    def test_successful_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'Buyer',
            'password': 'Nicolaecasian1',
        })
        self.assertEqual(response.status_code, 302)

    # Test method to test login with invalid credentials
    def test_login_with_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password.")

    