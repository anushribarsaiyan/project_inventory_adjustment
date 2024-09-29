from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSignupSerializer, InventoryItemSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import InventoryItem
from django.core.cache import cache
import logging

# Setting up logging
logger = logging.getLogger(__name__)

class UserSignupView(APIView):
    permission_classes = [AllowAny] 

    def post(self, request):
        logger.info("User signup attempt.")
        serializer = UserSignupSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            logger.info("User created successfully.")
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        
        logger.error("User signup failed: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("User login attempt.")
        username = request.data.get("username")
        password = request.data.get("password")
        
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            refresh = RefreshToken.for_user(user)
            logger.info("User logged in successfully: %s", username)
            return Response({
                'refresh_token': str(refresh),
                'access_token': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        else:
            logger.warning("Invalid credentials for user: %s", username)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class InventoryCreateItems(APIView):
    # permission_classes = [AllowAny] 
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        logger.info("Received request to create an inventory item.")
        serializer = InventoryItemSerializer(data=request.data)
        
        if serializer.is_valid():
            item = serializer.save()
            cache.set(f'inventory_item_{item.id}', serializer.data, timeout=60 * 5)  
            cache.delete('inventory_items_all')
            logger.info("Inventory item created: %s", item.name)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        logger.error("Failed to create inventory item: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        logger.info("Received request to list inventory items.")
        try:
            cached_items = cache.get('inventory_items_all')
            if cached_items is not None:
                logger.info("Returning cached inventory items.")
                return Response(cached_items, status=status.HTTP_200_OK)

            items = InventoryItem.objects.all()
            serializer = InventoryItemSerializer(items, many=True)
            cache.set('inventory_items_all', serializer.data, timeout=60 * 5)  # Cache for 5 minutes
            logger.info("Inventory items fetched from the database.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error("Error fetching inventory items: %s", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InventoryItemDetailView(APIView):
    # permission_classes = [AllowAny] 
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self, pk):
        try:
            return InventoryItem.objects.get(pk=pk)
        except InventoryItem.DoesNotExist:
            logger.warning("Inventory item not found: %s", pk)
            return None

    def get(self, request, pk):
        logger.info("Received request for inventory item detail: %s", pk)
        try:
            cached_item = cache.get(f'inventory_item_{pk}')
            if cached_item is not None:
                logger.info("Returning cached inventory item: %s", pk)
                return Response(cached_item, status=status.HTTP_200_OK)

            item = self.get_object(pk)
            if item is not None:
                serializer = InventoryItemSerializer(item)
                cache.set(f'inventory_item_{pk}', serializer.data, timeout=60 * 5)  
                logger.info("Inventory item found: %s", item.name)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error("Error fetching inventory item: %s", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        logger.info("Received request to update inventory item: %s", pk)
        item = self.get_object(pk)
        
        if item is not None:
            serializer = InventoryItemSerializer(item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                cache.delete(f'inventory_item_{pk}')
                cache.delete('inventory_items_all')
                cache.set(f'inventory_item_{pk}', serializer.data, timeout=60 * 5) 
                logger.info("Inventory item updated: %s", item.name)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            logger.error("Failed to update inventory item: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        logger.warning("Attempted to update non-existent inventory item: %s", pk)
        return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        logger.info("Received request to delete inventory item: %s", pk)
        item = self.get_object(pk)
        
        if item is not None:
            item.delete()
            cache.delete(f'inventory_item_{pk}')
            cache.delete('inventory_items_all')
            logger.info("Inventory item deleted: %s", pk)
            return Response({"message": "Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        
        logger.warning("Attempted to delete non-existent inventory item: %s", pk)
        return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
