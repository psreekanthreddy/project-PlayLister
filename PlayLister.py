#!/usr/bin/env python3
#  This script creates VLC playlist for a given YouTube video or playlist
#         Note: here, In this script ID meant to URL
#
#   USAGE: python Playlister.py youtube-playlist-link[or youtube-video-link]
#
#
try:
    from lxml import etree
    import os
    import pafy
    import re
    import threading
    import sys
    from os import sep
except ImportError as err:
    print(err.args)
    exit(1)
# a trigger to acknowledge pyperclip module availability( because some users would
#   not want to use this module.
try:
    import pyperclip
    PYPERCLIP = True
except ImportError:
    PYPERCLIP = False

# path to store YouTube Playlist
if os.sys.platform == "win32":
    MUSIC_FOLDER_PATH = sep.join(
        (os.path.expandvars("%userprofile%"), "Music", ""))
elif os.sys.platform == "linux" or os.sys.platform == 'linux2':
    MUSIC_FOLDER_PATH = sep.join((os.path.expanduser("~"), "Music", ""))
else:
    exit(1)


class Video:
    ''' Class to buid VLC playlist for a YT video'''

    def __init__(self, videoID):
        ''' Assigning  videoId/url to a variable'''
        self.videoId = videoID

    def getVideo(self):
        ''' Retrieving YT video details'''

        try:
            video = pafy.new(self.videoId)
            print("Video title:", video.title)

            self.videoDetails = {"url": video.getbestaudio().url,
                                 "title": video.title,
                                 "thumb": video.bigthumbhd,
                                 "creator": video.author,
                                 "category": video.category
                                 }
            sys.stdout.write("\r video(s) details retrieved ! ")
            self.videoTitle = re.sub(
                r'[^\w]', ' ', video.title).replace(' ', "_")
        except:
            print("Error occurred with", self.videoId)

    def createXSPF(self):
        ''' Creating XSPF (VLC playlist file'''

        root = etree.Element('playlist', id=self.videoId)
        # in the root
        title = etree.SubElement(root, 'title')
        title.text = self.videoDetails['title']
        # in the tracklist
        tracklist = etree.SubElement(root, 'trackList')
        track = etree.SubElement(tracklist, 'track')
        # in the track
        location = etree.SubElement(track, 'location')
        location.text = self.videoDetails['url']
        tracktitle = etree.SubElement(track, 'title')
        tracktitle.text = self.videoDetails['title']
        author = etree.SubElement(track, 'creator')
        author.text = self.videoDetails['creator']
        trackimage = etree.SubElement(track, 'image')
        trackimage.text = self.videoDetails['thumb']
        self.root = root
        print('\n\n')

    def save(self):
        ''' Saving Playlist to the disk'''
        if not os.path.exists(MUSIC_FOLDER_PATH+self.videoDetails['category']):
            os.mkdir(MUSIC_FOLDER_PATH+self.videoDetails['category'])
        with open(MUSIC_FOLDER_PATH+self.videoDetails['category']+sep+self.videoTitle + ".xspf", 'wb') as f:
            f.write(etree.tostring(self.root, pretty_print=True))


class VideoPlaylist:
    '''class to create vlc playlist for a YT playlist '''

    # Thread limit (You can change it based on your internet speed)
    THREAD_LIMIT = 15

    def __init__(self, plid):
        ''' Assigning PlaylistId to a variable'''
        self.playlistID = plid
        self.playlist = []

    def getVideo(self, videoId):
        ''' Retrieving YT video details'''

        try:
            self.playlist.append({"url": videoId.getbestaudio().url,
                                  "title": videoId.title,
                                  "thumb": videoId.bigthumbhd,
                                  "viewcount": videoId.viewcount,
                                  "author": videoId.author,
                                  "watchv_url": videoId.watchv_url,
                                  "length": videoId.length
                                  })
            sys.stdout.write(
                "\r {} video(s) details retrieved ! ".format(len(self.playlist)))
        except:
            print("Error occurred with", videoId)

    def getVideoPlaylist(self):
        ''' retrieving videos from the list'''

        try:
            playList = pafy.get_playlist2(self.playlistID)
            print("Playlist Title:{}".format(playList.title))
            self.playlistTitle = listtitle = playList.title
            # title of the xspf (vlc playlist) file to avoid symbol
            self.XSPFTitle = re.sub(r'[^\w]', ' ', listtitle).replace(" ", "_")
            print("Playlist author: {}".format(playList.author))
            self.playlistLength = len(playList)
            print("Videos in Playlist: {}".format(self.playlistLength))
            print('Getting videos from the playlist')
            td = []
            for id, video in enumerate(playList):
                #     thread = threading.Thread(target=self.getVideo, args=(video,))
                #     thread.start()
                #     td.append(thread)
                # for t in td:
                #     t.join(5)

                if threading.active_count() == VideoPlaylist.THREAD_LIMIT:
                    while not threading.active_count() == 5:
                        pass
                thread = threading.Thread(target=self.getVideo, args=(video,))
                thread.start()
            while not threading.active_count() == 1:
                pass

        except ValueError as r:
            print(r)
            exit(1)

    def createXSPF(self):
        ''' Creating XSPF (VLC playlist file'''
        playlist = sorted(
            self.playlist, key=lambda x: x['viewcount'], reverse=True)
        self.playlist = playlist
        root = etree.Element('playlist', id=self.playlistID)
        # in the root
        title = etree.SubElement(root, 'title')
        title.text = self.playlistTitle
        # in the tracklist
        tracklist = etree.SubElement(root, 'trackList')
        for each in self.playlist:
            track = etree.SubElement(tracklist, 'track')
            # in the track
            location = etree.SubElement(track, 'location')
            location.text = each['url']
            tracktitle = etree.SubElement(track, 'title')
            tracktitle.text = each['title']
            creator = etree.SubElement(track, 'creator')
            creator.text = each['author']
            info = etree.SubElement(track, 'info')
            info.text = each['watchv_url']
            trackimage = etree.SubElement(track, 'image')
            trackimage.text = each['thumb']
            duration = etree.SubElement(track, 'duration')
            duration.text = str(each['length'])
        self.root = root

    def save(self):
        ''' Saving Playlist to the disk'''

        with open(MUSIC_FOLDER_PATH+self.XSPFTitle+".xspf", 'wb') as f:
            f.write(etree.tostring(self.root, pretty_print=True))


class Update:
    ''' Updating existing XSPF file '''

    def __init__(self):
        ''' print the length of sys.argv and call run function '''
        print("Found {} file(s)/folder(s) !".format(len(sys.argv[1:])))
        self.run()

    def getID(self, filepath):
        ''' reading the id tag from the file'''

        with open(filepath, 'rb') as f:
            root = etree.parse(f)
            id = root.getroot().get('id', None)
            if not id:
                print('No Playlist/Video id found in', filepath)
                return None
            print('Playlist/Video URL found:\n  ', id)
            return id

    def update(self, id, path):
        ''' updating the existing XSPF file '''

        if re.match('^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+', id):

            if id.count('list') > 0:
                playlist = VideoPlaylist(id)
                playlist.getVideoPlaylist()
                playlist.createXSPF()
                with open(path, 'wb') as f:
                    f.write(etree.tostring(playlist.root, pretty_print=True))

            else:
                video = Video(id)
                video.getVideo()
                video.createXSPF()
                with open(path, 'wb') as f:
                    f.write(etree.tostring(video.root, pretty_print=True))

        else:
            print("Corrupted URL or not a YouTube URL")

    def run(self):
        ''' for each path in sys.argv, Getting id from XSPF file and do required stuff'''

        for path in sys.argv[1:]:
            if not os.path.exists(path):
                print(path, "not exists!")
                continue

            elif os.path.isdir(path):
                for dir, subdir, files in os.walk(path):
                    for file in files:
                        if os.path.splitext(file)[-1] == ".xspf":
                            filepath = os.path.join(dir, file)
                            print(filepath)
                            id = self.getID(filepath)
                            self.update(id, filepath)

            if os.path.splitext(path)[-1] == ".xspf":
                id = self.getID(path)
                self.update(id, path)


class Playlist:
    ''' this class deals with external inputs. i.e., system arguments,
     clipboard text. If none given we prompt for input '''

    def __init__(self):
        ''' external inputs. i.e., system arguments, clipboard text, prompting inputs '''

        if len(sys.argv) > 1:
            Update()
            return

        if PYPERCLIP:
            if not pyperclip.paste() == '':
                url = pyperclip.paste().strip()
                if re.match('^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+', url):
                    self.run(url)
                    return

        url =input("enter  the url").strip()
        if re.match("^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+", url):
            self.run(url)
        else:
            print("wrong input. Try again...")

    def run(self, url):
        ''' checking the url(given input) and if matches , do the stuff '''

        if url.count('list') > 0:
            playlist = VideoPlaylist(url)
            playlist.getVideoPlaylist()
            playlist.createXSPF()
            playlist.save()

        else:
            playlist = Video(url)
            playlist.getVideo()
            playlist.createXSPF()
            playlist.save()


if __name__ == '__main__':
    Playlist()
