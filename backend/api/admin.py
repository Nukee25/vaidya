from django.contrib import admin
from .models import Symptom, Disease, Prediction


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    filter_horizontal = ('symptoms',)


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('predicted_disease', 'confidence', 'created_at')
    list_filter = ('predicted_disease',)
    readonly_fields = ('input_symptoms', 'predicted_disease', 'confidence', 'created_at')
