from rest_framework import serializers
from .models import Symptom, Disease, Prediction


class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = ['id', 'name', 'description']


class DiseaseSerializer(serializers.ModelSerializer):
    symptoms = SymptomSerializer(many=True, read_only=True)

    class Meta:
        model = Disease
        fields = ['id', 'name', 'description', 'symptoms', 'precautions']


class DiseaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = ['id', 'name', 'description']


class PredictionSerializer(serializers.ModelSerializer):
    predicted_disease = DiseaseSerializer(read_only=True)

    class Meta:
        model = Prediction
        fields = ['id', 'input_symptoms', 'predicted_disease', 'confidence', 'created_at']


class PredictRequestSerializer(serializers.Serializer):
    symptoms = serializers.ListField(
        child=serializers.CharField(max_length=100),
        min_length=1,
        max_length=50,
    )
