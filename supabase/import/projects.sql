--
-- PostgreSQL database dump
--

\restrict cQn99D6GFNyaxeIfFGzx9RgwtwXLSgJQumFQpKxOeDQQG5kj1KnNLTq8rPXZOvT

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
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.projects (id, name, slug, description, location_city, location_area, state, property_type, price_min, price_max, units_total, units_available, rera_number, amenities, metadata, is_active, created_at, updated_at) VALUES ('ac5d5b99-3298-4ee4-9061-d7ae04af7958', 'Nivara Skyline Residences', 'nivara-skyline', 'Premium 2/3 BHK apartments in OMR with sea-view balconies', 'Chennai', 'OMR Sholinganallur', 'Tamil Nadu', 'apartment', 6500000.00, 12500000.00, 240, 87, 'TN/29/Building/0123/2024', '["pool", "gym", "clubhouse", "24x7 security"]', '{}', true, '2026-06-13 11:00:46.188243+00', '2026-06-13 11:00:46.188243+00');
INSERT INTO public.projects (id, name, slug, description, location_city, location_area, state, property_type, price_min, price_max, units_total, units_available, rera_number, amenities, metadata, is_active, created_at, updated_at) VALUES ('841c5646-1446-4e99-ac25-548fdf02aef3', 'Nivara Green Meadows', 'nivara-green-meadows', 'Gated villa community near ECR', 'Chennai', 'ECR Neelankarai', 'Tamil Nadu', 'villa', 15000000.00, 35000000.00, 48, 12, 'TN/29/Building/0456/2024', '["private garden", "EV charging", "tennis court"]', '{}', true, '2026-06-13 11:00:46.188243+00', '2026-06-13 11:00:46.188243+00');
INSERT INTO public.projects (id, name, slug, description, location_city, location_area, state, property_type, price_min, price_max, units_total, units_available, rera_number, amenities, metadata, is_active, created_at, updated_at) VALUES ('791e3108-0e24-48db-ac85-9ecd030884f8', 'Nivara Amaravati Heights', 'nivara-amaravati-heights', 'Affordable plots in capital region growth corridor', 'Amaravati', 'Thullur', 'Andhra Pradesh', 'plot', 2500000.00, 8000000.00, 120, 95, 'AP/CRDA/Plot/0789/2024', '["CRDA approved", "road access", "underground drainage"]', '{}', true, '2026-06-13 11:00:46.188243+00', '2026-06-13 11:00:46.188243+00');
INSERT INTO public.projects (id, name, slug, description, location_city, location_area, state, property_type, price_min, price_max, units_total, units_available, rera_number, amenities, metadata, is_active, created_at, updated_at) VALUES ('87e8420a-982e-4d8b-a553-1feef414a6a2', 'Nivara Vizag Bay View', 'nivara-vizag-bay', 'Luxury sea-facing apartments in Rushikonda', 'Visakhapatnam', 'Rushikonda', 'Andhra Pradesh', 'apartment', 8000000.00, 18000000.00, 180, 45, 'AP/VSP/Building/0321/2024', '["sea view", "infinity pool", "concierge"]', '{}', true, '2026-06-13 11:00:46.188243+00', '2026-06-13 11:00:46.188243+00');


--
-- PostgreSQL database dump complete
--

\unrestrict cQn99D6GFNyaxeIfFGzx9RgwtwXLSgJQumFQpKxOeDQQG5kj1KnNLTq8rPXZOvT

