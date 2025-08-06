from django.urls import path
from . import views

app_name = 'shop_admin'

urlpatterns = [
    path('users/', views.AdminUserListView.as_view(), name='admin-user-list'),
    path('transactions/', views.AdminTransactionListView.as_view(), name='admin-transaction-list'),
    path('add-currency/', views.AdminAddCurrencyView.as_view(), name='admin-add-currency'),
] 