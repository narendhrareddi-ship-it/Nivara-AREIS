-- NIVARA REALTY — Sample seed data (Chennai / Andhra Pradesh)
-- Run after 001_initial_schema.sql in Supabase SQL Editor

INSERT INTO projects (name, slug, description, location_city, location_area, state, property_type, price_min, price_max, units_total, units_available, rera_number, amenities) VALUES
  ('Nivara Skyline Residences', 'nivara-skyline', 'Premium 2/3 BHK apartments in OMR with sea-view balconies', 'Chennai', 'OMR Sholinganallur', 'Tamil Nadu', 'apartment', 6500000, 12500000, 240, 87, 'TN/29/Building/0123/2024', '["pool", "gym", "clubhouse", "24x7 security"]'),
  ('Nivara Green Meadows', 'nivara-green-meadows', 'Gated villa community near ECR', 'Chennai', 'ECR Neelankarai', 'Tamil Nadu', 'villa', 15000000, 35000000, 48, 12, 'TN/29/Building/0456/2024', '["private garden", "EV charging", "tennis court"]'),
  ('Nivara Amaravati Heights', 'nivara-amaravati-heights', 'Affordable plots in capital region growth corridor', 'Amaravati', 'Thullur', 'Andhra Pradesh', 'plot', 2500000, 8000000, 120, 95, 'AP/CRDA/Plot/0789/2024', '["CRDA approved", "road access", "underground drainage"]'),
  ('Nivara Vizag Bay View', 'nivara-vizag-bay', 'Luxury sea-facing apartments in Rushikonda', 'Visakhapatnam', 'Rushikonda', 'Andhra Pradesh', 'apartment', 8000000, 18000000, 180, 45, 'AP/VSP/Building/0321/2024', '["sea view", "infinity pool", "concierge"]');

INSERT INTO campaigns (name, description, channel, status, budget, spend, start_date, target_audience) VALUES
  ('OMR Launch Q2', 'Lead gen for Skyline Residences launch', 'facebook', 'active', 150000, 42000, CURRENT_DATE - 30, '{"age": "28-45", "income": "15L+", "locations": ["Chennai", "Bangalore"]}'),
  ('Google Search - Plots AP', 'Intent-based search for Amaravati plots', 'google_ads', 'active', 200000, 78000, CURRENT_DATE - 45, '{"keywords": ["plots in amaravati", "crda approved plots"]}'),
  ('LinkedIn NRIs', 'NRI investment campaign for Vizag project', 'linkedin', 'draft', 100000, 0, CURRENT_DATE + 7, '{"job_titles": ["IT Professional", "Doctor"], "locations": ["USA", "UK", "Singapore"]}');

UPDATE campaigns SET project_id = (SELECT id FROM projects WHERE slug = 'nivara-skyline') WHERE name = 'OMR Launch Q2';
UPDATE campaigns SET project_id = (SELECT id FROM projects WHERE slug = 'nivara-amaravati-heights') WHERE name = 'Google Search - Plots AP';
UPDATE campaigns SET project_id = (SELECT id FROM projects WHERE slug = 'nivara-vizag-bay') WHERE name = 'LinkedIn NRIs';

INSERT INTO competitors (name, website, location_city, state, price_range_min, price_range_max, strengths, weaknesses) VALUES
  ('Prestige Group Chennai', 'https://www.prestigeconstructions.com', 'Chennai', 'Tamil Nadu', 7000000, 20000000, ARRAY['brand trust', 'timely delivery'], ARRAY['premium pricing']),
  ('Aparna Constructions', 'https://www.aparnaconstructions.com', 'Hyderabad', 'Telangana', 5000000, 15000000, ARRAY['volume builder', 'multiple locations'], ARRAY['less personalization']),
  ('Lansum Properties', 'https://www.lansum.com', 'Amaravati', 'Andhra Pradesh', 3000000, 10000000, ARRAY['CRDA expertise'], ARRAY['limited Chennai presence']);

INSERT INTO leads (full_name, email, phone, whatsapp_number, source, status, score, budget_min, budget_max, preferred_property_type, preferred_locations, city, state, project_id, campaign_id) VALUES
  ('Rajesh Kumar', 'rajesh.k@email.com', '+919876543210', '+919876543210', 'facebook', 'qualified', 78, 7000000, 10000000, 'apartment', ARRAY['OMR', 'ECR'], 'Chennai', 'Tamil Nadu',
    (SELECT id FROM projects WHERE slug = 'nivara-skyline'),
    (SELECT id FROM campaigns WHERE name = 'OMR Launch Q2')),
  ('Priya Reddy', 'priya.reddy@email.com', '+919123456789', '+919123456789', 'google_ads', 'new', 45, 3000000, 6000000, 'plot', ARRAY['Amaravati', 'Vijayawada'], 'Amaravati', 'Andhra Pradesh',
    (SELECT id FROM projects WHERE slug = 'nivara-amaravati-heights'),
    (SELECT id FROM campaigns WHERE name = 'Google Search - Plots AP')),
  ('Arun Nair', 'arun.nair@email.com', '+919988776655', '+919988776655', 'whatsapp', 'site_visit_scheduled', 92, 12000000, 18000000, 'apartment', ARRAY['Rushikonda', 'Beach Road'], 'Visakhapatnam', 'Andhra Pradesh',
    (SELECT id FROM projects WHERE slug = 'nivara-vizag-bay'), NULL);

INSERT INTO crm_activity (lead_id, activity_type, title, description, performed_by, agent_name) VALUES
  ((SELECT id FROM leads WHERE phone = '+919876543210'), 'whatsapp', 'Initial inquiry response', 'Sent project brochure and pricing sheet', 'ai', 'LeadQualification'),
  ((SELECT id FROM leads WHERE phone = '+919876543210'), 'call', 'Follow-up call', 'Discussed 3BHK options, budget confirmed', 'human', 'Sales Rep'),
  ((SELECT id FROM leads WHERE phone = '+919988776655'), 'site_visit', 'Site visit scheduled', 'Visit booked for Saturday 10 AM at Rushikonda', 'ai', 'CRM');

INSERT INTO ad_performance (campaign_id, date, channel, impressions, clicks, spend, leads_generated, conversions, ctr, cpl, is_mock) VALUES
  ((SELECT id FROM campaigns WHERE name = 'OMR Launch Q2'), CURRENT_DATE - 1, 'facebook', 12500, 340, 4200, 8, 1, 2.72, 525, true),
  ((SELECT id FROM campaigns WHERE name = 'Google Search - Plots AP'), CURRENT_DATE - 1, 'google_ads', 3200, 180, 6500, 5, 0, 5.63, 1300, true);
