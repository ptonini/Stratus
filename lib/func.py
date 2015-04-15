__author__ = 'ptonini'

import re
import os
import sys

from gmusicapi import Musicmanager
from pymongo import MongoClient
from gmusicapi import Mobileclient


def open_db(database):
    client = MongoClient(database)
    db = client.stratus
    return db


def open_gmusic(cred):
    mm = Musicmanager()
    if mm.login(oauth_credentials=cred):
        return mm
    else:
        print 'Error conectiong to Google Music'
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


def get_song_list(user, password):
    api = Mobileclient()
    api.login(user, password)
    return api.get_all_songs()

