from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import time


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create(**params)


class PublicUserApiTest(TestCase):
    """Test the users API public, unauthenticated"""

    def setUp(self):
        self.client = APIClient()
        self.user_test = create_user(**{"email": "tesaaat@test.com", "password": "testestpass123"})

    def test_create_valid_user_successful(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'test@test.com',
            'password': 'password123',
            'name': 'test_name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
            'email': 'test@test.com',
            'password': 'password123',
            'name': 'test_name'
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'test@test.com',
            'password': 'pa',
            'name': 'test'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(email=payload['email'])
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        # payload = {"email": "test@test.com", "password": "testestpass123"}
        # u = create_user(**payload)
       
        res = self.client.post(TOKEN_URL, {'email': self.user_test.email, 'password': self.user_test.password})
        
        print(res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains('token', res.data)
       

    def test_create_invalid_credentials(self):
        """Test that token is not created when invalid credentials provided"""
         
        create_user(email='carlos@test.com', password='password123123')
        res = self.client.post(TOKEN_URL, {'email':'carlos@test.com', 'password': 'wrongpass'})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_token_no_user(self):
        """Test that no token is created if there is no user with credentials"""
        payload = {'email':'carlos@test.com', 'password': 'wrongpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_token_missing_field(self):
        """Test no token is created when request missing fields is made"""
        payload = {'email': 'carlos', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)