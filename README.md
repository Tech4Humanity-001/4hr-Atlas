# T4H Atlas ENH

Production Atlas service: taxonomy deep-match, opportunities, WIN_SCORE, funder intelligence, partner pipeline, Control Room queues and action planning.

## Outcome loop

Atlas connects research to action:

`live estate context → match → score → evidence gap → priority → next action → Control Room`

The system is designed to keep state between AI sessions and make the next useful action visible.

## Features

- **API** (`/api/v1`): health, estate context, action plan, themes, opportunities, deep-match, rescore, control-room
- **Deep-match engine**: keyword + search-profile scoring → theme_ids
- **WIN_SCORE**: decision and evidence requirements for opportunities
- **Action plan**: ranks open work using WIN_SCORE, deadline urgency and evidence gaps
- **Control Room**: turns scored opportunities into operational queues
- **Full schema**: themes, topics, subtopics, opportunities, opportunity_themes, win_scores, funder_intelligence, partner_pipeline_states, control_room_queue_items
- **Config**: `.env.example` + production validation
- **Tests**: unit and API integration coverage
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
| GET | `/api/v1/estate-context` | Live Atlas first-read context |
| GET | `/api/v1/action-plan` | Prioritized work and next actions |
| POST | `/api/v1/match` | Deep-match text → themes |
| GET | `/api/v1/themes` | Taxonomy |
| GET | `/api/v1/opportunities` | Filter status/theme/decision/geo |
| GET | `/api/v1/opportunities/{id}` | Detail + WIN_SCORE + funder intelligence |
| POST | `/api/v1/opportunities/{id}/rescore` | Recompute WIN_SCORE |
| POST | `/api/v1/control-room/rebuild` | Rebuild queues |
| GET | `/api/v1/control-room/queues` | Queue contents |
| POST | `/api/v1/admin/seed` | Load seed JSON (API key if set) |
