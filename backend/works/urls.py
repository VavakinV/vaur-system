from django.urls import path

from works.views import WorkDocumentView


urlpatterns = [
    path('<int:pk>/document/', WorkDocumentView.as_view(), name='work-document'),
]
