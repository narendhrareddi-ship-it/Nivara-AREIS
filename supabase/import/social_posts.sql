--
-- PostgreSQL database dump
--

\restrict knOwdHgmhcGpkP89hPfZ3XmOLx3FTMeSjY4OuGtH7Mb2fKYdZgjd3QxYwdGg8qm

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
-- Data for Name: social_posts; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.social_posts (id, platform, campaign_id, project_id, content, media_urls, scheduled_at, published_at, external_post_id, likes, shares, comments, reach, is_mock, metadata, created_at, updated_at, post_status, media_asset_id) VALUES ('dcbc1488-00e1-4d41-abe4-373b49ba0609', 'instagram', NULL, NULL, 'NIVARA live test post', '[]', NULL, '2026-06-13 11:02:55.228724+00', 'mock_6b3fddbc', 0, 0, 0, 0, true, '{"mock": true, "phase": 2, "media_type": "text", "media_urls": []}', '2026-06-13 11:02:55.23855+00', '2026-06-13 11:02:55.23855+00', 'published', NULL);
INSERT INTO public.social_posts (id, platform, campaign_id, project_id, content, media_urls, scheduled_at, published_at, external_post_id, likes, shares, comments, reach, is_mock, metadata, created_at, updated_at, post_status, media_asset_id) VALUES ('d8622ee0-ef0d-4aea-9b82-60b5ce767936', 'instagram', NULL, NULL, 'NIVARA REALTY — Luxury living in OMR Chennai 🏙️ #ChennaiRealEstate', '[]', NULL, '2026-06-13 11:14:53.460973+00', 'mock_2d9a75c9', 0, 0, 0, 0, true, '{"mock": true, "phase": 2, "media_type": "text", "media_urls": []}', '2026-06-13 11:14:53.470109+00', '2026-06-13 11:14:53.470109+00', 'published', NULL);
INSERT INTO public.social_posts (id, platform, campaign_id, project_id, content, media_urls, scheduled_at, published_at, external_post_id, likes, shares, comments, reach, is_mock, metadata, created_at, updated_at, post_status, media_asset_id) VALUES ('566ecc0f-b7f3-4629-81c0-f9066ceafc0a', 'instagram', NULL, NULL, 'Premium 3BHK apartments in OMR Chennai with world-class amenities. Starting at ₹89L. DM for virtual tour! #ChennaiRealEstate #LuxuryLiving', '[]', NULL, '2026-06-13 11:41:08.382948+00', NULL, 0, 0, 0, 14711, true, '{}', '2026-06-13 11:41:08.382948+00', '2026-06-13 11:41:08.382948+00', 'published', NULL);


--
-- PostgreSQL database dump complete
--

\unrestrict knOwdHgmhcGpkP89hPfZ3XmOLx3FTMeSjY4OuGtH7Mb2fKYdZgjd3QxYwdGg8qm

