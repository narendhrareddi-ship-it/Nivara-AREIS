--
-- PostgreSQL database dump
--

\restrict 7hXuiesa3BC5oZXeJWJtRhE1oLFJAMVNOwzbVrd85nv1vjfWNG9MoynZxEbXqoN

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
-- Data for Name: leads; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.leads (id, full_name, email, phone, whatsapp_number, source, status, score, budget_min, budget_max, preferred_property_type, preferred_locations, city, state, project_id, campaign_id, assigned_agent, ai_qualification_notes, metadata, last_contacted_at, converted_at, created_at, updated_at) VALUES ('87527384-50fc-4620-87f5-b626ba725a84', 'Priya Reddy', 'priya.reddy@email.com', '+919123456789', '+919123456789', 'google_ads', 'new', 45, 3000000.00, 6000000.00, 'plot', '{Amaravati,Vijayawada}', 'Amaravati', 'Andhra Pradesh', '791e3108-0e24-48db-ac85-9ecd030884f8', '1cef25ff-ef2f-4cb0-aca1-8f94f7ea963c', NULL, NULL, '{}', NULL, NULL, '2026-06-13 11:00:46.195307+00', '2026-06-13 11:00:46.195307+00');
INSERT INTO public.leads (id, full_name, email, phone, whatsapp_number, source, status, score, budget_min, budget_max, preferred_property_type, preferred_locations, city, state, project_id, campaign_id, assigned_agent, ai_qualification_notes, metadata, last_contacted_at, converted_at, created_at, updated_at) VALUES ('d9d0a8b9-267d-4472-9df9-cb6b1c6648fc', 'Arun Nair', 'arun.nair@email.com', '+919988776655', '+919988776655', 'whatsapp', 'site_visit_scheduled', 92, 12000000.00, 18000000.00, 'apartment', '{Rushikonda,"Beach Road"}', 'Visakhapatnam', 'Andhra Pradesh', '87e8420a-982e-4d8b-a553-1feef414a6a2', NULL, NULL, NULL, '{}', NULL, NULL, '2026-06-13 11:00:46.195307+00', '2026-06-13 11:00:46.195307+00');
INSERT INTO public.leads (id, full_name, email, phone, whatsapp_number, source, status, score, budget_min, budget_max, preferred_property_type, preferred_locations, city, state, project_id, campaign_id, assigned_agent, ai_qualification_notes, metadata, last_contacted_at, converted_at, created_at, updated_at) VALUES ('a901e504-3bb0-4734-91e3-77b6734b0469', 'Rajesh Kumar', 'rajesh.k@email.com', '+919876543210', '+919876543210', 'facebook', 'qualified', 83, 7000000.00, 10000000.00, 'apartment', '{OMR,ECR}', 'Chennai', 'Tamil Nadu', 'ac5d5b99-3298-4ee4-9061-d7ae04af7958', 'cbaf34b4-18f2-4bd5-8516-e93d7c9b6366', NULL, NULL, '{}', NULL, NULL, '2026-06-13 11:00:46.195307+00', '2026-06-13 11:41:08.382948+00');


--
-- PostgreSQL database dump complete
--

\unrestrict 7hXuiesa3BC5oZXeJWJtRhE1oLFJAMVNOwzbVrd85nv1vjfWNG9MoynZxEbXqoN

