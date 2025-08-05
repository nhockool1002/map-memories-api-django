from django.urls import path
from . import views

app_name = 'memories'

urlpatterns = [
    path('', views.MemoryListView.as_view(), name='memory-list'),
    path('<int:pk>/', views.MemoryDetailView.as_view(), name='memory-detail'),
    path('public/', views.PublicMemoriesView.as_view(), name='public-memories'),
    path('<int:pk>/like/', views.MemoryLikeView.as_view(), name='memory-like'),
    path('search/', views.MemorySearchView.as_view(), name='memory-search'),
] 