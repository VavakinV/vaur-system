from django.urls import path

from works.views import (
    WorkCorrectionListCreateView,
    WorkCorrectionUpdateView,
    WorkDetailView,
    WorkDocumentView,
    WorkListView,
    WorkRequestAcceptView,
    WorkRequestListCreateView,
    WorkRequestMyView,
    WorkRequestRejectView,
    WorkRequestUpdateView,
    WorkShortView,
    WorkTypeListView,
    WorkUserView,
)


urlpatterns = [
    path('', WorkListView.as_view(), name='work-list'),
    path('types/', WorkTypeListView.as_view(), name='work-types'),
    path('requests/', WorkRequestListCreateView.as_view(), name='work-requests'),
    path('requests/my/', WorkRequestMyView.as_view(), name='work-requests-my'),
    path('requests/<int:pk>/', WorkRequestUpdateView.as_view(), name='work-request-detail'),
    path('requests/<int:pk>/accept/', WorkRequestAcceptView.as_view(), name='work-request-accept'),
    path('requests/<int:pk>/reject/', WorkRequestRejectView.as_view(), name='work-request-reject'),
    path('user/<int:user_id>/', WorkUserView.as_view(), name='work-user'),
    path('corrections/<int:correction_id>/', WorkCorrectionUpdateView.as_view(), name='work-correction-update'),
    path('<int:pk>/', WorkShortView.as_view(), name='work-short'),
    path('<int:pk>/detail/', WorkDetailView.as_view(), name='work-detail'),
    path('<int:pk>/document/', WorkDocumentView.as_view(), name='work-document'),
    path('<int:pk>/corrections/', WorkCorrectionListCreateView.as_view(), name='work-corrections'),
]
