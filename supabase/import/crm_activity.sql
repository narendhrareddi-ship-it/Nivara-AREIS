--
-- PostgreSQL database dump
--

\restrict rtA87R5p0HonFdci1CcOaUe9wPkjQ5LnZHRjG637XrmGDvX6bDzbZuSS0cuO0lC

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: crm_activity; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.crm_activity (id, lead_id, customer_id, activity_type, title, description, performed_by, agent_name, metadata, created_at) VALUES ('68cb1f43-8e68-4423-97f1-99d3a7a272f6', 'a901e504-3bb0-4734-91e3-77b6734b0469', NULL, 'whatsapp', 'Initial inquiry response', 'Sent project brochure and pricing sheet', 'ai', 'LeadQualification', '{}', '2026-06-13 11:00:46.196901+00');
INSERT INTO public.crm_activity (id, lead_id, customer_id, activity_type, title, description, performed_by, agent_name, metadata, created_at) VALUES ('ec438955-ff6c-4298-8ac8-cc4ee68c0589', 'a901e504-3bb0-4734-91e3-77b6734b0469', NULL, 'call', 'Follow-up call', 'Discussed 3BHK options, budget confirmed', 'human', 'Sales Rep', '{}', '2026-06-13 11:00:46.196901+00');
INSERT INTO public.crm_activity (id, lead_id, customer_id, activity_type, title, description, performed_by, agent_name, metadata, created_at) VALUES ('fb93162a-0c61-4367-9cc1-39b51081090e', 'd9d0a8b9-267d-4472-9df9-cb6b1c6648fc', NULL, 'site_visit', 'Site visit scheduled', 'Visit booked for Saturday 10 AM at Rushikonda', 'ai', 'CRM', '{}', '2026-06-13 11:00:46.196901+00');
INSERT INTO public.crm_activity (id, lead_id, customer_id, activity_type, title, description, performed_by, agent_name, metadata, created_at) VALUES ('76e50cca-42d3-42e6-8a3c-7d3a427553ce', 'd9d0a8b9-267d-4472-9df9-cb6b1c6648fc', NULL, 'whatsapp', 'EMI options question', 'What are the EMI options available for the 2BHK configuration?', 'lead', 'WhatsAppAgent', '{}', '2026-06-13 11:41:08.382948+00');


--
-- PostgreSQL database dump complete
--

\unrestrict rtA87R5p0HonFdci1CcOaUe9wPkjQ5LnZHRjG637XrmGDvX6bDzbZuSS0cuO0lC

