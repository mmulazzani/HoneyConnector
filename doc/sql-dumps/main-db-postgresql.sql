--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: SSLFraud; Type: TABLE; Schema: public; Owner: honeyconnector; Tablespace: 
--

CREATE TABLE "SSLFraud" (
    id integer NOT NULL,
    fingerprint character varying(40) NOT NULL,
    url character varying(80) NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    certificate text
);


ALTER TABLE public."SSLFraud" OWNER TO "honeyconnector";

--
-- Name: SSLFraud_id_seq; Type: SEQUENCE; Schema: public; Owner: honeyconnector
--

CREATE SEQUENCE "SSLFraud_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public."SSLFraud_id_seq" OWNER TO "honeyconnector";

--
-- Name: SSLFraud_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: honeyconnector
--

ALTER SEQUENCE "SSLFraud_id_seq" OWNED BY "SSLFraud".id;


--
-- Name: credentials; Type: TABLE; Schema: public; Owner: honeyconnector; Tablespace: 
--

CREATE TABLE credentials (
    id integer NOT NULL,
    protocol character varying(20) NOT NULL,
    username character(128) NOT NULL,
    password character varying(128) NOT NULL,
    date timestamp without time zone NOT NULL,
    node character varying(300) NOT NULL
);


ALTER TABLE public.credentials OWNER TO "honeyconnector";

--
-- Name: credentials_id_seq; Type: SEQUENCE; Schema: public; Owner: honeyconnector
--

CREATE SEQUENCE credentials_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.credentials_id_seq OWNER TO "honeyconnector";

--
-- Name: credentials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: honeyconnector
--

ALTER SEQUENCE credentials_id_seq OWNED BY credentials.id;


--
-- Name: knownNodeIPs; Type: TABLE; Schema: public; Owner: honeyconnector; Tablespace: 
--

CREATE TABLE "knownNodeIPs" (
    id integer NOT NULL,
    fingerprint character varying(40) NOT NULL,
    address character varying(20) NOT NULL
);


ALTER TABLE public."knownNodeIPs" OWNER TO "honeyconnector";

--
-- Name: knownNodeIPs_id_seq; Type: SEQUENCE; Schema: public; Owner: honeyconnector
--

CREATE SEQUENCE "knownNodeIPs_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public."knownNodeIPs_id_seq" OWNER TO "honeyconnector";

--
-- Name: knownNodeIPs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: honeyconnector
--

ALTER SEQUENCE "knownNodeIPs_id_seq" OWNED BY "knownNodeIPs".id;


--
-- Name: knownNodes; Type: TABLE; Schema: public; Owner: honeyconnector; Tablespace: 
--

CREATE TABLE "knownNodes" (
    id integer NOT NULL,
    nickname character varying(20) NOT NULL,
    fingerprint character varying(40) NOT NULL,
    published timestamp without time zone NOT NULL,
    contact character varying(300) NOT NULL,
    "lastSeen" timestamp without time zone NOT NULL,
    "firstSeen" timestamp without time zone NOT NULL,
    "countIMAPLogins" integer,
    "countFTPLogins" integer,
    "countSSLChecks" integer,
    "exitPolicies" text,
    "platformVersion" character varying(200)
);


ALTER TABLE public."knownNodes" OWNER TO "honeyconnector";

--
-- Name: knownNodes_id_seq; Type: SEQUENCE; Schema: public; Owner: honeyconnector
--

CREATE SEQUENCE "knownNodes_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public."knownNodes_id_seq" OWNER TO "honeyconnector";

--
-- Name: knownNodes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: honeyconnector
--

ALTER SEQUENCE "knownNodes_id_seq" OWNED BY "knownNodes".id;


--
-- Name: loginEvents; Type: TABLE; Schema: public; Owner: honeyconnector; Tablespace: 
--

CREATE TABLE "loginEvents" (
    id integer NOT NULL,
    protocol character varying(10) NOT NULL,
    account character varying(120) NOT NULL,
    password character varying(120),
    "timestamp" timestamp without time zone,
    ip character varying(20) NOT NULL,
    type character varying(120) NOT NULL
);


ALTER TABLE public."loginEvents" OWNER TO "honeyconnector";

--
-- Name: loginEvent_id_seq; Type: SEQUENCE; Schema: public; Owner: honeyconnector
--

CREATE SEQUENCE "loginEvent_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public."loginEvent_id_seq" OWNER TO "honeyconnector";

--
-- Name: loginEvent_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: honeyconnector
--

ALTER SEQUENCE "loginEvent_id_seq" OWNED BY "loginEvents".id;


--
-- Name: message; Type: TABLE; Schema: public; Owner: honeyconnector; Tablespace: 
--

CREATE TABLE message (
    id integer NOT NULL,
    type character varying(80) NOT NULL,
    text text NOT NULL,
    "timestamp" timestamp without time zone NOT NULL
);


ALTER TABLE public.message OWNER TO "honeyconnector";

--
-- Name: message_id_seq; Type: SEQUENCE; Schema: public; Owner: honeyconnector
--

CREATE SEQUENCE message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.message_id_seq OWNER TO "honeyconnector";

--
-- Name: message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: honeyconnector
--

ALTER SEQUENCE message_id_seq OWNED BY message.id;


--
-- Name: queue; Type: TABLE; Schema: public; Owner: honeyconnector; Tablespace: 
--

CREATE TABLE queue (
    id integer NOT NULL,
    nickname character varying(20) NOT NULL,
    fingerprint character varying(40) NOT NULL,
    address character varying(20) NOT NULL,
    published timestamp without time zone,
    uptime integer NOT NULL,
    contact character varying(300),
    "queueTimestamp" timestamp without time zone NOT NULL,
    "hasHTTPS" boolean NOT NULL,
    "hasIMAP" boolean NOT NULL,
    "hasFTP" boolean NOT NULL,
    "exitPolicies" text,
    "platformVersion" character varying(200)
);


ALTER TABLE public.queue OWNER TO "honeyconnector";

--
-- Name: queue_id_seq; Type: SEQUENCE; Schema: public; Owner: honeyconnector
--

CREATE SEQUENCE queue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.queue_id_seq OWNER TO "honeyconnector";

--
-- Name: queue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: honeyconnector
--

ALTER SEQUENCE queue_id_seq OWNED BY queue.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: honeyconnector
--

ALTER TABLE ONLY "SSLFraud" ALTER COLUMN id SET DEFAULT nextval('"SSLFraud_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: honeyconnector
--

ALTER TABLE ONLY credentials ALTER COLUMN id SET DEFAULT nextval('credentials_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: honeyconnector
--

ALTER TABLE ONLY "knownNodeIPs" ALTER COLUMN id SET DEFAULT nextval('"knownNodeIPs_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: honeyconnector
--

ALTER TABLE ONLY "knownNodes" ALTER COLUMN id SET DEFAULT nextval('"knownNodes_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: honeyconnector
--

ALTER TABLE ONLY "loginEvents" ALTER COLUMN id SET DEFAULT nextval('"loginEvent_id_seq"'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: honeyconnector
--

ALTER TABLE ONLY message ALTER COLUMN id SET DEFAULT nextval('message_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: honeyconnector
--

ALTER TABLE ONLY queue ALTER COLUMN id SET DEFAULT nextval('queue_id_seq'::regclass);


--
-- Name: SSLFraud_pkey; Type: CONSTRAINT; Schema: public; Owner: honeyconnector; Tablespace: 
--

ALTER TABLE ONLY "SSLFraud"
    ADD CONSTRAINT "SSLFraud_pkey" PRIMARY KEY (id);


--
-- Name: credentials_pkey; Type: CONSTRAINT; Schema: public; Owner: honeyconnector; Tablespace: 
--

ALTER TABLE ONLY credentials
    ADD CONSTRAINT credentials_pkey PRIMARY KEY (id);


--
-- Name: knownNodeIPs_pkey; Type: CONSTRAINT; Schema: public; Owner: honeyconnector; Tablespace: 
--

ALTER TABLE ONLY "knownNodeIPs"
    ADD CONSTRAINT "knownNodeIPs_pkey" PRIMARY KEY (id);


--
-- Name: knownNodes_pkey; Type: CONSTRAINT; Schema: public; Owner: honeyconnector; Tablespace: 
--

ALTER TABLE ONLY "knownNodes"
    ADD CONSTRAINT "knownNodes_pkey" PRIMARY KEY (id, fingerprint);


--
-- Name: loginEvent_pkey; Type: CONSTRAINT; Schema: public; Owner: honeyconnector; Tablespace: 
--

ALTER TABLE ONLY "loginEvents"
    ADD CONSTRAINT "loginEvent_pkey" PRIMARY KEY (id);


--
-- Name: message_pkey; Type: CONSTRAINT; Schema: public; Owner: honeyconnector; Tablespace: 
--

ALTER TABLE ONLY message
    ADD CONSTRAINT message_pkey PRIMARY KEY (id);


--
-- Name: queue_pkey; Type: CONSTRAINT; Schema: public; Owner: honeyconnector; Tablespace: 
--

ALTER TABLE ONLY queue
    ADD CONSTRAINT queue_pkey PRIMARY KEY (id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

