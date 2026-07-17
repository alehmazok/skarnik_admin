from django.urls import path

from .views import (
    StressWordListAPIView,
    StressWordRetrieveAPIView,
    WordByIdRetrieveAPIView,
    WordByExternalIdRetrieveAPIView,
)

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
    path(
        'stress_words/',
        StressWordListAPIView.as_view(),
        name='stress_word_list',
    ),
    path(
        'stress_words/<int:pk>/',
        StressWordRetrieveAPIView.as_view(),
        name='stress_word_detail',
    ),
]
