"""Management command to seed the database with diseases and symptoms."""
from django.core.management.base import BaseCommand
from api.models import Symptom, Disease
from api.ml.predictor import SYMPTOM_DISEASE_DATA, DISEASE_DESCRIPTIONS


class Command(BaseCommand):
    help = 'Seed the database with diseases and symptoms from the ML dataset'

    def handle(self, *args, **options):
        self.stdout.write('Seeding symptoms...')
        symptom_objects = {}

        # Collect all unique symptoms
        all_symptoms = sorted(
            {s for symptoms in SYMPTOM_DISEASE_DATA.values() for s in symptoms}
        )
        for sym_key in all_symptoms:
            display_name = sym_key.replace('_', ' ').title()
            obj, created = Symptom.objects.get_or_create(
                name=display_name,
                defaults={'description': ''},
            )
            symptom_objects[sym_key] = obj
            if created:
                self.stdout.write(f'  Created symptom: {display_name}')

        self.stdout.write('Seeding diseases...')
        for disease_name, symptoms in SYMPTOM_DISEASE_DATA.items():
            desc, precautions = DISEASE_DESCRIPTIONS.get(
                disease_name, ('', 'Consult a doctor.')
            )
            disease_obj, created = Disease.objects.get_or_create(
                name=disease_name,
                defaults={
                    'description': desc,
                    'precautions': precautions,
                },
            )
            if not created:
                disease_obj.description = desc
                disease_obj.precautions = precautions
                disease_obj.save()

            for sym_key in symptoms:
                sym_obj = symptom_objects.get(sym_key)
                if sym_obj:
                    disease_obj.symptoms.add(sym_obj)

            action = 'Created' if created else 'Updated'
            self.stdout.write(f'  {action} disease: {disease_name}')

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
