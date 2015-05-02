#!/usr/bin/python
# -*- coding: utf-8 -*-


import warnings
import sys

import lib.classes as classes
import lib.func as func


def main():
    oauth_file, gm_user, gm_pass, mongo_address, mongo_port, library_home, playlists_home = func.get_vars(sys.argv[1])

    mm = func.open_musicmanager(oauth_file)
    mc = func.open_mobileclient(gm_user, gm_pass)
    db = func.open_db('mongodb://' + mongo_address + ':' + mongo_port)
    gm_playlists = mc.get_all_user_playlist_contents()

    # db.tracks.drop()
    #db.playlists.drop()


    # Build track collection from mp3 files
    if False:
        for folder, root, file in func.get_filelist(library_home, '.*.mp3$'):
            track = classes.Tracks([folder, file])
            track.update_db(db)

    # Upload/match database to gmusic
    if False:
        for entry in db.tracks.find():
            track = classes.Tracks(entry)
            track.update_gmusic(mm)
            track.update_db(db)

    # Build playlist collection from m3u files
    if True:
        for folder, root, file in func.get_filelist(playlists_home, '.*.m3u$'):
            playlist = classes.Playlists([folder, file], db)
            playlist.update_db(db)

    # Sync DB playlists to gmusic
    if True:
        for entry in db.playlists.find():
            playlist = classes.Playlists(entry)
            playlist.update_gmusic(db, mc, gm_playlists)
            playlist.update_db(db)

    # Sync gmusic playlists to DB
    if True:
        for gm_playlist in gm_playlists:
            playlist = classes.Playlists(gm_playlist, db, playlists_home)
            playlist.update_db(db)


if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    main()