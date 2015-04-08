#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
import os

import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from gmusicapi import Mobileclient
from gmusicapi import Musicmanager

from pymongo import MongoClient
import warnings




def get_song_list(user, password):
    api = Mobileclient()
    api.login(user, password)
    return api.get_all_songs()


def open_tracks_collection(database):
    client = MongoClient(database)
    db = client.stratus
    #db.tracks.drop()
    return db.tracks


def get_file_list(folder):
    filelist = []
    for root, path, files in os.walk(folder):
        for name in files:
            p = re.compile('.*.mp3$')
            if p.match(name):
                file = os.path.join(root, name)
                filelist.append(file)
    print 'filelist', len(filelist)
    return filelist


def build_tracks_collection(tracks_collection, filelist):
    for file in filelist:
        track = Tracks(file)
        trackCount = tracks_collection.find({'filename': file}).count()
        if trackCount == 0:
            tracks_collection.insert(track.__dict__)
        elif trackCount == 1:
            pass
        elif trackCount > 1:
            print 'Error: duplicate tracks on database'


def upload_tracks(tracks_collection, cred):
    mm = Musicmanager()
    if mm.login(oauth_credentials=cred):
        for doc in tracks_collection.find():
            track = Tracks(doc)
            print 'uploading', track.filename
            result = mm.upload(track.filename, enable_matching=True)
            if not result[0] == {}:
                print track.filename, 'uploaded\n'
                gmusic_id = result[0][track.filename]
            elif not result[2] == {}:
                print track.filename, 'already exists\n'
                gmusic_id = re.search("\((.*)\)", str(result[2])).group(1)
            setattr(track, 'gmusic_id', gmusic_id)
            tracks_collection.update({'_id': track._id}, track.__dict__)


def main():

    tracks_collection = open_tracks_collection('mongodb://localhost:27017')
    filelist = get_file_list('/mnt/Musicas/Google Music/AC DC')
    #songlist = getSonglist(sys.argv[1], sys.arv[2])

    build_tracks_collection(tracks_collection, filelist)
    upload_tracks(tracks_collection, './oauth.cred')


if __name__ == '__main__':

    warnings.filterwarnings('ignore')

    main()


