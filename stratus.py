#!/usr/bin/python

from gmusicapi import Musicmanager
import os

from gmusicapi import Mobileclient
from prettytable import PrettyTable
from prettytable import ALL
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

    def checkGMusic(self):
        return True


def __init__(self, user, password):
    api = Mobileclient()
    api.login('pedro.tonini', 'besTeira07')
    return api.get_all_songs()


songs = songlist[0]
#for s in songs.iteritems:
#    print s
#    break

t = PrettyTable(['Key', 'Value'])
t.hrules = ALL
t.header_style = 'upper'
t.align = 'l'
t.padding_width = 3
song = songlist[0]
for k, v in song.iteritems():
    t.add_row([k, v])
print t.get_string(sortby='Key')
print len(songlist)


#for root, path, files in os.walk('/mnt/Musicas/Google Music/AC DC'):
#    for name in files:
#        file = os.path.join(root, name)
#/        track = Tracks(file)
        #print track.genre, track.artist, track.year, track.album, track.trackNum, track.trackName



