3#!/usr/bin/python
# -*- coding: utf-8 -*-



import warnings

import lib.classes as classes
import lib.func as func


def main():

    #mm = func.open_gmusic('./oauth.cred')
    db = func.open_db('mongodb://localhost:27017')

    # db.drop()

    tracklist = func.get_filelist('/home/ptonini/Música', '.*.mp3$')
    playlists = func.get_filelist('/home/ptonini/Música/0-Playlists', '.*.m3u$')
    #songlist = getSonglist(sys.argv[1], sys.arv[2])


    for folder, root, file in tracklist:
        #track = classes.Tracks(file, type='file', path=folder)
        #track.update_gmusic(mm)
        #track.update_db(db)
        pass

    for folder, root, file in playlists:
        #playlist = classes.Playlists([folder, file], type='list')
        #playlist.update_db(db)
        pass

    for dict in db.tracks.find():
        track = classes.Tracks(dict, type='dict')
        print track.filename

    for dict in db.playlists.find():
        playlist = classes.Playlists(dict, type='dict')
        print playlist.name


if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    main()


