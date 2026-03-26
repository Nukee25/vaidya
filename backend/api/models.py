from django.db import models


class Symptom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Disease(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    symptoms = models.ManyToManyField(Symptom, related_name='diseases', blank=True)
    precautions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Prediction(models.Model):
    input_symptoms = models.JSONField()
    predicted_disease = models.ForeignKey(
        Disease, on_delete=models.SET_NULL, null=True, blank=True
    )
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        disease_name = self.predicted_disease.name if self.predicted_disease else 'Unknown'
        return f'Prediction: {disease_name} ({self.confidence:.1%})'
