from django.urls import path
from .views import (
    LoginView,
    UserListView,
    UserDetailView,
    ChangePasswordView,
    ProfileView,
    LogoutView,
)

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),  
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
]