__author__ = 'ptonini'

import os
import re

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3


class Tracks:
    def __init__(self, object, type, path=''):
        if type == 'dict':
            self.__dict__.update(object)
        elif type == 'file':
            try:
                os.path.isfile(path + object)
            except:
                print 'Invalid filname' , path + object
            audio = MP3(path + object)
            tag = EasyID3(path + object)
            self.filename = object
            self.path = path
            self.length = audio.info.length
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

    def add_to_gmusic(self, mm):
        fullname = self.path + self.filename
        r = mm.upload(fullname, enable_matching=True)
        if not r[0] == {}:
            self.gmusic_id = r[0][fullname]
            print 'Uploaded:', self.filename
        elif not r[1] == {}:
            self.gmusic_id = r[1][fullname]
            print 'Matched:', self.filename
        elif not r[2] == {}:
            if 'TrackSampleResponse code 4' in r[2][fullname]:
                self.gmusic_id = re.search("\((.*)\)", str(r[2])).group(1)
                print 'Exists:', self.filename
            else:
                print 'Error: could no upload or match', self.filename

    def delete_from_db(self, TracksColl):
        pass

    def delete_from_disk(self):
        pass

    def delete_from_gmusic(self, mm):
        pass

    def delete_from_device(self):
        pass

    def is_on_db(self):
        pass

    def is_on_disk(self):
        pass

    def is_on_gmusic(self):
        pass

    def is_on_device(self):
        pass


class Playlists:
    def __init__(self):
        pass