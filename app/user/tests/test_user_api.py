from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from pyrsistent import T

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

def create_user(**params):
    """Helper function"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Tests the user api(public)"""
    
    def setUp(self):
        self.client = APIClient()
        
    def test_create_valid_user_success(self):
        """Test creating a valid user"""
        payload = {
            'email': 'test@example.com',
            'password': 'test123',
            'name': 'test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password'
        ]))
        self.assertNotIn('password', res.data)
    
    def test_user_exists(self):
        """Test that if user exists it fails"""
        payload = {'email': 'test@example.com', 'password': 'testpassword'}
        create_user(**payload)
        
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_password_too_short(self):
        """Pass must be more than 5 characters long"""
        payload = {'email': 'test@example.com', 'password': 'test'}
        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)
        
    def test_create_token_for_user(self):
        payload = {'email': 'test@example.com', 'password': 'testpassword'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        
    def test_create_token_invalid(self):
        """Test that token is not created if the credentials are invalid"""
        create_user(email='test@example.com', password='testpassword')
        payload = {'email': 'test@example.com', 'password': 'testpasswordBAD'}
        res = self.client.post(TOKEN_URL, payload)
        
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_create_token_not_user(self):
        """Test that token is not created if the user does not exists"""
        payload = {'email': 'test@example.com', 'password': 'testpassword'}
        res = self.client.post(TOKEN_URL, payload)
        
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_token_missing_field(self):
        """Test that email and password fields are required."""
        res = self.client.post(TOKEN_URL, {'email': 'test@example.com', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_retrieve_user_unautorized(self):
        """Test that authentication is required"""
        res = self.client.get(ME_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Tests for apis requiests that requiere authorization"""
    
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpassword',
            name='name'
        )
    
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_profile_success(self):
        """Test that retrieves the profile for a logged in user"""
        res = self.client.get(ME_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })
        
    def test_post_not_allowed(self):
        """Test that post is not allowed on the me url"""
        res = self.client.post(ME_URL, {})
        
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
    def test_update_user_profile(self):
        """Test updating user profile"""
        payload = {'name': 'new name', 'password': 'new password'}
        res = self.client.patch(ME_URL, payload)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    