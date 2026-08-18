# Deploy T4H Atlas ENH

## Local

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/migrate.py
# seed via API after start, or:
python -c "from app.db.session import SessionLocal; from app.services.seed import seed_taxonomy, seed_opportunities; db=SessionLocal(); print(seed_taxonomy(db), seed_opportunities(db))"
uvicorn app.main:app --reload --port 8080
curl http://127.0.0.1:8080/api/v1/health
```

## Docker

```bash
docker compose up --build -d
curl http://127.0.0.1:8080/api/v1/health
curl -X POST http://127.0.0.1:8080/api/v1/admin/seed
```

## Production checklist

1. Set `APP_ENV=production`
2. Set `DATABASE_URL` to Postgres
3. Set `ATLAS_API_KEY`
4. Set `DEBUG=false`
5. Configure CORS_ORIGINS
6. Run migrations + seed
7. Health check: `GET /api/v1/health`
