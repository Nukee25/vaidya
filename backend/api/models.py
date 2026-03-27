from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class DiagnosisReport(models.Model):
    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("pending", "Pending"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="diagnosis_reports")
    diagnosis = models.CharField(max_length=255)
    predicted_diseases = models.JSONField(default=list)
    severity = models.CharField(max_length=32, default="Mild")
    symptoms = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    precautions = models.JSONField(default=list)
    medications = models.JSONField(default=list)
    when_to_see_doctor = models.TextField(blank=True)
    additional_info = models.TextField(blank=True)
    user_symptoms = models.TextField(blank=True)
    symptom_cards = models.JSONField(default=list)
    summary = models.CharField(max_length=255, default="Medical diagnosis report")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="completed")
    medical_image = models.FileField(upload_to="medical-images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Report #{self.pk} - {self.user.username}"

# Create your models here.
