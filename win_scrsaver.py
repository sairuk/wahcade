# -*- coding: utf-8 -*-
#
###
# Application: wah!cade
# File:        win_scrsaver.py
# Description: screen saver window
# Copyright (c) 2005-2010   Andy Balcombe <http://www.anti-particle.com>
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
#import os
import sys
#import time
import gc

#gtk
import pygtk
if sys.platform != 'win32':
    pygtk.require('2.0')
import gtk
import gobject
gobject.threads_init()
#import pango

#project modules
from constants import *
from wc_common import WahCade
#import vidinfo
import filters
gst_media_imported = False
try:
    import gst_media
    gst_media_imported = True
except:
    pass
_ = gettext.gettext


class WinScrSaver(WahCade):
    """Wah!Cade Screen Saver Window"""

    def __init__(self, WinMain):
        """init screen saver window"""
        global gst_media_imported
        #set main window
        self.WinMain = WinMain
        #build the window
        self.winScrSaver = gtk.Fixed()
        self.winScrSaver.set_has_window(True)
        #self.drwVideo = gtk.DrawingArea()
        self.imgArtwork1 = gtk.Image()
        self.imgArtwork2 = gtk.Image()
        self.imgArtwork3 = gtk.Image()
        self.imgArtwork4 = gtk.Image()
        self.imgArtwork5 = gtk.Image()
        self.imgArtwork6 = gtk.Image()
        self.imgArtwork7 = gtk.Image()
        self.imgArtwork8 = gtk.Image()
        self.imgArtwork9 = gtk.Image()
        self.imgArtwork10 = gtk.Image()
        self.lblGameDescription = gtk.Label()
        self.lblMP3Name = gtk.Label()
        self.winScrSaver.show()
        WinMain.fixd.add(self.winScrSaver)
        self.lblGameDescription.show()
        self.lblMP3Name.show()
        self._main_images = [
            self.imgArtwork1,
            self.imgArtwork2,
            self.imgArtwork3,
            self.imgArtwork4,
            self.imgArtwork5,
            self.imgArtwork6,
            self.imgArtwork7,
            self.imgArtwork8,
            self.imgArtwork9,
            self.imgArtwork10]
        for widget in self._main_images:
            self.winScrSaver.add(widget)
        #video widget
        self.video_enabled = False
        self.video_playing = False
        if gst_media_imported:
            try:
                self.drwVideo = gst_media.VideoWidget()
                self.video_player = gst_media.GstVideo(self.drwVideo)
                self.video_player.set_volume(self.WinMain.movievol)
                self.video_enabled = True
            except:
                #gstreamer object creation failed
                self.video_enabled = False
                self.video_player.set_volume(0)
                self.WinMain.log_msg('Warning: ScrSaver: Failed to create Video gstreamer objects','0')
        if not self.video_enabled:
            self.drwVideo = gtk.Image()
            self.video_player = None
            self.WinMain.log_msg('Warning: ScrSaver: video objects not created, reverting to images','0')
        #self.drwVideo.connect_after('realize', self.on_drwVideo_realize)
        self.drwVideo.show()
        self.winScrSaver.put(self.drwVideo, 0, 0)
        self.winScrSaver.add(self.lblGameDescription)
        self.winScrSaver.add(self.lblMP3Name)
        self.drwVideo.set_property('visible', False)
        #interval
        self.slide_duration = 10
        self.scr_timer_id = None
        self.running = False
        self.movie_type = ''
        #currently selected screen saver image / movie
        self.game_idx = 0

    def start_scrsaver(self, saver_type):
        """start screen saver"""
        #start duration timer
        self.video_artwork_widget = self._main_images[(self.WinMain.emu_ini.getint('movie_artwork_no') - 1)]
        self.slide_duration = self.WinMain.wahcade_ini.getint('slide_duration') * 1000
        self.running = True
        self.movie_type = ''
        self.saver_type = saver_type
        self.WinMain.show_window('scrsaver')
        if saver_type in ['slideshow', 'movie']:
            self.scr_timer_id = gobject.timeout_add(self.slide_duration, self.on_slide_timer)
            #show first game
            self.on_slide_timer()
        elif saver_type == 'launch_scr':
            #start external screen saver
            os.system(self.WinMain.emu_ini.get('scr_file'))

    def stop_scrsaver(self):
        """stop screen saver"""
        if self.scr_timer_id:
            gobject.source_remove(self.scr_timer_id)
        if self.video_playing:
            self.movie_type = ''
            self.video_playing = False
            self.video_player.stop()
            self.drwVideo.set_property('visible', False)
        self.running = False
        self.WinMain.hide_window('scrsaver')

    def play_movie(self, movie_file, movie_type):
        """play given movie file once, then exit"""
        if gst_media_imported:
            try:
                self.drwVideo = gst_media.VideoWidget()
                self.video_enabled = True
            except:
                self.video_enabled = False
                self.WinMain.log_msg('Warning: ScrSaver: Failed to create Video gstreamer objects','0')
        if self.video_enabled:
            self.video_player = gst_media.GstVideo(self.drwVideo)
            self.video_player.set_volume(self.WinMain.movievol)
            self.WinMain.stop_video()
            self.running = False
            if movie_type in ('intro', 'exit'):
                if self.WinMain.music_enabled:
                    self.WinMain.gstMusic.stop()
            self.movie_type = movie_type
            self.WinMain.show_window('scrsaver')
            try:
                self.video_player.set_volume(self.WinMain.wahcade_ini.getint('movie_volume'))
            except:
                self.WinMain.log_msg('Warning: ScrSaver: Problem setting movie volume, system has muted as exception','0')
                self.video_player.set_volume(0)
            #play new vid
            self.video_player.play(movie_file)
            self.video_playing = True

    def movie_finished(self):
        """intro / exit movie finished"""
        movie_type = self.movie_type
        self.stop_scrsaver()
        #do callbacks depending on movie type
        if movie_type == 'intro':
            if self.WinMain.music_enabled:
                self.WinMain.gstMusic.play()
            self.WinMain.on_sclGames_changed()
        elif movie_type == 'exit':
            self.WinMain.on_winMain_destroy()

    def on_slide_timer(self):
        """change the image(s)"""
        layout_path = os.path.dirname(self.WinMain.layout_file)
        if self.running:
            if self.saver_type == 'slideshow':
                #change images
                self.game_idx = self.WinMain.get_random_game_idx()
                game_info = filters.get_game_dict(self.WinMain.lsGames[self.game_idx])
                for i, img in enumerate(self._main_images):
                    img_path = self.WinMain.emu_ini.get('artwork_%s_image_path' % (i + 1))
                    if img.get_property('visible'):
                        #get image filename
                        img_filename = self.WinMain.get_artwork_image(
                            img_path,
                            layout_path,
                            game_info,
                            self.WinMain.current_emu,
                            (i + 1))
                        #display image
                        self.display_scaled_image(img, img_filename, self.WinMain.keep_aspect, img.get_data('text-rotation'))
            elif self.saver_type == 'movie':
                #video working
                if not self.video_enabled:
                    return
                #play a movie
                movie_found = False
                cnt = 0
                while not movie_found or cnt > 10000:
                    cnt += 1 #ensure we don't go into a infinite loop
                    self.game_idx = self.WinMain.get_random_game_idx()
                    game_info = filters.get_game_dict(self.WinMain.lsGames[self.game_idx])
                    #vid file
                    vid_filename = self.get_video_file(
                        self.WinMain.emu_ini.get('movie_path'),
                        game_info)
                    movie_found = os.path.isfile(vid_filename)
                    if movie_found:
                        #stop existing vid playing
                        if self.video_playing:
                            self.video_playing = False
                            self.video_player.stop()
                        #play new vid
                        self.video_playing = True
                        self.movie_type = 'scrsaver'
                        self.drwVideo.set_property('visible', True)
                        self.video_player.play(vid_filename)
            #set desc
            self.lblGameDescription.set_text(self.WinMain.lsGames[self.game_idx][GL_GAME_NAME])
            #collect any memory "leaks"
            gc.collect()
        else:
            #stop, so hide window
            #self.winScrSaver.hide()
            #self.WinMain.winMain.show()
            self.WinMain.hide_window('scrsaver')
        #done
        return self.running
