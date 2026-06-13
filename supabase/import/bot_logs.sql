--
-- PostgreSQL database dump
--

\restrict YTIaqD6WQkYVl79U9lxNvfahr89z99HrNa7CnNUYirpjy0gZLjnUc5eTzEXXCjS

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
-- Data for Name: bot_logs; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('22f320fa-9e04-4728-98c2-c36e10d31de8', 'MarketAnalyst', 'Starting task', 'processing', 'Analyzing Chennai property market trends', '2026-06-13 11:39:44.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('06212064-0e64-4e0e-abbb-f1090dbb900d', 'MarketAnalyst', 'Task completed', 'success', 'Market report: OMR prices up 11% YoY, ECR demand rising', '2026-06-13 11:39:47.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('a82baf8d-7919-45db-9e8b-1e8dbb1c4a71', 'CompetitorSpy', 'Starting task', 'processing', 'Scanning competitor real estate listings', '2026-06-13 11:39:51.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('8fb26e02-6863-4e73-b96e-5b23700e462d', 'CompetitorSpy', 'Task completed', 'success', '3 new competitor projects detected in Sholinganallur', '2026-06-13 11:39:54.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('47a382b8-47c2-43cc-a543-0436af719eef', 'ContentStrategist', 'Starting task', 'processing', 'Generating luxury property content', '2026-06-13 11:39:58.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('1f4efc5a-9088-4332-8822-d7b25853828c', 'ContentStrategist', 'Task completed', 'success', 'Content calendar for Q3 luxury segment created', '2026-06-13 11:40:01.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('98b9c178-467a-492e-ae25-7438a85548fd', 'SEOAgent', 'Starting task', 'processing', 'Optimizing property pages for search', '2026-06-13 11:40:05.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('2e61bfca-2b17-4c1c-a62a-62d7dd4c09f9', 'SEOAgent', 'Task completed', 'success', '12 property keywords now rank in top 20', '2026-06-13 11:40:08.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('8e46d41d-6c11-4d85-8086-31c7a89bd089', 'SocialMediaManager', 'Starting task', 'processing', 'Scheduling property showcase posts', '2026-06-13 11:40:12.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('d4ca84c1-2faa-4252-a697-fefcfabddd56', 'SocialMediaManager', 'Task completed', 'success', 'Posts scheduled across Facebook, Instagram, LinkedIn', '2026-06-13 11:40:15.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('45668501-41ce-4682-9727-4c0f3b518eae', 'VisualDesigner', 'Starting task', 'processing', 'Generating cinematic videos from site photos', '2026-06-13 11:40:19.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('e29a89a3-289e-4380-8ef7-8aafa421ea56', 'VisualDesigner', 'Task completed', 'success', 'Gemini Veo videos created for property listings', '2026-06-13 11:40:22.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('41c4d71e-bc2a-4c2f-9697-75c4d00dee2d', 'LeadQualification', 'Starting task', 'processing', 'Scoring incoming property inquiries', '2026-06-13 11:40:26.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('638262fe-e909-48e1-a70f-402c5303c74d', 'LeadQualification', 'Task completed', 'success', '2 hot leads, 3 warm leads identified', '2026-06-13 11:40:29.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('57ce07dc-e9ec-4d10-af84-fa4d10c458ee', 'WhatsAppAgent', 'Starting task', 'processing', 'Sending property recommendations', '2026-06-13 11:40:33.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('43c27a93-4c89-484d-a883-555fdddf1369', 'WhatsAppAgent', 'Task completed', 'success', 'Campaign delivered to 38 contacts, 12 replies', '2026-06-13 11:40:36.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('bb868358-cec3-49d1-a482-3e5258010e98', 'AppointmentScheduler', 'Starting task', 'processing', 'Scheduling site visits', '2026-06-13 11:40:40.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('4158c66d-5276-4172-8ad8-119d0d4acf7b', 'AppointmentScheduler', 'Task completed', 'success', '4 site visits confirmed for this week', '2026-06-13 11:40:43.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('d8a98224-cbcf-44c9-9ee7-84432a457e4b', 'CRM', 'Starting task', 'processing', 'Syncing lead data to PostgreSQL', '2026-06-13 11:40:47.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('65eeb5f1-335f-48c9-9747-315a23232b13', 'CRM', 'Task completed', 'success', 'CRM synchronized — 7 records updated', '2026-06-13 11:40:50.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('376e3302-f5a8-4b28-8aa8-c5ad2ee33525', 'Analytics', 'Starting task', 'processing', 'Compiling performance metrics', '2026-06-13 11:40:54.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('5f70f155-bcd9-4fa3-a401-efcce5bdcd15', 'Analytics', 'Task completed', 'success', 'Dashboard metrics refreshed, 15% MoM growth', '2026-06-13 11:40:57.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('dc5ae6fc-6a55-493a-9cf4-c84624b759d9', 'CEO', 'Starting task', 'processing', 'Reviewing market strategy', '2026-06-13 11:41:01.384754+00');
INSERT INTO public.bot_logs (id, agent_name, action, status, details, "timestamp") VALUES ('64479c10-6013-48dd-81b2-a9aa275973d0', 'CEO', 'Task completed', 'success', 'Strategy report: focus on OMR corridor approved', '2026-06-13 11:41:04.384754+00');


--
-- PostgreSQL database dump complete
--

\unrestrict YTIaqD6WQkYVl79U9lxNvfahr89z99HrNa7CnNUYirpjy0gZLjnUc5eTzEXXCjS

