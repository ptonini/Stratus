#!/usr/bin/python

from gmusicapi import Musicmanager
from gmusicapi import Mobileclient
from tabulate import tabulate
from prettytable import PrettyTable
from prettytable import PLAIN_COLUMNS, FRAME, ALL, NONE
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
