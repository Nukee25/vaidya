"""
Ollama-based predictor for Symptoms → Disease.

Sends the symptom list to a local Ollama LLM and parses the structured
JSON response.  No local model training is required.
"""
from __future__ import annotations

import json
import logging
import os

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration (overridable via environment variables)
# ---------------------------------------------------------------------------
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

# ---------------------------------------------------------------------------
# Static symptom list exposed to the frontend
# ---------------------------------------------------------------------------
ALL_SYMPTOMS: list[str] = sorted([
    "abdominal_cramps", "abdominal_pain", "abdominal_tenderness", "anemia",
    "blood_in_cough", "blurred_vision", "body_aches", "burning_urination",
    "chest_discomfort", "chest_pain", "chest_tightness", "chills",
    "cloudy_urine", "cold_hands_feet", "congestion", "constipation",
    "cough", "dark_urine", "dehydration", "diarrhea", "difficulty_breathing",
    "dizziness", "dry_cough", "excessive_thirst", "fatigue", "fever",
    "frequent_infections", "frequent_urination", "headache", "high_fever",
    "itching", "itchy_rash", "joint_pain", "joint_stiffness", "joint_swelling",
    "light_sensitivity", "loss_of_appetite", "loss_of_smell", "loss_of_taste",
    "low_grade_fever", "lower_abdominal_pain", "mild_bleeding", "mild_fever",
    "mild_headache", "mucus_production", "muscle_pain", "nausea",
    "night_sweats", "nocturnal_cough", "nosebleeds", "pain_behind_eyes",
    "pale_skin", "pale_stool", "palpitations", "pelvic_pain",
    "persistent_cough", "productive_cough", "prolonged_fever",
    "rebound_tenderness", "reduced_range_of_motion", "redness",
    "rose_spots", "runny_nose", "severe_headache", "shortness_of_breath",
    "skin_blisters", "skin_rash", "slow_healing_wounds", "sneezing",
    "sore_throat", "sound_sensitivity", "strong_urine_odor", "sweating",
    "tingling_hands_feet", "unexplained_weight_loss", "visual_disturbances",
    "vomiting", "warmth_around_joints", "watery_eyes", "weakness",
    "weight_loss", "wheezing", "yellow_eyes", "yellow_skin",
])

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """\
You are a medical AI assistant. Given a list of symptoms, predict the top 3 \
most likely diseases.

Respond ONLY with a valid JSON array — no markdown fences, no extra text. \
Use exactly this structure:

[
  {
    "disease": "Disease Name",
    "confidence": 0.85,
    "description": "One-sentence description of the disease.",
    "precautions": "Key precautions and first-line treatments."
  }
]

Rules:
- "confidence" is a float between 0 and 1, ordered highest first.
- Return exactly 3 objects.
- Be medically accurate but conservative.
- Always recommend consulting a qualified healthcare professional.\
"""


class DiseasePredictor:
    """Symptom → disease predictor backed by an Ollama LLM."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def predict(self, symptoms: list[str]) -> list[dict]:
        """
        Predict top-3 diseases for the given symptom list.

        Returns a list of dicts with keys:
            disease (str), confidence (float 0-1),
            description (str), precautions (str)

        Raises RuntimeError if the Ollama service is unreachable or returns
        an unparseable response.
        """
        symptom_text = ", ".join(s.replace("_", " ") for s in symptoms)
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": f"Symptoms: {symptom_text}"},
            ],
            "stream": False,
            "format": "json",
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                resp = client.post(f"{OLLAMA_HOST}/api/chat", json=payload)
                resp.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("Ollama HTTP error: %s", exc)
            raise RuntimeError(f"Could not reach Ollama at {OLLAMA_HOST}: {exc}") from exc

        try:
            content = resp.json()["message"]["content"]
            raw = json.loads(content)
        except (KeyError, json.JSONDecodeError) as exc:
            logger.error("Ollama response parse error: %s — body: %s", exc, resp.text)
            raise RuntimeError(f"Unexpected response from Ollama: {exc}") from exc

        if not isinstance(raw, list):
            raise RuntimeError("Ollama returned non-list JSON; expected an array of predictions.")

        results: list[dict] = []
        for item in raw[:3]:
            results.append({
                "disease": str(item.get("disease", "Unknown")),
                "confidence": max(0.0, min(1.0, float(item.get("confidence", 0.5)))),
                "description": str(item.get("description", "")),
                "precautions": str(item.get("precautions", "Consult a doctor.")),
            })
        return results

    @property
    def all_symptoms(self) -> list[str]:
        return ALL_SYMPTOMS


# Module-level singleton
predictor = DiseasePredictor()
