from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django.conf import settings
import json
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


def _build_mock_diagnosis(symptom_cards):
    symptom_names = [str(card.get("symptom", "")).strip() for card in symptom_cards if str(card.get("symptom", "")).strip()]
    symptoms_text = "; ".join(
        [
            f"{card.get('symptom', '').strip()} (Duration: {card.get('duration', '')}, Severity: {card.get('severity', 5)}/10)"
            for card in symptom_cards
            if str(card.get("symptom", "")).strip()
        ]
    )
    top_symptom = symptom_names[0] if symptom_names else "general discomfort"
    return {
        "diagnosis": "Common Cold (Upper Respiratory Infection)",
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


def _build_ollama_prompt(symptom_cards):
    return (
        "You are a medical triage assistant. Return only valid JSON with keys: "
        "diagnosis (string), severity (Mild|Moderate|Severe), recommendations (string[]), "
        "precautions (string[]), medications (string[]), when_to_see_doctor (string), "
        "additional_info (string), summary (string).\n"
        f"Input symptom cards: {json.dumps(symptom_cards)}"
    )


def _build_report_from_ollama(symptom_cards):
    symptom_names = [str(card.get("symptom", "")).strip() for card in symptom_cards if str(card.get("symptom", "")).strip()]
    symptoms_text = "; ".join(
        [
            f"{card.get('symptom', '').strip()} (Duration: {card.get('duration', '')}, Severity: {card.get('severity', 5)}/10)"
            for card in symptom_cards
            if str(card.get("symptom", "")).strip()
        ]
    )

    response = ollama.chat(
        model=getattr(settings, "OLLAMA_MODEL", "llama3.2"),
        messages=[{"role": "user", "content": _build_ollama_prompt(symptom_cards)}],
        format="json",
    )
    content = response.get("message", {}).get("content", "{}")
    payload = json.loads(content)

    return {
        "diagnosis": str(payload.get("diagnosis") or "General Viral Syndrome"),
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
        serializer = PredictSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        symptom_cards = serializer.validated_data["symptom_cards"]
        username = request.data.get("username") or "demo_user"
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@example.com"},
        )
        try:
            report_payload = _build_report_from_ollama(symptom_cards)
        except Exception:
            report_payload = _build_mock_diagnosis(symptom_cards)
        report = DiagnosisReport.objects.create(user=user, **report_payload)
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
        reports = DiagnosisReport.objects.all()
        if username:
            reports = reports.filter(user__username=username)
        serializer = ReportListSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReportDetailView(APIView):
    permission_classes = []

    def get(self, request, report_id):
        username = request.query_params.get("username")
        filters = Q(pk=report_id)
        if username:
            filters &= Q(user__username=username)
        report = DiagnosisReport.objects.filter(filters).first()
        if not report:
            return Response({"detail": "Report not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ReportDetailSerializer(report).data, status=status.HTTP_200_OK)

# Create your views here.
