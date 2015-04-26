#!/usr/bin/python
# -*- coding: utf-8 -*-


import warnings
import sys

import lib.classes as classes
import lib.func as func


def main():

    oauth_file, gm_user, gm_pass, mongo_address, mongo_port, library_home, playlists_home = func.get_vars(sys.argv[1])

    mm = func.open_musicmanager(oauth_file)
    #mc = func.open_mobileclient(gm_user, gm_pass)
    db = func.open_db('mongodb://' + mongo_address + ':' + mongo_port)

    tracklist = func.get_filelist(library_home, '.*.mp3$')
    playlists = func.get_filelist(playlists_home, '.*.m3u$')


    #db.tracks.drop()
    #db.playlists.drop()




    if False:
        for folder, root, file in tracklist:
            track = classes.Tracks([folder, file], db, mm)
            track.update_db(db)
    if True:
        for entry in db.tracks.find():
            track = classes.Tracks(entry)
            track.update_gmusic(mm)
            track.update_db(db)

    if False:
        for folder, root, file in playlists:
            listinfo = func.get_playlists_from_folder(file, folder, db)
            playlist = classes.Playlists(listinfo)
            playlist.update_db(db)

        for list in db.playlists.find():
            playlist = classes.Playlists(list)
            playlist.update_gmusic(db, mc)
            playlist.update_db(db)
    #func.get_playlists_from_gmusic(db, mc, playlists_home)

if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    main()