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
    oauth_file = config.get('global', 'oauth_file')
    gmusic_user = config.get('global', 'gmusic_user')
    gmusic_pass = config.get('global', 'gmusic_pass')
    mongo_address = config.get('global', 'mongo_address')
    mongo_port = config.get('global', 'mongo_port')
    library_home = config.get('global', 'library_home')
    playlists_home = config.get('global', 'playlists_home')
    return oauth_file, gmusic_user, gmusic_pass, mongo_address, mongo_port, library_home, playlists_home


def open_db(database):
    try:
        print 'Connecting to DB',
        client = MongoClient(database)
    except Exception as e:
        print '                         error:', type(e), e
        sys.exit(1)
    else:
        print '                         ok'
        return client.stratus


def open_musicmanager(cred):
    mm = Musicmanager()
    try:
        print 'Connecting to Google Music (MM)',
        mm.login(oauth_credentials=cred)
    except Exception as e:
        print '          error:', type(e), e
        sys.exit(1)
    else:
        print '          ok'
        return mm


def open_mobileclient(user, paswd):
    mc = Mobileclient()
    try:
        print 'Connecting to Google Music (MC)',
        mc.login(user, paswd)
    except Exception as e:
        print '          error:', type(e), e
        sys.exit(1)
    else:
        print '          ok'
        return mc


def get_gm_playlists(mc):
    try:
        print 'Retrieving Google Music playlists',
        gm_playlists = mc.get_all_user_playlist_contents()
    except Exception as e:
        print '        error:', type(e), e
        sys.exit(1)
    else:
        print '        ok'
        return gm_playlists


def get_filelist(folder, pattern):
    filelist = list()
    for root, path, files in os.walk(folder):
        for file in files:
            if re.match(pattern, file):
                root = root.replace(folder, '')
                file = os.path.join(root, file)
                filelist.append([folder, root, file])
    return filelist


