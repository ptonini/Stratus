__author__ = 'ptonini'

import re
import os


from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen import File
import bson.binary




class Tracks:

    def __init__(self, source):
        if isinstance(source, dict):
            self.__dict__.update(source)
        elif isinstance(source, list):
            full_filename = source[0] + source[1]
            try:
                os.path.isfile(full_filename)
                audio = MP3(full_filename)
                tag = EasyID3(full_filename)
                file = File(full_filename)
            except Exception:
                print 'Invalid file', full_filename
            else:
                self.path = source[0]
                self.filename = source[1]
                self.full_filename = full_filename
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


    def update_gmusic(self, mm):
        if not hasattr(self, 'gmusic_id'):
            r = mm.upload(self.full_filename, enable_matching=True)
            if not r[0] == {}:
                self.gmusic_id = r[0][self.full_filename]
            elif not r[1] == {}:
                self.gmusic_id = r[1][self.full_filename]
            elif not r[2] == {}:
                if 'TrackSampleResponse code 4' in r[2][self.full_filename]:
                    self.gmusic_id = re.search("\((.*)\)", str(r[2][self.full_filename])).group(1)
                else:
                    print 'Error: could no upload or match', self.filename

    def update_db(self, db):
        if hasattr(self, '_id'):
            db.tracks.update({'_id': self._id}, self.__dict__)
        else:
            track_count = db.tracks.find({'filename': self.filename}).count()
            if track_count == 0:
                db.tracks.insert(self.__dict__)
            elif track_count > 1:
                print 'Error: duplicate tracks on database'

    def delete_from_db(self, db):
        pass

    def delete_from_gmusic(self, mm):
        pass


class Playlists:
    def __init__(self, source, db=None, playlists_home=None):
        if isinstance(source, dict):
            if '_id' in source:
                self.__dict__.update(source)
            elif 'id' in source:
                self.full_filename = playlists_home + '/' + source['name'] + '.m3u'
                self.name = source['name']
                self.timestamp = int(int(source['lastModifiedTimestamp'])/1000000)
                self.tracks = list()
                for track in source['tracks']:
                    self.tracks.append(db.tracks.find_one({'gmusic_id': track['trackId']})['_id'])
                self.gmusic_id = source['id']

        elif isinstance(source, list):
            self.full_filename = os.path.join(source[0], source[1])
            self.name = source[1][:-4]
            self.timestamp = int(os.path.getmtime(self.full_filename))
            with open(self.full_filename, 'r+') as file:
                self.tracks = list()
                for line in file.readlines():
                    if line != '\n':
                        self.tracks.append(db.tracks.find_one({'filename': line[:-1]})['_id'])
    def update_db(self, db):
        if hasattr(self, '_id'):
            self.__find_one_and_update_db(db, {'_id': self._id})
        else:
            count = db.playlists.find({'name': self.name}).count()
            if count == 0:
                db.playlists.insert(self.__dict__)
            elif count == 1:
                self.__find_one_and_update_db(db, {'name': self.name})
            else:
                print 'Error: duplicate playlists on database:', self.name


    def update_gmusic(self, db, mc, gm_playlists):

        if  hasattr(self, 'gmusic_id'):
            for gm_playlist in gm_playlists:
                if self.gmusic_id == gm_playlist['id']:
                    self.__find_most_recent_and_update(db, mc, gm_playlist)
                    break
                else:
                    print 'Error - could not match gmusic_id:', self.name

        else:

            matched_lists = list()
            for gm_playlist in gm_playlists:
                if self.name == gm_playlist['name']:
                    matched_lists.append(gm_playlist)

            if len(matched_lists) == 0:
                self.gmusic_id = mc.create_playlist(self.name)
                self.__build_list_and_update_gmusic(db, mc)
            elif len(matched_lists) == 1:
                self.gmusic_id = matched_lists[0]['id']
                self.__find_most_recent_and_update(db, mc, matched_lists[0])
            else:
                 print 'Error - duplicate playlists on gmusic:', matched_lists[0]['name']


    def __find_one_and_update_db(self, db, criteria):
            playlist = db.playlists.find_one(criteria)
            if self.timestamp < playlist['timestamp']:
                self.tracks = playlist['tracks']
            db.playlists.update(criteria, self.__dict__)

    def __build_list_and_update_gmusic(self, db, mc):
        track_list = list()
        for track_id in self.tracks:
            track_list.append(db.tracks.find_one({'_id': track_id})['gmusic_id'])
        mc.add_songs_to_playlist(self.gmusic_id, track_list)

    def __find_most_recent_and_update(self, db, mc, gm_playlist):
        gm_timestamp = int(int(gm_playlist['lastModifiedTimestamp'])/1000000)
        if self.timestamp > gm_timestamp:
            self.__build_list_and_update_gmusic(db, mc)
        else:
            self.timestamp = gm_timestamp
            track_list = list()
            for track in gm_playlist['tracks']:
                track_list.append(db.tracks.find_one({'gmusic_id': track['trackId']})['_id'])
            self.tracks = track_list


