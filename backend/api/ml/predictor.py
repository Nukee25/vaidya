"""
ML predictor for Symptoms → Disease using a Random Forest classifier.

Training data is embedded directly — no external files needed.
The model is trained lazily on first use and cached in memory.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# ---------------------------------------------------------------------------
# Embedded training data
# ---------------------------------------------------------------------------
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

# Flat list of all unique symptoms
ALL_SYMPTOMS: list[str] = sorted(
    {s for symptoms in SYMPTOM_DISEASE_DATA.values() for s in symptoms}
)

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
        "A chronic metabolic disease characterised by elevated blood glucose levels.",
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
        "A neurological condition characterised by recurring severe headaches.",
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
        "A highly contagious viral infection causing itchy blister-like rash.",
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


class DiseasePredictor:
    """Random-Forest-based symptom → disease predictor with lazy training."""

    def __init__(self) -> None:
        self._model: RandomForestClassifier | None = None
        self._label_encoder = LabelEncoder()
        self._symptom_index: dict[str, int] = {s: i for i, s in enumerate(ALL_SYMPTOMS)}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_training_data(self):
        """Build (X, y) arrays from the embedded dataset."""
        X_rows, y_labels = [], []

        for disease, symptoms in SYMPTOM_DISEASE_DATA.items():
            n_symptoms = len(symptoms)

            # Positive examples (the canonical symptom set)
            for _ in range(10):
                vec = np.zeros(len(ALL_SYMPTOMS), dtype=np.float32)
                # Randomly drop 0-2 symptoms to add variety
                k = max(1, n_symptoms - np.random.randint(0, 3))
                chosen = np.random.choice(symptoms, k, replace=False)
                for s in chosen:
                    if s in self._symptom_index:
                        vec[self._symptom_index[s]] = 1.0
                X_rows.append(vec)
                y_labels.append(disease)

            # Additional partial examples (2-5 symptoms)
            for _ in range(5):
                vec = np.zeros(len(ALL_SYMPTOMS), dtype=np.float32)
                k = max(2, min(5, n_symptoms))
                chosen = np.random.choice(symptoms, k, replace=False)
                for s in chosen:
                    if s in self._symptom_index:
                        vec[self._symptom_index[s]] = 1.0
                X_rows.append(vec)
                y_labels.append(disease)

        return np.array(X_rows), np.array(y_labels)

    def _ensure_trained(self) -> None:
        if self._model is not None:
            return

        np.random.seed(42)
        X, y = self._build_training_data()
        self._label_encoder.fit(y)
        y_enc = self._label_encoder.transform(y)

        self._model = RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            random_state=42,
            n_jobs=-1,
        )
        self._model.fit(X, y_enc)

    def _symptoms_to_vector(self, symptoms: list[str]) -> np.ndarray:
        vec = np.zeros(len(ALL_SYMPTOMS), dtype=np.float32)
        for s in symptoms:
            normalised = s.strip().lower().replace(" ", "_")
            if normalised in self._symptom_index:
                vec[self._symptom_index[normalised]] = 1.0
        return vec

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict(self, symptoms: list[str]) -> list[dict]:
        """
        Predict top-3 diseases for the given symptom list.

        Returns a list of dicts with keys:
            disease (str), confidence (float 0-1),
            description (str), precautions (str)
        """
        self._ensure_trained()

        vec = self._symptoms_to_vector(symptoms).reshape(1, -1)
        proba = self._model.predict_proba(vec)[0]  # shape: (n_classes,)

        # Top-3 indices by probability
        top3_idx = np.argsort(proba)[::-1][:3]
        results = []
        for idx in top3_idx:
            disease_name = self._label_encoder.inverse_transform([idx])[0]
            desc, precautions = DISEASE_DESCRIPTIONS.get(
                disease_name, ("No description available.", "Consult a doctor.")
            )
            results.append(
                {
                    "disease": disease_name,
                    "confidence": round(float(proba[idx]), 4),
                    "description": desc,
                    "precautions": precautions,
                }
            )
        return results

    @property
    def all_symptoms(self) -> list[str]:
        return ALL_SYMPTOMS


# Module-level singleton
predictor = DiseasePredictor()
