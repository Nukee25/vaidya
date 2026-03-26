"""Management command to seed the database with diseases and symptoms."""
from django.core.management.base import BaseCommand
from api.models import Symptom, Disease

# Seed data is embedded here so it is independent of the ML/LLM predictor.
SYMPTOM_DISEASE_DATA = {
    "Flu": [
        "fever", "chills", "body_aches", "headache", "fatigue",
        "sore_throat", "runny_nose", "cough", "loss_of_appetite",
    ],
    "Common Cold": [
        "runny_nose", "sore_throat", "sneezing", "mild_fever",
        "congestion", "watery_eyes", "mild_headache", "cough",
    ],
    "Diabetes": [
        "frequent_urination", "excessive_thirst", "unexplained_weight_loss",
        "fatigue", "blurred_vision", "slow_healing_wounds",
        "frequent_infections", "tingling_hands_feet",
    ],
    "Hypertension": [
        "headache", "dizziness", "blurred_vision", "chest_pain",
        "shortness_of_breath", "nosebleeds", "fatigue", "palpitations",
    ],
    "Pneumonia": [
        "high_fever", "productive_cough", "chest_pain", "shortness_of_breath",
        "fatigue", "sweating", "chills", "nausea", "difficulty_breathing",
    ],
    "Bronchitis": [
        "persistent_cough", "mucus_production", "fatigue", "shortness_of_breath",
        "mild_fever", "chest_discomfort", "wheezing",
    ],
    "Asthma": [
        "wheezing", "shortness_of_breath", "chest_tightness",
        "cough", "difficulty_breathing", "nocturnal_cough",
    ],
    "Migraine": [
        "severe_headache", "nausea", "vomiting", "light_sensitivity",
        "sound_sensitivity", "visual_disturbances", "dizziness", "fatigue",
    ],
    "Appendicitis": [
        "abdominal_pain", "nausea", "vomiting", "fever", "loss_of_appetite",
        "abdominal_tenderness", "rebound_tenderness",
    ],
    "Malaria": [
        "high_fever", "chills", "sweating", "headache", "nausea",
        "vomiting", "muscle_pain", "fatigue", "anemia",
    ],
    "Typhoid": [
        "prolonged_fever", "abdominal_pain", "headache", "weakness",
        "loss_of_appetite", "constipation", "rose_spots", "fatigue",
    ],
    "Dengue": [
        "high_fever", "severe_headache", "pain_behind_eyes",
        "joint_pain", "muscle_pain", "skin_rash", "mild_bleeding",
        "nausea", "vomiting",
    ],
    "COVID-19": [
        "fever", "dry_cough", "fatigue", "loss_of_smell", "loss_of_taste",
        "shortness_of_breath", "body_aches", "sore_throat", "headache",
        "diarrhea",
    ],
    "Gastroenteritis": [
        "nausea", "vomiting", "diarrhea", "abdominal_cramps",
        "mild_fever", "loss_of_appetite", "dehydration",
    ],
    "UTI": [
        "burning_urination", "frequent_urination", "cloudy_urine",
        "lower_abdominal_pain", "strong_urine_odor", "pelvic_pain",
        "mild_fever",
    ],
    "Anemia": [
        "fatigue", "weakness", "pale_skin", "shortness_of_breath",
        "dizziness", "cold_hands_feet", "headache", "chest_pain",
    ],
    "Arthritis": [
        "joint_pain", "joint_stiffness", "joint_swelling", "reduced_range_of_motion",
        "redness", "warmth_around_joints", "fatigue",
    ],
    "Chickenpox": [
        "itchy_rash", "skin_blisters", "fever", "fatigue",
        "loss_of_appetite", "headache", "sore_throat",
    ],
    "Jaundice": [
        "yellow_skin", "yellow_eyes", "dark_urine", "pale_stool",
        "fatigue", "abdominal_pain", "nausea", "itching",
    ],
    "Tuberculosis": [
        "persistent_cough", "blood_in_cough", "chest_pain", "fatigue",
        "weight_loss", "night_sweats", "low_grade_fever", "loss_of_appetite",
    ],
}

DISEASE_DESCRIPTIONS = {
    "Flu": (
        "Influenza is a contagious respiratory illness caused by influenza viruses.",
        "Rest, stay hydrated, take antiviral medications if prescribed. "
        "Avoid contact with others. Get annual flu vaccine.",
    ),
    "Common Cold": (
        "A viral infection of the upper respiratory tract caused by rhinoviruses.",
        "Rest, drink fluids, use OTC cold remedies. Wash hands frequently.",
    ),
    "Diabetes": (
        "A chronic metabolic disease characterized by elevated blood glucose levels.",
        "Monitor blood sugar, follow a healthy diet, exercise regularly, "
        "take prescribed medications or insulin.",
    ),
    "Hypertension": (
        "A condition of persistently elevated arterial blood pressure.",
        "Reduce salt intake, exercise, maintain healthy weight, "
        "take antihypertensive medications as prescribed.",
    ),
    "Pneumonia": (
        "An infection that inflames the air sacs in one or both lungs.",
        "Take prescribed antibiotics, rest, stay hydrated. "
        "Seek emergency care if breathing worsens.",
    ),
    "Bronchitis": (
        "Inflammation of the bronchial tubes that carry air to the lungs.",
        "Rest, stay hydrated, use a humidifier. "
        "Avoid smoking and air pollutants.",
    ),
    "Asthma": (
        "A condition in which airways narrow and swell, producing extra mucus.",
        "Use inhalers as prescribed, identify and avoid triggers, "
        "follow an asthma action plan.",
    ),
    "Migraine": (
        "A neurological condition characterized by recurring severe headaches.",
        "Rest in a dark quiet room, take prescribed medications, "
        "identify and avoid personal triggers.",
    ),
    "Appendicitis": (
        "Inflammation of the appendix requiring prompt medical attention.",
        "Seek immediate medical care. Do not eat or drink. "
        "Surgery (appendectomy) is usually required.",
    ),
    "Malaria": (
        "A life-threatening disease caused by Plasmodium parasites transmitted by mosquitoes.",
        "Take antimalarial medications, use mosquito nets and repellents, "
        "eliminate standing water.",
    ),
    "Typhoid": (
        "A bacterial infection caused by Salmonella typhi spread through contaminated food/water.",
        "Take prescribed antibiotics, drink safe water, "
        "maintain proper hygiene and sanitation.",
    ),
    "Dengue": (
        "A mosquito-borne viral infection causing flu-like illness.",
        "Rest, stay hydrated, take paracetamol for fever. "
        "Avoid NSAIDs. Use mosquito protection.",
    ),
    "COVID-19": (
        "A respiratory illness caused by the SARS-CoV-2 coronavirus.",
        "Isolate, rest, stay hydrated. Seek medical care if breathing is difficult. "
        "Get vaccinated.",
    ),
    "Gastroenteritis": (
        "Inflammation of the stomach and intestines, typically from infection.",
        "Stay hydrated with ORS, eat bland foods, "
        "avoid dairy. Wash hands thoroughly.",
    ),
    "UTI": (
        "A urinary tract infection affecting the bladder, urethra, or kidneys.",
        "Take prescribed antibiotics, drink plenty of water, "
        "avoid holding urine for long periods.",
    ),
    "Anemia": (
        "A condition where you lack enough healthy red blood cells to carry oxygen.",
        "Eat iron-rich foods, take supplements as advised, "
        "treat underlying cause.",
    ),
    "Arthritis": (
        "Inflammation of one or more joints causing pain and stiffness.",
        "Exercise gently, maintain healthy weight, "
        "take anti-inflammatory medications, use hot/cold therapy.",
    ),
    "Chickenpox": (
        "A highly contagious viral infection causing an itchy blister-like rash.",
        "Avoid scratching blisters, use calamine lotion, "
        "take antivirals if prescribed. Vaccinate against varicella.",
    ),
    "Jaundice": (
        "Yellowing of the skin and eyes caused by excess bilirubin.",
        "Treat underlying cause, stay hydrated, eat a liver-friendly diet, "
        "avoid alcohol.",
    ),
    "Tuberculosis": (
        "A potentially serious infectious disease mainly affecting the lungs.",
        "Complete the full course of antibiotics (6-9 months), "
        "isolate during infectious period, get regular check-ups.",
    ),
}


class Command(BaseCommand):
    help = 'Seed the database with diseases and symptoms'

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
