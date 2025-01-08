import json
import os
import random

from app import app
from flask import render_template, request, redirect, flash, url_for
from .models import TrackManager, User, UserManager
from flask_login import current_user, login_user, login_required, logout_user
from .readtags import explore

# init the database
from .schema import create_tables
create_tables()

# init mocp
os.system("mocp --server")

@app.route("/")
@login_required
def home():
    return render_template("skeleton.html", playlist=get_playlist())


@app.route("/albums/", methods=["POST"]) # ajax / render
@login_required
def albums():
    albs = TrackManager().get_all_albums()
    if len(albs) == 0:
        return "Il faut ajouter de la musique -> update db"
    albums_random = []
    for i in range(10):
       albums_random.append(albs[random.randint(0, len(albs)-1)])
    albums_random = [TrackManager().get_full_album(int(a.album_id)) for a in albums_random]
    last_albums = albs[-10:]
    last_albums = [TrackManager().get_full_album(int(a.album_id)) for a in last_albums]
    last_albums.reverse()

    return render_template("albums.html",albums_random=albums_random, last_albums=last_albums)


@app.route("/search/", methods=["POST"]) # ajax / render
@login_required
def search():
    pattern = request.json["pattern"]
    trks = TrackManager().search_tracks(pattern)
    alb = TrackManager().search_albums(pattern)
    arts = TrackManager().search_artists(pattern)
    return render_template("search.html", trks=trks, albums=alb, arts=arts)


@app.route("/album/", methods=["POST"]) # ajax / render
@login_required
def album():
    album_id = request.json["album_id"]
    return render_template("album.html", album=TrackManager().get_full_album(int(album_id)))


@app.route('/get_track/', methods=["POST"]) # ajax
def get_track():
    track_id = request.json["track_id"]
    return json.dumps(TrackManager().get_track2(int(track_id)).__dict__)


@app.route("/get_album", methods=["POST"]) # ajax
def get_album():
    album_id = request.json["album_id"]
    res = []
    for a in TrackManager().get_full_album(int(album_id)).tracks:
        res.append(a.__dict__)
    return json.dumps(res)


@app.route('/get_track_list', methods=['POST']) # ajax
def get_track_list():
    return get_playlist()


@app.route("/artist/", methods=['POST'] ) # ajax / render
@login_required
def artist():
    artist_id = request.json["artist_id"]
    art = TrackManager().get_artist_by_id(int(artist_id))
    return render_template("artist.html", art=art)


@app.route("/artists/", methods=['POST']) # ajax / render
@login_required
def artists():
    arts = TrackManager().get_all_artists()
    return render_template("artists.html", arts=arts)


@app.route("/genres/", methods=['POST']) # ajax / render
@login_required
def genres():
    gnr = TrackManager().get_all_genres()
    return render_template("genres.html", gnr=gnr)


@app.route("/genre/", methods=['POST'])  # ajax / render
@login_required
def genre():
    genre_id = request.json["genre_id"]
    gnr = TrackManager().get_genre_by_id(int(genre_id))
    return render_template("genre.html", gnr=gnr)


@app.route('/save_playlist', methods=['POST']) # ajax
def save_playlist():
    with open ("app/static/user_data/%d_playlist.json" % current_user.id, "w") as f:
        json.dump(request.json["playlist"], f, ensure_ascii=False, indent=4)
    return "playlist saved!"


@app.route("/clear_playlist", methods=["POST"]) #ajax
def clear_playlist():
    try:
        os.remove("app/static/user_data/%d_playlist.json" % current_user.id)
    except FileNotFoundError:
        return "no playlist to delete"
    return "playlist deleted"


def get_playlist():
    playlist = []
    try:
        with open("app/static/user_data/%d_playlist.json" % current_user.id, "r") as f:
            playlist = json.load(f)
    except FileNotFoundError:
        pass
    return playlist


@app.route("/update_db/", methods=["POST"]) #ajax
def update_data_base():
    print("Start update database")
    explore(app.config["SOURCE"])
    return render_template("skeleton.html", playlist=get_playlist())

@app.route("/play", methods=["POST"]) #ajax)
def play():
    instruction = ""
    match request.json["instruction"]:
        case "playit":
            instruction = "mocp --playit \"app/%s\"" % request.json["arg"]
        case "stop":
            instruction = "mocp --stop"
        case "pause":
            instruction = "mocp --pause"
        case "play":
            instruction = "mocp --unpause"
        case "seek":
            instruction = "mocp --jump %ss" % request.json["arg"]
        case "volume":
            instruction = "mocp --volume %s" % request.json["arg"]
    os.system(instruction)
    print(instruction)
    return instruction


@app.route("/server_info", methods=["POST"]) #ajax)
def server_info():
    res = dict()
    res["state"] = os.popen("mocp --format '%state'").read().rstrip('\n')
    res["duration"] = os.popen("mocp --format '%ts'").read().rstrip('\n')
    res["currentSeconds"] = os.popen("mocp --format '%cs'").read().rstrip('\n')
    res["file"] = os.popen("mocp --format '%file'").read().rstrip('\n')
    res["artist"] = os.popen("mocp --format '%artist'").read().rstrip('\n')
    res["title"] = os.popen("mocp --format '%song'").read().rstrip('\n')

    return json.dumps(res)


# Users
@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    else:
        if request.method ==  "POST":
            u = UserManager().get_user(request.form["email"])
            if u is None or not u.check_password(request.form["password"]):
                flash("Echec de l'authentification")
                return render_template("login.html")
            login_user(u, remember=True)
            return redirect("/")
    return render_template("login.html", title="Sign In")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = {"firstname": "", "lastname": "", "email": "", "password": ""}
    if request.method == "POST":
        if request.form["password"] != request.form["password2"]:
            flash("Les deux mots de passe ne sont pas identiques")
            form = {"firstname": request.form["firstname"], "lastname": request.form["lastname"], "email": request.form["email"], "password": request.form["password"]}
            return render_template("register.html", form=form)
        else:
            u = User(request.form["email"], request.form["firstname"], request.form["lastname"])
            u.set_password(request.form["password"])
            u = UserManager().add_user(u)
            login_user(u, remember=True)
        return  redirect("/")
    return render_template("register.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for('login'))
