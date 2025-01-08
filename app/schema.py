import sqlite3
from app import app

data_base = app.config["DATABASE"]

def create_tables():
    print(data_base)
    conn = sqlite3.connect(data_base)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS artists (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL )
              ''')

    c.execute('''CREATE TABLE IF NOT EXISTS albums (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL UNIQUE,
                    date INTEGER,
                    cover STRING )
              ''')

    c.execute('''CREATE TABLE IF NOT EXISTS genres (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE )
              ''')

    c.execute('''CREATE TABLE IF NOT EXISTS tracks (
                    id INTEGER PRIMARY KEY,
                    genreID INTEGER NOT NULL,
                    artistID INTEGER NOT NULL,
                    albumID INTEGER,
                    tracknumber INTEGER,
                    title text NOT NULL,
                    date INTEGER NOT NULL,
                    cover STRING,
                    embedded_cover INTEGER CHECK(embedded_cover <2) NOT NULL,
                    path STRING NOT NULL UNIQUE )
            ''')

    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    firstname TEXT NOT NULL,
                    lastname TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL  )
              ''')
