#!/usr/bin/python


#from gmusicapi import Musicmanager
from gmusicapi import Mobileclient
from prettytable import PrettyTable
from prettytable import PLAIN_COLUMNS, FRAME, ALL, NONE
import os
from mutagen.id3 import ID3


class Tracks:
   """"""
    def __init__(self, file):
        tag = ID3(file)
        self.filename = file
        self.genre = str(tag['TCON'].pprint())[5:]
        self.artist = str(tag['TPE1'].pprint())[5:]
        self.albumArtist = str(tag['TPE2'].pprint())[5:]
        self.album = str(tag['TALB'].pprint())[5:]
        self.year = int(str(tag['TDRC'].pprint())[5:])
        self.trackNum = int(str(tag['TRCK'].pprint())[5:])
        self.trackName = str(tag['TIT2'].pprint())[5:]



def teste ():

    #mm = Musicmanager()
    #mm.login(oauth_credentials='/home/ptonini/oauth.cred')

    api = Mobileclient()
    logged_in = api.login('', '')

    songlist = api.get_all_songs()

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



for root, path,  files in os.walk('/mnt/Musicas/Google Music/AC DC'):
    for name in files:
        file = os.path.join(root, name)
        track = Tracks(file)
        print track.genre, track.artist, track.album, track.trackNum, track.trackName
        print type(track.year)



