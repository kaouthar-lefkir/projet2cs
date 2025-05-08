from django.urls import path
from .views import (
    LoginView,
    UserListView,
    UserDetailView,
    ChangePasswordView,
    ProfileView
)

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
]