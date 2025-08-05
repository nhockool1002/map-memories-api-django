from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('items/', views.ShopItemListView.as_view(), name='shop-item-list'),
    path('items/<int:pk>/', views.ShopItemDetailView.as_view(), name='shop-item-detail'),
    path('purchase/', views.PurchaseItemView.as_view(), name='purchase-item'),
    path('inventory/', views.UserInventoryView.as_view(), name='user-inventory'),
] 