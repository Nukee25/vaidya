from django.contrib.auth.models import User
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

    def test_predict_requires_symptom_cards(self):
        res = self.client.post(reverse("predict"), {"username": "john"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_report_detail_not_found(self):
        User.objects.create_user(username="alice", email="alice@example.com", password="pass12345")
        res = self.client.get(reverse("report-detail", kwargs={"report_id": 999}), {"username": "alice"})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

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

# Create your tests here.
