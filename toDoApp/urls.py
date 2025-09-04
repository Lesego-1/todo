from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import SignUpView, TaskListCreateView, TaskRetrieveUpdateDestroyView

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path("signup/", SignUpView.as_view(), name='signup'),
    path("tasks/", TaskListCreateView.as_view(), name='task-list-create'),
    path("tasks/<int:pk>/", TaskRetrieveUpdateDestroyView.as_view(), name='task-update'),
]