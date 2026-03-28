from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_diagnosisreport_medical_image_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="diagnosisreport",
            name="age",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="diagnosisreport",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[
                    ("male", "Male"),
                    ("female", "Female"),
                    ("other", "Other"),
                    ("prefer_not_to_say", "Prefer not to say"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
