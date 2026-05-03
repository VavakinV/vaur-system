from django.urls import path

from users.views import (
    LoginView,
    LogoutView,
    MeView,
    RefreshView,
    RegisterView,
    GroupView,
    UserDetailView,
    UserView,
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', RefreshView.as_view(), name='refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    path('groups/', GroupView.as_view(), name='groups'),
    path('groups/<int:pk>/', GroupView.as_view(), name='group'),
    path('users/<int:pk>/detail/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/', UserView.as_view(), name='user'),
]
