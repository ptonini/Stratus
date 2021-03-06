from time import sleep

__author__ = 'ptonini'

import re
import os
import sys
import time


from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3


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
            except Exception:
                print 'Invalid file', full_filename
            else:
                self.path = source[0]
                self.filename = source[1]
                self.full_filename = full_filename
                self.timestamp = int(os.path.getmtime(self.full_filename))
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

    def update_db(self, db):
        if hasattr(self, '_id'):
            db.tracks.update({'_id': self._id}, self.__dict__)
            print 'Updated to DB:', self.filename
        else:
            track_count = db.tracks.find({'filename': self.filename}).count()
            if track_count == 0:
                db.tracks.insert(self.__dict__)
                print 'Added to DB:', self.filename
            elif track_count > 1:
                print 'Error: duplicate tracks on database:', self.filename

    def upload_to_gmusic(self, mm):
        if not hasattr(self, 'gmusic_id'):
            r = mm.upload(self.full_filename, enable_matching=True)
            if not r[0] == {}:
                self.gmusic_id = r[0][self.full_filename]
                print 'Uploaded:', self.filename
            elif not r[1] == {}:
                self.gmusic_id = r[1][self.full_filename]
                print 'Matched: ', self.filename
            elif not r[2] == {}:
                if 'TrackSampleResponse code 4' in r[2][self.full_filename]:
                    self.gmusic_id = re.search("\((.*)\)", str(r[2][self.full_filename])).group(1)
                    print 'Exists:  ', self.filename
                else:
                    print 'Error: could no upload or match', self.filename


class Playlists:

    def __init__(self, source, db=None, playlists_home=None):
        if isinstance(source, dict):
            if 'id' in source:
                self.full_filename = playlists_home + '/' + source['name'].encode('utf-8') + '.m3u'
                self.name = source['name']
                self.timestamp = int(int(source['lastModifiedTimestamp'])/1000000)
                self.tracks = list()
                print self.name
                for track in source['tracks']:
                    self.tracks.append(db.tracks.find_one({'gmusic_id': track['trackId']})['_id'])
                self.gmusic_id = source['id']
            else:
                self.__dict__.update(source)
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
            print 'Updating playlist "' + self.name + '" on database'
            self.__find_one_and_update_db(db, {'_id': self._id})
        else:
            count = db.playlists.find({'name': self.name}).count()
            if count == 0:
                print 'Adding playlist "' + self.name + '" to database.'
                db.playlists.insert(self.__dict__)
            elif count == 1:
                print 'Updating playlist "' + self.name + '" on database'
                self.__find_one_and_update_db(db, {'name': self.name})
            else:
                print 'Error: duplicate playlists on database:', self.name

    def update_gmusic(self, db, mc, gm_playlists):
        if hasattr(self, 'gmusic_id'):
            for gm_playlist in gm_playlists:
                if self.gmusic_id == gm_playlist['id']:
                    self.__find_most_recent_and_update_gmusic(db, mc, gm_playlist)
                    matched_gmusic_id = True
                    break
            if not matched_gmusic_id:
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
                self.__find_most_recent_and_update_gmusic(db, mc, matched_lists[0])
            else:
                 print 'Error - duplicate playlists on gmusic:', matched_lists[0]['name']

    def __find_one_and_update_db(self, db, criteria):
        playlist = db.playlists.find_one(criteria)
        if self.timestamp < playlist['timestamp']:
            self.tracks = playlist['tracks']
        db.playlists.update(criteria, self.__dict__)

    def __build_list_and_update_gmusic(self, db, mc):
        new_list = list()
        for track_id in self.tracks:
            new_list.append(db.tracks.find_one({'_id': track_id})['gmusic_id'])
        try:
            mc.add_songs_to_playlist(self.gmusic_id, new_list)
        except:
            print 'Error'
            sys.exit(1)

    def __find_most_recent_and_update_gmusic(self, db, mc, gm_playlist):
        gm_timestamp = int(gm_playlist['lastModifiedTimestamp'])/1000000
        if self.timestamp > gm_timestamp:
            old_list = list()
            for entry in gm_playlist['tracks']:
                old_list.append(entry['id'])
            print 'Updating playlist "' + self.name + '"',
            mc.remove_entries_from_playlist(old_list)
            time.sleep(len(old_list)/90 )
            self.__build_list_and_update_gmusic(db, mc)
            print '    finished'
        else:
            self.timestamp = gm_timestamp
            track_list = list()
            for track in gm_playlist['tracks']:
                track_list.append(db.tracks.find_one({'gmusic_id': track['trackId']})['_id'])
            self.tracks = track_list


