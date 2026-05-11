from django.urls import path

from users.views import GroupView, UserDetailView, UserView, MeView


urlpatterns = [
    path('groups/', GroupView.as_view(), name='groups'),
    path('groups/<int:pk>/', GroupView.as_view(), name='group'),
    path('users/<int:pk>/detail/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/', UserView.as_view(), name='user'),
    path('users/me', MeView.as_view(), name='me'),
]
