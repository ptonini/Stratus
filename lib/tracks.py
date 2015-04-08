__author__ = 'ptonini'

import os

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3


class Tracks:
    def __init__(self, source):
        if isinstance(source, dict):
            self.__dict__.update(source)
            self.source = "db"
        elif os.path.isfile(source):
            audio = MP3(source)
            tag = EasyID3(source)
            self.source = 'file'
            self.filename = source
            self.length = audio.info.length
            if 'genre' in tag:
                self.genre = tag['genre'][0]
            if 'artist' in tag:
                self.artist = tag['artist'][0]
            if 'performer' in tag:
                self.albumArtist = tag['performer'][0]
            if 'album' in tag:
                self.album = tag['album'][0]
            if "date" in tag:
                self.year = tag['date'][0]
            if 'tracknumber' in tag:
                self.trackNumber = tag['tracknumber'][0]
            if 'title' in tag:
                self.title = tag['title'][0]
            if 'discnumber' in tag:
                self.discNumber = tag['discnumber'][0]
            else:
                self.discNumber = "1"
        else:
            print 'Unable to create instance: undefined source: ' + str(source)

    def delete_from_db(self, TracksColl):
        pass

    def delete_from_disk(self):
        pass

    def delete_from_gmusic(self, cred):
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