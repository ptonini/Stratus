#!/usr/bin/python
# -*- coding: utf-8 -*-



import json

import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from gmusicapi import Mobileclient


import lib.classes as classes
import lib.func as func


import warnings




def get_song_list(user, password):
    api = Mobileclient()
    api.login(user, password)
    return api.get_all_songs()


def build_db(db, tracklist, playlists):

    for folder, root, file in tracklist:
        track = classes.Tracks(file, type='file', path=folder)
        track_count = db.tracks.find({'filename': file}).count()
        if track_count == 0:
            pass
            db.tracks.insert(track.__dict__)
        elif track_count == 1:
            pass
        elif track_count > 1:
            print 'Error: duplicate tracks on database'

    for folder, root, file in playlists:
        playlist = classes.Playlists([folder, file], type='list')

        print json.dumps(playlist.__dict__)


def sync_disk_to_gmusic(tracks_collection, mm):
    for dict in tracks_collection.find():
        track = classes.Tracks(dict, type='dict')
        if not hasattr(track, 'gmusic_id'):
            track.add_to_gmusic(mm)
            tracks_collection.update({'_id': track._id}, track.__dict__)


def main():

    mm = func.open_gmusic('./oauth.cred')
    db = func.open_db('mongodb://localhost:27017')

    tracklist = func.get_filelist('/home/ptonini/Música', '.*.mp3$')
    playlists = func.get_filelist('/home/ptonini/Música/0-Playlists','.*.m3u$' )

    #songlist = getSonglist(sys.argv[1], sys.arv[2])

    build_db(db, tracklist, playlists)
    #sync_disk_to_gmusic(tracks_collection, mm)


if __name__ == '__main__':

    warnings.filterwarnings('ignore')

    main()


