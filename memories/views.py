from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Memory, MemoryLike
from .serializers import MemorySerializer, MemoryLikeSerializer


class MemoryListView(generics.ListCreateAPIView):
    """
    List and create memories
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MemorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_public', 'visit_date']
    search_fields = ['title', 'content', 'tags']
    ordering_fields = ['created_at', 'visit_date', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Memory.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MemoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update and delete memory
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MemorySerializer
    
    def get_queryset(self):
        return Memory.objects.filter(user=self.request.user)


class PublicMemoriesView(generics.ListAPIView):
    """
    Get public memories
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MemorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['visit_date']
    search_fields = ['title', 'content', 'tags']
    ordering_fields = ['created_at', 'visit_date', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Memory.objects.filter(is_public=True)


class MemoryLikeView(generics.GenericAPIView):
    """
    Like/unlike a memory
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            memory = Memory.objects.get(pk=pk, is_public=True)
            is_liked = memory.toggle_like(request.user)
            return Response({
                'liked': is_liked,
                'like_count': memory.like_count
            })
        except Memory.DoesNotExist:
            return Response(
                {'error': 'Memory not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class MemorySearchView(generics.ListAPIView):
    """
    Search memories by tags
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MemorySerializer
    
    def get_queryset(self):
        tags = self.request.query_params.get('tags', '')
        if tags:
            return Memory.search_by_tags(tags, self.request.user)
        return Memory.objects.none() 