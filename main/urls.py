from django.urls import path

from .views import WordByIdRetrieveAPIView, WordByExternalIdRetrieveAPIView

urlpatterns = [
    path(
        'words/<int:pk>/',
        WordByIdRetrieveAPIView.as_view(),
        name='word_by_id',
    ),
    path(
        'words/<str:direction>/<int:external_id>/',
        WordByExternalIdRetrieveAPIView.as_view(),
        name='word_by_external_id',
    ),
]
