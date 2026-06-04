from django.urls import path

from works.views import WorkDetailView, WorkDocumentView, WorkShortView


urlpatterns = [
    path('<int:pk>/', WorkShortView.as_view(), name='work-short'),
    path('<int:pk>/detail/', WorkDetailView.as_view(), name='work-detail'),
    path('<int:pk>/document/', WorkDocumentView.as_view(), name='work-document'),
]
