#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
import os

import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from gmusicapi import Mobileclient
from gmusicapi import Musicmanager
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from pymongo import MongoClient
import warnings


class Tracks:
    def __init__(self, source):
        if isinstance(source, dict):
            self.__dict__.update(source)
            self.source = "db"
        elif os.path.isfile(source):
            audio = MP3(source)
            tag = EasyID3(source)
            self.source = 'file'
            self.filename = source
            self.length = audio.info.length
            if 'genre' in tag:
                self.genre = tag['genre'][0]
            if 'artist' in tag:
                self.artist = tag['artist'][0]
            if 'performer' in tag:
                self.albumArtist = tag['performer'][0]
            if 'album' in tag:
                self.album = tag['album'][0]
            if "date" in tag:
                self.year = tag['date'][0]
            if 'tracknumber' in tag:
                self.trackNumber = tag['tracknumber'][0]
            if 'title' in tag:
                self.title = tag['title'][0]
            if 'discnumber' in tag:
                self.discNumber = tag['discnumber'][0]
            else:
                self.discNumber = "1"
        else:
            print 'Unable to create instance: undefined source: ' + str(source)
    def deleteFromDb(self, TracksColl):
        pass
    def deleteFromDisk(self):
        pass
    def deleteFromGMusic(self, cred):
        pass


def getSonglist(user, password):
    api = Mobileclient()
    api.login(user, password)
    return api.get_all_songs()


def openTracksCollection(database):
    client = MongoClient(database)
    db = client.stratus
    #db.tracks.drop()
    return db.tracks


def getFilelist(folder):
    filelist = []
    for root, path, files in os.walk(folder):
        for name in files:
            p = re.compile('.*.mp3$')
            if p.match(name):
                file = os.path.join(root, name)
                filelist.append(file)
    print 'filelist', len(filelist)
    return filelist


def buildTracksCollection(tracksColl, filelist):
    for file in filelist:
        track = Tracks(file)
        trackCount = tracksColl.find({'filename': file}).count()
        if trackCount == 0:
            tracksColl.insert(track.__dict__)
        elif trackCount == 1:
            pass
        elif trackCount > 1:
            print 'Error: duplicate tracks on database'


def uploadTracks(tracksColl, cred):
    mm = Musicmanager()
    if mm.login(oauth_credentials=cred):
        for doc in tracksColl.find():
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
            tracksColl.update({'_id': track._id}, track.__dict__)


def main():

    tracksColl = openTracksCollection('mongodb://localhost:27017')
    filelist = getFilelist('/mnt/Musicas/Google Music/AC DC')
    #songlist = getSonglist(sys.argv[1], sys.arv[2])

    buildTracksCollection(tracksColl, filelist)
    uploadTracks(tracksColl, './oauth.cred')


if __name__ == '__main__':

    warnings.filterwarnings('ignore')

    main()


