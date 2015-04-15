__author__ = 'ptonini'

import os
import re
import time

from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen import File
import bson.binary


class Tracks:
    def __init__(self, object, type, path=''):
        if type == 'dict':
            self.__dict__.update(object)
        elif type == 'file':
            self.filename = object
            self.path = path
            self.full_filename = path + object
            try:
                os.path.isfile(self.full_filename)
                audio = MP3(self.full_filename)
                tag = EasyID3(self.full_filename)
                file = File(self.full_filename)
            except Exception:
                print 'Invalid file', self.full_filename
            self.length = audio.info.length
            self.coverart = bson.binary.Binary(file.tags['APIC:'].data)
            if 'genre' in tag:
                self.genre = tag['genre'][0]
            if 'artist' in tag:
                self.artist = tag['artist'][0]
            if 'performer' in tag:
                self.album_artist = tag['performer'][0]
            if 'album' in tag:
                self.album = tag['album'][0]
            if "date" in tag:
                self.year = tag['date'][0]
            if 'tracknumber' in tag:
                self.track_num = tag['tracknumber'][0]
            if 'title' in tag:
                self.title = tag['title'][0]
            if 'discnumber' in tag:
                self.disc_num = tag['discnumber'][0]
            else:
                self.disc_num = "1"
        else:
            print 'Unable to create instance'

    def update_gmusic(self, mm):
        if not hasattr(self, 'gmusic_id'):
            r = mm.upload(self.full_filename, enable_matching=True)
            if not r[0] == {}:
                self.gmusic_id = r[0][self.full_filename]
                print 'Uploaded:', self.filename
            elif not r[1] == {}:
                self.gmusic_id = r[1][self.full_filename]
                print 'Matched:', self.filename
            elif not r[2] == {}:
                if 'TrackSampleResponse code 4' in r[2][self.full_filename]:
                    self.gmusic_id = re.search("\((.*)\)", str(r[2])).group(1)
                    print 'Exists:', self.filename
                else:
                    print 'Error: could no upload or match', self.filename

    def update_db(self, db):
        if hasattr(self, '_id'):
            db.tracks.update({'_id': self._id}, self.__dict__)
        else:
            track_count = db.tracks.find({'filename': self.filename}).count()
            if track_count == 0:
                db.tracks.insert(self.__dict__)
            elif track_count == 1:
                pass
            elif track_count > 1:
                print 'Error: duplicate tracks on database'


    def delete_from_db(self, db):
        pass

    def delete_from_gmusic(self, mm):
        pass


class Playlists:
    def __init__(self, object, type):
        if type == 'dict':
            self.__dict__.update(object)
        elif type == 'list':
            self.full_filename = os.path.join(object[0], object[1])
            self.name = object[1][:-4]
            self.timestamp = time.ctime(os.path.getmtime(self.full_filename))
            self.tracks = list()
            with open(self.full_filename, 'r+') as file:
                for line in file.readlines():
                    if line != '\n':
                        self.tracks.append([line[:-1]])

    def __get_gmusic_ids(self):
        for track in self.tracks:
            pass

    def update_db(self, db):
        if hasattr(self, '_id'):
            dict = db.playlists.find_one({'_id': self._id})
            if dict != self.__dict__:
                db.playlists.update({'_id': self._id}, self.__dict__)
            else: print 'no need for update'
        else:
            print "oi"
            for index, track in enumerate(self.tracks):
                self.tracks[index].append(db.tracks.find_one({'filename': track[0]})['_id'])
            playlist_count = db.playlists.find({'name': self.name}).count()
            if playlist_count == 0:
                db.playlists.insert(self.__dict__)
            elif playlist_count == 1:
                pass
            elif playlist_count > 1:
                print 'Error: duplicate playlists on database'
