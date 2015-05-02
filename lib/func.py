__author__ = 'ptonini'

import re
import os
import sys
from ConfigParser import ConfigParser

from gmusicapi import Musicmanager
from pymongo import MongoClient
from gmusicapi import Mobileclient


def get_vars(filename):
    config = ConfigParser()
    config.read(filename)
    oauth_file = config.get('global', 'oauth_file').decode('utf-8')
    gmusic_user = config.get('global', 'gmusic_user')
    gmusic_pass = config.get('global', 'gmusic_pass')
    mongo_address = config.get('global', 'mongo_address')
    mongo_port = config.get('global', 'mongo_port')
    library_home = config.get('global', 'library_home').decode('utf-8')
    playlists_home = config.get('global', 'playlists_home').decode('utf-8')
    return oauth_file, gmusic_user, gmusic_pass, mongo_address, mongo_port, library_home, playlists_home


def open_db(database):
    client = MongoClient(database)
    return client.stratus


def open_musicmanager(cred):
    mm = Musicmanager()
    if mm.login(oauth_credentials=cred):
        return mm
    else:
        print 'Error conecting to Google Music (MM)'
        sys.exit(1)


def open_mobileclient(user, paswd):
    mc = Mobileclient()
    if mc.login(user, paswd):
        return mc
    else:
        print 'Error conecting to Google Music (MC)'
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


