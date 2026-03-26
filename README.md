# Vaidya – AI-Powered Disease Predictor 🩺

Vaidya is a full-stack AI web application that predicts likely diseases from a list of user-selected symptoms using an Ollama large-language model.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 + Django REST Framework |
| AI | Ollama LLM (default: `llama3.2`) |
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
- Ollama: http://localhost:11434

> **Note:** On first startup, pull the model inside the running Ollama container:
> ```bash
> docker exec -it vaidya-ollama-1 ollama pull llama3.2
> ```

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data      # populate DB with diseases/symptoms
OLLAMA_HOST=http://localhost:11434 python manage.py runserver
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

## AI / LLM Integration

- **Engine**: [Ollama](https://ollama.com) running `llama3.2` (configurable via `OLLAMA_MODEL` env var)
- **Endpoint**: `POST /api/chat` on the Ollama service (`OLLAMA_HOST`, default `http://ollama:11434`)
- **No training required**: The LLM reasons over symptoms at inference time and returns structured JSON predictions
- **Prompt**: A system prompt instructs the model to return exactly 3 disease predictions with confidence scores, descriptions, and precautions

## Disclaimer

This application is for **educational purposes only** and is **not** a substitute for professional medical advice, diagnosis, or treatment.

