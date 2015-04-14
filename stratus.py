#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
import os
import sys

import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from gmusicapi import Mobileclient
from gmusicapi import Musicmanager

import lib.classes as classes

from pymongo import MongoClient
import warnings


def open_tracks_collection(database):
    client = MongoClient(database)
    db = client.stratus
    db.tracks.drop()
    return db.tracks


def open_gmusic(cred):
    mm = Musicmanager()
    if mm.login(oauth_credentials=cred):
        return mm
    else:
        print 'Error conectiong to Google Music'
        sys.exit(1)


def get_filelist(folder):
    filelist = []
    for root, path, files in os.walk(folder):
        for name in files:
            if re.match('.*.mp3$', name):
                root = root.replace(folder, '')
                file = os.path.join(root, name)
                filelist.append([folder, file])
    print 'filelist', len(filelist)
    return filelist

def get_playlists(folder):
    playlists = dict()
    for root, path, files in os.walk(folder):
        for name in files:
            if re.match('.*.m3u$', name):
                playlist = name[:-4]
                playlists[playlist] = list()
                with open(os.path.join(root, name), 'r+') as file:
                    for line in file.readlines():
                        if line != '\n':
                            playlists[playlist].append(line[:-1])
    for playlist in playlists:
        print playlist
        for index, track in enumerate(playlists.get(playlist)):
            print (index + 1), track



def get_song_list(user, password):
    api = Mobileclient()
    api.login(user, password)
    return api.get_all_songs()


def build_db(tracks_collection, filelist):
    for folder, file in filelist:
        track = classes.Tracks(file, type='file', path=folder)

        trackCount = tracks_collection.find({'filename': file}).count()
        if trackCount == 0:
            pass
            tracks_collection.insert(track.__dict__)
        elif trackCount == 1:
            pass
        elif trackCount > 1:
            print 'Error: duplicate tracks on database'


def sync_disk_to_gmusic(tracks_collection, mm):
    for dict in tracks_collection.find():
        track = classes.Tracks(dict, type='dict')
        if not hasattr(track, 'gmusic_id'):
            track.add_to_gmusic(mm)
            tracks_collection.update({'_id': track._id}, track.__dict__)


def main():

    #gmusic_mm = open_gmusic('./oauth.cred')
    #tracks_collection = open_tracks_collection('mongodb://localhost:27017')

    #filelist = get_filelist('/home/ptonini/Música')
    get_playlists('/home/ptonini/Música/0-Playlists')
    #songlist = getSonglist(sys.argv[1], sys.arv[2])

    #build_db(tracks_collection, filelist)
    #sync_disk_to_gmusic(tracks_collection, gmusic_mm)


if __name__ == '__main__':

    warnings.filterwarnings('ignore')

    main()


