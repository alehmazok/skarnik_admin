from django.urls import path

from .views import get_word_by_id, get_word_by_external_id

urlpatterns = [
    path('words/<int:word_id>/', get_word_by_id, name='get_word_by_id'),
    path('words/<str:direction>/<int:external_id>/', get_word_by_external_id, name='get_word_by_external_id'),
]
