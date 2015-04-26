#!/usr/bin/python
# -*- coding: utf-8 -*-


import warnings
import sys

import lib.classes as classes
import lib.func as func


def main():

    oauth_file, gmusic_user, gmusic_pass, mongo_address, mongo_port, library_home, playlists_home = func.get_global_vars(sys.argv[1])
    print oauth_file, gmusic_user, gmusic_pass, mongo_address, mongo_port, library_home, playlists_home

    mm = func.open_musicmanager(oauth_file)
    mc = func.open_mobileclient(gmusic_user, gmusic_pass)
    db = func.open_db('mongodb://' + mongo_address + ':' + mongo_port)

    tracklist = func.get_filelist(library_home, '.*.mp3$')
    playlists = func.get_filelist(playlists_home, '.*.m3u$')


    db.tracks.drop()
    db.playlists.drop()

    #func.get_playlists_from_gmusic(db, mc)

    if True:
        for folder, root, file in tracklist:
            trackinfo = func.get_trackinfo_from(file, folder)
            track = classes.Tracks(trackinfo)
            track.update_db(db)

        for trackinfo in db.tracks.find():
            track = classes.Tracks(trackinfo)
            track.update_gmusic(mm)
            track.update_db(db)

    if True:
        for folder, root, file in playlists:
            listinfo = func.get_playlists_from_folder(file, folder, db)
            playlist = classes.Playlists(listinfo)
            playlist.update_db(db)

        for list in db.playlists.find():
            playlist = classes.Playlists(list)
            playlist.update_gmusic(db, mc)
            playlist.update_db(db)

if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    main()