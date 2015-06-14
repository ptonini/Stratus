__author__ = 'ptonini'

import re
import os
import sys
import math
import time

from ConfigParser import ConfigParser

from gmusicapi import Musicmanager
from pymongo import MongoClient
from gmusicapi import Mobileclient
import lib.classes as classes

def get_vars(filename):
    config = ConfigParser()
    config.read(filename)
    oauth_file = config.get('global', 'oauth_file')
    gmusic_user = config.get('global', 'gmusic_user')
    gmusic_pass = config.get('global', 'gmusic_pass')
    mongo_address = config.get('global', 'mongo_address')
    mongo_port = config.get('global', 'mongo_port')
    library_home = config.get('global', 'library_home')
    playlists_home = config.get('global', 'playlists_home')
    return oauth_file, gmusic_user, gmusic_pass, mongo_address, mongo_port, library_home, playlists_home


def open_db(database):
    try:
        print 'Connecting to DB',
        client = MongoClient(database)
    except Exception as e:
        print '                         error:', type(e), e
        sys.exit(1)
    else:
        print '                         ok'
        return client.stratus


def open_musicmanager(cred):
    mm = Musicmanager()
    try:
        print 'Connecting to Google Music (MM)',
        mm.login(oauth_credentials=cred)
    except Exception as e:
        print '          error:', type(e), e
        sys.exit(1)
    else:
        print '          ok'
        return mm


def open_mobileclient(user, paswd):
    mc = Mobileclient()
    try:
        print 'Connecting to Google Music (MC)',
        mc.login(user, paswd)
    except Exception as e:
        print '          error:', type(e), e
        sys.exit(1)
    else:
        print '          ok'
        return mc


def get_gm_playlists(mc):
    try:
        print 'Retrieving Google Music playlists',
        gm_playlists = mc.get_all_user_playlist_contents()
    except Exception as e:
        print '        error:', type(e), e
        sys.exit(1)
    else:
        print '        ok'
        return gm_playlists


def get_filelist(folder, pattern):
    filelist = list()
    for root, path, files in os.walk(folder):
        for file in files:
            if re.match(pattern, file):
                root = root.replace(folder, '')
                file = os.path.join(root, file)
                filelist.append([folder, root, file])
    return filelist


def build_track_collection_from_mp3(db, library_home):
    for folder, root, file in get_filelist(library_home, '.*.mp3$'):
        track = classes.Tracks([folder, file])
        track.update_db(db)

def match_database_to_gmusic(db, mm):
        print 'Matching database do Google Music:',
        missing_tracks = db.tracks.find( { "gmusic_id" : { "$exists" : False } }).batch_size(1)
        if missing_tracks.count() == 0:
            print 'all tracks matched.'
        else:
            print len(missing_tracks), 'tracks will be uploaded.'
            for entry in missing_tracks:
                track = classes.Tracks(entry)
                try:
                    track.upload_to_gmusic(mm)
                except:
                    print "Error uploading", track.filename
                else:
                    track.update_db(db)

def build_master_playlists(db, mc, gm_playlists):
    print 'Building Master playlists:',
    all_tracks_list = list()
    partial_track_lists = list()
    tracks = list()
    for entry in db.playlists.find():
        if 'Master playlist' not in entry['name']:
            playlist = classes.Playlists(entry)
            for track in playlist.tracks:
                all_tracks_list.append(track)
    list_count =  int(math.ceil(len(all_tracks_list)/1000.0))
    print str(len(all_tracks_list)) + ' tracks found, building '  + str(list_count) + ' playlist(s).'
    for index, track in enumerate(all_tracks_list):
        tracks.append(track)
        if len(tracks) == 1000 or len(all_tracks_list) - 1 == index:
            partial_track_lists.append(tracks)
            tracks = list()
    for index, track_list in enumerate(partial_track_lists):
        master_playlist = dict()
        master_playlist['name'] = 'Master playlist ' + str(index)
        master_playlist['full_filename'] = None
        master_playlist['timestamp'] = int(time.time())
        master_playlist['tracks'] = track_list
        playlist = classes.Playlists(master_playlist)
        playlist.update_db(db)
        playlist.update_gmusic(db, mc, gm_playlists)
        playlist.update_db(db)