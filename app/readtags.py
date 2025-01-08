import mutagen
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import os
from .models import TrackManager

#source = "static/musique"
music_ext = {"flac": ["flac", "FLAC"], "ogg": ["ogg", "OGG"], "mp3": ["mp3", "MP3"]}
cover_ext = ["jpg", "JPG"]
cover_name = ["cover", "Cover", "Folder", "folder", ]

def explore(current_dir):
	try:
		for entry in os.listdir(current_dir):
			explore("%s/%s" % (current_dir, entry))
	except NotADirectoryError:
		f_m = "jojo"
		parent_dir = "/".join(current_dir.split('/')[0:-1])
		ext = current_dir.split(".")[-1]
		embedded_cover = 0
		cover = None

		if ext in music_ext["flac"]:
			try:
				f_m = FLAC(current_dir)
			except mutagen.flac.FLACNoHeaderError:
				pass
			pics = f_m.pictures
			for p in pics:
				if p.type == 3:  # front cover
					pass
					break

		elif ext in music_ext["mp3"]:
			try:
				f_m = MP3(current_dir, ID3=EasyID3)
			except mutagen.mp3.HeaderNotFoundError:
				pass
			# embedded cover

		# recherhe image
		for f in os.listdir(parent_dir):
			if f.split(".")[-1] in cover_ext and f.split(".")[0] in cover_name:
				cover = "%s/%s" % (parent_dir, f)
				# adaptation foireuse, la même pour le fichier son:
				cover = "/".join(cover.split("/")[1:])
				break

		# genre_name, artist_name, album_title, album_date, track_number, track_title, track_date, album_cover = None, track_cover = None, track_embedded_cover = None)
		if f_m != "jojo":
			TrackManager().add_track(f_m["genre"][0], f_m["artist"][0], f_m["album"][0], f_m["date"][0],
								 f_m["tracknumber"][0], f_m["title"][0], f_m["date"][0], "/".join(current_dir.split("/")[1:]), cover, cover, embedded_cover)

		return 1
	# delete from base if file doesn't exist


#explore(source)

