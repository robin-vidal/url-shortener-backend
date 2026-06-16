# url-shortener-backend

FastAPI backend for the URL Shortener project.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

## Test

```bash
pytest tests/ -v --cov=app --cov-report=xml:coverage.xml
```

## SonarCloud

Organization: `robin-vidal`
Project key: `robin-vidal_url-shortener-backend`

Required GitHub secret: `SONAR_TOKEN`.
