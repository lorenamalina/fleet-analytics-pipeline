--
-- PostgreSQL database dump
--


-- Dumped from database version 16.15 (Debian 16.15-1.pgdg13+2)
-- Dumped by pg_dump version 16.15 (Debian 16.15-1.pgdg13+2)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: obd_telemetry; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.obd_telemetry (
    id integer NOT NULL,
    vehicle_id character varying(50) NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    vehicle_speed_kmh numeric(5,2),
    engine_rpm numeric(7,2),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    engine_run_time_s numeric(10,2),
    trip_id character varying(20),
    throttle_pct numeric(7,3),
    engine_load_pct numeric(7,3),
    coolant_temp_c numeric(6,2)
);


--
-- Name: obd_telemetry_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.obd_telemetry_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: obd_telemetry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.obd_telemetry_id_seq OWNED BY public.obd_telemetry.id;


--
-- Name: obd_telemetry id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.obd_telemetry ALTER COLUMN id SET DEFAULT nextval('public.obd_telemetry_id_seq'::regclass);


--
-- Name: obd_telemetry obd_telemetry_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.obd_telemetry
    ADD CONSTRAINT obd_telemetry_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--


