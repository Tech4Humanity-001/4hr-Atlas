# T4H Atlas ENH

Production Atlas service: taxonomy deep-match, opportunities, WIN_SCORE, funder intelligence, partner pipeline, Control Room queues.

## Commercial membership

Atlas Unlimited uses one annual membership ladder:

- **A$399/year** founding membership
- **A$499/year** standard annual membership
- **A$1,995/year** Team membership for up to 10 learners

The pricing definition is maintained in `commercial/membership.json`. These are commercial product definitions. Billing, enrolment and delivery are not represented as live until connected and verified.

## Features

- **API** (`/api/v1`): health, themes, opportunities (filterable), deep-match, rescore, control-room
- **Deep-match engine**: keyword + search-profile scoring → theme_ids
- **Full schema**: themes, topics, subtopics, opportunities, opportunity_themes, win_scores, funder_intelligence, partner_pipeline_states, control_room_queue_items
- **Config**: `.env.example` + production validation
- **Tests**: unit (deep-match, WIN_SCORE, queues) + API integration
- **Deploy**: Dockerfile, docker-compose, healthchecks

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env
python scripts/migrate.py
python -c "from app.db.session import SessionLocal; from app.services.seed import *; db=SessionLocal(); print('themes', seed_taxonomy(db), 'opps', seed_opportunities(db))"
uvicorn app.main:app --port 8080
pytest -q
```

## API (selected)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/health` | Liveness + counts |
| POST | `/api/v1/match` | Deep-match text → themes |
| GET | `/api/v1/themes` | Taxonomy |
| GET | `/api/v1/opportunities` | Filter status/theme/decision/geo |
| GET | `/api/v1/opportunities/{id}` | Detail + win_score + funder intel |
| POST | `/api/v1/opportunities/{id}/rescore` | Recompute WIN_SCORE |
| POST | `/api/v1/control-room/rebuild` | Rebuild queues |
| GET | `/api/v1/control-room/queues` | Queue contents |
| POST | `/api/v1/admin/seed` | Load seed JSON (API key if set) |
