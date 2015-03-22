#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
import os

from gmusicapi import Mobileclient
from mutagen.easyid3 import EasyID3
from pymongo import MongoClient


class Tracks:

    def __init__(self, source):
        """ """
        if isinstance(source, dict):
             self.__dict__.update(source)
        elif os.path.isfile(source):
            try:
                tag = EasyID3(source)
                self.filename = source
                self.genre = tag['genre'][0]
                self.artist = tag['artist'][0]
                self.albumArtist = tag['performer'][0]
                self.album = tag['album'][0]
                self.year = tag['date'][0]
                self.trackNumber = tag['tracknumber'][0]
                self.title = tag['title'][0]
                if 'discnumber' in tag:
                    self.discNumber = tag['discnumber'][0]

            except:
                print source
        else:
            print 'Undefined source'


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


def buildTracksCollection(filelist, tracksColl):
    for file in filelist:
        track = Tracks(file)
        trackCount = tracksColl.find({"filename": file}).count()
        if trackCount == 0:
            tracksColl.insert(track.__dict__)
        elif trackCount > 1:
            print 'Error: duplicate tracks on database'


def main():

    #songlist = getSonglist('')
    tracksColl = openTracksCollection('mongodb://localhost:27017/')
    filelist = getFilelist('/mnt/Musicas/Google Music/AC DC')
    buildTracksCollection(filelist, tracksColl)

    for document in tracksColl.find():
        track = Tracks(document)
        print track.title




if __name__ == '__main__':
    main()


# for song in songlist:
                #     if song['title'] == self.title and song['albumArtist'] == self.albumArtist and song['album'] == self.album:
                #         self.gmusic_id = song['id']
                #         break