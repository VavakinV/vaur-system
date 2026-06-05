from django.urls import path

from works.views import MyWorkRequestsView, UserWorksView, WorkDetailView, WorkDocumentView, WorkRequestAcceptView, WorkRequestCreateView, WorkRequestRejectView, WorkShortView, WorkTypeListView


urlpatterns = [
    path('types/', WorkTypeListView.as_view(), name='work-type-list'),
    path('requests/my/', MyWorkRequestsView.as_view(), name='my-work-requests'),
    path('requests/<int:pk>/accept/', WorkRequestAcceptView.as_view(), name='work-request-accept'),
    path('requests/<int:pk>/reject/', WorkRequestRejectView.as_view(), name='work-request-reject'),
    path('requests/', WorkRequestCreateView.as_view(), name='work-request-create'),
    path('user/<int:user_pk>/', UserWorksView.as_view(), name='user-works'),
    path('<int:pk>/', WorkShortView.as_view(), name='work-short'),
    path('<int:pk>/detail/', WorkDetailView.as_view(), name='work-detail'),
    path('<int:pk>/document/', WorkDocumentView.as_view(), name='work-document'),
]
