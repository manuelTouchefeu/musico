CREATE TABLE artists (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL );
CREATE TABLE albums (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL UNIQUE,
                    date INTEGER,
                    cover STRING );
CREATE TABLE genres (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE );
CREATE TABLE tracks (
                    id INTEGER PRIMARY KEY,
                    genreID INTEGER NOT NULL,
                    artistID INTEGER NOT NULL,
                    albumID INTEGER,
                    tracknumber INTEGER,
                    title text NOT NULL,
                    date INTEGER NOT NULL,
                    cover STRING,
                    embedded_cover INTEGER CHECK(embedded_cover <2) NOT NULL,
                    path STRING NOT NULL UNIQUE );
CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    firstname TEXT NOT NULL,
                    lastname TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL  );
