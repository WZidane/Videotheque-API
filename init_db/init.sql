-- Adminer 4.8.1 PostgreSQL 17.2 (Debian 17.2-1.pgdg120+1) dump

DROP TABLE IF EXISTS "Movie";

CREATE TABLE "public"."Movie" (
    "id" SERIAL PRIMARY KEY,
    "id_tmdb" bigint NOT NULL UNIQUE,
    "title_fr" character varying(250) NOT NULL,
    "title_en" character varying(250) NOT NULL,
    "country" character varying(5) NOT NULL,
    "director" character varying(100) NOT NULL,
    "release_date" character varying(20) NOT NULL,
    "synopsis_fr" text NOT NULL,
    "synopsis_en" text NOT NULL,
    "poster" character varying(200) NOT NULL
);


DROP TABLE IF EXISTS "Role";

CREATE TABLE "public"."Role" (
    "id" SERIAL PRIMARY KEY,
    "name" character varying(20) NOT NULL
);


DROP TABLE IF EXISTS "User";

CREATE TABLE "public"."User" (
    "id" SERIAL PRIMARY KEY,
    "username" character varying(20) NOT NULL UNIQUE,
    "email" character varying(254) NOT NULL UNIQUE,
    "password" character varying(128) NOT NULL,
    "id_role" integer NOT NULL
);


DROP TABLE IF EXISTS "Videotheque";

CREATE TABLE "public"."Videotheque" (
    "id" SERIAL PRIMARY KEY,
    "user_id" integer NOT NULL,
    "movie_id" integer NOT NULL,
    CONSTRAINT "Videotheque_user_id_movie_id" UNIQUE ("user_id", "movie_id")
);

DROP TABLE IF EXISTS "blacklist_token";

CREATE TABLE "blacklist_token" (
  "id" serial NOT NULL,
  PRIMARY KEY ("id"),
  "jti" uuid NOT NULL,
  "created_at" date NOT NULL
);


ALTER TABLE ONLY "public"."User" ADD CONSTRAINT "User_id_role_fkey" FOREIGN KEY (id_role) REFERENCES "Role"(id) NOT DEFERRABLE;

ALTER TABLE ONLY "public"."Videotheque" ADD CONSTRAINT "Videotheque_movie_id_fkey" FOREIGN KEY (movie_id) REFERENCES "Movie"(id) ON DELETE CASCADE NOT DEFERRABLE;
ALTER TABLE ONLY "public"."Videotheque" ADD CONSTRAINT "Videotheque_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "User"(id) ON DELETE CASCADE NOT DEFERRABLE;
-- 2024-12-13 13:18:40.474562+00