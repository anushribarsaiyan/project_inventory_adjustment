from django.urls import reverse
from  rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import InventoryItem


User = get_user_model()

class UserApiTests(APITestCase):
    def setUp(self):
        self.sigup_url = reverse('signup')
        self.login_url = reverse('loginup')

        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_sinup(self):
        data ={
            'username':'password',
            'password':'new password'   
        }

        response = self.client.post(self.sigup_url, data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertIn("User created successfully", response.data.values())

    def test_user_login(self):
        data = {
            'username': self.user_data['username'],
            'password': self.user_data['password'],

        }

        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh_token", response.data)

    def test_invlaid_login_(self):
        data = {
            'username':'invlaiduser',
            'password':'invlaidpassword'  
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid credentials", response.data.values())



class InventoryAPITests(APITestCase):

    def setUp(self):
        self.create_inventory_url = reverse('InventoryCreateItems') 
        self.item_detail_url = lambda pk: reverse('inventory_item_detail', kwargs={'pk': pk}) 
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        self.user = User.objects.create_user(**self.user_data)
        self.client.login(username=self.user_data['username'], password=self.user_data['password'])


    def test_create_inventory_item(self):
        data = {
            'name': 'Test Item',
            'description': 'Test Description',
        }
        response = self.client.post(self.create_inventory_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Test Item", response.data.values())
    
    def test_list_inventory_items(self):
       
        self.test_create_inventory_item()
        response = self.client.get(self.create_inventory_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  

    def test_get_inventory_item_detail(self):
      
        response = self.client.post(self.create_inventory_url, {
            'name': 'Test Item',
            'description': 'Test Description',
        })

        item_id = response.data['id']
        
        response = self.client.get(self.item_detail_url(item_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Test Item", response.data.values())


    def test_update_inventory_item(self):
        response = self.client.post(self.create_inventory_url, {
            'name': 'Test Item',
            'description': 'Test Description',

        })
        item_id = response.data['id']
        
        update_data = {
            'name': 'Updated Test Item',
            'description': 'Updated Description',
           
        }
        response = self.client.put(self.item_detail_url(item_id), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Updated Test Item", response.data.values())

    def test_delete_inventory_item(self):
        response = self.client.post(self.create_inventory_url, {
            'name': 'Test Item',
            'description': 'Test Description',
          
        })
        item_id = response.data['id']
        
        response = self.client.delete(self.item_detail_url(item_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.item_detail_url(item_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


   