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

    tracklist = func.get_filelist(library_home, '.*.mp3$')
    playlists = func.get_filelist(playlists_home, '.*.m3u$')


    #db.tracks.drop()
    #db.playlists.drop()


    # Build track collection from mp3 files
    if False:
        for folder, root, file in tracklist:
            track = classes.Tracks([folder, file])
            track.update_db(db)

    # Upload/match database to gmusic
    if False:
        for entry in db.tracks.find():
            track = classes.Tracks(entry)
            track.update_gmusic(mm)
            track.update_db(db)

    # Build playlist collection from m3u files
    if False:
        for folder, root, file in playlists:
            playlist = classes.Playlists([folder, file], db)
            playlist.update_db(db)

    # Sync DB playlists to gmusic
    if False:
        for entry in db.playlists.find():
            playlist = classes.Playlists(entry)
            playlist.update_gmusic(db, mc)
            playlist.update_db(db)

    if True:
        for songlist in mc.get_all_user_playlist_contents():
            gmusic_list = dict()
            gmusic_list['name'] = songlist['name']
            gmusic_list['timestamp'] = int(int(songlist['lastModifiedTimestamp']) / 1000000)
            gmusic_list['gmusic_id'] = songlist['id']
            gmusic_list['full_filename'] = playlists_home + '/' + songlist['name'] + '.m3u'
            gmusic_list['tracks'] = list()
            for track in songlist['tracks']:
                gmusic_list['tracks'].append(db.tracks.find_one({'gmusic_id': track['trackId']})['_id'])
            playlist = classes.Playlists(gmusic_list)
            playlist.update_db(db)


if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    main()