-- T4H Atlas ENH — full schema (Postgres-compatible; works on SQLite with minor types)
-- Apply via scripts/migrate.py or alembic equivalent

CREATE TABLE IF NOT EXISTS themes (
  id VARCHAR(16) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  subtopic_count INTEGER DEFAULT 0,
  high_priority_count INTEGER DEFAULT 0,
  keywords JSON,
  search_profile JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS topics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  theme_id VARCHAR(16) NOT NULL REFERENCES themes(id) ON DELETE CASCADE,
  topic_id VARCHAR(32) NOT NULL,
  name VARCHAR(255) NOT NULL,
  subtopic_count INTEGER DEFAULT 0,
  UNIQUE (theme_id, topic_id)
);

CREATE TABLE IF NOT EXISTS subtopics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
  subtopic_id VARCHAR(64) NOT NULL,
  name VARCHAR(512) NOT NULL,
  priority VARCHAR(32),
  idea_id VARCHAR(64),
  UNIQUE (topic_id, subtopic_id)
);

CREATE TABLE IF NOT EXISTS opportunities (
  id VARCHAR(64) PRIMARY KEY,
  title VARCHAR(512) NOT NULL,
  funder VARCHAR(255) NOT NULL,
  funder_type VARCHAR(64),
  programme VARCHAR(255),
  geography JSON,
  eligible_countries JSON,
  status VARCHAR(32) DEFAULT 'unknown',
  open_date VARCHAR(32),
  close_date VARCHAR(32),
  value_min_aud REAL,
  value_max_aud REAL,
  value_total_pool_aud REAL,
  currency_original VARCHAR(8),
  value_notes TEXT,
  match_rationale TEXT,
  source_url TEXT,
  application_url TEXT,
  last_verified VARCHAR(32),
  is_pattern BOOLEAN DEFAULT 0,
  portal VARCHAR(128),
  notes TEXT,
  topic_hints JSON,
  actions JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_opportunities_status ON opportunities(status);
CREATE INDEX IF NOT EXISTS ix_opportunities_close_date ON opportunities(close_date);

CREATE TABLE IF NOT EXISTS opportunity_themes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  opportunity_id VARCHAR(64) NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  theme_id VARCHAR(16) NOT NULL REFERENCES themes(id),
  rank INTEGER DEFAULT 0,
  UNIQUE (opportunity_id, theme_id)
);

CREATE TABLE IF NOT EXISTS win_scores (
  opportunity_id VARCHAR(64) PRIMARY KEY REFERENCES opportunities(id) ON DELETE CASCADE,
  score REAL NOT NULL,
  decision VARCHAR(16) NOT NULL,
  dimensions JSON NOT NULL,
  rationale JSON,
  evidence_requirements JSON,
  scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_win_scores_decision ON win_scores(decision);

CREATE TABLE IF NOT EXISTS funder_intelligence (
  opportunity_id VARCHAR(64) PRIMARY KEY REFERENCES opportunities(id) ON DELETE CASCADE,
  funder VARCHAR(255) NOT NULL,
  funder_type VARCHAR(64),
  portal VARCHAR(128),
  geography JSON,
  prior_winners_note TEXT,
  evaluator_language_hints JSON,
  clarification_channel TEXT,
  extras JSON,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS partner_pipeline_states (
  opportunity_id VARCHAR(64) PRIMARY KEY REFERENCES opportunities(id) ON DELETE CASCADE,
  stage VARCHAR(64) NOT NULL,
  notes TEXT,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_partner_stage ON partner_pipeline_states(stage);

CREATE TABLE IF NOT EXISTS control_room_queue_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  queue VARCHAR(64) NOT NULL,
  opportunity_id VARCHAR(64) NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  title VARCHAR(512),
  decision VARCHAR(16),
  close_date VARCHAR(32),
  days_remaining INTEGER,
  score REAL,
  payload JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_cr_queue ON control_room_queue_items(queue);
