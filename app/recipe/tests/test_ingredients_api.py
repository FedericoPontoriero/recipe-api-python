from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

class PublicIngredientsApiTests(TestCase):
    """Test public ingredients api"""
    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test login required"""
        res = self.client.get(INGREDIENTS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    

class PrivateIngredientsApiTest(TestCase):
    """Test private ingredients api"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'testpassword'
        )
        self.client.force_authenticate(self.user)
    
    def test_retrieve_ingredient_list(self):
        """Test retrieving the list of ingredients"""
        Ingredient.objects.create(user=self.user, name='pepe')
        Ingredient.objects.create(user=self.user, name='pepa')
        
        res = self.client.get(INGREDIENTS_URL)
        
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_ingredients_limited_to_user(self):
        """Test that the ingredients for the user are returned when authenticated"""
        user2 = get_user_model().objects.create_user(
            'othertest@example.com',
            'otherpassword'
        )
        Ingredient.objects.create(user=user2, name='Lettuce')
        
        ingredient = Ingredient.objects.create(user=self.user, name='Olive oil')
        res = self.client.get(INGREDIENTS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        
    def test_create_ingredients_successfull(self):
        """Test creating a new ingredient"""
        payload = {'name': 'Apple'}
        self.client.post(INGREDIENTS_URL, payload)
        
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)
        
    def test_create_ingredients_failed(self):
        """Test failing to create a new ingredient"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)