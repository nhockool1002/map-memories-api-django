from django.urls import path
from . import views

app_name = 'currency'

urlpatterns = [
    path('balance/', views.CurrencyBalanceView.as_view(), name='currency-balance'),
    path('transactions/', views.TransactionHistoryView.as_view(), name='transaction-history'),
] 