from django.contrib.auth.models import User
from rest_framework import serializers

from .models import DiagnosisReport


class SignupSerializer(serializers.Serializer):
    email_id = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email_id(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)


class PredictSerializer(serializers.Serializer):
    symptom_cards = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False,
    )
    medical_image = serializers.FileField(required=False, allow_null=True)
    gender = serializers.ChoiceField(
        choices=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
            ("prefer_not_to_say", "Prefer not to say"),
        ],
        required=False,
        allow_null=True,
    )
    age = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=150)


class ReportListSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(source="created_at")

    class Meta:
        model = DiagnosisReport
        fields = ["id", "date", "summary", "status"]


class ReportDetailSerializer(serializers.ModelSerializer):
    whenToSeeDoctor = serializers.CharField(source="when_to_see_doctor")
    additionalInfo = serializers.CharField(source="additional_info")
    medicalImage = serializers.FileField(source="medical_image", read_only=True)

    class Meta:
        model = DiagnosisReport
        fields = [
            "diagnosis",
            "predicted_diseases",
            "severity",
            "symptoms",
            "recommendations",
            "precautions",
            "medications",
            "whenToSeeDoctor",
            "additionalInfo",
            "user_symptoms",
            "symptom_cards",
            "medicalImage",
        ]
