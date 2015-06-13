#!/usr/bin/python
# -*- coding: utf-8 -*-


import warnings
import sys
import time
import math

import lib.classes as classes
import lib.func as func



def main():

    oauth_file, gm_user, gm_pass, mongo_address, mongo_port, library_home, playlists_home = func.get_vars(sys.argv[1])
    mm = func.open_musicmanager(oauth_file)
    mc = func.open_mobileclient(gm_user, gm_pass)
    db = func.open_db('mongodb://' + mongo_address + ':' + mongo_port)
    gm_playlists = mc.get_all_user_playlist_contents()
    #gm_playlists = func.get_gm_playlists(mc)



    #for gm_playlist in gm_playlists:
    #    if gm_playlist['name'] == 'Master playlist':
    #        mc.delete_playlist(gm_playlist['id'])


    # Build track collection from mp3 files
    #if True:
    if False:
        for folder, root, file in func.get_filelist(library_home, '.*.mp3$'):
            track = classes.Tracks([folder, file])
            track.update_db(db)

    # Upload/match database to gmusic
    if True:
        print 'Matching database do Google Music:',
        missing_tracks = db.tracks.find( { "gmusic_id" : { "$exists" : False } }).batch_size(1)
        if missing_tracks.count() == 0:
            print 'all tracks matched.'
        else:
            print len(missing_tracks), 'tracks will be uploaded.'
            for entry in missing_tracks:
                track = classes.Tracks(entry)
                try:
                    track.upload_to_gmusic(mm)
                except:
                    print "Error uploading", track.filename
                else:
                    track.update_db(db)

    # Build playlist collection from m3u files
    #if True:
    if False:
        for folder, root, file in func.get_filelist(playlists_home, '.*.m3u$'):
            playlist = classes.Playlists([folder, file], db)
            playlist.update_db(db)

    # Build Master playlists
    if True:
    #if False:
        print 'Building Master playlists:',
        all_tracks_list = list()
        partial_track_lists = list()
        tracks = list()
        for entry in db.playlists.find():
            if 'Master playlist' not in entry['name']:
                playlist = classes.Playlists(entry)
                for track in playlist.tracks:
                    all_tracks_list.append(track)
        list_count =  int(math.ceil(len(all_tracks_list)/1000.0))
        print str(len(all_tracks_list)) + ' tracks found, building '  + str(list_count) + ' playlist(s).'
        for index, track in enumerate(all_tracks_list):
            tracks.append(track)
            if len(tracks) == 1000 or len(all_tracks_list) - 1 == index:
                partial_track_lists.append(tracks)
                tracks = list()
        for index, track_list in enumerate(partial_track_lists):
            master_playlist = dict()
            master_playlist['name'] = 'Master playlist ' + str(index)
            master_playlist['full_filename'] = None
            master_playlist['timestamp'] = int(time.time())
            master_playlist['tracks'] = track_list
            playlist = classes.Playlists(master_playlist)
            playlist.update_db(db)
            playlist.update_gmusic(db, mc, gm_playlists)
            playlist.update_db(db)

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
