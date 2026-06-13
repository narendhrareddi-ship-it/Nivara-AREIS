--
-- PostgreSQL database dump
--

\restrict KP1ZRMK51bia5djJQneOXZiAxcpsWDhd2fgt7cGInSuDMAb0yI9vlo4qenaAFGZ

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
-- Data for Name: competitors; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.competitors (id, name, website, location_city, state, projects, price_range_min, price_range_max, strengths, weaknesses, last_scraped_at, scrape_data, metadata, created_at, updated_at) VALUES ('080981a1-94b3-4f05-a2be-80464a196c50', 'Prestige Group Chennai', 'https://www.prestigeconstructions.com', 'Chennai', 'Tamil Nadu', '[]', 7000000.00, 20000000.00, '{"brand trust","timely delivery"}', '{"premium pricing"}', NULL, '{}', '{}', '2026-06-13 11:00:46.194745+00', '2026-06-13 11:00:46.194745+00');
INSERT INTO public.competitors (id, name, website, location_city, state, projects, price_range_min, price_range_max, strengths, weaknesses, last_scraped_at, scrape_data, metadata, created_at, updated_at) VALUES ('91da1e67-30d3-4f04-b0a8-2e8c82282377', 'Aparna Constructions', 'https://www.aparnaconstructions.com', 'Hyderabad', 'Telangana', '[]', 5000000.00, 15000000.00, '{"volume builder","multiple locations"}', '{"less personalization"}', NULL, '{}', '{}', '2026-06-13 11:00:46.194745+00', '2026-06-13 11:00:46.194745+00');
INSERT INTO public.competitors (id, name, website, location_city, state, projects, price_range_min, price_range_max, strengths, weaknesses, last_scraped_at, scrape_data, metadata, created_at, updated_at) VALUES ('bfd0a2c8-0fcb-48b3-b835-6c682ef7dd70', 'Lansum Properties', 'https://www.lansum.com', 'Amaravati', 'Andhra Pradesh', '[]', 3000000.00, 10000000.00, '{"CRDA expertise"}', '{"limited Chennai presence"}', NULL, '{}', '{}', '2026-06-13 11:00:46.194745+00', '2026-06-13 11:00:46.194745+00');


--
-- PostgreSQL database dump complete
--

\unrestrict KP1ZRMK51bia5djJQneOXZiAxcpsWDhd2fgt7cGInSuDMAb0yI9vlo4qenaAFGZ

