from django.urls import path

from works.views import (
    WorkDetailView,
    WorkDocumentView,
    WorkListView,
    WorkRequestListCreateView,
    WorkRequestUpdateView,
    WorkShortView,
    WorkTypeListView,
)


urlpatterns = [
    path('', WorkListView.as_view(), name='work-list'),
    path('types/', WorkTypeListView.as_view(), name='work-types'),
    path('requests/', WorkRequestListCreateView.as_view(), name='work-requests'),
    path('requests/<int:pk>/', WorkRequestUpdateView.as_view(), name='work-request-detail'),
    path('<int:pk>/', WorkShortView.as_view(), name='work-short'),
    path('<int:pk>/detail/', WorkDetailView.as_view(), name='work-detail'),
    path('<int:pk>/document/', WorkDocumentView.as_view(), name='work-document'),
]
