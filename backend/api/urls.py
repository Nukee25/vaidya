from django.urls import path
from .views import (
    SymptomsListView,
    DiseasesListView,
    DiseaseDetailView,
    PredictDiseaseView,
)

urlpatterns = [
    path('symptoms/', SymptomsListView.as_view(), name='symptoms-list'),
    path('diseases/', DiseasesListView.as_view(), name='diseases-list'),
    path('diseases/<int:pk>/', DiseaseDetailView.as_view(), name='disease-detail'),
    path('predict/', PredictDiseaseView.as_view(), name='predict-disease'),
]
