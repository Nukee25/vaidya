from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0003_diagnosisreport_age_diagnosisreport_gender"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="diagnosisreport",
            name="age",
        ),
        migrations.RemoveField(
            model_name="diagnosisreport",
            name="gender",
        ),
    ]
