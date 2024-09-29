from django.urls import path
from Inventory_data.views import UserSignupView, UserLoginView, InventoryCreateItems, InventoryItemDetailView

urlpatterns = [
      path('signup/', UserSignupView.as_view(), name='signup'),
      path('loginup/', UserLoginView.as_view(), name='loginup'),
      path('InventoryCreateItems/', InventoryCreateItems.as_view(), name='InventoryCreateItems'),
      path('inventory/<int:pk>/', InventoryItemDetailView.as_view(), name='inventory_item_detail'),
]


