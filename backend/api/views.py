from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Disease, Symptom, Prediction
from .serializers import (
    DiseaseSerializer,
    DiseaseListSerializer,
    SymptomSerializer,
    PredictRequestSerializer,
)
from .ml.predictor import predictor, ALL_SYMPTOMS


class SymptomsListView(APIView):
    """GET /api/symptoms/ — Return all symptoms (DB + embedded ML list)."""

    def get(self, request):
        db_symptoms = Symptom.objects.all()
        if db_symptoms.exists():
            serializer = SymptomSerializer(db_symptoms, many=True)
            return Response(serializer.data)

        # Fall back to the embedded ML symptom list when DB is empty
        symptoms = [
            {"id": i + 1, "name": s.replace("_", " ").title(), "description": ""}
            for i, s in enumerate(ALL_SYMPTOMS)
        ]
        return Response(symptoms)


class DiseasesListView(APIView):
    """GET /api/diseases/ — Return all diseases."""

    def get(self, request):
        diseases = Disease.objects.all()
        serializer = DiseaseListSerializer(diseases, many=True)
        return Response(serializer.data)


class DiseaseDetailView(APIView):
    """GET /api/diseases/<pk>/ — Return a single disease with its symptoms."""

    def get(self, request, pk):
        try:
            disease = Disease.objects.get(pk=pk)
        except Disease.DoesNotExist:
            return Response(
                {"error": "Disease not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = DiseaseSerializer(disease)
        return Response(serializer.data)


class PredictDiseaseView(APIView):
    """POST /api/predict/ — Predict diseases from a list of symptoms."""

    def post(self, request):
        req_serializer = PredictRequestSerializer(data=request.data)
        if not req_serializer.is_valid():
            return Response(
                {"error": req_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        symptoms = req_serializer.validated_data["symptoms"]

        # Normalise symptom names for the ML model
        normalised = [s.strip().lower().replace(" ", "_") for s in symptoms]

        try:
            predictions = predictor.predict(normalised)
        except Exception as exc:  # pragma: no cover
            return Response(
                {"error": f"Prediction failed: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not predictions:
            return Response(
                {"error": "Unable to predict with the given symptoms."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Persist the top prediction if the disease exists in the DB
        top = predictions[0]
        predicted_disease_obj = Disease.objects.filter(name=top["disease"]).first()
        Prediction.objects.create(
            input_symptoms=symptoms,
            predicted_disease=predicted_disease_obj,
            confidence=top["confidence"],
        )

        return Response(
            {
                "symptoms": symptoms,
                "predictions": predictions,
            },
            status=status.HTTP_200_OK,
        )
