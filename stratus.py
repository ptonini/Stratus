#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
import os

from gmusicapi import Mobileclient
from mutagen.easyid3 import EasyID3
from pymongo import MongoClient


class Tracks:
    """"""

    def __init__(self, file, songlist):
        """ """

        tags = EasyID3(file)
        self.filename = file
        self.genre = tags['genre'][0]
        self.artist = tags['artist'][0]
        self.albumArtist = tags['performer'][0]
        self.album = tags['album'][0]
        self.year = tags['date'][0]
        self.trackNumber = tags['tracknumber'][0]
        self.title = tags['title'][0]
        for song in songlist:
            if song['title'] == self.title and song['albumArtist'] == self.albumArtist and song['album'] == self.album \
                    and song['trackNumber'] == self.trackNumber:
                self.gmusic_id = song['id']
                break



def getSonglist(user, password):
    api = Mobileclient()
    api.login(user, password)
    return api.get_all_songs()


def buildTrackCollection(filelist, songlist, tracksColl):
    for file in filelist:
        track = Tracks(file, songlist)
        trackCount = tracksColl.find({"filename": file}).count()
        if trackCount == 0:
            tracksColl.insert(track.__dict__)
        elif trackCount > 1:
            print 'Error: duplicate tracks on database'


def openTracksCollection(database):
    client = MongoClient()
    db = client.stratus
    tracksColl = db.tracks
    return tracksColl

def getFileList(folder):
    filelist = []
    for root, path, files in os.walk(folder):
        for name in files:
            p = re.compile('.*.mp3$')
            if p.match(name):
                file = os.path.join(root, name)
                filelist.append(file)
    return filelist

def main():
    songlist = getSonglist()
    tracksColl = openTracksCollection('mongodb://localhost:27017/')
    filelist = getFileList('/mnt/Musicas/Google Music')
    buildTrackCollection(filelist, songlist, tracksColl)

if __name__ == '__main__':
    main()
