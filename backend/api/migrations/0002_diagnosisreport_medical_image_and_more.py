from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="diagnosisreport",
            name="medical_image",
            field=models.FileField(blank=True, null=True, upload_to="medical-images/"),
        ),
        migrations.AddField(
            model_name="diagnosisreport",
            name="predicted_diseases",
            field=models.JSONField(default=list),
        ),
    ]
