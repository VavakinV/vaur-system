from django.urls import path

from users.views import LoginView, LogoutView, MeView, RefreshView, RegisterView, GroupView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', RefreshView.as_view(), name='refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', MeView.as_view(), name='me'),
    path('groups/', GroupView.as_view(), name='groups'),
    path('groups/<int:pk>/', GroupView.as_view(), name='group')
]
