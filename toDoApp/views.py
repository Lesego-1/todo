from .models import Task
from .serializers import TaskSerializer, SignUpSerializer
from rest_framework import generics, status, pagination
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters import rest_framework as filters

class TaskPaginator(pagination.PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 18
    
class TaskFilter(filters.FilterSet):
    title  = filters.CharFilter(field_name="title", lookup_expr="icontains")
    due_date = filters.DateFilter(field_name="due_date", lookup_expr="exact")
    completed = filters.BooleanFilter()
    
    class Meta:
        model = Task
        fields = ['title', 'due_date', 'completed']

User = get_user_model()
class SignUpView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'User created successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TaskPaginator
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = TaskFilter
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TaskPaginator
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = TaskFilter
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)