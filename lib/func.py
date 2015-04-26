__author__ = 'ptonini'

import re
import os
import sys
import codecs
from ConfigParser import ConfigParser

from gmusicapi import Musicmanager
from pymongo import MongoClient
from gmusicapi import Mobileclient
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen import File
import bson.binary


def get_global_vars(filename):
    config = ConfigParser()
    config.read(filename)
    oauth_file = config.get('global', 'oauth_file').decode('utf-8')
    gmusic_user = config.get('global', 'gmusic_user')
    gmusic_pass = config.get('global', 'gmusic_pass')
    mongo_address = config.get('global', 'mongo_address')
    mongo_port = config.get('global', 'mongo_port')
    library_home = config.get('global', 'library_home').decode('utf-8')
    playlists_home = config.get('global', 'playlists_home').decode('utf-8')
    return  oauth_file, gmusic_user, gmusic_pass, mongo_address, mongo_port, library_home, playlists_home


def open_db(database):
    client = MongoClient(database)
    db = client.stratus
    return db


def open_musicmanager(cred):
    mm = Musicmanager()
    if mm.login(oauth_credentials=cred):
        return mm
    else:
        print 'Error conecting to Google Music (MM)'
        sys.exit(1)


def open_mobileclient(user, paswd):
    mc = Mobileclient()
    if mc.login(user, paswd):
        return mc
    else:
        print 'Error conecting to Google Music (MC)'
        sys.exit(1)


def get_filelist(folder, pattern):
    filelist = list()
    for root, path, files in os.walk(folder):
        for file in files:
            if re.match(pattern, file):
                root = root.replace(folder, '')
                file = os.path.join(root, file)
                filelist.append([folder, root, file])
    return filelist


def get_trackinfo_from(filename, path):
    full_filename = path + filename
    try:
        os.path.isfile(full_filename)
        audio = MP3(full_filename)
        tag = EasyID3(full_filename)
        file = File(full_filename)
    except Exception:
        print 'Invalid file', full_filename
    else:
        metadata = dict()
        metadata['filename'] = filename
        metadata['path'] = path
        metadata['full_filename'] = full_filename
        metadata['length'] = audio.info.length
        metadata['coverart'] = bson.binary.Binary(file.tags['APIC:'].data)
        if 'genre' in tag:
            metadata['genre'] = tag['genre'][0]
        if 'artist' in tag:
            metadata['artist'] = tag['artist'][0]
        if 'performer' in tag:
            metadata['album_artist'] = tag['performer'][0]
        if 'album' in tag:
            metadata['album'] = tag['album'][0]
        if "date" in tag:
            metadata['year'] = tag['date'][0]
        if 'tracknumber' in tag:
            metadata['track_num'] = tag['tracknumber'][0]
        if 'title' in tag:
            metadata['title'] = tag['title'][0]
        if 'discnumber' in tag:
            metadata['disc_num'] = tag['discnumber'][0]
        else:
            metadata['disc_num'] = "1"
        return metadata


def get_playlists_from_folder(filename, path, db):
    metadata = dict()
    metadata['full_filename'] = os.path.join(path, filename)
    metadata['name'] = filename[:-4]
    metadata['timestamp'] = int(os.path.getmtime(metadata['full_filename']))
    with open(metadata['full_filename'], 'r+') as file:
        metadata['tracks'] = list()
        for line in file.readlines():
            if line != '\n':
                metadata['tracks'].append(db.tracks.find_one({'filename': line[:-1]})['_id'])
    return metadata


def get_playlists_from_gmusic(db, mc):
    for playlist in mc.get_all_user_playlist_contents():
        print playlist['name']
        print int(int(playlist['lastModifiedTimestamp']) / 1000000)
        print playlist['id']
        for entry in playlist['tracks']:
            print db.tracks.find_one({'gmusic_id': entry['trackId']})['filename']
