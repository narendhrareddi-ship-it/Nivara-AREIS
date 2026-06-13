-- NIVARA REALTY — Phase 2: bot_logs, media_assets, social posting support

-- Bot activity logs (used by orchestrator + dashboard)
CREATE TABLE IF NOT EXISTS bot_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  agent_name TEXT NOT NULL,
  action TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'processing',
  details TEXT,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bot_logs_agent ON bot_logs(agent_name);
CREATE INDEX IF NOT EXISTS idx_bot_logs_timestamp ON bot_logs(timestamp DESC);

-- Media asset types
DO $$ BEGIN
  CREATE TYPE media_asset_type AS ENUM ('photo', 'video', 'image');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE media_asset_status AS ENUM (
    'uploaded', 'queued', 'generating', 'completed', 'failed', 'published'
  );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Site photos and Higgsfield-generated videos
CREATE TABLE IF NOT EXISTS media_assets (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
  asset_type media_asset_type NOT NULL DEFAULT 'photo',
  status media_asset_status NOT NULL DEFAULT 'uploaded',
  source_url TEXT,
  output_url TEXT,
  thumbnail_url TEXT,
  filename TEXT,
  mime_type TEXT,
  file_size_bytes BIGINT,
  provider TEXT DEFAULT 'local',
  provider_job_id TEXT,
  prompt TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_media_assets_project ON media_assets(project_id);
CREATE INDEX IF NOT EXISTS idx_media_assets_status ON media_assets(status);
CREATE INDEX IF NOT EXISTS idx_media_assets_provider_job ON media_assets(provider_job_id);

-- Extend social_posts for video publishing
ALTER TABLE social_posts ADD COLUMN IF NOT EXISTS post_status TEXT DEFAULT 'published';
ALTER TABLE social_posts ADD COLUMN IF NOT EXISTS media_asset_id UUID REFERENCES media_assets(id) ON DELETE SET NULL;

-- Add social_media to crm_activity enum if missing
DO $$ BEGIN
  ALTER TYPE crm_activity_type ADD VALUE IF NOT EXISTS 'social_media';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE TRIGGER trg_media_assets_updated BEFORE UPDATE ON media_assets
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

ALTER TABLE bot_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE media_assets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated read bot_logs" ON bot_logs FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated read media_assets" ON media_assets FOR SELECT TO authenticated USING (true);
CREATE POLICY "Service role all bot_logs" ON bot_logs FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role all media_assets" ON media_assets FOR ALL TO service_role USING (true) WITH CHECK (true);
