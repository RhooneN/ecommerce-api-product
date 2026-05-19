from rest_framework.test import APITestCase
from rest_framework import status
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime, timedelta
# ~ from rest_framework.authentication import BaseAuthentication
# ~ from rest_framework.exceptions import AuthenticationFailed
import jwt

def make_token(user):
    # ~ print("wesss", dir(user))
    # ~ print("super", getattr(user, "is_staff", False))
    payload = {
        "user_id": user.id,
        "username": user.username,
        "is_admin": getattr(user, "is_staff", False),
        "exp": datetime.now() + timedelta(hours=1),
    }
    print("payload", payload)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    
class CategoryTests(APITestCase):
	
    def authenticate(self, user):
        token = make_token(user)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
    def setUp(self):
        self.admin_user = User.objects.create_user(username='admin', password='adminpassword', is_staff=True)
        self.regular_user = User.objects.create_user(username='user', password='userpassword')
        self.category = Category.objects.create(owner_id=self.admin_user.id, name="Test Category")

    def test_category_list_authenticated(self):
        self.authenticate(self.regular_user)
        response = self.client.get('/categories/')

        """Test that the category list is available for authenticated users."""
      
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_category_list_unauthenticated(self):
        """Test that the category list is available for unauthenticated users."""
        response = self.client.get('/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_create_admin(self):
        """Test that only an admin can create a category."""
        x = self.authenticate(self.admin_user)
        data = {"name": 'New Category', 'owner_id': 2, "description": "hola"}
        response = self.client.post('/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_category_create_non_admin(self):
        """Test that a non-admin user cannot create a category."""
        y = self.authenticate(self.regular_user)
        data = {"name": "New Category", "owner_id":self.client}
        response = self.client.post('/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_detail(self):
        """Test that the category detail is available to both authenticated and unauthenticated users."""
        response = self.client.get(f'/categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_update_admin(self):
        """Test that only an admin can update a category."""
        self.authenticate(self.admin_user)
        data = {"name": "Updated Category"}
        response = self.client.patch(f'/categories/{self.category.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_update_non_admin(self):
        """Test that a non-admin cannot update a category."""
        self.authenticate(self.regular_user)
        data = {"name": "Updated Category", 'owner_id': self.client}
        response = self.client.patch(f'/categories/{self.category.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_delete_admin(self):
        """Test that only an admin can delete a category."""
        self.authenticate(self.admin_user)
        response = self.client.delete(f'/categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_category_delete_non_admin(self):
        """Test that a non-admin cannot delete a category."""
        self.authenticate(self.regular_user)
        response = self.client.delete(f'/categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProductTests(APITestCase):
	
    def authenticate(self, user):
        token = make_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
    def setUp(self):
        self.admin_user = User.objects.create_user(username='admin', password='adminpassword', is_staff=True)
        self.regular_user = User.objects.create_user(username='user', password='userpassword')
        self.category = Category.objects.create(name="Test Category", owner_id=self.admin_user.id)
        self.product = Product.objects.create(name="Test Product", category=self.category, price=2, owner_id=self.admin_user.id)
        

    def test_product_list_authenticated(self):
        """Test that the product list is available for authenticated users."""
        self.authenticate(self.regular_user)
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_list_unauthenticated(self):
        """Test that the product list is available for unauthenticated users."""
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_create_admin(self):
        """Test that only an admin can create a product."""
        self.authenticate(self.admin_user)
        data = {
            "name": "New Product",
            "category": self.category.id,
            'price': 25,
			# ~ 'owner_id': self.admin_user.id,
            'description': "holocostatat"
            
        }
        print("dddd", data)
        
        response = self.client.post('/products/', data)
        print("response", response)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_product_create_non_admin(self):
        """Test that a non-admin cannot create a product."""
        self.authenticate(self.regular_user)
        data = {
            "name": "New Product",
            "category": self.category.id,
            'price': 2,
            # ~ 'owner_id': self.regular_user.id
            
        }
        response = self.client.post('/products/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_detail(self):
        """Test that the product detail is available to both authenticated and unauthenticated users."""
        response = self.client.get(f'/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_update_admin(self):
        """Test that only an admin can update a product."""
        self.authenticate(self.admin_user)
        data = {"price": 54, "owner_id": 1}
        response = self.client.patch(f'/products/{self.product.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_product_update_non_admin(self):
        """Test that a non-admin cannot update a product."""
        self.authenticate(self.regular_user)
        data = {"name": "Updated Product"}
        response = self.client.patch(f'/products/{self.product.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_delete_admin(self):
        """Test that only an admin can delete a product."""
        self.authenticate(self.admin_user)
        response = self.client.delete(f'/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_product_delete_non_admin(self):
        """Test that a non-admin cannot delete a product."""
        self.authenticate(self.regular_user)
        response = self.client.delete(f'/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
