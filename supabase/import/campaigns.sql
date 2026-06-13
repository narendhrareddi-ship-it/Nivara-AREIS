--
-- PostgreSQL database dump
--

\restrict gNVbzLMw7DdExlgkBM8SAVLrk4GvfcydnvoaZqlaCZ2kg3jDQdHq2GG5HtndtlC

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
-- Data for Name: campaigns; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.campaigns (id, name, description, channel, status, project_id, budget, spend, start_date, end_date, target_audience, creative_assets, n8n_workflow_id, metadata, created_at, updated_at) VALUES ('cbaf34b4-18f2-4bd5-8516-e93d7c9b6366', 'OMR Launch Q2', 'Lead gen for Skyline Residences launch', 'facebook', 'active', 'ac5d5b99-3298-4ee4-9061-d7ae04af7958', 150000.00, 42000.00, '2026-05-14', NULL, '{"age": "28-45", "income": "15L+", "locations": ["Chennai", "Bangalore"]}', '[]', NULL, '{}', '2026-06-13 11:00:46.190487+00', '2026-06-13 11:00:46.191618+00');
INSERT INTO public.campaigns (id, name, description, channel, status, project_id, budget, spend, start_date, end_date, target_audience, creative_assets, n8n_workflow_id, metadata, created_at, updated_at) VALUES ('1cef25ff-ef2f-4cb0-aca1-8f94f7ea963c', 'Google Search - Plots AP', 'Intent-based search for Amaravati plots', 'google_ads', 'active', '791e3108-0e24-48db-ac85-9ecd030884f8', 200000.00, 78000.00, '2026-04-29', NULL, '{"keywords": ["plots in amaravati", "crda approved plots"]}', '[]', NULL, '{}', '2026-06-13 11:00:46.190487+00', '2026-06-13 11:00:46.193331+00');
INSERT INTO public.campaigns (id, name, description, channel, status, project_id, budget, spend, start_date, end_date, target_audience, creative_assets, n8n_workflow_id, metadata, created_at, updated_at) VALUES ('3b9b9632-e202-4ca7-8a35-900fb0d68726', 'LinkedIn NRIs', 'NRI investment campaign for Vizag project', 'linkedin', 'draft', '87e8420a-982e-4d8b-a553-1feef414a6a2', 100000.00, 0.00, '2026-06-20', NULL, '{"locations": ["USA", "UK", "Singapore"], "job_titles": ["IT Professional", "Doctor"]}', '[]', NULL, '{}', '2026-06-13 11:00:46.190487+00', '2026-06-13 11:00:46.194022+00');


--
-- PostgreSQL database dump complete
--

\unrestrict gNVbzLMw7DdExlgkBM8SAVLrk4GvfcydnvoaZqlaCZ2kg3jDQdHq2GG5HtndtlC

