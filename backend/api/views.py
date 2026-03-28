import json
import logging

from django.contrib.auth import authenticate
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
import ollama
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DiagnosisReport
from .serializers import (
    LoginSerializer,
    PredictSerializer,
    ReportDetailSerializer,
    ReportListSerializer,
    SignupSerializer,
)

logger = logging.getLogger(__name__)
MAX_REPORTS_FOR_HEALTH_SCORE = 10
UNKNOWN_SEVERITY_SCORE = 75


def _calculate_health_score(reports):
    if not reports:
        return 85
    severity_to_score = {
        "mild": 90,
        "moderate": 70,
        "severe": 40,
    }
    values = [severity_to_score.get(str(report.severity).strip().lower(), UNKNOWN_SEVERITY_SCORE) for report in reports]
    return round(sum(values) / len(values))


def _normalized_symptom_cards(symptom_cards):
    return [card for card in symptom_cards if str(card.get("symptom", "")).strip()]


def _build_mock_diagnosis(symptom_cards):
    valid_cards = _normalized_symptom_cards(symptom_cards)
    symptom_names = [str(card.get("symptom", "")).strip() for card in valid_cards]
    symptoms_text = "; ".join(
        [
            f"{card.get('symptom', '').strip()} (Duration: {card.get('duration', '')}, Severity: {card.get('severity', 5)}/10)"
            for card in valid_cards
        ]
    )
    top_symptom = symptom_names[0] if symptom_names else "general discomfort"
    return {
        "diagnosis": "Common Cold (Upper Respiratory Infection)",
        "predicted_diseases": [
            {"disease": "Common Cold (Upper Respiratory Infection)", "probability": 65},
            {"disease": "Seasonal Allergic Rhinitis", "probability": 22},
            {"disease": "Influenza", "probability": 13},
        ],
        "severity": "Mild",
        "symptoms": symptom_names
        or [
            "Runny or stuffy nose",
            "Sore throat",
            "Cough",
        ],
        "recommendations": [
            "Get plenty of rest and sleep",
            "Stay hydrated by drinking lots of water, warm tea, or soup",
            "Use a humidifier to ease congestion",
        ],
        "precautions": [
            "Wash hands frequently with soap and water",
            "Avoid close contact with others to prevent spreading",
            "Cover your mouth and nose when coughing or sneezing",
        ],
        "medications": [
            "Acetaminophen or ibuprofen for pain and fever",
            "Cough suppressant if needed",
        ],
        "when_to_see_doctor": (
            "Seek medical attention if symptoms worsen, fever exceeds 101.3°F (38.5°C) for more than 3 days, "
            "difficulty breathing, severe headache, or symptoms persist beyond 10 days."
        ),
        "additional_info": (
            f"Based on the provided symptom '{top_symptom}', this appears to be a mild self-limiting illness. "
            "Consult a doctor for persistent or worsening symptoms."
        ),
        "user_symptoms": symptoms_text,
        "symptom_cards": symptom_cards,
        "summary": "Respiratory symptoms analysis",
        "status": "completed",
    }


def _build_ollama_prompt(symptom_cards, gender=None, age=None):
    demographics = []
    if gender is not None:
        demographics.append(f"Gender: {gender}")
    if age is not None:
        demographics.append(f"Age: {age}")
    demographics_text = f"Patient demographics: {', '.join(demographics)}.\n" if demographics else ""
    return (
        "You are a medical triage assistant. Return only valid JSON with keys: "
        "predicted_diseases (array of at least 3 items with keys disease (string) and probability (number in percent)), "
        "diagnosis (string), severity (Mild|Moderate|Severe), recommendations (string[]), "
        "precautions (string[]), medications (string[]), when_to_see_doctor (string), "
        "additional_info (string), summary (string).\n"
        f"{demographics_text}"
        f"Input symptom cards: {json.dumps(symptom_cards)}"
    )


def _normalize_predicted_diseases(raw_predictions, diagnosis_fallback):
    normalized = []
    if isinstance(raw_predictions, list):
        for item in raw_predictions:
            if not isinstance(item, dict):
                continue
            disease = str(item.get("disease") or item.get("diagnosis") or "").strip()
            if not disease:
                continue
            try:
                probability = float(item.get("probability", 0))
            except (TypeError, ValueError):
                probability = 0.0
            probability = max(0.0, min(100.0, probability))
            normalized.append(
                {
                    "disease": disease,
                    "probability": round(probability, 2),
                }
            )
            if len(normalized) == 3:
                break
    if len(normalized) < 3:
        defaults = _build_mock_diagnosis([])["predicted_diseases"]
        default_seed = defaults[0]["disease"] if defaults else "General Viral Syndrome"
        seed = diagnosis_fallback or (normalized[0]["disease"] if normalized else default_seed)
        fallback_predictions = [{"disease": seed, "probability": 60}] + defaults
        for candidate in fallback_predictions:
            if len(normalized) == 3:
                break
            if any(existing["disease"].lower() == candidate["disease"].lower() for existing in normalized):
                continue
            normalized.append(candidate)
    return normalized[:3]


def _build_report_from_ollama(symptom_cards, gender=None, age=None):
    valid_cards = _normalized_symptom_cards(symptom_cards)
    symptom_names = [str(card.get("symptom", "")).strip() for card in valid_cards]
    symptoms_text = "; ".join(
        [
            f"{card.get('symptom', '').strip()} (Duration: {card.get('duration', '')}, Severity: {card.get('severity', 5)}/10)"
            for card in valid_cards
        ]
    )

    response = ollama.chat(
        model=getattr(settings, "OLLAMA_MODEL", "qwen3.5:397b-cloud"),
        messages=[{"role": "user", "content": _build_ollama_prompt(symptom_cards, gender=gender, age=age)}],
        format="json",
    )
    content = response.get("message", {}).get("content", "{}")
    payload = json.loads(content)
    diagnosis = str(payload.get("diagnosis") or "General Viral Syndrome")
    predicted_diseases = _normalize_predicted_diseases(payload.get("predicted_diseases"), diagnosis)

    return {
        "diagnosis": diagnosis,
        "predicted_diseases": predicted_diseases,
        "severity": str(payload.get("severity") or "Mild"),
        "symptoms": symptom_names,
        "recommendations": payload.get("recommendations") or [],
        "precautions": payload.get("precautions") or [],
        "medications": payload.get("medications") or [],
        "when_to_see_doctor": str(payload.get("when_to_see_doctor") or ""),
        "additional_info": str(payload.get("additional_info") or ""),
        "user_symptoms": symptoms_text,
        "symptom_cards": symptom_cards,
        "summary": str(payload.get("summary") or "Medical diagnosis report"),
        "status": "completed",
    }


class SignupView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(
            username=serializer.validated_data["username"],
            email=serializer.validated_data["email_id"],
            password=serializer.validated_data["password"],
        )
        return Response(
            {
                "message": "Account created successfully",
                "user": {"id": user.id, "username": user.username, "email_id": user.email},
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if not user:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"message": "Login successful", "username": user.username}, status=status.HTTP_200_OK)


class PredictView(APIView):
    permission_classes = []

    def post(self, request):
        serializer_payload = {
            "symptom_cards": request.data.get("symptom_cards"),
            "medical_image": request.data.get("medical_image"),
            "gender": request.data.get("gender"),
            "age": request.data.get("age"),
        }
        if isinstance(serializer_payload["symptom_cards"], str):
            try:
                serializer_payload["symptom_cards"] = json.loads(serializer_payload["symptom_cards"])
            except (TypeError, ValueError, json.JSONDecodeError):
                pass
        serializer = PredictSerializer(data=serializer_payload)
        serializer.is_valid(raise_exception=True)
        symptom_cards = serializer.validated_data["symptom_cards"]
        medical_image = serializer.validated_data.get("medical_image")
        gender = serializer.validated_data.get("gender")
        age = serializer.validated_data.get("age")
        username = request.data.get("username")
        if not username:
            return Response({"detail": "username is required"}, status=status.HTTP_400_BAD_REQUEST)
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@example.com"},
        )
        try:
            report_payload = _build_report_from_ollama(symptom_cards, gender=gender, age=age)
        except (ConnectionError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            logger.exception("Ollama report generation failed; falling back to mock diagnosis.")
            report_payload = _build_mock_diagnosis(symptom_cards)
        report = DiagnosisReport.objects.create(
            user=user,
            medical_image=medical_image,
            gender=gender,
            age=age,
            **report_payload,
        )
        response = ReportDetailSerializer(report).data
        response["id"] = report.id
        response["date"] = report.created_at
        response["summary"] = report.summary
        response["status"] = report.status
        return Response(response, status=status.HTTP_201_CREATED)


class ReportsView(APIView):
    permission_classes = []

    def get(self, request):
        username = request.query_params.get("username")
        if not username:
            return Response({"detail": "username query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        reports = DiagnosisReport.objects.filter(user__username=username)
        serializer = ReportListSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HealthScoreView(APIView):
    permission_classes = []

    def get(self, request):
        username = request.query_params.get("username")
        if not username:
            return Response({"detail": "username query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(username=username).first()
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        reports = DiagnosisReport.objects.filter(user=user)[:MAX_REPORTS_FOR_HEALTH_SCORE]
        return Response({"score": _calculate_health_score(reports)}, status=status.HTTP_200_OK)


class ReportDetailView(APIView):
    permission_classes = []

    def get(self, request, report_id):
        username = request.query_params.get("username")
        if not username:
            return Response({"detail": "username query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        filters = Q(pk=report_id)
        filters &= Q(user__username=username)
        report = DiagnosisReport.objects.filter(filters).first()
        if not report:
            return Response({"detail": "Report not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ReportDetailSerializer(report).data, status=status.HTTP_200_OK)

# Create your views here.
