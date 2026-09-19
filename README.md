# PAIMANA AI — Project Intelligence Prototype

A runnable full-stack prototype for predicting cost and time overruns, prioritising project risk, and giving programme teams an early-warning view of public-project delivery.

> **Data notice:** every record in this prototype is synthetically generated. The generators intentionally resemble common PAIMANA/CUF fields, but do not contain government data. In a production deployment, replace `backend/data/generate_data.py` with a PAIMANA API/database adapter and map the source columns into the feature contract in `backend/ml/train.py`.

## What is included

- React + Tailwind dashboard with risk ranking, portfolio KPIs, filters and responsive SIH-ready visual design
- FastAPI REST API with CORS enabled for the frontend
- Synthetic PAIMANA/CUF-style project portfolio (generated deterministically)
- Scikit-learn cost-overrun and time-overrun models
- Composite project risk scores, early-warning alerts, driver analysis, benchmarking and comparative analytics
- Project detail endpoint and a deterministic LLM-style intelligence assistant endpoint
- Training script and model artefacts generated locally

## Prerequisites

- Python 3.10+
- Node.js 18+

## Run the backend

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m ml.train
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`; interactive documentation is at `http://localhost:8000/docs`.

## Run the frontend

In a second terminal from the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Open the address printed by Vite (normally `http://localhost:5173`). The frontend targets `http://localhost:8000` by default. To change it, create `frontend/.env` with `VITE_API_URL=https://your-api`.

## Verify backend logic

With the backend virtual environment active:

```powershell
cd backend
python -m pytest -q
```

## Real PAIMANA integration point

1. Replace `generate_portfolio()` in `backend/data/generate_data.py` with authenticated PAIMANA/CUF extraction.
2. Keep or update `FEATURE_COLUMNS` in `backend/ml/train.py` to match the mapped source fields.
3. Retrain using `python -m ml.train`, persist model versions in governed storage, and replace the synthetic-data banner in the frontend.
4. Add authentication, audit logging, source refresh scheduling, validation rules, and human review before using predictions for operational decisions.

## Repository layout

```text
backend/     FastAPI app, synthetic data generator, ML training, API tests
frontend/    Vite React + Tailwind dashboard
```
