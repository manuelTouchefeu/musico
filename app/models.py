import random
import re
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager

#from .routes import app
from app import login

data_base = "musico.sqlite3"


class Connection:
    def __init__(self):
        global data_base
        self.db = sqlite3.connect(data_base)
        self.conn = self.db.cursor()

# Users

@login.user_loader
def load_user(user_id):
    return UserManager().get_user_id(user_id)


class User(UserMixin):
    def __init__(self, email, firstname, lastname, user_id=None, password_hash=None):
        self.id = user_id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.password_hash = password_hash

    def __repr__(self):
        return "{} {}".format(self.firstname, self.lastname)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class UserManager(Connection):
    def __init__(self):
        Connection.__init__(self)

    def get_user(self, email):
        sql = "SELECT email, firstname, lastname, id, password FROM users WHERE email='%s'" % email
        self.conn.execute(sql)
        res = self.conn.fetchone()
        if res is None:
            return None
        return User(res[0], res[1], res[2], res[3], res[4])

    def get_user_id(self, user_id):
        try:
            sql = "SELECT email, firstname, lastname, id, password FROM users WHERE id=%d" % int(user_id)
            self.conn.execute(sql)
            res = self.conn.fetchone()
            if res is None:
                return None
        except ValueError:
            return None
        return User(res[0], res[1], res[2], res[3], res[4])


    def add_user(self, u):
        if self.get_user(u.email) is not None:
            return self.get_user(u.email)
        else:
            sql = "INSERT INTO users (firstname, lastname, email, password) \
                   VALUES (?, ?, ?, ?)"
            self.conn.execute(sql,(u.firstname, u.lastname, u.email, u.password_hash))
            self.db.commit()
        return self.get_user(u.email)


# Musique
class Genre:
    def __init__(self, genre_id, name, image=None):
        self.genre_id = genre_id
        self.genre_name = name
        self.genre_image = image
        self.albums = []


class Artist:
    def __init__(self, artist_id, name):
        self.artist_id = artist_id
        self.artist_name = name
        self.albums = []
        self.artist_image = None


class Album:
    def __init__(self, album_id, album_title, album_date, album_cover=None):
        self.album_id = album_id
        self.album_title = album_title
        self.album_date = album_date
        self.album_cover = album_cover
        self.tracks = []


class Track(Genre, Artist, Album):
    def __init__(self, genre_id, genre_name, artist_id, artist_name, album_id, album_title, album_date,
                 track_id, track_number, track_title, track_date, path, album_cover=None, track_cover=None, track_embedded_cover=None):
        Genre.__init__(self, genre_id, genre_name)
        Artist.__init__(self, artist_id, artist_name)
        Album.__init__(self, album_id, album_title, album_date, album_cover)
        self.track_id = track_id
        self.track_number = track_number
        self.track_title = track_title
        self.track_date = track_date
        self.track_cover = track_cover
        self.track_embedded_cover = track_embedded_cover
        self.path = path


class TrackManager(Connection):
    def __init__(self):
        Connection.__init__(self)

    def add_genre(self, genre_name):
        if TrackManager().get_genre(genre_name) is None:
            sql = "INSERT INTO genres (name) VALUES ('%s')" % genre_name
            self.conn.execute(sql)
            self.db.commit()
        return TrackManager().get_genre(genre_name)

    def add_artist(self, artist_name):
        if TrackManager().get_artist(artist_name) is None:
            sql="INSERT INTO artists (name) VALUES ('%s')" % artist_name
            self.conn.execute(sql)
            self.db.commit()
        return TrackManager().get_artist(artist_name)

    def add_album(self, album_title, album_date, album_cover):
        if TrackManager().get_album(album_title) is None:
            sql = "INSERT INTO albums (title, date, cover) VALUES ('%s', %d, '%s')" % (album_title, int(album_date), album_cover)
            self.conn.execute(sql)
            self.db.commit()
        return TrackManager().get_album(album_title)

    def add_or_update_track(self, genre_name, artist_name, album_title, album_date, track_number, track_title,
                            track_date, path, album_cover=None, track_cover=None, track_embedded_cover=0):
        genre_name = check_text(genre_name)
        artist_name = check_text(artist_name)
        album_title = check_text(album_title)
        track_title = check_text(track_title)
        path = check_text(path)
        album_cover = album_cover if album_cover is None else check_text(album_cover)
        track_cover = track_cover if track_cover is None else check_text(track_cover)

        if re.match(r"\d+/\d+", track_number):
            track_number = track_number.split('/')[0]

        artist = TrackManager().get_artist(artist_name)
        artist = artist if artist is not None else TrackManager().add_artist(artist_name)

        genre = TrackManager().get_genre(genre_name)
        genre = genre if genre is not None else TrackManager().add_genre(genre_name)

        album = TrackManager().get_album(album_title)
        # for tag in album ....
        if album and album.album_cover != album_cover:
            sql = "UPDATE albums SET cover = '%s' WHERE title = '%s'" % (album_cover, album_title)
            self.conn.execute(sql)
            self.db.commit()
        else:
            album = TrackManager().add_album(album_title, album_date, album_cover)

        res = self.get_track(path)
        sql = ""

        if res is None:
            sql= "INSERT INTO tracks \
                (genreID, artistID, albumID, tracknumber, title, date, cover, embedded_cover, path) \
                VALUES (%d, %d, %d, %d, '%s', %d, '%s', %d, '%s')" % (genre.genre_id, artist.artist_id, album.album_id, int(track_number),
                                                                 track_title, int(track_date), track_cover, track_embedded_cover, path)

        # update tags
        else:
            sql = "UPDATE tracks SET \
                genreID = %d, artistID = %d, albumID = %d, tracknumber = %d, title = '%s', date = %d, cover = '%s', embedded_cover = '%s', path = '%s' \
                WHERE id = %d" % (genre.genre_id, artist.artist_id, album.album_id, int(track_number),
                                    track_title, int(track_date), track_cover, track_embedded_cover, path, res.track_id)
                
        self.conn.execute(sql)
        self.db.commit()
        return self.get_track(path)

    def get_genre(self, genre_name):
        sql = "SELECT id, name FROM genres WHERE genres.name ='%s'" % genre_name
        self.conn.execute(sql)
        res = self.conn.fetchone()
        return Genre(res[0], res[1]) if res else None

    def get_all_genres(self):
        sql = "SELECT id, name FROM genres ORDER BY RANDOM() LIMIT 50"
        self.conn.execute(sql)
        res = self.conn.fetchall()
        grs = [Genre(g[0], g[1]) for g in res]
        random.shuffle(grs)
        for g in grs:
            sql = "SELECT cover FROM tracks WHERE genreID=%d" % g.genre_id
            self.conn.execute(sql)
            res = self.conn.fetchone()
            g.genre_image = res[0]
        return grs

    def get_genre_by_id(self, genre_id):
        sql = "SELECT id, name FROM genres WHERE id=%d" % genre_id
        self.conn.execute(sql)
        res = self.conn.fetchone()
        gr = Genre(res[0], res[1])
        sql = ("SELECT genres.id, genres.name, artists.id, artists.name, albums.id, \
                albums.title, albums.date, tracks.id, tracks.tracknumber, tracks.title, tracks.date, tracks.path, albums.cover, tracks.cover, tracks.embedded_cover \
             FROM tracks \
            LEFT JOIN genres ON genres.id = tracks.genreID \
               LEFT JOIN artists on artists.id = tracks.artistID \
               LEFT join albums on albums.id = tracks.albumID \
            WHERE genres.id = %d" % gr.genre_id)
        self.conn.execute(sql)
        res = self.conn.fetchall()
        alb_id = {}
        for trk in res:
            if trk[4] not in alb_id.keys():
                alb_id[trk[4]] = Album(trk[4], trk[5], trk[6], trk[12])
                alb_id[trk[4]].tracks.append(trk)
            else:
                pass
                alb_id[trk[4]].tracks.append(
                    Track(trk[0], trk[1], trk[2], trk[3], trk[4], trk[5], trk[6], trk[7], trk[8], trk[9], trk[10],
                            trk[11], trk[12], trk[13]))

        alb = [a for a in alb_id.values()]
        gr.albums = alb
        return gr

    def get_all_artists(self):
        sql = "SELECT id, name FROM artists ORDER BY RANDOM() LIMIT 100"
        self.conn.execute(sql)
        res = self.conn.fetchall()
        arts = [Artist(a[0], a[1]) for a in res]
        random.shuffle(arts)
        for a in arts:
            sql = "SELECT cover FROM tracks WHERE artistID=%d" % a.artist_id
            self.conn.execute(sql)
            res = self.conn.fetchone()
            a.artist_image = res[0]
        return arts

    def get_artist_by_id(self, artist_id):
        sql = "SELECT id, name FROM artists WHERE id=%d" % artist_id
        self.conn.execute(sql)
        res = self.conn.fetchone()
        artist = Artist(res[0], res[1])
        sql = ("SELECT genres.id, genres.name, artists.id, artists.name, albums.id, \
                albums.title, albums.date, tracks.id, tracks.tracknumber, tracks.title, tracks.date, tracks.path, albums.cover, tracks.cover, tracks.embedded_cover \
             FROM tracks \
            LEFT JOIN genres ON genres.id = tracks.genreID \
               LEFT JOIN artists on artists.id = tracks.artistID \
               LEFT join albums on albums.id = tracks.albumID \
            WHERE artists.id = %d" % artist.artist_id)
        self.conn.execute(sql)
        res = self.conn.fetchall()
        alb_id = {}
        for trk in res:
            if trk[4] not in alb_id.keys():
                alb_id[trk[4]] = Album(trk[4], trk[5], trk[6], trk[12])
                alb_id[trk[4]].tracks.append(Track(res[0], trk[1], trk[2], trk[3], trk[4], trk[5], trk[6], trk[7], trk[8], trk[9], trk[10], trk[11], trk[12], trk[13]))
            else:
                alb_id[trk[4]].tracks.append(Track(res[0], trk[1], trk[2], trk[3], trk[4], trk[5], trk[6], trk[7], trk[8], trk[9], trk[10], trk[11], trk[12], trk[13]))
        alb = [a for a in alb_id.values()]
        artist.albums = alb
        return artist

    def get_artist(self, artist_name):
        sql = "SELECT id, name FROM artists WHERE name='%s'" % artist_name
        self.conn.execute(sql)
        res = self.conn.fetchone()
        return Artist(res[0], res[1]) if res is not None else None

    def get_album(self, album_title):
        sql = "SELECT id, title, date, cover FROM albums WHERE title='%s'" % album_title
        self.conn.execute(sql)
        res = self.conn.fetchone()
        return Album(res[0], res[1], res[2], res[3]) if res else None

    def get_full_album(self, album_id):
        sql = "SELECT id, title, date, cover FROM albums WHERE id=%d" % album_id
        self.conn.execute(sql)
        res = self.conn.fetchone()
        album = Album(res[0], res[1], res[2], res[3])
        sql = "SELECT id FROM tracks WHERE albumID = %d" % album_id
        self.conn.execute(sql)
        res = self.conn.fetchall()
        album.tracks = sorted([self.get_track2(t_id) for t_id in res], key=lambda t:t.track_number)
        return album

    def get_all_albums (self):
        sql = "SELECT id, title, date, cover FROM albums ORDER BY id"
        self.conn.execute(sql)
        albums = []
        for a in self.conn.fetchall():
            albums.append(Album(a[0], a[1], a[2], a[3]))
        return albums

    def get_track(self, path):
        sql = "SELECT genres.id, genres.name, artists.id, artists.name, albums.id, \
                albums.title, albums.date, tracks.id, tracks.tracknumber, tracks.title, tracks.date, tracks.path, albums.cover, tracks.cover, tracks.embedded_cover \
             FROM tracks \
            LEFT JOIN genres ON genres.id = tracks.genreID \
               LEFT JOIN artists on artists.id = tracks.artistID \
               LEFT join albums on albums.id = tracks.albumID \
            WHERE path = '%s'" % path
        self.conn.execute(sql)
        res = self.conn.fetchone()
        return Track(res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7], res[8], res[9], res[10], res[11], res[12], res[13]) if res else None

    def get_track2(self, track_id):
        sql = "SELECT genres.id, genres.name, artists.id, artists.name, albums.id, \
                albums.title, albums.date, tracks.id, tracks.tracknumber, tracks.title, tracks.date, tracks.path, albums.cover, tracks.cover, tracks.embedded_cover \
             FROM tracks \
            LEFT JOIN genres ON genres.id = tracks.genreID \
               LEFT JOIN artists on artists.id = tracks.artistID \
               LEFT join albums on albums.id = tracks.albumID \
            WHERE tracks.id = %d" % track_id
        self.conn.execute(sql)
        res = self.conn.fetchone()
        return Track(res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7], res[8], res[9], res[10], res[11], res[12], res[13]) if res else None

    def search_tracks(self, pattern):
        sql = "SELECT genres.id, genres.name, artists.id, artists.name, albums.id, \
                        albums.title, albums.date, tracks.id, tracks.tracknumber, tracks.title, tracks.date, tracks.path, albums.cover, tracks.cover, tracks.embedded_cover \
                     FROM tracks \
                    LEFT JOIN genres ON genres.id = tracks.genreID \
                       LEFT JOIN artists on artists.id = tracks.artistID \
                       LEFT join albums on albums.id = tracks.albumID \
                    WHERE tracks.title LIKE '%{}%'".format(pattern)
        self.conn.execute(sql)
        res = self.conn.fetchall()
        res = [Track(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10], item[11],
                     item[12], item[13]) for item in res]
        return res

    def get_all_tracks(self):
        sql = "SELECT genres.id, genres.name, artists.id, artists.name, albums.id, \
                        albums.title, albums.date, tracks.id, tracks.tracknumber, tracks.title, tracks.date, tracks.path, albums.cover, tracks.cover, tracks.embedded_cover \
                     FROM tracks \
                    LEFT JOIN genres ON genres.id = tracks.genreID \
                       LEFT JOIN artists on artists.id = tracks.artistID \
                       LEFT join albums on albums.id = tracks.albumID "
        self.conn.execute(sql)
        res = self.conn.fetchall()
        res = [Track(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10],
                     item[11],
                     item[12], item[13]) for item in res]
        return res

    def search_albums(self, pattern):
        sql = "SELECT id, title, date, cover FROM albums WHERE title LIKE '%{}%'".format(pattern)
        self.conn.execute(sql)
        resp = self.conn.fetchall()
        albums = []
        for res in resp:
            album = Album(res[0], res[1], res[2], res[3])
            sql = "SELECT id FROM tracks WHERE albumID = %d" % album.album_id
            self.conn.execute(sql)
            res = self.conn.fetchall()
            album.tracks = sorted([self.get_track2(t_id) for t_id in res], key=lambda t: t.track_number)
            albums.append(album)
        return albums

    def search_artists(self, pattern):
        sql = "SELECT id FROM artists WHERE name LIKE '%{}%'".format(pattern)
        self.conn.execute(sql)
        res = self.conn.fetchall()
        arts = [self.get_artist_by_id(int(a[0])) for a in res]
        for a in arts:
            sql = "SELECT cover FROM tracks WHERE artistID=%d" % a.artist_id
            self.conn.execute(sql)
            res = self.conn.fetchone()
            a.artist_image = res[0]
        return arts if res is not None else None

    def del_track(self, track_id):
        sql = "DELETE FROM tracks WHERE id = %d" % track_id
        self.conn.execute(sql)
        self.db.commit()

    def del_album(self, album_id):
        sql = "DELETE FROM albums WHERE id = %d" % album_id
        self.conn.execute(sql)
        self.db.commit()

    def del_artist(self, artist_id):
        sql = "DELETE FROM artists WHERE id = %d" % artist_id
        self.conn.execute(sql)
        self.db.commit()

    def del_genre(self, genre_id):
        sql = "DELETE FROM genres WHERE id = %d" % genre_id
        self.conn.execute(sql)
        self.db.commit()


def check_text(text):
    text = text.strip()
    text = text.replace("'", "''")
    return text
