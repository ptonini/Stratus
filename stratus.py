#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
import os
import argparse
import sys
import json

from gmusicapi import Mobileclient
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from pymongo import MongoClient


class Tracks:
    def __init__(self, source):
        if isinstance(source, dict):
            self.__dict__.update(source)
            self.source = "db"
        elif os.path.isfile(source):
            tag = EasyID3(source)
            self.filename = source
            self.source = 'file'
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

            audio = MP3(source)
            self.length = int(audio.info.length)

            #print json.dumps(self.__dict__)

        else:
            print 'Unable to create instance: undefined source: ' + str(source)


def getSonglist(user, password):
    api = Mobileclient()
    api.login(user, password)
    return api.get_all_songs()


def openTracksCollection(database):
    client = MongoClient(database)
    db = client.stratus
#    db.tracks.drop()
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
    i = 0
    for file in filelist:
        track = Tracks(file)
        trackCount = tracksColl.find({"filename": file}).count()
        if trackCount == 0:
            tracksColl.insert(track.__dict__)
        elif trackCount > 1:
            print 'Error: duplicate tracks on database'


def matchTrackToSong(tracksColl, songlist):
    matched = []
    notmatched = []
    print 'songlist', len(songlist)
    print 'docs', tracksColl.find().count()
    for doc in tracksColl.find():
        track = Tracks(doc)
        for song in songlist:
            length = int(song['durationMillis']) / 1000
            if song['title'] == track.title and song['album'] == track.album: #and (track.length - 2) < length < (track.length + 2):
               # print 'matched "' + track.filename + ' -------> "' + song['title']
                matched.append(True)
                setattr(track, 'gmusic_id', song['id'])
                tracksColl.update({'_id': track._id}, track.__dict__)
                break

    for doc in tracksColl.find():
        if 'gmusic_id' not in doc:
            notmatched.append(True)
            #print doc['filename']
    print 'matched', len(matched)
    print 'not matched', len(notmatched)

def main():



    tracksColl = openTracksCollection('mongodb://localhost:27017')
    filelist = getFilelist('/mnt/Musicas/Google Music')
    songlist = getSonglist(sys.argv[1], sys.argv[2])

    #
    buildTracksCollection(tracksColl, filelist)
    matchTrackToSong(tracksColl, songlist)



if __name__ == '__main__':
    main()


