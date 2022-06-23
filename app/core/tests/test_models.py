from random import sample
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def sample_user(email='test@example.com', password='testpassword'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a user with email is successful"""
        email = 'test@example.com'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the new user email is normalized"""
        email = 'test@EXAMPLE.com'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Error when creating a new user with no email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')
            
    def test_create_new_superuser(self):
        """Create a new superuser test"""
        user = get_user_model().objects.create_superuser('test@example.com', 'test123')
        
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        
    def test_tag_str(self):
        """Test that that the tag string is correct"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegetarian'
        )
        
        self.assertEqual(str(tag), tag.name)