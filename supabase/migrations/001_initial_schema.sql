-- NIVARA REALTY — Initial Schema (Phase 1)
-- Run via Supabase SQL Editor or: supabase db push

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enums
CREATE TYPE lead_status AS ENUM (
  'new', 'contacted', 'qualified', 'site_visit_scheduled',
  'negotiating', 'converted', 'lost', 'nurturing'
);

CREATE TYPE lead_source AS ENUM (
  'website', 'whatsapp', 'facebook', 'instagram', 'linkedin',
  'google_ads', 'referral', 'walk_in', 'n8n_webhook', 'other'
);

CREATE TYPE campaign_status AS ENUM (
  'draft', 'active', 'paused', 'completed', 'archived'
);

CREATE TYPE campaign_channel AS ENUM (
  'google_ads', 'facebook', 'instagram', 'linkedin',
  'youtube', 'whatsapp', 'email', 'organic'
);

CREATE TYPE appointment_status AS ENUM (
  'scheduled', 'confirmed', 'completed', 'cancelled', 'no_show'
);

CREATE TYPE site_visit_status AS ENUM (
  'scheduled', 'completed', 'cancelled', 'rescheduled'
);

CREATE TYPE social_platform AS ENUM (
  'facebook', 'instagram', 'linkedin', 'twitter', 'youtube'
);

CREATE TYPE crm_activity_type AS ENUM (
  'call', 'email', 'whatsapp', 'site_visit', 'note',
  'status_change', 'campaign_touch', 'ai_action'
);

CREATE TYPE property_type AS ENUM (
  'apartment', 'villa', 'plot', 'commercial', 'farmhouse', 'penthouse'
);

-- Projects (real estate developments)
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  description TEXT,
  location_city TEXT NOT NULL DEFAULT 'Chennai',
  location_area TEXT,
  state TEXT NOT NULL DEFAULT 'Tamil Nadu',
  property_type property_type NOT NULL DEFAULT 'apartment',
  price_min NUMERIC(15, 2),
  price_max NUMERIC(15, 2),
  units_total INTEGER,
  units_available INTEGER,
  rera_number TEXT,
  amenities JSONB DEFAULT '[]'::jsonb,
  metadata JSONB DEFAULT '{}'::jsonb,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Customers (converted leads / existing buyers)
CREATE TABLE customers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  full_name TEXT NOT NULL,
  email TEXT,
  phone TEXT NOT NULL,
  whatsapp_number TEXT,
  city TEXT DEFAULT 'Chennai',
  state TEXT DEFAULT 'Tamil Nadu',
  budget_min NUMERIC(15, 2),
  budget_max NUMERIC(15, 2),
  preferred_property_type property_type,
  preferred_locations TEXT[] DEFAULT '{}',
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
  notes TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Leads
CREATE TABLE leads (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  full_name TEXT NOT NULL,
  email TEXT,
  phone TEXT NOT NULL,
  whatsapp_number TEXT,
  source lead_source NOT NULL DEFAULT 'website',
  status lead_status NOT NULL DEFAULT 'new',
  score INTEGER DEFAULT 0 CHECK (score >= 0 AND score <= 100),
  budget_min NUMERIC(15, 2),
  budget_max NUMERIC(15, 2),
  preferred_property_type property_type,
  preferred_locations TEXT[] DEFAULT '{}',
  city TEXT DEFAULT 'Chennai',
  state TEXT DEFAULT 'Tamil Nadu',
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
  campaign_id UUID,
  assigned_agent TEXT,
  ai_qualification_notes TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  last_contacted_at TIMESTAMPTZ,
  converted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Campaigns
CREATE TABLE campaigns (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  description TEXT,
  channel campaign_channel NOT NULL,
  status campaign_status NOT NULL DEFAULT 'draft',
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
  budget NUMERIC(15, 2),
  spend NUMERIC(15, 2) DEFAULT 0,
  start_date DATE,
  end_date DATE,
  target_audience JSONB DEFAULT '{}'::jsonb,
  creative_assets JSONB DEFAULT '[]'::jsonb,
  n8n_workflow_id TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE leads ADD CONSTRAINT fk_leads_campaign
  FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL;

-- Competitors
CREATE TABLE competitors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  website TEXT,
  location_city TEXT DEFAULT 'Chennai',
  state TEXT DEFAULT 'Tamil Nadu',
  projects JSONB DEFAULT '[]'::jsonb,
  price_range_min NUMERIC(15, 2),
  price_range_max NUMERIC(15, 2),
  strengths TEXT[],
  weaknesses TEXT[],
  last_scraped_at TIMESTAMPTZ,
  scrape_data JSONB DEFAULT '{}'::jsonb,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Appointments
CREATE TABLE appointments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  description TEXT,
  scheduled_at TIMESTAMPTZ NOT NULL,
  duration_minutes INTEGER DEFAULT 30,
  status appointment_status NOT NULL DEFAULT 'scheduled',
  location TEXT,
  assigned_agent TEXT,
  reminder_sent BOOLEAN DEFAULT false,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Site visits
CREATE TABLE site_visits (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
  scheduled_at TIMESTAMPTZ NOT NULL,
  status site_visit_status NOT NULL DEFAULT 'scheduled',
  feedback TEXT,
  interest_level INTEGER CHECK (interest_level >= 1 AND interest_level <= 5),
  photos JSONB DEFAULT '[]'::jsonb,
  assigned_agent TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Social posts (mock + future real integrations)
CREATE TABLE social_posts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  platform social_platform NOT NULL,
  campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
  project_id UUID REFERENCES projects(id) ON DELETE SET NULL,
  content TEXT NOT NULL,
  media_urls JSONB DEFAULT '[]'::jsonb,
  scheduled_at TIMESTAMPTZ,
  published_at TIMESTAMPTZ,
  external_post_id TEXT,
  likes INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  reach INTEGER DEFAULT 0,
  is_mock BOOLEAN NOT NULL DEFAULT true,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Ad performance (mock data in Phase 1)
CREATE TABLE ad_performance (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  channel campaign_channel NOT NULL,
  impressions INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0,
  spend NUMERIC(15, 2) DEFAULT 0,
  leads_generated INTEGER DEFAULT 0,
  conversions INTEGER DEFAULT 0,
  ctr NUMERIC(8, 4) DEFAULT 0,
  cpl NUMERIC(15, 2) DEFAULT 0,
  is_mock BOOLEAN NOT NULL DEFAULT true,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (campaign_id, date, channel)
);

-- CRM activity log
CREATE TABLE crm_activity (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
  activity_type crm_activity_type NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  performed_by TEXT DEFAULT 'system',
  agent_name TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_source ON leads(source);
CREATE INDEX idx_leads_score ON leads(score DESC);
CREATE INDEX idx_leads_phone ON leads(phone);
CREATE INDEX idx_leads_created_at ON leads(created_at DESC);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_channel ON campaigns(channel);
CREATE INDEX idx_appointments_scheduled ON appointments(scheduled_at);
CREATE INDEX idx_site_visits_scheduled ON site_visits(scheduled_at);
CREATE INDEX idx_social_posts_platform ON social_posts(platform);
CREATE INDEX idx_ad_performance_date ON ad_performance(date DESC);
CREATE INDEX idx_crm_activity_lead ON crm_activity(lead_id);
CREATE INDEX idx_crm_activity_created ON crm_activity(created_at DESC);
CREATE INDEX idx_projects_city ON projects(location_city);
CREATE INDEX idx_competitors_city ON competitors(location_city);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_projects_updated BEFORE UPDATE ON projects
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_customers_updated BEFORE UPDATE ON customers
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_leads_updated BEFORE UPDATE ON leads
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_campaigns_updated BEFORE UPDATE ON campaigns
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_competitors_updated BEFORE UPDATE ON competitors
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_appointments_updated BEFORE UPDATE ON appointments
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_site_visits_updated BEFORE UPDATE ON site_visits
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_social_posts_updated BEFORE UPDATE ON social_posts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Row Level Security (basic — service role bypasses RLS)
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitors ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE site_visits ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE ad_performance ENABLE ROW LEVEL SECURITY;
ALTER TABLE crm_activity ENABLE ROW LEVEL SECURITY;

-- Authenticated users can read all (adjust in Phase 2 for role-based access)
CREATE POLICY "Authenticated read projects" ON projects FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated read customers" ON customers FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated read leads" ON leads FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated read campaigns" ON campaigns FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated read competitors" ON competitors FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated read appointments" ON appointments FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated read site_visits" ON site_visits FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated read social_posts" ON social_posts FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated read ad_performance" ON ad_performance FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated read crm_activity" ON crm_activity FOR SELECT TO authenticated USING (true);

-- Service role full access (used by agents and MCP servers)
CREATE POLICY "Service role all projects" ON projects FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role all customers" ON customers FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role all leads" ON leads FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role all campaigns" ON campaigns FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role all competitors" ON competitors FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role all appointments" ON appointments FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role all site_visits" ON site_visits FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role all social_posts" ON social_posts FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role all ad_performance" ON ad_performance FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "Service role all crm_activity" ON crm_activity FOR ALL TO service_role USING (true) WITH CHECK (true);
