from django.urls import path

from users.views import DepartmentListView, GroupView, MeView, TeachersByDepartmentView, UserDetailView, UserView


urlpatterns = [
    path('groups/', GroupView.as_view(), name='groups'),
    path('groups/<int:pk>/', GroupView.as_view(), name='group'),
    path('users/<int:pk>/detail/', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/', UserView.as_view(), name='user'),
    path('users/me/', MeView.as_view(), name='me'),
    path('departments/', DepartmentListView.as_view(), name='departments'),
    path('departments/<int:pk>/teachers/', TeachersByDepartmentView.as_view(), name='department-teachers'),
]
