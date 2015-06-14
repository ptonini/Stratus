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
    gm_playlists = func.get_gm_playlists(mc)


    #func.build_track_collection_from_mp3(db, library_home)
    func.match_database_to_gmusic(db, mm)




    # Build playlist collection from m3u files
    #if True:
    if False:
        for folder, root, file in func.get_filelist(playlists_home, '.*.m3u$'):
            playlist = classes.Playlists([folder, file], db)
            playlist.update_db(db)

    #func.build_master_playlists(db, mc, gm_playlists)


    # Sync DB playlists to gmusic
    # if True:
    if False:
        for entry in db.playlists.find():
            playlist = classes.Playlists(entry)
            playlist.update_gmusic(db, mc, gm_playlists)
            playlist.update_db(db)

    # Sync gmusic playlists to DB
    #if True:
    if False:
        for gm_playlist in gm_playlists:
            playlist = classes.Playlists(gm_playlist, db, playlists_home)
            playlist.update_db(db)





if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    main()
