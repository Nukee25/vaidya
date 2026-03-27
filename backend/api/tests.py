import os
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import DiagnosisReport


class AuthAndReportsApiTests(APITestCase):
    def test_signup_login_predict_and_report_flow(self):
        signup_res = self.client.post(
            reverse("signup"),
            {"email_id": "user@example.com", "username": "john", "password": "strongpass123"},
            format="json",
        )
        self.assertEqual(signup_res.status_code, status.HTTP_201_CREATED)

        login_res = self.client.post(
            reverse("login"),
            {"username": "john", "password": "strongpass123"},
            format="json",
        )
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.assertEqual(login_res.data["username"], "john")

        predict_res = self.client.post(
            reverse("predict"),
            {
                "username": "john",
                "symptom_cards": [
                    {"symptom": "Fever", "duration": "1-2 days", "severity": 7},
                    {"symptom": "Cough", "duration": "3-5 days", "severity": 5},
                ],
            },
            format="json",
        )
        self.assertEqual(predict_res.status_code, status.HTTP_201_CREATED)
        report_id = predict_res.data["id"]

        list_res = self.client.get(reverse("reports"), {"username": "john"})
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_res.data), 1)
        self.assertEqual(list_res.data[0]["id"], report_id)

        detail_res = self.client.get(reverse("report-detail", kwargs={"report_id": report_id}), {"username": "john"})
        self.assertEqual(detail_res.status_code, status.HTTP_200_OK)
        self.assertIn("diagnosis", detail_res.data)
        self.assertEqual(detail_res.data["symptoms"], ["Fever", "Cough"])
        self.assertGreaterEqual(len(detail_res.data["predicted_diseases"]), 3)

    def test_predict_requires_symptom_cards(self):
        res = self.client.post(reverse("predict"), {"username": "john"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_predict_requires_username(self):
        res = self.client.post(
            reverse("predict"),
            {"symptom_cards": [{"symptom": "Fever", "duration": "1 day", "severity": 5}]},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_report_detail_not_found(self):
        User.objects.create_user(username="alice", email="alice@example.com", password="pass12345")
        res = self.client.get(reverse("report-detail", kwargs={"report_id": 999}), {"username": "alice"})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_report_endpoints_require_username_query_param(self):
        user = User.objects.create_user(username="alice", password="pass12345")
        report = DiagnosisReport.objects.create(
            user=user,
            diagnosis="Diagnosis A",
            severity="Mild",
            symptoms=["Cough"],
            recommendations=["Rest"],
            precautions=["Hydrate"],
            summary="A report",
        )

        list_res = self.client.get(reverse("reports"))
        self.assertEqual(list_res.status_code, status.HTTP_400_BAD_REQUEST)

        detail_res = self.client.get(reverse("report-detail", kwargs={"report_id": report.id}))
        self.assertEqual(detail_res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reports_filter_by_username(self):
        john = User.objects.create_user(username="john", password="pass12345")
        jane = User.objects.create_user(username="jane", password="pass12345")
        DiagnosisReport.objects.create(
            user=john,
            diagnosis="Diagnosis A",
            severity="Mild",
            symptoms=["Cough"],
            recommendations=["Rest"],
            precautions=["Hydrate"],
            summary="A report",
        )
        DiagnosisReport.objects.create(
            user=jane,
            diagnosis="Diagnosis B",
            severity="Mild",
            symptoms=["Headache"],
            recommendations=["Sleep"],
            precautions=["Monitor"],
            summary="B report",
        )

        res = self.client.get(reverse("reports"), {"username": "john"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["summary"], "A report")

    @patch("api.views.ollama.chat")
    def test_predict_uses_ollama_generated_report(self, mock_chat):
        mock_chat.return_value = {
            "message": {
                "content": (
                    '{"diagnosis":"Influenza","severity":"Moderate","recommendations":["Rest"],'
                    '"precautions":["Hydrate"],"medications":["Paracetamol"],'
                    '"when_to_see_doctor":"If fever persists","additional_info":"AI generated",'
                    '"summary":"Flu triage"}'
                )
            }
        }

        res = self.client.post(
            reverse("predict"),
            {
                "username": "john",
                "symptom_cards": [{"symptom": "Fever", "duration": "1-2 days", "severity": 7}],
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["diagnosis"], "Influenza")
        self.assertEqual(res.data["severity"], "Moderate")
        self.assertEqual(res.data["recommendations"], ["Rest"])
        self.assertEqual(res.data["summary"], "Flu triage")
        self.assertEqual(len(res.data["predicted_diseases"]), 3)

    def test_predict_accepts_medical_image_upload(self):
        image = SimpleUploadedFile("xray.png", b"fake-image-content", content_type="image/png")
        res = self.client.post(
            reverse("predict"),
            {
                "username": "john",
                "symptom_cards": '[{"symptom":"Chest pain","duration":"1-2 days","severity":6}]',
                "medical_image": image,
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(res.data["medicalImage"].startswith("medical-images/"))

    def test_legacy_apilogin_endpoint_maps_to_login_view(self):
        User.objects.create_user(username="john", email="john@example.com", password="strongpass123")
        res = self.client.post(
            "/apilogin/",
            {"username": "john", "password": "strongpass123"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["username"], "john")


class DatabaseConfigTests(APITestCase):
    def test_database_url_required(self):
        from config.database_config import get_database_url

        original = os.environ.pop("DATABASE_URL", None)
        try:
            with self.assertRaises(ImproperlyConfigured):
                get_database_url()
        finally:
            if original is not None:
                os.environ["DATABASE_URL"] = original

    def test_database_url_must_be_mysql_scheme(self):
        from config.database_config import get_database_url

        original = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        try:
            with self.assertRaises(ImproperlyConfigured):
                get_database_url()
        finally:
            if original is None:
                os.environ.pop("DATABASE_URL", None)
            else:
                os.environ["DATABASE_URL"] = original

# Create your tests here.
