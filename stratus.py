#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
import os
import argparse
import sys

from gmusicapi import Mobileclient
from mutagen.easyid3 import EasyID3
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
            print 'Unable to create instance: undefined source: ' + str(source)


def getSonglist(user, password):
    api = Mobileclient()
    api.login(user, password)
    return api.get_all_songs()


def openTracksCollection(database):
    client = MongoClient(database)
    db = client.stratus
    tracksColl = db.tracks
    return tracksColl


def getFilelist(folder):
    filelist = []
    for root, path, files in os.walk(folder):
        for name in files:
            p = re.compile('.*.mp3$')
            if p.match(name):
                file = os.path.join(root, name)
                filelist.append(file)
    return filelist


def buildTracksCollection(tracksColl, filelist):

    for file in filelist:
        track = Tracks(file)
        trackCount = tracksColl.find({"filename": file}).count()
        if trackCount == 0:
            tracksColl.insert(track.__dict__)
        elif trackCount > 1:
            print 'Error: duplicate tracks on database'


def matchTrackToSong(tracksColl, songlist):

    for doc in tracksColl.find():
        track = Tracks(doc)
        for song in songlist:
            if song['title'] == track.title and song['albumArtist'] == track.albumArtist and song['album'] == track.album:
                setattr(track, 'gmusic_id', song['id'])
                break
        tracksColl.update({'_id': track._id}, track.__dict__)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', dest='root', required=True, help='Hostname')
    parser.add_argument('-d', dest='db', required=True, help='Database')
    parser.add_argument('-U', dest='user', required=True, help='Username')
    parser.add_argument('-P', dest='password', required=True, help='Password')
    args = parser.parse_args(sys.argv[1:])

    tracksColl = openTracksCollection(args.db)
    filelist = getFilelist(args.root)
    songlist = getSonglist(args.user, args.password)

    buildTracksCollection(tracksColl, filelist)
    matchTrackToSong(tracksColl, songlist)



if __name__ == '__main__':
    main()


