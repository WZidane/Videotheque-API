-- Adminer 4.8.1 PostgreSQL 17.2 (Debian 17.2-1.pgdg120+1) dump

DROP TABLE IF EXISTS "Actors";

CREATE TABLE "public"."Actors" (
    "id" SERIAL PRIMARY KEY,
    "firstname" character(50) NOT NULL,
    "surname" character(50) NOT NULL,
    CONSTRAINT "Actors_firstname_surname" UNIQUE ("firstname", "surname")
);


DROP TABLE IF EXISTS "Genre";

CREATE TABLE "public"."Genre" (
    "id" SERIAL PRIMARY KEY,
    "name" character(50) NOT NULL,
    CONSTRAINT "Genre_name" UNIQUE ("name")
);


DROP TABLE IF EXISTS "Language";

CREATE TABLE "public"."Language" (
    "id" SERIAL PRIMARY KEY,
    "name" character(10) NOT NULL
);


DROP TABLE IF EXISTS "Movie";

CREATE TABLE "public"."Movie" (
    "id" SERIAL PRIMARY KEY,
    "title" character(250) NOT NULL,
    "country" character(5) NOT NULL,
    "director" character(100) NOT NULL,
    "release_date" date NOT NULL,
    "synopsis" text NOT NULL,
    "duration" smallint NOT NULL,
    "poster" character(200) NOT NULL
);


DROP TABLE IF EXISTS "Role";

CREATE TABLE "public"."Role" (
    "id" SERIAL PRIMARY KEY,
    "name" character(20) NOT NULL
);


DROP TABLE IF EXISTS "User";

CREATE TABLE "public"."User" (
    "id" SERIAL PRIMARY KEY,
    "username" character(20) NOT NULL,
    "email" character(254) NOT NULL,
    "password" character(128) NOT NULL,
    "id_role" integer NOT NULL
);


DROP TABLE IF EXISTS "Videotheque";

CREATE TABLE "public"."Videotheque" (
    "id" SERIAL PRIMARY KEY,
    "user_id" integer NOT NULL,
    "movie_id" integer NOT NULL,
    CONSTRAINT "Videotheque_user_id_movie_id" UNIQUE ("user_id", "movie_id")
);


DROP TABLE IF EXISTS "actor_movie";

CREATE TABLE "public"."actor_movie" (
    "id" SERIAL PRIMARY KEY,
    "actor_id" integer NOT NULL,
    "movie_id" integer NOT NULL,
    CONSTRAINT "actor_movie_actor_id_movie_id" UNIQUE ("actor_id", "movie_id")
);


DROP TABLE IF EXISTS "genre_movie";
CREATE TABLE "public"."genre_movie" (
    "id" SERIAL PRIMARY KEY,
    "genre_id" integer NOT NULL,
    "movie_id" integer NOT NULL,
    CONSTRAINT "genre_movie_genre_id_movie_id" UNIQUE ("genre_id", "movie_id")
);


DROP TABLE IF EXISTS "language_movie";

CREATE TABLE "public"."language_movie" (
    "id" SERIAL PRIMARY KEY,
    "id_language" integer NOT NULL,
    "id_movie" integer NOT NULL,
    CONSTRAINT "language_movie_id_language_id_movie" UNIQUE ("id_language", "id_movie")
);


ALTER TABLE ONLY "public"."User" ADD CONSTRAINT "User_id_role_fkey" FOREIGN KEY (id_role) REFERENCES "Role"(id) NOT DEFERRABLE;

ALTER TABLE ONLY "public"."Videotheque" ADD CONSTRAINT "Videotheque_movie_id_fkey" FOREIGN KEY (movie_id) REFERENCES "Movie"(id) ON DELETE CASCADE NOT DEFERRABLE;
ALTER TABLE ONLY "public"."Videotheque" ADD CONSTRAINT "Videotheque_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "User"(id) ON DELETE CASCADE NOT DEFERRABLE;

ALTER TABLE ONLY "public"."actor_movie" ADD CONSTRAINT "actor_movie_actor_id_fkey" FOREIGN KEY (actor_id) REFERENCES "Actors"(id) NOT DEFERRABLE;
ALTER TABLE ONLY "public"."actor_movie" ADD CONSTRAINT "actor_movie_movie_id_fkey" FOREIGN KEY (movie_id) REFERENCES "Movie"(id) NOT DEFERRABLE;

ALTER TABLE ONLY "public"."genre_movie" ADD CONSTRAINT "genre_movie_genre_id_fkey" FOREIGN KEY (genre_id) REFERENCES "Genre"(id) NOT DEFERRABLE;
ALTER TABLE ONLY "public"."genre_movie" ADD CONSTRAINT "genre_movie_movie_id_fkey" FOREIGN KEY (movie_id) REFERENCES "Movie"(id) NOT DEFERRABLE;

ALTER TABLE ONLY "public"."language_movie" ADD CONSTRAINT "language_movie_id_language_fkey" FOREIGN KEY (id_language) REFERENCES "Language"(id) NOT DEFERRABLE;
ALTER TABLE ONLY "public"."language_movie" ADD CONSTRAINT "language_movie_id_movie_fkey" FOREIGN KEY (id_movie) REFERENCES "Movie"(id) NOT DEFERRABLE;

-- 2024-12-13 13:18:40.474562+00