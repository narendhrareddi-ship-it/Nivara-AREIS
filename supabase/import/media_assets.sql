--
-- PostgreSQL database dump
--

\restrict Nt5KbfKjKNG4tA2renDGzkOV2PGzIci9a6pP4prLhqqG1XX1JTRM5Fg05cZnIxy

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
-- Data for Name: media_assets; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.media_assets (id, project_id, asset_type, status, source_url, output_url, thumbnail_url, filename, mime_type, file_size_bytes, provider, provider_job_id, prompt, metadata, created_at, updated_at) VALUES ('408d6f5c-27fb-429b-9fd0-c4a3777d30f5', NULL, 'photo', 'uploaded', 'http://localhost:8006/media/8e448dbc034f_test_site_photo.jpg', NULL, NULL, '8e448dbc034f_test_site_photo.jpg', 'image/jpeg', 22, 'local', NULL, NULL, '{"original_filename": "test_site_photo.jpg"}', '2026-06-13 11:02:44.690904+00', '2026-06-13 11:02:44.690904+00');
INSERT INTO public.media_assets (id, project_id, asset_type, status, source_url, output_url, thumbnail_url, filename, mime_type, file_size_bytes, provider, provider_job_id, prompt, metadata, created_at, updated_at) VALUES ('476ba9ae-83a2-4e51-89e8-df7499fc9526', NULL, 'photo', 'uploaded', 'http://localhost:8006/media/d6143a054f36_test_property.jpg', NULL, NULL, 'd6143a054f36_test_property.jpg', 'image/jpeg', 58752, 'local', NULL, NULL, '{"original_filename": "test_property.jpg"}', '2026-06-13 11:14:52.840648+00', '2026-06-13 11:14:52.840648+00');
INSERT INTO public.media_assets (id, project_id, asset_type, status, source_url, output_url, thumbnail_url, filename, mime_type, file_size_bytes, provider, provider_job_id, prompt, metadata, created_at, updated_at) VALUES ('bf282090-83cb-4004-a0d3-3e261cebb367', NULL, 'video', 'failed', 'http://localhost:8006/media/8e448dbc034f_test_site_photo.jpg', NULL, NULL, NULL, NULL, NULL, 'veo', NULL, 'Cinematic pan across luxury property', '{"error": "Client error ''403 Forbidden'' for url ''https://platform.higgsfield.ai/higgsfield-ai/dop/standard''\nFor more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403"}', '2026-06-13 11:03:00.989488+00', '2026-06-13 11:22:46.239229+00');
INSERT INTO public.media_assets (id, project_id, asset_type, status, source_url, output_url, thumbnail_url, filename, mime_type, file_size_bytes, provider, provider_job_id, prompt, metadata, created_at, updated_at) VALUES ('6ec10154-d23e-4af9-a186-73938698c262', NULL, 'video', 'failed', 'http://localhost:8006/media/8e448dbc034f_test_site_photo.jpg', NULL, NULL, NULL, NULL, NULL, 'veo', NULL, 'Cinematic slow pan across this Chennai real estate property, golden hour lighting, luxury atmosphere, smooth camera movement', '{"error": "Client error ''403 Forbidden'' for url ''https://platform.higgsfield.ai/higgsfield-ai/dop/standard''\nFor more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403"}', '2026-06-13 11:03:01.497472+00', '2026-06-13 11:22:46.239229+00');
INSERT INTO public.media_assets (id, project_id, asset_type, status, source_url, output_url, thumbnail_url, filename, mime_type, file_size_bytes, provider, provider_job_id, prompt, metadata, created_at, updated_at) VALUES ('8c4c4cbb-5d31-43ae-a33d-f5ae4dc4e67c', NULL, 'video', 'failed', 'http://localhost:8006/media/d6143a054f36_test_property.jpg', NULL, NULL, NULL, NULL, NULL, 'veo', NULL, 'Cinematic slow pan across luxury Chennai apartment, golden hour', '{"error": "PixVerse API error 500090: Insufficient balance. Unable to generate video. Please top up your credits."}', '2026-06-13 11:14:52.898966+00', '2026-06-13 11:22:46.239229+00');


--
-- PostgreSQL database dump complete
--

\unrestrict Nt5KbfKjKNG4tA2renDGzkOV2PGzIci9a6pP4prLhqqG1XX1JTRM5Fg05cZnIxy

