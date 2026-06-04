from django.urls import path

from works.views import UserWorksView, WorkDetailView, WorkDocumentView, WorkShortView


urlpatterns = [
    path('user/<int:user_pk>/', UserWorksView.as_view(), name='user-works'),
    path('<int:pk>/', WorkShortView.as_view(), name='work-short'),
    path('<int:pk>/detail/', WorkDetailView.as_view(), name='work-detail'),
    path('<int:pk>/document/', WorkDocumentView.as_view(), name='work-document'),
]
