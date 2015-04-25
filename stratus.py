3#!/usr/bin/python
# -*- coding: utf-8 -*-


import warnings

import lib.classes as classes
import lib.func as func


def main():

    #mm = func.open_gmusic('./oauth.cred')
    db = func.open_db('mongodb://localhost:27017')

    db.tracks.drop()
    db.playlists.drop()

    tracklist = func.get_filelist('/home/ptonini/Música', '.*.mp3$')
    playlists = func.get_filelist('/home/ptonini/Música/0-Playlists', '.*.m3u$')
    #songlist = getSonglist(sys.argv[1], sys.arv[2])


    for folder, root, file in tracklist:
        metadata = func.get_metadata_from(file, folder)
        track = classes.Tracks(metadata)
        #track.update_gmusic(mm)
        track.update_db(db)
        pass

    for folder, root, file in playlists:
        #playlist = classes.Playlists(dict, db)
        #playlist.update_db(db)
        pass

    for metadata in db.tracks.find():
        track = classes.Tracks(metadata)
        print track.filename
        pass

    for dict in db.playlists.find():
        playlist = classes.Playlists(dict, db)
        for track_ids in playlist.tracks:
            print db.tracks.find_one({'_id': track_ids[0]})['filename']
        pass


if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    main()


