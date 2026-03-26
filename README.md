# Vaidya – AI-Powered Disease Predictor 🩺

Vaidya is a full-stack AI web application that predicts likely diseases from a list of user-selected symptoms using a Random Forest ML model.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 + Django REST Framework |
| ML | scikit-learn Random Forest |
| Database | MariaDB 10.11 (SQLite fallback for dev) |
| Frontend | React 18 + Vite 5 |
| Container | Docker + Docker Compose |

## Quick Start (Docker)

```bash
docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data      # populate DB with diseases/symptoms
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/symptoms/` | List all available symptoms |
| GET | `/api/diseases/` | List all diseases |
| GET | `/api/diseases/<id>/` | Disease detail |
| POST | `/api/predict/` | Predict diseases from symptoms |

### Predict Request

```json
POST /api/predict/
{
  "symptoms": ["Fever", "Cough", "Fatigue"]
}
```

### Predict Response

```json
{
  "symptoms": ["Fever", "Cough", "Fatigue"],
  "predictions": [
    {
      "disease": "Flu",
      "confidence": 0.72,
      "description": "...",
      "precautions": "..."
    }
  ]
}
```

## ML Model

- **Algorithm**: Random Forest Classifier (200 estimators)
- **Training data**: Embedded dataset — 20 diseases, 84+ unique symptoms
- **Lazy training**: Model trains on first prediction request and is cached in memory
- **No external files**: All training data is embedded directly in `backend/api/ml/predictor.py`

## Disclaimer

This application is for **educational purposes only** and is **not** a substitute for professional medical advice, diagnosis, or treatment.

