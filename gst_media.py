#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
###
# Application: wah!cade
# File:        gst_video.py
# Description: gstreamer video widget
# Copyright (c) 2005-2010   Andy Balcombe <http://www.anti-particle.com>
#       Taken from gstreamer docs example code
###
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
import os
import urllib
import fnmatch
import random
import sys

import pygtk
pygtk.require('2.0')
#import gobject
import pygst
pygst.require('0.10')
import gst
import gtk
import gc

class GstPlayer:

    def __init__(self, videowidget):
        """initialise player class"""
        #print "GstPlayer.__init__"
        self.playing = False
        self.player = gst.element_factory_make('playbin2','player')
        #self.player.set_property('n-audio',5)
        if videowidget:
            self.media_type = 'video'
            self.videowidget = videowidget
        else:
            self.media_type = 'music'
        self.on_eos = False
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect('message', self.on_message)
        bus.connect('sync-message::element', self.on_sync_message)

    def on_message(self, bus, message):
        """message from player?"""
        t = message.type
        if message.type == (gst.MESSAGE_ERROR or gst.MESSAGE_EOS):
            self.player.set_state(gst.STATE_NULL)
            if self.on_eos:
                self.on_eos()
            self.playing = False
            if message.type == gst.MESSAGE_ERROR:
                err, debug = message.parse_error()

    def on_sync_message(self, bus, message):
        """ """
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            # Assign the viewport
            self.imagesink = message.src
            self.imagesink.set_property('force-aspect-ratio', True)
            if sys.platform == 'win32':
                self.imagesink.set_xwindow_id(self.videowidget.window.handle)
            else:
                self.imagesink.set_xwindow_id(self.videowidget.window.xid)
            self.player.set_property('video-sink', self.imagesink)

    def set_location(self, location):
        """set filename"""
        self.player.set_property('uri', location)

    def query_position(self):
        """Returns a (position, duration) tuple"""
        #get position
        try:
            position, format = self.player.query_position(gst.FORMAT_TIME)
        except:
            position = gst.CLOCK_TIME_NONE
        #get duration
        try:
            duration, format = self.player.query_duration(gst.FORMAT_TIME)
        except:
            duration = gst.CLOCK_TIME_NONE
        #done
        return (position, duration)

    def seek(self, location):
        """
        @param location: time to seek to, in nanoseconds
        """
        gst.debug("seeking to %r" % location)
        event = gst.event_new_seek(1.0, gst.FORMAT_TIME,
            gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE,
            gst.SEEK_TYPE_SET, location,
            gst.SEEK_TYPE_NONE, 0)
        res = self.player.send_event(event)
        if res:
            gst.info("setting new stream time to 0")
            self.player.set_new_stream_time(0L)
        else:
            gst.error("seek to %r failed" % location)

    def pause(self):
        """pause player"""
        gst.info("pausing player")
        self.player.set_state(gst.STATE_PAUSED)
        self.playing = False

    def play(self):
        """play file"""
        gst.info("playing player")
        self.player.set_state(gst.STATE_PLAYING)
        self.playing = True

    def stop(self):
        """stop playing"""
        self.player.set_state(gst.STATE_NULL)
        gst.info("stopped player")
        self.playing = False

    def get_state(self, timeout=1):
        """get state (playing / paused / etc)"""
        return self.player.get_state(timeout=timeout)

    def is_playing(self):
        """is file playing"""
        return self.playing

    def set_volume(self, volume_level):
        """set the volume level"""
        self.player.set_property('volume', volume_level)
        gst.info("changed volume to [%s]" % volume_level)


class VideoWidget(gtk.DrawingArea):

    def __init__(self):
        """initialise video widget"""
        #print "VideoWidget.__init__"
        gtk.DrawingArea.__init__(self)
        self.connect('realize', self.on_realize)

    def on_realize(self, sender):
        """video widget realized"""
        #print "VideoWidget.on_realize XID: " + str(self.window.xid)
        if sys.platform == 'win32':
            return self.window.handle
        else:
            return self.window.xid

class GstVideo:

    def __init__(self, videowidget):
        """initialise video widget"""
        #print "GstVideo.__init__"
        self.videowidget = videowidget
        self.player = GstPlayer(self.videowidget)
        self.player.on_eos = lambda *x: self.on_eos()
        self.vid_finished_cb = None
        self.update_id = -1
        self.changed_id = -1
        self.seek_timeout_id = -1
        self.p_position = gst.CLOCK_TIME_NONE
        self.p_duration = gst.CLOCK_TIME_NONE

    def on_eos(self):
        """video file has finished"""
        if not self.vid_finished_cb:
            #play it again
            self.player.seek(0L)
            self.player.play()
        else:
            #finished
            self.vid_finished_cb()

    def play(self, vid_filename, vid_finished_cb=None):
        """play given video file"""
        self.vid_finished_cb = vid_finished_cb
        self.player.set_location('file:%s' % urllib.pathname2url(vid_filename))
        self.player.play()

    def stop(self):
        """stop playing"""
        self.player.stop()
        if self.vid_finished_cb:
            self.vid_finished_cb()

    def close(self):
        """close"""
        pass

    def set_volume(self, volume_level):
        """change volume level"""
        if volume_level > 0:
            self.player.set_volume((volume_level / 100.0))


class MusicPlayer:

    def __init__(self):
        """initialise"""
        self.player = GstPlayer(None)
        self.player.on_eos = self.on_eos
        self.current_track = -1
        self.current_dir = ''
        self.tracks = []

    def get_uris_from_pls(self, uri):
        """return list of tracks from playlist"""
        uris = []
        lines = open(uri).readlines()
        # = content.splitlines()
        for line in lines:
            if line.lower().startswith("file") and line.find("=") != -1:
                uris.append(line[line.find("=") + 1:].strip())
        uris = [self.pls_rebuild_uri(uri, u) for u in uris]
        return uris

    def pls_rebuild_uri(self, base_uri, uri):
        base_uri = base_uri[:base_uri.rfind("/")]
        if uri.find("://") != -1:
            return uri
        elif  uri[0] == "/":
            return "file:%s" % urllib.pathname2url(urllib.quote(uri))
        else:
            return "%s/%s" % (base_uri, urllib.quote(uri))

    def on_eos(self):
        """end of track"""
        self.next_track()

    def load_file(self, location, play=True):
        """load individual track"""
        self.tracks = [location]
        self.current_track = -1
        if play:
            self.next_track()

    def load_playlist(self, playlist, play=True, shuffle=False):
        """load playlist"""
        self.tracks = playlist
        if shuffle:
            random.shuffle(self.tracks)
        self.current_track = -1
        if play:
            self.next_track()

    def load_playlist_file(self, playlist_file, play=True):
        """load playlist"""
        self.tracks = self.get_uris_from_pls(playlist_file)
        self.current_track = -1
        if play:
            self.next_track()

    def next_track(self):
        """goto next track in playlist"""
        self.current_track += 1
        if self.current_track >= len(self.tracks):
            self.current_track = 0
        #print "self.current_track=", self.current_track + 1
        #print "setting track to: ", self.tracks[self.current_track]
        self.player.stop()
        if len(self.tracks) > 0:
            self.player.set_location('file:%s' % urllib.pathname2url(self.tracks[self.current_track]))
            self.player.seek(0L)
            self.player.play()

    def previous_track(self):
        """goto previous track in playlist"""
        self.current_track -= 1
        if self.current_track < 0:
            self.current_track = len(self.tracks) - 1
        #print "self.current_track=", self.current_track + 1
        #print "setting track to: ", self.tracks[self.current_track]
        self.player.stop()
        if len(self.tracks) > 0:
            self.player.set_location('file:%s' % urllib.pathname2url(self.tracks[self.current_track]))
            self.player.seek(0L)
            self.player.play()

    def play(self):
        """pause"""
        self.player.play()

    def pause(self):
        """pause"""
        self.player.pause()

    def stop(self):
        """pause"""
        self.player.stop()

    def play_toggle(self):
        """play / pause"""
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()

    def set_volume(self, volume_level):
        """change volume level"""
        if volume_level > 0:
            self.player.set_volume((volume_level / 100.0))

    def set_directory(self, music_dir, filespec):
        """set player to given dir & load files in it"""
        self.current_dir = music_dir
        first_tracks = []
        if os.path.exists(self.current_dir):
            self.first_dir_matched = False
            first_tracks = self.get_first_music_tracks(
                root = self.current_dir,
                recurse = True,
                pattern = filespec)
            first_tracks.sort()
        return first_tracks

    def get_first_music_tracks(self, root, recurse=False, pattern='*'):
        """get list of music tracks"""
        #initialize
        result = []
        #must have at least root folder
        try:
            names = os.listdir(root)
        except os.error:
            return result
        #expand pattern
        pattern = pattern or '*'
        pat_list = pattern.split(';')
        #check each file
        for name in names:
            fullname = os.path.normpath(os.path.join(root, name))
            #grab if it matches our pattern and entry type
            for pat in pat_list:
                if fnmatch.fnmatch(name, pat):
                    if os.path.isfile(fullname):
                        result.append(fullname)
                        self.first_dir_matched = True
                        recurse = False
                    continue
            #recursively scan other folders, appending results
            if recurse and not self.first_dir_matched:
                if os.path.isdir(fullname) and not os.path.islink(fullname):
                    result += self.get_first_music_tracks(fullname, recurse, pattern)
        return result

class SoundPlayer:

    def __init__(self):
        """initialise"""
        self.player = GstPlayer(None)
        #self.player.on_eos = self.on_eos

    def on_eos(self):
        """end of track"""
        self.player.stop()
        
    def set_volume(self, volume_level):
        """change volume level"""
        if volume_level > 0:
            self.player.set_volume((volume_level / 100.0))
       
    def play(self,file=None):
        """play"""
        self.player.set_location('file:%s' % urllib.pathname2url(file))
        self.player.seek(0L)
        self.player.play()

    def pause(self):
        """pause"""
        self.player.pause()

    def get_state(self):
        return self.player.is_playing()

    def stop(self):
        """pause"""
        self.player.stop()