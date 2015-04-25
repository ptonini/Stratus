__author__ = 'ptonini'

import os
import re





class Tracks:
    def __init__(self, metadata):
        self.__dict__.update(metadata)

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
    def __init__(self, listinfo):
        self.__dict__.update(listinfo)

    def update_db(self, db):
        if hasattr(self, '_id'):
            dict = db.playlists.find_one({'_id': self._id})
            if dict != self.__dict__:
                db.playlists.update({'_id': self._id}, self.__dict__)
            else:
                print 'no need for update'
        else:
            playlist_count = db.playlists.find({'name': self.name}).count()
            if playlist_count == 0:
                db.playlists.insert(self.__dict__)
            elif playlist_count == 1:
                pass
            elif playlist_count > 1:
                print 'Error: duplicate playlists on database'
