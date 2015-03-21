#!/usr/bin/python

import re
import os

from gmusicapi import Mobileclient
from mutagen.id3 import ID3


class Tracks:
    """"""

    def __init__(self, file):
        """ """

        tag = ID3(file)
        self.filename = file
        self.genre = str(tag['TCON'].pprint())[5:]
        self.artist = str(tag['TPE1'].pprint())[5:]
        self.albumArtist = str(tag['TPE2'].pprint())[5:]
        self.album = str(tag['TALB'].pprint())[5:]
        self.year = int(str(tag['TDRC'].pprint())[5:])
        self.trackNumber = int(str(tag['TRCK'].pprint())[5:])
        self.title = str(tag['TIT2'].pprint())[5:]


    def matchSong(self, songlist):
        """"""
        matched = False
        for song in songlist:
            if song['title'] == self.title:
                print self.title, '- is on Google Music'
                matched = True
                break
        if not matched:
            print '!!! Could not find "' + self.title + '" on Google Music'


def getSongList(user, password):
    api = Mobileclient()
    api.login('', '')
    return api.get_all_songs()


songlist = getSongList('pedro.tonini', 'besTeira07')

for root, path, files in os.walk('/mnt/Musicas/01 Principal/Albums/AC DC/'):
    for name in files:
        p = re.compile('.*.mp3$')
        if p.match(name):
            file = os.path.join(root, name)
            track = Tracks(file)
            track.matchSong(songlist)


