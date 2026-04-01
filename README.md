# Vaidya – AI-Powered Disease Predictor 🩺

Vaidya is a full-stack AI web application that predicts likely diseases from a list of user-selected symptoms using a locally-hosted Ollama large-language model. Users enter their symptoms, receive an AI-generated diagnosis report, and can track their medical history over time.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start (Docker)](#quick-start-docker)
- [Local Development](#local-development)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Disclaimer](#disclaimer)

---

## Features

- 🔐 **User authentication** – signup and login with email
- 🩻 **Symptom-based diagnosis** – add symptom cards with severity and duration, then get an AI prediction
- 📋 **Diagnosis reports** – view a full history of past reports with predicted diseases, recommendations, precautions, and medications
- 📊 **Health score** – aggregated health score calculated from recent diagnosis reports
- 🖼️ **Medical image upload** – optionally attach a medical image to a report
- 🤖 **Local LLM** – powered by [Ollama](https://ollama.com); no data sent to external APIs
- 🐳 **Docker Compose** – single command to spin up the entire stack

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite 5, Tailwind CSS 4, Radix UI, Material UI |
| Backend | Django 4.2 + Django REST Framework |
| AI / LLM | Ollama (local, configurable model) |
| Database | MariaDB 10.11 |
| Container | Docker + Docker Compose |

---

## Architecture

```
┌──────────────┐        ┌─────────────────┐        ┌──────────────┐
│   Browser    │◄──────►│  Django Backend │◄──────►│   MariaDB    │
│ React + Vite │  REST  │      (DRF)      │        │  (database)  │
└──────────────┘        └────────┬────────┘        └──────────────┘
                                 │ HTTP
                         ┌───────▼────────┐
                         │     Ollama     │
                         │  (local LLM)  │
                         └───────────────┘
```

- The **frontend** runs on port `5173` and talks to the backend via `REACT_APP_API_URL`.
- The **backend** exposes a REST API on port `8000` under `/api/`.
- The **Ollama** service runs the LLM locally; the backend calls it at `OLLAMA_HOST`.
- **MariaDB** is the persistent store for users and diagnosis reports.

---

## Prerequisites

### For Docker (recommended)

- [Docker](https://docs.docker.com/get-docker/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/) ≥ 2

### For local development

- Python 3.12+
- Node.js 20+ and npm
- MariaDB / MySQL server
- [Ollama](https://ollama.com/download) installed and running

---

## Quick Start (Docker)

```bash
# 1. Clone the repository
git clone https://github.com/Nukee25/vaidya.git
cd vaidya

# 2. Create the external Docker network (only needed once)
docker network create publicweb

# 3. Start all services
docker-compose up --build
```

The services will be available at:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api/ |

> **Note:** On first startup you must pull the Ollama model. While the containers are running, execute:
> ```bash
> docker compose exec ollama ollama pull llama3.2
> ```
> You can use any model supported by Ollama. Set the `OLLAMA_MODEL` environment variable to change the default (see [Environment Variables](#environment-variables)).

---

## Local Development

### Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure the database and run migrations
export DATABASE_URL="mysql://root:password@127.0.0.1:3306/vaidya?charset=utf8mb4"
python manage.py migrate

# Start the development server (Ollama must be running locally)
export OLLAMA_HOST=http://localhost:11434
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/api/`.

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend is now available at `http://localhost:5173`.

---

## Environment Variables

### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | *(required)* | MySQL/MariaDB connection URL, e.g. `mysql://root:password@127.0.0.1:3306/vaidya?charset=utf8mb4` |
| `OLLAMA_HOST` | `http://ollama:11434` | Base URL of the Ollama API |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model to use for predictions |
| `DJANGO_SECRET_KEY` | `django-insecure-dev-key-change-me` | Django secret key – **change in production** |
| `DJANGO_DEBUG` | `true` | Set to `false` in production |
| `DJANGO_ALLOWED_HOSTS` | `*` | Comma-separated list of allowed hostnames |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `http://backend:8000/api` | Backend API base URL |

---

## API Reference

All endpoints are prefixed with `/api/`.

### Authentication

#### `POST /api/signup/`

Create a new user account.

**Request body:**
```json
{
  "username": "john_doe",
  "email_id": "john@example.com",
  "password": "securepassword"
}
```

**Response `201`:**
```json
{
  "message": "User created successfully"
}
```

---

#### `POST /api/login/`

Log in and receive a session token.

**Request body:**
```json
{
  "email_id": "john@example.com",
  "password": "securepassword"
}
```

**Response `200`:**
```json
{
  "message": "Login successful",
  "username": "john_doe"
}
```

---

### Diagnosis

#### `POST /api/predict/`

Submit symptom cards and receive an AI-generated diagnosis report.

**Request body:**
```json
{
  "username": "john_doe",
  "symptom_cards": [
    { "symptom": "Fever", "duration": "1-2 days", "severity": 7 },
    { "symptom": "Cough", "duration": "3-5 days", "severity": 5 }
  ]
}
```

**Response `200`:**
```json
{
  "id": 1,
  "date": "2026-03-26T10:00:00Z",
  "summary": "Respiratory symptoms analysis",
  "status": "completed",
  "diagnosis": "Common Cold (Upper Respiratory Infection)",
  "severity": "Mild",
  "symptoms": ["Fever", "Cough"],
  "predicted_diseases": [
    { "name": "Common Cold", "confidence": 85, "description": "..." }
  ],
  "recommendations": ["Get plenty of rest and sleep"],
  "precautions": ["Wash hands frequently with soap and water"],
  "medications": ["Acetaminophen or ibuprofen for pain and fever"],
  "whenToSeeDoctor": "Seek care if fever exceeds 39 °C or symptoms worsen after 7 days.",
  "additionalInfo": "Stay hydrated and avoid contact with others."
}
```

---

### Reports

#### `GET /api/reports/?username=<username>`

List all diagnosis reports for a user.

**Response `200`:**
```json
[
  {
    "id": 1,
    "date": "2026-03-26T10:00:00Z",
    "summary": "Respiratory symptoms analysis",
    "diagnosis": "Common Cold",
    "severity": "Mild",
    "status": "completed"
  }
]
```

---

#### `GET /api/reports/<id>/?username=<username>`

Get the full details of a single diagnosis report.

**Response `200`:** *(same shape as the predict response)*

---

### Health Score

#### `GET /api/health-score/?username=<username>`

Returns an aggregated health score calculated from the user's recent diagnosis reports.

**Response `200`:**
```json
{
  "health_score": 78
}
```

---

## Project Structure

```
vaidya/
├── docker-compose.yml
├── README.md
│
├── backend/                        # Django application
│   ├── Dockerfile
│   ├── manage.py
│   ├── requirements.txt
│   ├── api/
│   │   ├── models.py               # DiagnosisReport model
│   │   ├── serializers.py          # DRF serializers
│   │   ├── views.py                # API views (signup, login, predict, reports, health-score)
│   │   ├── urls.py                 # URL routing for /api/
│   │   ├── tests.py                # Backend unit tests
│   │   └── migrations/
│   └── config/
│       ├── settings.py             # Django settings
│       ├── test_settings.py        # Settings override for tests (SQLite in-memory)
│       ├── database_config.py      # DATABASE_URL validation helper
│       └── urls.py                 # Root URL config
│
└── frontend/                       # React application
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── main.tsx
        └── app/
            ├── pages/
            │   ├── Auth.tsx         # Login / Signup page
            │   ├── Home.tsx         # Landing page
            │   ├── Dashboard.tsx    # Report history dashboard
            │   ├── NewReport.tsx    # Create a new diagnosis report
            │   ├── ReportDetails.tsx# View a single report
            │   └── NotFound.tsx     # 404 page
            ├── components/
            │   ├── ui/              # Radix UI component wrappers
            │   └── figma/           # Custom Figma-generated components
            ├── utils/               # Shared utilities
            └── styles/              # Global styles
```

---

## Running Tests

### Backend

```bash
cd backend
DJANGO_SETTINGS_MODULE=config.test_settings python manage.py test api.tests
```

The test configuration (`config/test_settings.py`) uses an in-memory SQLite database so no MariaDB instance is required.

---

## AI / LLM Integration

- **Engine**: [Ollama](https://ollama.com) – runs the LLM locally; no symptoms are sent to any external service.
- **Default model**: `llama3.2` (override with `OLLAMA_MODEL` env var).
- **How it works**: The backend sends a structured prompt with the user's symptom cards to Ollama and parses the JSON response into a `DiagnosisReport`.
- **Fallback**: If Ollama is unavailable, the API returns a fallback mock diagnosis so the application remains functional during development.

---

## Disclaimer

> ⚠️ **This application is for educational purposes only.**
>
> Vaidya is **not** a certified medical device and has **not** been approved by any medical authority. The predictions generated by the AI model are not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional for any health concerns.
