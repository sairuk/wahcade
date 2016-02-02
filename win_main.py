# -*- coding: utf-8 -*-
#
###
# Application: wah!cade
# File:        wahcade.py
# Description: Main Window
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
## System Modules
import sys
import glob
import random
import time
import gc
import re
import imp
import shlex
from operator import itemgetter
import subprocess
from subprocess import Popen


## GTK Modules
#gtk
import pygtk
if sys.platform != 'win32':
    pygtk.require('2.0')
import gtk
import gobject
gobject.threads_init()
import pango

#dbus
dbus_imported = False
try:
    import dbus
    dbus_imported = True
except ImportError:
    pass

# gStreamer Modules
gst_media_imported = False
try:
    import gst_media
    gst_media_imported = True
except:
    pass

### Project modules
from constants import *
from scrolled_list import ScrollList
from key_consts import mamewah_keys
from wc_common import WahCade
from win_options import WinOptions
from win_message import WinMessage
from win_scrsaver import WinScrSaver
from win_history import WinHistory
from win_cpviewer import WinCPViewer
import filters
from mamewah_ini import MameWahIni
import joystick
#set gettext function
_ = gettext.gettext


class WinMain(WahCade):
    """Wah!Cade Main Window"""

    def __init__(self, config_opts):
        """initialise main Wah!Cade window"""
        ### Set Global Variables
        self.init = True
        WahCade.__init__(self)
        
        ### Defaults
        self.gst_media_imported = gst_media_imported
        self.pygame_imported = True
        self.old_keyb_events = False
        self.debug_mode = False
        self.tw_api = None
        
        ### USER PROFILE
        self.userpath = os.path.expanduser(CONFIG_DIR)
        if not os.path.exists(CONFIG_DIR):
            # copy over ALL config files
            self.copy_user_config('all')
            # now we've copied stuff, quit and tell the user
            self.log_msg("First run, Wah!Cade setting user config profile in: "+ self.userpath,0)
            self.log_msg("Restart after configuring (run wahcade-setup or see the README file).",0)
            sys.exit(0)
        else:
            #update current config
            self.copy_user_config()
            # now we've copied stuff, quit and tell the user
            self.log_msg("Wah!Cade updating user config files in: "+ self.userpath)

        ### SETUP WAHCADE INI FILE
        self.wahcade_ini = MameWahIni(os.path.join(CONFIG_DIR, 'wahcade.ini'))
        ## read in options wahcade.ini, 
        self.lck_time = self.wahcade_ini.getint('lock_time')
        self.keep_aspect = self.wahcade_ini.getint('keep_image_aspect')
        self.scrsave_delay = self.wahcade_ini.getint('delay')
        self.layout_orientation = self.wahcade_ini.getint('layout_orientation', 0)
        self.screentype = self.wahcade_ini.getint('fullscreen', 0)
        self.intro_movie = self.wahcade_ini.get('intro_movie_file')
        self.showcursor = self.wahcade_ini.getint('show_cursor')       
        self.display_limiters = self.wahcade_ini.getint('show_list_arrows', 0)
        self.wrap_list = self.wahcade_ini.getint('wrap_list')
        self.movievol = self.wahcade_ini.getint('movie_volume')
        self.music_enabled = self.wahcade_ini.getint('enable_music')
        self.music_vol = self.wahcade_ini.getint('music_volume')
        self.musicpath = self.wahcade_ini.get('music_path')
        self.musicshuffle = self.wahcade_ini.get('shuffle_music', 0)
        self.music_movies_mix = self.wahcade_ini.get('music_movie_mix')
        self.sound_vol = self.wahcade_ini.getint('sound_volume')
        self.sound_enabled = self.wahcade_ini.getint('enable_sounds')
        self.delaymovieprev = self.wahcade_ini.getint('delay_before_movie_preview')
        self.exit_movie_file = self.wahcade_ini.get('exit_movie_file') 
        self.layout = self.wahcade_ini.get('layout')
        self.splash_use = self.wahcade_ini.getint('splash_use',1)
        self.splash_show_text = self.wahcade_ini.getint('splash_show_text',1)
        self.splash_border_width = self.wahcade_ini.getint('splash_border_width',10)
 
        ### SETUP EMULATOR INI FILE       
        self.current_emu = self.wahcade_ini.get('current_emulator')
        self.emu_ini = MameWahIni(os.path.join(CONFIG_DIR, 'ini/' + self.current_emu + '.ini'))
        ## read in options emulator.ini,        
        self.emumovieprevpath = self.emu_ini.get('movie_preview_path')
        self.emumovieartworkno = self.emu_ini.getint('movie_artwork_no')

        ### SETUP CTRLR INI
        # Load emulator ctrlr if applicable
        try:
          self.ctrlr_ini = MameWahIni(os.path.join(CONFIG_DIR, 'ctrlr', self.emu_ini.get('ctrlr')+'.ini'), 'ctrlr')
        except:
          self.ctrlr_ini = MameWahIni(os.path.join(CONFIG_DIR, 'ctrlr', 'default.ini'), 'ctrlr')
        self.use_mouse = self.ctrlr_ini.getint('mouse')
        self.joyint = self.ctrlr_ini.getint('joystick')
        self.dx_sensitivity = self.ctrlr_ini.getint('mouse_x_sensitivity',100) * 0.01
        self.dy_sensitivity = self.ctrlr_ini.getint('mouse_y_sensitivity',100) * 0.01

        ### Command-line options (parsed after ini is read)
        self.check_params(config_opts)

        ### LOCK FILE
        self.lck_filename = os.path.join(CONFIG_DIR, 'emulator.lck')
        ### remove lock file if it exists
        if os.path.exists(self.lck_filename):
            self.log_msg('Lock file found: Removing')
            os.remove(self.lck_filename)
            if not os.path.exists(self.lck_filename):
                self.log_msg('Lock File removed successfully')

        ### Twitter OAuth
        self.tw_oath_ckey = self.wahcade_ini.get('consumer_key')
        self.tw_oath_csecret = self.wahcade_ini.get('consumer_secret')
        self.tw_oath_akey = self.wahcade_ini.get('access_key')
        self.tw_oath_asecret = self.wahcade_ini.get('access_secret')
        self.tw_ctags = self.wahcade_ini.get('custom_tags')

        ### WINDOW SETUP            
        #build the main window
        self.winMain = gtk.Window()
        self.fixd = gtk.Fixed()
        self.imgBackground = gtk.Image()
        self.imgMainLogo = gtk.Image()
        self.lblGameListIndicator = gtk.Label()
        self.lblEmulatorName = gtk.Label()
        self.lblGameSelected = gtk.Label()
        if self.splash_use == 1:
            self.display_splash()  
        if self.gst_media_imported:
            self.drwVideo = gst_media.VideoWidget()
        else:
            self.drwVideo = gtk.Image()
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
        self.lblRomName = gtk.Label()
        self.lblYearManufacturer = gtk.Label()
        self.lblScreenType = gtk.Label()
        self.lblControllerType = gtk.Label()
        self.lblDriverStatus = gtk.Label()
        self.lblCatVer = gtk.Label()
        # create scroll list widget
        self.sclGames = ScrollList()
        # image & label lists
        self._layout_items = [
            (8, self.imgMainLogo),
            (21, self.lblGameListIndicator),
            (34, self.lblEmulatorName),
            (60, self.lblGameSelected),
            (73, self.imgArtwork1),
            (86, self.imgArtwork2),
            (99, self.imgArtwork3),
            (112, self.imgArtwork4),
            (125, self.imgArtwork5),
            (138, self.imgArtwork6),
            (151, self.imgArtwork7),
            (164, self.imgArtwork8),
            (177, self.imgArtwork9),
            (190, self.imgArtwork10),
            (47, self.sclGames),
            (203, self.lblGameDescription),
            (216, self.lblRomName),
            (229, self.lblYearManufacturer),
            (242, self.lblScreenType),
            (255, self.lblControllerType),
            (268, self.lblDriverStatus),
            (281, self.lblCatVer)]
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
        self.visible_img_list = []
        self.visible_img_paths = []
        self._main_labels = [
            # self.lblGameListIndicator,
            self.lblGameSelected,
            self.lblGameDescription,
            self.lblRomName,
            self.lblYearManufacturer,
            self.lblScreenType,
            self.lblControllerType,
            self.lblDriverStatus,
            self.lblCatVer]
        # add widgets to main window
        self.current_window = 'main'
        self.fixd.add(self.imgBackground)
        self.imgBackground.show()
        self.fixd.show()
        self.winMain.add(self.fixd)
        for line, widget in self._layout_items:
            if widget != self.sclGames:
                self.fixd.add(self.make_evb_widget(widget))
            else:
                self.fixd.add(widget.fixd)
        # video widget
        self.video_playing = False
        self.video_enabled = False
        self.video_timer = None
        self.video_player = None
        self.drwVideo.show()
        self.fixd.add(self.drwVideo)
        

        # list
        self.sclGames.auto_update = False
        self.sclGames.display_limiters = False
        # set window properties
        self.winMain.set_position(gtk.WIN_POS_NONE)
        self.winMain.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_NORMAL)
        self.winMain.set_title('Wah!Cade')
        # init random engine
        random.seed()
        # build list
        self.lsGames = []
        self.lsGames_len = 0
        # timers
        self.scrsave_time = time.time()
       
        ### CREATE OPTIONS WINDOW
        self.options = WinOptions(self)
        self.options.winOptions.hide()
        ### create message window
        self.message = WinMessage(self)
        self.message.winMessage.hide()
        ### create screen saver window
        self.scrsaver = WinScrSaver(self)
        self.scrsaver.winScrSaver.hide()
        self.scrsave_timer = None

        
        # add options, message & screen saver widgets to _layout_items
        self._layout_items += [
            (301, self.options.lblHeading),
            (314, self.options.sclOptions),
            (327, self.options.lblSettingHeading),
            (340, self.options.lblSettingValue),
            (357, self.message.lblHeading),
            (370, self.message.lblMessage),
            (383, self.message.lblPrompt),
            (396, self.scrsaver.imgArtwork1),
            (409, self.scrsaver.imgArtwork2),
            (422, self.scrsaver.imgArtwork3),
            (435, self.scrsaver.imgArtwork4),
            (448, self.scrsaver.imgArtwork5),
            (461, self.scrsaver.imgArtwork6),
            (474, self.scrsaver.imgArtwork7),
            (487, self.scrsaver.imgArtwork8),
            (500, self.scrsaver.imgArtwork9),
            (513, self.scrsaver.imgArtwork10),
            (526, self.scrsaver.lblGameDescription),
            (539, self.scrsaver.lblMP3Name)]

        
        ### build list of emulators
        self.emu_lists = self.buildemulist()
        
        ### check that current emu exists...
        el = [e[1] for e in self.emu_lists]
        if self.current_emu not in el:
            #...no, switch to one that does
            self.current_emu = el[0]
            self.wahcade_ini.set('current_emulator', self.current_emu)
            
        ### load list
        self.current_list_ini = None
        self.emu_ini = None
        self.layout_file = ''
        self.load_emulator()
        
        self.check_music_settings()
        
        self.winMain.show()

        self.drwVideo.set_property('visible', False)


        if not self.showcursor:
            self.hide_mouse_cursor(self.winMain)
        self.screen = self.winMain.get_screen()
        self.display = self.screen.get_display()
        self.old_mouse = (0, 0)
        
        #fullscreen
        if self.screentype == 1:
            self.log_msg('Fullscreen mode')
            self.winMain.fullscreen()
        else:
            self.log_msg('Windowed mode')
            pass
        
        # show the window to the user
        self.winMain.present()
        
        if self.splash_use == 1:
            ### hide splash
            self.splash.destroy()
        self.do_events()
        self.on_winMain_focus_in()

        #### start intro movie
        if self.gst_media_imported and os.path.isfile(self.intro_movie):
            self.log_msg("Found intro movie file, attempting to play " + self.intro_movie)
            #self.scrsaver.play_movie(self.intro_movie,'intro')
        else:
            self.start_timer('scrsave')
            if self.gst_media_imported and self.music_enabled:
                self.gstMusic.play()


        ### INPUT CONFIGURATION
        # input defaults
        self.pointer_grabbed = False
       
        # get keyboard & mouse events
        self.sclGames.connect('update', self.on_sclGames_changed)
        self.sclGames.connect('mouse-left-click', self.on_sclGames_changed)
        self.sclGames.connect('mouse-right-click', self.on_winMain_key_press)
        self.sclGames.connect('mouse-double-click', self.launch_auto_apps_then_game)
        self.winMain.connect('destroy', self.on_winMain_destroy)
        self.winMain.connect('focus-in-event', self.on_winMain_focus_in)
        self.winMain.connect('focus-out-event', self.on_winMain_focus_out)
        self.winMain.add_events(
            gtk.gdk.POINTER_MOTION_MASK |
            gtk.gdk.SCROLL_MASK |
            gtk.gdk.BUTTON_RELEASE_MASK |
            gtk.gdk.KEY_PRESS_MASK |
            gtk.gdk.KEY_RELEASE_MASK)
        key_press_events = [
            'key-press-event', 'key-release-event', 'button-release-event',
            'scroll-event', 'motion-notify-event']
        [self.winMain.connect(kpev, self.on_winMain_key_press) for kpev in key_press_events]
        #[self.drwVideo.connect(kpev, self.on_winMain_key_press) for kpev in key_press_events]
        #key_press_events = ['key-press-event', 'key-release-event']
        #[self.drwVideo.connect(kpev, self.on_winMain_key_press) for kpev in key_press_events]
        self.main_scroll_keys = [
            'UP_1_GAME', 'DOWN_1_GAME',
            'UP_1_PAGE', 'DOWN_1_PAGE',
            'UP_1_LETTER', 'DOWN_1_LETTER']
        self.keypress_count = 0
       
        #### joystick setup
        self.joy = None
        if (self.joyint == 1) and self.pygame_imported:
            self.joy = joystick.joystick(self.debug_mode)
            self.joy.use_ini_controls(self.ctrlr_ini)
            self.joy.joy_info()
            self.start_timer('joystick')
    
        self.on_sclGames_changed()
               
        ### __INIT__ Complete
        self.init = False

    def on_winMain_destroy(self, *args):
        """done, quit the application"""
        #stop vid playing if necessary
        self.stop_video()
        #save ini files
        self.wahcade_ini.write()
        self.emu_ini.write()
        self.current_list_ini.write()
        #write fav list
        filters.write_fav_list(
            os.path.join(CONFIG_DIR, 'files', '%s.fav' % (self.current_emu)),
            self.emu_favs_list)
        #exit gtk loop
        gtk.main_quit()
        sys.exit(0)

    def exit_wahcade(self, exit_mode='default'):
        """quit"""
        exit_movie = os.path.isfile(self.exit_movie_file)
        self.stop_video()
        if dbus_imported and not exit_mode == 'default':
                bus = dbus.SystemBus()
                try:
                    # CONSOLE KIT
                    ck_obj = bus.get_object('org.freedesktop.ConsoleKit', '/org/freedesktop/ConsoleKit/Manager')
                    ck = dbus.Interface(ck_obj, 'org.freedesktop.ConsoleKit.Manager')
                    # UPOWER (for suspend)
                    up_obj = bus.get_object('org.freedesktop.UPower', '/org/freedesktop/UPower')
                    up = dbus.Interface(up_obj, 'org.freedesktop.UPower')
                except:
                    # HAL
                    hal_obj = bus.get_object('org.freedesktop.Hal', '/org/freedesktop/Hal/devices/computer')
                    hal = dbus.Interface(hal_obj, 'org.freedesktop.Hal.Device.SystemPowerManagement')
        if exit_mode == 'default':
            if self.gst_media_imported and exit_movie:
                #start exit movie
                self.log_msg('Exit with movie file, exit mode selected')
                #self.scrsaver.play_movie(exit_movie,'exit')
            else:
                self.log_msg('Default, exit mode selected')
                self.on_winMain_destroy()
        elif exit_mode == 'reboot':
            #reboot
            self.log_msg('Reboot, exit mode selected')
            try:
                if ck:
                    rv = ck.Restart()
                elif hal:
                    rv = hal.Reboot()
                else:
                    self.log_msg('Could not find suitable system manager for: ' + exit_mode)    
            except: 
                self.log_msg('Failed to initiate reboot through console kit/hal')
        elif exit_mode == 'shutdown':
            #turn off
            self.log_msg('Shutdown, exit mode selected')
            try:
                if ck:
                    rv = ck.Stop()
                elif hal:
                    rv = hal.Shutdown()
                else:
                    self.log_msg('Could not find suitable system manager for: ' + exit_mode) 
            except:
                self.log_msg('Failed to initiate shutdown through console kit/hal')
        elif exit_mode == 'suspend':
            #turn off
            self.log_msg('Suspend mode selected')
            try:
                if ck:
                    rv = up.Suspend()
                elif hal:
                    rv = hal.Suspend()
                else:
                    self.log_msg('Could not find suitable system manager for: ' + exit_mode) 
            except:
                self.log_msg('Failed to initiate suspend through console kit/hal')
        if not exit_mode == 'suspend':
            self.log_msg('Exiting Wah!Cade, destroying window. Guess we didn\'t choose suspend')
            self.on_winMain_destroy()

    def on_winMain_focus_in(self, *args):
        """window received focus"""
        self.pointer_grabbed = False
        if self.sclGames.use_mouse and not self.showcursor:
            #need to grab?
            mw_keys = ['MOUSE_LEFT', 'MOUSE_RIGHT', 'MOUSE_UP', 'MOUSE_DOWN']
            for mw_key in mw_keys:
                mw_functions = self.ctrlr_ini.reverse_get(mw_key)
                if mw_functions:
                    #grab pointer
                    r = gtk.gdk.pointer_grab(
                        self.winMain.window,
                        event_mask= gtk.gdk.POINTER_MOTION_MASK |
                            gtk.gdk.SCROLL_MASK |
                            gtk.gdk.BUTTON_RELEASE_MASK |
                            gtk.gdk.KEY_PRESS_MASK |
                            gtk.gdk.KEY_RELEASE_MASK)#,
                        #confine_to=self.winMain.window)
                    if r==gtk.gdk.GRAB_SUCCESS:
                        self.pointer_grabbed = True
                    #done
                    #break
        # Remove Lock File workaround
        if os.path.exists(self.lck_filename):
            self.log_msg('Lock file found: Waiting ' + str(self.lck_time))
            self.wait_with_events(self.lck_time)
            self.log_msg('Lock time elapsed, removing file')
            try:
                os.remove(self.lck_filename)
                if not os.path.exists(self.lck_filename):
                    self.log_msg('Lock File removed successfully')
            except:
                self.log_msg("WARNING: Could not remove lock file, remove manually or restart Wah!Cade")

    def on_winMain_focus_out(self, *args):
        """window lost focus"""
        self.pointer_grabbed = False
        gtk.gdk.pointer_ungrab()

    def on_winMain_key_press(self, widget, event, *args):
        """key pressed - translate to mamewah setup"""
        if not os.path.exists(self.lck_filename):
            current_window = self.current_window
            mw_keys = []
            mw_key = ''
            mw_func = ''
            mw_functions = []
            joystick_key = None
            if len(args) > 1:
                if args[0] == "JOYSTICK":
                    joystick_key = args[1]
                    if self.debug_mode:
                        self.log_msg("on_winMain_key_press: joystick:" + str(joystick_key),1)
            #reset screen saver time (and turn off if necessary)
            self.scrsave_time = time.time()
            if self.scrsaver.running:
                self.scrsaver.stop_scrsaver()
                #print "on_winMain_key_press: callifile_listsng start timer"
                self.start_timer('scrsave')
            if event.type == gtk.gdk.MOTION_NOTIFY and self.pointer_grabbed:
                #mouse moved
                x, y = event.get_coords()
                dx = x - self.old_mouse[0]
                dy = y - self.old_mouse[1]
                #print "x,y=", x,y, "    ox=,oy=",self.old_mouse[0],self.old_mouse[1], "    dx=,dy=",dx,dy
                if abs(dx) >= abs(dy):
                    #x-axis
                    mm = dx
                    if mm < -3.0:
                        mw_keys = ['MOUSE_LEFT']
                    elif mm > 3.0:
                        mw_keys = ['MOUSE_RIGHT']
                else:
                    #y-axis
                    mm = dy
                    if mm < -3.0:
                        mw_keys = ['MOUSE_UP']
                    elif mm > 3.0:
                        mw_keys = ['MOUSE_DOWN']
                self.keypress_count += int(abs(mm) / 10) + 1
                #print "mm=",mm, "    keyp=",self.keypress_count
                if not mw_keys:
                    self.keypress_count = 0
                    if widget == self.winMain:
                        self.sclGames.update()
                    return
                #warp pointer - stops mouse hitting screen edges
                winpos = self.winMain.get_position()
                self.old_mouse = (200, 200)
                self.display.warp_pointer(self.screen, winpos[0] + 200, winpos[1] + 200)
            elif event.type == gtk.gdk.BUTTON_RELEASE:
                #mouse click
                mw_keys = ['MOUSE_BUTTON%s' % (event.button - 1)]
            elif event.type == gtk.gdk.SCROLL:
                #mouse scroll wheel
                if event.direction in [gtk.gdk.SCROLL_UP, gtk.gdk.SCROLL_LEFT]:
                    mw_keys = ['MOUSE_SCROLLUP']
                elif event.direction in [gtk.gdk.SCROLL_DOWN, gtk.gdk.SCROLL_RIGHT]:
                    mw_keys = ['MOUSE_SCROLLDOWN']
                else:
                    return
            elif event.type == gtk.gdk.KEY_PRESS:
                if self.debug_mode:
                    self.log_msg("  key-press",1)
                self.keypress_count += 1
                if joystick_key:
                    #joystick action
                    mw_keys = [joystick_key]
                else:
                    #keyboard pressed, get gtk keyname
                    keyname = gtk.gdk.keyval_name(event.keyval).lower()
                    #got something?
                    if keyname not in mamewah_keys:
                        return
                    #get mamewah keyname
                    mw_keys = mamewah_keys[keyname]
                    if mw_keys == []:
                        return
            elif event.type == gtk.gdk.KEY_RELEASE:
                self.keypress_count = 0
                #keyboard released, update labels, images, etc
                if widget == self.winMain:
                    #only update if no further events pending
                    self.sclGames.update()
                    if self.old_keyb_events:
                        if self.debug_mode:
                            self.log_msg("  key-release",1)
                        self.sclGames.update()
                    elif not gtk.gdk.events_pending():
                        if self.debug_mode:
                            self.log_msg("  key-release",1)
                        self.sclGames.update()
                if joystick_key:
                    #don't need "release" joystick actions to be executed
                    mw_keys = []
                    if self.debug_mode:
                        self.log_msg("  joystick: cleared_events",1)
            #get mamewah function from key
            for mw_key in mw_keys:
                mw_functions = self.ctrlr_ini.reverse_get(mw_key)
                if mw_functions:
                    break
            for mw_func in mw_functions:
                #which function?
                if current_window == 'main':
                    #main form
                    if mw_func == 'UP_1_GAME':
                        self.play_clip('UP_1_GAME')
                        self.sclGames.scroll((int(self.keypress_count / 20) * -1) - 1)
                    elif mw_func == 'DOWN_1_GAME':
                        self.play_clip('DOWN_1_GAME')
                        self.sclGames.scroll(int(self.keypress_count / 20) + 1)
                    elif mw_func == 'UP_1_PAGE':
                        self.play_clip('UP_1_PAGE')
                        self.sclGames.scroll(-self.sclGames.num_rows)
                    elif mw_func == 'DOWN_1_PAGE':
                        self.play_clip('DOWN_1_PAGE')
                        self.sclGames.scroll(+self.sclGames.num_rows)
                    elif mw_func == 'UP_1_LETTER':
                        self.play_clip('UP_1_LETTER')
                        if self.lsGames_len == 0:
                            break
                        cl = self.lsGames[self.sclGames.get_selected()][0][0]
                        games = [r[0] for r in self.lsGames]
                        games = games[:self.sclGames.get_selected()]
                        games.reverse()
                        i = 0
                        for row in games:
                            i += 1
                            if row[0] != cl:
                                self.sclGames.scroll(-i)
                                break
                            if i >= len(games):
                                self.sclGames.scroll(-i)
                    elif mw_func == 'DOWN_1_LETTER':
                        self.play_clip('DOWN_1_LETTER')
                        if self.lsGames_len == 0:
                            break
                        cl = self.lsGames[self.sclGames.get_selected()][0][0]
                        games = [r[0] for r in self.lsGames]
                        games = games[self.sclGames.get_selected():]
                        i = -1
                        for row in games:
                            i += 1
                            if row[0] != cl:
                                self.sclGames.scroll(+i)
                                break
                    elif mw_func == 'RANDOM_GAME':
                        self.play_clip('RANDOM_GAME')
                        self.sclGames.set_selected(self.get_random_game_idx())
                    elif mw_func == 'FIND_GAME':
                        self.play_clip('FIND_GAME')
                        self.options.set_menu('find')
                        self.show_window('options')
                    elif mw_func == 'ADD_GAME_TO_LIST':
                        self.play_clip('ADD_GAME_TO_LIST')
                        self.options.set_menu('add_to_list')
                        self.show_window('options')
                    elif mw_func == 'REMOVE_GAME_FROM_LIST':
                        self.play_clip('REMOVE_GAME_FROM_LIST')
                        self.remove_current_game()
                    elif mw_func == 'LAUNCH_GAME':
                        self.play_clip('LAUNCH_GAME')
                        self.launch_auto_apps_then_game()
                    elif mw_func == 'LAUNCH_GAME_WITH_OPTIONS1':
                        self.play_clip('LAUNCH_GAME_WITH_OPTIONS1')
                        self.launch_auto_apps_then_game(
                            self.emu_ini.get('alt_commandline_format_1'))
                    elif mw_func == 'LAUNCH_GAME_WITH_OPTIONS2':
                        self.play_clip('LAUNCH_GAME_WITH_OPTIONS2')
                        self.launch_auto_apps_then_game(
                            self.emu_ini.get('alt_commandline_format_2'))
                    elif mw_func == 'MENU_SHOW':
                        self.play_clip('MENU_SHOW')
                        self.options.set_menu('main')
                        self.show_window('options')
                    elif mw_func == 'SELECT_EMULATOR':
                        self.play_clip('SELECT_EMULATOR')
                        self.options.set_menu('emu_list')
                        self.show_window('options')
                    elif mw_func == 'NEXT_EMULATOR':
                        self.play_clip('NEXT_EMULATOR')
                        emu_list = [e[1] for e in self.emu_lists]
                        emu_idx = emu_list.index(self.current_emu)
                        if emu_idx < len(emu_list) - 1:
                            emu_idx += 1
                        else:
                            emu_idx = 0
                        self.load_emulator(emu_list[emu_idx])
                    elif mw_func == 'PREVIOUS_EMULATOR':
                        self.play_clip('PREVIOUS_EMULATOR')
                        emu_list = [e[1] for e in self.emu_lists]
                        emu_idx = emu_list.index(self.current_emu)
                        if emu_idx > 0:
                            emu_idx -= 1
                        else:
                            emu_idx = len(emu_list) - 1
                        self.load_emulator(emu_list[emu_idx])
                    elif mw_func == 'SELECT_GAMELIST':
                        self.play_clip('SELECT_GAMELIST')
                        self.options.set_menu('game_list')
                        self.show_window('options')
                    elif mw_func == 'NEXT_GAMELIST':
                        self.play_clip('NEXT_GAMELIST')
                        self.current_list_idx = self.get_next_list_in_cycle(+1)
                        self.load_list()
                    elif mw_func == 'PREVIOUS_GAMELIST':
                        self.play_clip('PREVIOUS_GAMELIST')
                        self.current_list_idx = self.get_next_list_in_cycle(-1)
                        self.load_list()
                    elif mw_func == 'ROTATE_SCREEN_TOGGLE':
                        self.play_clip('ROTATE_SCREEN_TOGGLE')
                        self.load_layouts('toggle')
                    elif mw_func == 'ROTATE_SCREEN_0':
                        self.play_clip('ROTATE_SCREEN_0')
                        self.load_layouts(0)
                    elif mw_func == 'ROTATE_SCREEN_90':
                        self.play_clip('ROTATE_SCREEN_90')
                        self.load_layouts(90)
                    elif mw_func == 'ROTATE_SCREEN_180':
                        self.play_clip('ROTATE_SCREEN_180')
                        self.load_layouts(180)
                    elif mw_func == 'ROTATE_SCREEN_270':
                        self.play_clip('ROTATE_SCREEN_270')
                        self.load_layouts(270)
                    elif mw_func == 'NEXT_TRACK':
                        self.play_clip('NEXT_TRACK')
                        if self.music_enabled:
                            self.gstMusic.next_track()
                    elif mw_func == 'PREVIOUS_TRACK':
                        self.play_clip('PREVIOUS_TRACK')
                        if self.music_enabled:
                            self.gstMusic.previous_track()
                    elif mw_func == 'LAUNCH_APP_1':
                        self.play_clip('LAUNCH_APP_1')
                        self.external_app_queue = []
                        self.launch_external_application(1)
                    elif mw_func == 'LAUNCH_APP_2':
                        self.play_clip('LAUNCH_APP_2')
                        self.external_app_queue = []
                        self.launch_external_application(2)
                    elif mw_func == 'LAUNCH_APP_3':
                        self.play_clip('LAUNCH_APP_3')
                        self.external_app_queue = []
                        self.launch_external_application(3)
                    elif mw_func == 'EXIT_TO_WINDOWS':
                        self.play_clip('EXIT_TO_WINDOWS')
                        self.exit_wahcade()
                    elif mw_func == 'EXIT_WITH_CHOICE':
                        self.play_clip('EXIT_WITH_CHOICE')
                        self.options.set_menu('exit')
                        self.show_window('options')
                elif current_window == 'options':
                    #options form
                    if mw_func == 'OP_UP_1_OPTION':
                        self.play_clip('OP_UP_1_OPTION')
                        self.options.sclOptions.scroll(-1)
                    elif mw_func == 'OP_DOWN_1_OPTION':
                        self.play_clip('OP_DOWN_1_OPTION')
                        self.options.sclOptions.scroll(+1)
                    elif mw_func == 'OP_UP_1_OPTION_PAGE':
                        self.play_clip('OP_UP_1_OPTION_PAGE')
                        self.options.sclOptions.scroll(-self.options.sclOptions.num_rows)
                    elif mw_func == 'OP_DOWN_1_OPTION_PAGE':
                        self.play_clip('OP_DOWN_1_OPTION_PAGE')
                        self.options.sclOptions.scroll(+self.options.sclOptions.num_rows)
                    elif mw_func == 'OP_MENU_SELECT':
                        self.play_clip('OP_MENU_SELECT')
                        self.options.menu_selected()
                    elif mw_func == 'OP_MENU_HIDE':
                        self.play_clip('OP_MENU_HIDE')
                        self.hide_window('options')
                    elif mw_func == 'OP_MENU_BACK':
                        self.play_clip('OP_MENU_BACK')
                        if self.options.current_menu == 'main':
                            self.hide_window('options')
                        elif self.options.current_menu in ['emu_list', 'game_list', 'list_options', 'music', 'exit']:
                            self.options.set_menu('main')
                        elif self.options.current_menu == 'add_to_list':
                            self.options.set_menu('list_options')
                        elif self.options.current_menu == 'generate_ftr':
                            if self.current_filter_changed:
                                #generate new filter
                                self.options.set_menu('generate_new_list')
                            else:
                                self.options.set_menu('list_options')
                        elif self.options.current_menu.startswith('ftr:'):
                            self.options.set_menu('generate_ftr')
                        elif self.options.current_menu == 'find':
                            self.options.find_game('back')
                        elif self.options.current_menu == 'music_dir':
                            self.options.set_menu('music')
                elif current_window == 'scrsaver':
                    #screensaver
                    if mw_func == 'SS_FIND_N_SELECT_GAME':
                        self.sclGames.set_selected(self.scrsaver.game_idx)
                    #stop into / exit movie playing if any key is pressed
                    if self.scrsaver.movie_type in ('intro', 'exit'):
                        self.scrsaver.video_player.stop()
                #history viewer
                elif current_window == 'history':
                    if mw_func == 'UP_1_GAME':
                        self.play_clip('UP_1_GAME')
                        self.histview.sclHistory.scroll((int(self.keypress_count / 20) * -1) - 1)
                    elif mw_func == 'DOWN_1_GAME':
                        self.play_clip('DOWN_1_GAME')
                        self.histview.sclHistory.scroll(int(self.keypress_count / 20) + 1)
                    elif mw_func in ['UP_1_PAGE', 'UP_1_LETTER']:
                        self.play_clip('UP_1_PAGE')
                        self.histview.sclHistory.scroll(-self.histview.sclHistory.num_rows)
                    elif mw_func in ['DOWN_1_PAGE', 'DOWN_1_LETTER']:
                        self.play_clip('DOWN_1_PAGE')
                        self.histview.sclHistory.scroll(+self.histview.sclHistory.num_rows)
                    elif mw_func in [
                            'EXIT_TO_WINDOWS',
                            'LAUNCH_APP_%s' % self.histview.app_number,
                            'LAUNCH_GAME']:
                        self.hide_window('history')
                        self.auto_launch_external_app()
                #control panel viewer
                elif current_window == 'cpviewer':
                    if mw_func in [
                            'EXIT_TO_WINDOWS',
                            'LAUNCH_APP_%s' % self.cpviewer.app_number,
                            'LAUNCH_GAME']:
                        self.hide_window('cpviewer')
                        self.auto_launch_external_app()
                #message window
                elif current_window == 'message':
                    if self.message.wait_for_key:
                        self.message.hide()
            #force games list update if using mouse scroll wheel
            if 'MOUSE_SCROLLUP' in mw_keys or 'MOUSE_SCROLLDOWN' in mw_keys:
                if widget == self.winMain:
                    self.play_clip('UP_1_GAME')
                    self.sclGames.update()

    def on_sclGames_changed(self, *args):
        """game selected"""
        #print "on_sclGames_changed: sel=", self.sclGames.get_selected()
        self.game_ini_file = None
        self.stop_video()
        if self.sclGames.get_selected() > self.lsGames_len - 1:
            #blank labels & images
            for img in self.visible_img_list:
                img.set_from_file(None)
            for lbl in self._main_labels:
                lbl.set_text('')
            return
        #set current game in ini file
        self.current_list_ini.set('current_game', self.sclGames.get_selected())
        #get info
        game_info = filters.get_game_dict(self.lsGames[self.sclGames.get_selected()])
        #check for game ini file
        game_ini_file = os.path.join(CONFIG_DIR, 'ini', '%s' % self.current_emu, '%s' % game_info['rom_name'] + '.ini' )
        if os.path.isfile(game_ini_file):
            self.log_msg(game_info['rom_name'] + " has custom ini file")
            self.game_ini_file = MameWahIni(game_ini_file)
        #set layout text items
        self.lblGameDescription.set_text(game_info['game_name'])
        self.lblGameSelected.set_text(_('Game %s of %s selected') % (
            self.sclGames.get_selected() + 1,
            self.lsGames_len))
        if game_info['clone_of'] != '':
            rom_name_desc = _('%s (Clone of %s)') % (game_info['rom_name'], game_info['clone_of'])
        else:
            rom_name_desc = game_info['rom_name']
        self.lblRomName.set_text(rom_name_desc)
        self.lblYearManufacturer.set_text('%s %s' % (game_info['year'], game_info['manufacturer']))
        self.lblScreenType.set_text('%s %s' % (game_info['screen_type'], game_info['display_type']))
        self.lblControllerType.set_text(game_info['controller_type'])
        self.lblDriverStatus.set_text('%s, %s, %s' % (
            game_info['driver_status'],
            game_info['colour_status'],
            game_info['sound_status']))
        self.lblCatVer.set_text(game_info['category'])
        #start video timer
        if self.scrsaver.movie_type not in ('intro', 'exit'):
            self.start_timer('video')
        #set layout images
        for i, img in enumerate(self.visible_img_list):
            img_filename = self.get_artwork_image(
                self.visible_img_paths[i],
                self.layout_path,
                game_info,
                self.current_emu,
                (i + 1))
            self.display_scaled_image(img, img_filename, self.keep_aspect, img.get_data('text-rotation'))
            
    def on_scrsave_timer(self):
        if self.lsGames_len == 0:
            print _("Error: Empty Gamelist: [%s]") % (self.current_emu)
            return False
        """timer event - check to see if we need to start video or screen saver"""
        #need to start screen saver?
        if int(time.time() - self.scrsave_time) >= self.scrsave_delay:
            #yes, stop any vids playing
            self.stop_video()
            if self.emu_ini.get('saver_type') in ['blank_screen', 'slideshow', 'movie', 'launch_scr']:
                #start screen saver
                self.scrsaver.start_scrsaver(self.emu_ini.get('saver_type'))
            else:
                print _("Error: wrong screen saver type: [%s]") % (self.emu_ini.get('saver_type'))
            return False
        #done
        return True

    def on_video_timer(self):
        """timer event - start video playing"""
        #start video playing?
        if self.video_enabled and self.current_window == 'main':
            #stop existing vid playing
            self.stop_video()
            #something in the list?
            if self.lsGames_len == 0:
                return False
            #get info
            vid_filename = self.get_video_file(
                self.emu_ini.get('movie_preview_path'),
                filters.get_game_dict(self.lsGames[self.sclGames.get_selected()]))
            #print "vid_filename=",vid_filename
            if os.path.isfile(vid_filename):
                #resize video widget
                self.video_playing = True
                img_w, img_h = self.video_artwork_widget.get_size_request()
                xpos = (img_w - self.video_width) / 2
                ypos = (img_h - self.video_height) / 2
                self.fixd.move(
                    self.drwVideo,
                    self.fixd.child_get_property(self.video_artwork_widget.get_parent(), 'x') + xpos,
                    self.fixd.child_get_property(self.video_artwork_widget.get_parent(), 'y') + ypos,
                    )
                self.drwVideo.set_size_request(self.video_width, self.video_height)
                self.drwVideo.set_property('visible', True)
                self.video_artwork_widget.set_property('visible', False)
                #set volume
                if self.music_movies_mix == 'mute_movies':
                    vol = 0
                else:
                    vol = self.wahcade_ini.getint('movie_volume')
                self.video_player.set_volume(vol)
                #start video
                self.video_player.play(vid_filename)
        #done
        return False

    def stop_video(self):
        """stop and playing video and timer"""
        if self.video_timer:
            gobject.source_remove(self.video_timer)
            self.video_timer = None
        if self.video_playing:
            self.video_playing = False
            self.video_player.stop()
            self.drwVideo.set_property('visible', False)
            self.video_artwork_widget.set_property('visible', True)
            self.do_events()

    def get_next_list_in_cycle(self, direction):
        """return index of next "cycleable" list in current emulator lists"""
        # Create array of available lists for current emulator
        file_lists = self.build_filelist("int", "ini", "(?<=-)\d+", self.current_emu, "-")
        current_idx = file_lists.index(self.current_list_idx) + direction
        # find the next list then return number of list
        if current_idx == len(file_lists):
            new_idx = 0
        else:
            new_idx = file_lists[current_idx]
        return new_idx

    def launch_auto_apps_then_game(self, game_cmdline_args=''):
        """call any automatically launched external applications
           then run currently selected game"""
        self.external_app_queue = self.emu_ini.get('auto_launch_apps').split(',')
        self.external_app_queue.reverse() #get it into correct order
        if self.external_app_queue == ['']:
            self.external_app_queue = []
        if len(self.external_app_queue) > 0:
            self.auto_launch_external_app(True, game_cmdline_args)
        else:
            self.launch_game(game_cmdline_args)

    def get_launch_options(self, opts):
        """returns parsed command line options"""
        d = {}
        #minimize?
        d['minimize_wahcade'] = ('{minimize}' in opts)
        d['play_music'] = ('{music}' in opts)
        if self.music_enabled and not d['play_music']:
            self.gstMusic.pause()
        #replace markers with actual values
        opts = opts.replace('[name]', self.lsGames[self.sclGames.get_selected()][GL_ROM_NAME])
        opts = opts.replace('[year]', self.lsGames[self.sclGames.get_selected()][GL_YEAR])
        opts = opts.replace('[manufacturer]', self.lsGames[self.sclGames.get_selected()][GL_MANUFACTURER])
        opts = opts.replace('[clone_of]', self.lsGames[self.sclGames.get_selected()][GL_CLONE_OF])
        opts = opts.replace('[display_type]', self.lsGames[self.sclGames.get_selected()][GL_DISPLAY_TYPE])
        opts = opts.replace('[screen_type]', self.lsGames[self.sclGames.get_selected()][GL_SCREEN_TYPE])
        opts = opts.replace('[category]', self.lsGames[self.sclGames.get_selected()][GL_CATEGORY])
        # Automatically rotate to emulator based on the [autorotate] flag being present.
        # This is typically for the MAME emulator since all other emulators known to work
        # use a single orientation factor.
        screen_set = {0: '',
                      90: '-rol',
                      180: '-flipy',
                      270: '-ror'}
        opts = opts.replace('[autorotate]', screen_set[self.layout_orientation])
        opts = opts.replace('[rompath]', self.emu_ini.get('rom_path'))
        # If multiple rom extensions are used, check which file is correct
        # will break after first file is found
        self.romext = self.check_ext_on_game_launch(self.emu_ini.get('rom_extension'))
        try:
            opts = opts.replace('[romext]', self.romext)
        except:
            opts = opts.replace('[romext]', "")
        opts = opts.replace('{minimize}', '')
        opts = opts.replace('{music}', '')
        d['options'] = opts
        #done
        return d

    def launch_game(self, cmdline_args=''):
        """run currently selected game"""
        #collect any memory "leaks"
        gc.collect()
        #stop any vids playing
        self.stop_video()
        #get rom name
        if self.lsGames_len == 0:
            return
        rom = self.lsGames[self.sclGames.get_selected()][GL_ROM_NAME]
        #show launch message
        self.message.display_message(
            _('Starting...'),
            '%s: %s' % (rom, self.lsGames[self.sclGames.get_selected()][GL_GAME_NAME]))
        #tweet and log message
        if self.twitter_api:
                msg = self.procmsg(self.emu_ini.get('msg_format'))
                self.log_msg(self.post_tweet(msg[0:139]))
        #stop joystick poller
        if self.joy is not None:
            self.joy.joy_count('stop')
            gobject.source_remove(self.joystick_timer)
        #start timing
        time_game_start = time.time()
        #wait a bit - to let message window display
        self.show_window('message')
        self.wait_with_events(0.25)
        #get command line options
        if cmdline_args:
            opts = cmdline_args
        else:
            if self.game_ini_file:
                opts = self.game_ini_file.get(
                    option = 'commandline_format',
                    default_value = self.emu_ini.get('commandline_format'))
            else:
                opts = self.current_list_ini.get(
                    option = 'commandline_format',
                    default_value = self.emu_ini.get('commandline_format'))
        game_opts = self.get_launch_options(opts)
        #pause music?
        if self.music_enabled and not game_opts['play_music']:
            self.gstMusic.stop()    
        #check emu exe
        emulator_executable = self.emu_ini.get('emulator_executable')

        
        # CHECK FOR LAUNCHER PLUGINS
        #rom_extension = os.path.splitext(game_opts['options'])[1].replace('\"','')
        rom_extension = self.romext
        pass_check = False
        wshell = True
        args = ""
        mod = False
        fp = None
        plugin = "launcher_%s" % rom_extension
        try:
            fp, filename, desc = imp.find_module(plugin,  ['./plugins'])
            mod = imp.load_module(plugin, fp, filename, desc)
            self.log_msg('[PLUGIN] Using plugin %s' % plugin)
        except:
            self.log_msg('[PLUGIN] No plugin found for %s' % plugin)

        if mod:
            result = mod.read_scexec(game_opts['options'])
            emulator_executable = result[1].strip("\n")
            args = result[2].strip("\n")
            pass_check = result[4]
            wshell = result[5]
        if fp:
            fp.close()
        if not pass_check:
            if not os.path.isfile(emulator_executable):
                msg = _('Emulator Executable [%s] does not exist' % (emulator_executable))
                self.log_msg('Error: %s' % msg)
                self.message.display_message(
                    _('Error!'),
                    msg,
                    _('Press cancel key to continue...'),
                    wait_for_key=True)
                if self.music_enabled and not game_opts['play_music']:
                    self.gstMusic.play()
                return           
        #set command line
        if not args:
            if not pass_check:
                args = game_opts['options']
            else:
                args = ""
        #patch for ..[romext]
        if '..' in args:
            newargs = args.split('..')
            args = newargs[0] + '.' + newargs[1]
        cmd = '%s %s' % (emulator_executable, args)
        #write lock file for emulator
        f = open(self.lck_filename, 'w')
        f.write(cmd)
        f.close()
                       
        if not self.debug_mode:
            self.log_msg('******** Command from Wah!Cade is:  %s ' % cmd)
            #redirect output to log file
            self.log_msg('******** Begin command output')
            if sys.platform == 'win32':
                cmd = '%s >> %s' % (cmd, self.log_filename)
            else:
                cmd = '%s >> %s 2>&1' % (cmd, self.log_filename)

        #change to emu dir
        try:
            pwd = os.getcwd()
            os.chdir(os.path.dirname(emulator_executable))
        except:
            pass
   
        #run emulator & wait for it to finish
        if not wshell:
            p = Popen(cmd, shell=False)
        else:
            p = Popen(cmd, shell=True)
        sts = p.wait()
        self.log_msg("Child Process Returned: " + `sts`, "debug")
        #minimize wahcade
        if game_opts['minimize_wahcade']:
            self.winMain.iconify()
            self.do_events()
        ### write to log file
        self.log_msg('******** End command output')
        #change back to cwd
        os.chdir(pwd)
        #hide message window
        self.message.hide()  
        self.play_clip('EXIT_GAME')
        self.scrsave_time = time.time()
        #un-minimize
        if game_opts['minimize_wahcade']:
            self.winMain.present()
            self.do_events()
        #start timers again
        #self.wait_with_events(0.25)
        self.start_timer('scrsave')
        self.start_timer('video')
        if self.joy is not None:
            self.joy.joy_count('start')
        self.start_timer('joystick')
        if self.music_enabled and not game_opts['play_music']:
            self.gstMusic.play()
        #stop timing
        time_game_stop = time.time()
        #add to / update favs list
        if rom not in self.emu_favs_list:
            self.emu_favs_list[rom] = [
                rom,
                self.lsGames[self.sclGames.get_selected()][GL_GAME_NAME],
                0,
                0]
        self.emu_favs_list[rom][FAV_TIMES_PLAYED] += 1
        self.emu_favs_list[rom][FAV_MINS_PLAYED] += int((time_game_stop - time_game_start) / 60)
        #write favs list to disk, so we don't lose it on unclean exit
        filters.write_fav_list(
            os.path.join(CONFIG_DIR, 'files', '%s.fav' % (self.current_emu)),
            self.emu_favs_list)
        self.do_events()
        self.on_winMain_focus_in()

    def auto_launch_external_app(self, launch_game_after=False, cmdline_args=''):
        """laself.joy.joy_count('stop')unch next app in list, then launch game"""
        if launch_game_after:
            self.launch_game_after = True
        if len(self.external_app_queue) > 0:
            self.launch_external_application(self.external_app_queue.pop(), True, cmdline_args)
        elif self.launch_game_after:
            self.launch_game_after = False
            self.launch_game(cmdline_args)

    def launch_external_application(self, app_number, wait_for_finish=False, game_cmdline_args=''):
        """launch app specified in emu.ini"""
        #get app name
        app_name = self.emu_ini.get('app_%s_executable' % (app_number))
        app_params = self.emu_ini.get('app_%s_commandline_format' % (app_number))
        #pre-defined?
        if app_name == 'wahcade-history-viewer':
            if self.histview:
                #set app number so histview can be closed by same keypress that started it
                self.histview.app_number = app_number
                #display game history
                self.histview.set_history(
                    self.lsGames[self.sclGames.get_selected()][GL_ROM_NAME],
                    self.lsGames[self.sclGames.get_selected()][GL_GAME_NAME])
            else:
                self.auto_launch_external_app(cmdline_args=game_cmdline_args)
        elif app_name == 'wahcade-cp-viewer':
            if self.cpviewer:
                #set app number so cpviewer can be closed by same keypress that started it
                self.cpviewer.app_number = app_number
                #display control panel info
                cpvw_rom = self.lsGames[self.sclGames.get_selected()][GL_ROM_NAME]
                #use clone name if necessary
                if self.lsGames[self.sclGames.get_selected()][GL_CLONE_OF] != '':
                    cpvw_rom = self.lsGames[self.sclGames.get_selected()][GL_CLONE_OF]
                self.cpviewer.display_game_details(cpvw_rom)
            else:
                self.auto_launch_external_app(cmdline_args=game_cmdline_args)
        else:
            #get options
            game_opts = self.get_launch_options(app_params)
            #launch the app
            if os.path.isfile(app_name):
                #pause music?
                if self.music_enabled and not game_opts['play_music'] and wait_for_finish:
                    self.gstMusic.stop()
                #minimize wahcade
                if game_opts['minimize_wahcade'] and wait_for_finish:
                    self.winMain.iconify()
                    self.do_events()
                cmd = '%s %s' % (app_name, game_opts['options'])
                p = Popen(cmd, shell=True)
                if wait_for_finish:
                    sts = p.wait()
                    #un-minimize
                    if game_opts['minimize_wahcade']:
                        self.winMain.present()
                        self.do_events()
                    #resume music
                    if self.music_enabled and not game_opts['play_music']:
                        self.gstMusic.play()
            else:
                print _('Error: External Application [%s] does not exist' % (app_name))
            #call next app
            self.auto_launch_external_app(cmdline_args=game_cmdline_args)

    def load_emulator(self, emulator_name=None):
        """load emulator"""
        self.launch_game_after = False
        #stop any vids playing
        self.stop_video()
        #load emulator ini file
        if emulator_name:
            self.current_emu = emulator_name
            self.wahcade_ini.set('current_emulator', emulator_name)
        #save current emulator list
        if self.emu_ini:
            self.emu_ini.set('current_list', self.current_list_idx)
            self.emu_ini.write()
        #load new emulator
        ### create history viewer window
        self.cpviewer = None
        self.histview = WinHistory(self)
        ### create cp viewer window
        self.cpviewer = WinCPViewer(self)
        self.hide_window()
        self.emu_ini = MameWahIni(os.path.join(CONFIG_DIR, 'ini', '%s.ini' % (self.current_emu)))
        try: 
          self.ctrlr_ini = MameWahIni(os.path.join(CONFIG_DIR, 'ctrlr', self.emu_ini.get('ctrlr')+'.ini'), 'ctrlr')
        except:
          self.ctrlr_ini = MameWahIni(os.path.join(CONFIG_DIR, 'ctrlr', 'default.ini'), 'ctrlr')
        self.lblEmulatorName.set_text(self.emu_ini.get('emulator_title'))
        self.log_msg('Selected platform: ' + self.emu_ini.get('emulator_title'))
        #set catver file
	_catver_ini = os.path.join(self.emu_ini.get('catver_ini_file'))
	#check for existence of path  (BUG: #1314447)
	if os.path.exists(_catver_ini):
	    filters._catver_ini = _catver_ini
	else:
	    filters._catver_ini = ""
        #calc number of game lists
        file_list = self.build_filelist("", "ini", "(?<=-)\d+", self.current_emu, "-") 
        self.game_lists = []
        self.game_lists_normal = []
        for file in file_list:
            ini = MameWahIni(file)
            # Grab the List number from the current file
            i = self.return_listnum(file)
            # Append lists to both arrays
            self.game_lists.append([ini.get('list_title'), i, ini.getint('cycle_list')]) 
            self.game_lists_normal.append([ini.get('list_title'), i, ini.getint('cycle_list')])        

        #load fav list
        fav_name = os.path.join(CONFIG_DIR, 'files', '%s.fav' % (self.current_emu))
        if not os.path.isfile(fav_name):
            #create fav list if it doesn't exist
            f = open(fav_name, 'w')
            f.close()
        self.emu_favs_list = filters.read_fav_list(fav_name)
        #play videos?
        self.check_video_settings()
        #load list
        self.current_list_idx = self.emu_ini.getint('current_list')
        self.list_creation_attempted = False
        self.load_list()

    def load_list(self):
        """load current list"""
        #load layout for new list
        self.stop_video()
        #self.load_layout_file()
        self.load_layouts(self.layout_orientation)
        #save last list (if defined)
        if self.current_list_ini:
            self.current_list_ini.write()
        #load new list
        list_ini_file = os.path.join(CONFIG_DIR, 'ini', '%s-%s.ini' % (self.current_emu, self.current_list_idx))
        if not os.path.isfile(list_ini_file):
            list_ini_file = os.path.join(CONFIG_DIR, 'ini', '%s-0.ini' % (self.current_emu))
            self.current_list_idx = 0
        self.current_list_ini = MameWahIni(list_ini_file)
        self.emu_ini.set('current_list', self.current_list_idx)
        #load list & set current game
        self.lblGameListIndicator.set_text(self.current_list_ini.get('list_title'))
        self.log_msg('Selected gameslist: ' + self.current_list_ini.get('list_title'))
        #has initial lst file been created?
        game_list_file = os.path.join(
            CONFIG_DIR,
            'files',
            '%s-0.lst' % (self.current_emu))
        if not os.path.isfile(game_list_file):
            self.log_msg('Please Wait. Creating initial filter...')
            self.message.display_message(_('Please Wait'), _('Creating initial filter...'))
            self.list_creation_attempted = True
            self.do_events()
            self.current_list_idx = 0
            filters.create_initial_filter(
                self.emu_ini.get('dat_file'),
                os.path.join(
                    CONFIG_DIR,
                    'files',
                    '%s-0.ftr' % (self.current_emu)),
                game_list_file,
                self.emu_ini)
            self.load_list()
            #hide message
            self.message.hide()
        #load the list of games
        self.pop_games_list()
        #load the list filter
        self.current_filter_changed = False
        if self.current_emu in MAME_INI_FILES:
            filter_file = os.path.join(
                CONFIG_DIR,
                'files',
                '%s-%s.ftr' % (self.current_emu, self.current_list_idx))
            if not os.path.isfile(filter_file):
                #filter doesn't exist, so try and use use filter for list 0
                filter_file = os.path.join(
                    CONFIG_DIR,
                    'files',
                    '%s-0.ftr' % (self.current_emu))
            self.current_filter = filters.read_filter(filter_file)
        else:
            self.current_filter = None

    def get_layout_filename(self):
        """returns current layout filename"""
        layout_matched, layout_files = self.get_rotated_layouts(self.layout_orientation)
        if self.layout_orientation != 0 and not layout_matched:
            self.layout_orientation = 0
            layout_matched, layout_files = self.get_rotated_layouts(self.layout_orientation)
        return layout_files[0]

    def load_layout_file(self, layout_file):
        """load layout file"""
        self.lblGameDescription = self.label_type('wrap_game_description_label',self.lblGameDescription)
        self.lblRomName = self.label_type('wrap_romname_label',self.lblRomName)
        self.lblYearManufacturer = self.label_type('wrap_year_manufacturer_label',self.lblYearManufacturer)
        self.lblScreenType = self.label_type('wrap_screen_type_label',self.lblScreenType)
        self.lblControllerType = self.label_type('wrap_controller_type_label',self.lblControllerType)
        self.lblDriverStatus = self.label_type('wrap_driver_status_label',self.lblDriverStatus)
        self.lblCatVer = self.label_type('wrap_catver_label',self.lblCatVer)
        layout_path = os.path.join(CONFIG_DIR, 'layouts', self.layout)
        #if layout_file == '':
            #layout_file = self.get_layout_filename()
        self.layout_path = layout_path
        if layout_file == self.layout_file:
            #layout not changed, but emulator has, so...
            #...build visible lists for displaying artwork images and exit
            self.rebuild_visible_lists()
            return
        self.layout_file = layout_file
        #read file & strip any crap
        lines = open(self.layout_file, 'r').readlines()
        lines = [s.strip() for s in lines]
        lines.insert(0, '.')
        #window sizes
        main_width, main_height = int(lines[1].split(';')[0]), int(lines[2])
        opt_width, opt_height = int(lines[294].split(';')[0]), int(lines[295])
        msg_width, msg_height = int(lines[353].split(';')[0]), int(lines[354])
        #main window
        self.winMain.set_size_request(main_width, main_height)
        self.winMain.set_default_size(main_width, main_height)
        bg_col = gtk.gdk.color_parse(self.get_colour(int(lines[3])))
        self.winMain.modify_bg(gtk.STATE_NORMAL, bg_col)
        self.fixd.move(self.imgBackground, 0, 0)
        self.imgBackground.set_size_request(main_width, main_height)
        img_file = self.get_path(lines[4])
        if not os.path.dirname(img_file):
            img_file = os.path.join(self.layout_path, img_file)
        self.imgBackground.set_data('layout-image', img_file)
        #set options window
        self.options.winOptions.set_size_request(opt_width, opt_height)
        bg_col = gtk.gdk.color_parse(self.get_colour(int(lines[296])))
        self.options.winOptions.modify_bg(gtk.STATE_NORMAL, bg_col)
        self.options.winOptions.move(self.options.imgBackground, 0, 0)
        self.options.imgBackground.set_size_request(opt_width, opt_height)
        img_file = self.get_path(lines[297])
        if not os.path.dirname(img_file):
            img_file = os.path.join(self.layout_path, img_file)
        self.options.imgBackground.set_data('layout-image', img_file)
        self.fixd.move(self.options.winOptions, ((main_width - opt_width) / 2), ((main_height - opt_height) / 2))
        #games list highlight colours
        hl_bg_col = gtk.gdk.color_parse(self.get_colour(int(lines[6])))
        hl_fg_col = gtk.gdk.color_parse(self.get_colour(int(lines[7])))
        self.sclGames.modify_highlight_bg(gtk.STATE_NORMAL, hl_bg_col)
        self.sclGames.modify_highlight_fg(gtk.STATE_NORMAL, hl_fg_col)
        #options list highlight colours
        hl_bg_col = gtk.gdk.color_parse(self.get_colour(int(lines[299])))
        hl_fg_col = gtk.gdk.color_parse(self.get_colour(int(lines[300])))
        self.options.sclOptions.modify_highlight_bg(gtk.STATE_NORMAL, hl_bg_col)
        self.options.sclOptions.modify_highlight_fg(gtk.STATE_NORMAL, hl_fg_col)
        #set message window
        self.message.winMessage.set_size_request(msg_width, msg_height)
        bg_col = gtk.gdk.color_parse(self.get_colour(int(lines[355])))
        self.message.winMessage.modify_bg(gtk.STATE_NORMAL, bg_col)
        self.message.winMessage.move(self.message.imgBackground, 0, 0)
        self.message.imgBackground.set_size_request(msg_width, msg_height)
        img_file = self.get_path(lines[356])
        if not os.path.dirname(img_file):
            img_file = os.path.join(self.layout_path, img_file)
        self.message.imgBackground.set_data('layout-image', img_file)
        self.fixd.move(self.message.winMessage, ((main_width - msg_width) / 2), ((main_height - msg_height) / 2))
        #screen saver window
        self.fixd.move(self.scrsaver.winScrSaver, 0, 0)
        self.scrsaver.winScrSaver.set_size_request(main_width, main_height)
        self.scrsaver.winScrSaver.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('black'))
        self.scrsaver.drwVideo.set_size_request(main_width, main_height)
        #set all window items
        for offset, widget in self._layout_items:
            #get properties
            d = self.get_layout_item_properties(lines, offset)
            #font
            fd = d['font']
            if d['font-bold']:
                fd += ' Bold'
            fd += ' %s' % (d['font-size'])
            font_desc = pango.FontDescription(fd)
            #text colour
            fg_col = gtk.gdk.color_parse(d['text-col'])
            widget.modify_font(font_desc)
            widget.modify_fg(gtk.STATE_NORMAL, fg_col)
            #background colour & transparency
            bg_col = gtk.gdk.color_parse(d['background-col'])
            parent = widget.get_parent()
            if parent.get_ancestor(gtk.EventBox):
                if d['transparent']:
                    parent.set_visible_window(False)
                else:
                    parent.set_visible_window(True)
                    parent.modify_bg(gtk.STATE_NORMAL, bg_col)
            #alignment
            if d['text-align'] == 2:
                widget.set_property('xalign', 0.5)
            else:
                widget.set_property('xalign', d['text-align'])
            #rotation
            widget.set_data('text-rotation', d['text-rotation'])
            try:
                widget.set_angle(d['text-rotation'])
            except AttributeError:
                pass
            #visible?
            if not d['visible']:
                widget.hide()
                if parent.get_ancestor(gtk.EventBox):
                    parent.hide()
            else:
                widget.show()
                if parent.get_ancestor(gtk.EventBox):
                    parent.show()
            #move & size
            widget.set_size_request(d['width'], d['height'])
            #position video widget
            if self.emu_ini.getint('movie_artwork_no') > 0:
                self.video_artwork_widget = self._main_images[(self.emu_ini.getint('movie_artwork_no') - 1)]
                if widget == self.video_artwork_widget:
                    self.fixd.move(self.drwVideo, d['x'], d['y'])
                    self.drwVideo.set_size_request(d['width'], d['height'])
            #modify widget for lists
            if widget == self.sclGames:
                widget = self.sclGames.fixd
            elif widget == self.options.sclOptions:
                widget = self.options.sclOptions.fixd
            elif parent.get_ancestor(gtk.EventBox):
                widget = widget.get_parent()
            #add to fixed layout on correct window
            if offset < 293:
                #main window
                self.fixd.move(widget, d['x'], d['y'])
            elif offset < 353:
                #options window
                self.options.winOptions.move(widget, d['x'], d['y'])
            elif offset < 396:
                #message window
                self.message.winMessage.move(widget, d['x'], d['y'])
            else:
                #screen saver window
                self.scrsaver.winScrSaver.move(widget, d['x'], d['y'])
        #other stuff
        self.options.lblHeading.set_text(_('Options'))
        self.options.lblSettingHeading.set_text(_('Current Setting:'))
        self.options.lblSettingValue.set_text('')
        #load histview and cpviewer layouts
        self.histview.load_layout(self.histview.layout_filename)
        self.cpviewer.load_layout(self.cpviewer.layout_filename)
        #build visible lists for displaying artwork images
        self.rebuild_visible_lists()

    def rebuild_visible_lists(self):
        """get list of visible images & paths"""
        self.visible_img_list = [img for img in self._main_images if img.get_property('visible')]
        self.visible_img_paths = [self.emu_ini.get('artwork_%s_image_path' % (i + 1)) for i, img in enumerate(self.visible_img_list)]
        #self.buildartlist(self.visible_img_paths[0])
        #check background images
        bg_files = (
            [self.imgBackground,
            [os.path.split(os.path.splitext(self.imgBackground.get_data('layout-image'))[0]),
             (self.layout_path, '%s-%s-main.%s' % (self.current_emu, self.current_list_idx, self.layout_orientation)),
             (self.layout_path, '%s-%s-main' % (self.current_emu, self.current_list_idx)),
             (self.layout_path, '%s-main.%s' % (self.current_emu, self.layout_orientation)),
             (self.layout_path, '%s-main' % (self.current_emu)),
             (self.layout_path, 'main.%s' % (self.layout_orientation)),
             (self.layout_path, 'main')]],
            [self.options.imgBackground,
            [os.path.split(os.path.splitext(self.options.imgBackground.get_data('layout-image'))[0]),
             (self.layout_path, '%s-%s-options.%s' % (self.current_emu, self.current_list_idx, self.layout_orientation)),
             (self.layout_path, '%s-%s-options' % (self.current_emu, self.current_list_idx)),
             (self.layout_path, '%s-options.%s' % (self.current_emu, self.layout_orientation)),
             (self.layout_path, '%s-options' % (self.current_emu)),
             (self.layout_path, 'options.%s' % (self.layout_orientation)),
             (self.layout_path, 'options')]],
            [self.message.imgBackground,
            [os.path.split(os.path.splitext(self.message.imgBackground.get_data('layout-image'))[0]),
             (self.layout_path, '%s-%s-message.%s' % (self.current_emu, self.current_list_idx, self.layout_orientation)),
             (self.layout_path, '%s-%s-message' % (self.current_emu, self.current_list_idx)),
             (self.layout_path, '%s-message.%s' % (self.current_emu, self.layout_orientation)),
             (self.layout_path, '%s-message' % (self.current_emu)),
             (self.layout_path, 'message.%s' % (self.layout_orientation)),
             (self.layout_path, 'message')]]
        )
        for img, img_files in bg_files:
            img_filename = self.get_matching_filename(img_files, IMAGE_FILETYPES)
            if os.path.isfile(img_filename):
                img.set_from_file(img_filename)
                img.set_property('visible', True)
            else:
                img.set_property('visible', False)
        #check logo images
        if self.imgMainLogo.get_property('visible'):
            if self.current_emu in MAME_INI_FILES:
                image_files = []
                for emu in MAME_INI_FILES:
                    image_files.append((self.layout_path, '%s-%s-logo' % (emu, self.current_list_idx)))
                    image_files.append((self.layout_path, '%s-logo' % (emu)))
                    image_files.append((self.layout_path, '%slogo' % (emu)))
                image_files.append((self.layout_path, 'logo'))
            else:
                image_files = [
                    (self.layout_path, '%s-%s-logo' % (self.current_emu, self.current_list_idx)),
                    (self.layout_path, '%s-logo' % (self.current_emu)),
                    (self.layout_path, '%slogo' % (self.current_emu)),
                    (self.layout_path, 'logo')]
            #get logo filename
            logo_filename = self.get_matching_filename(image_files, IMAGE_FILETYPES)
            if os.path.isfile(logo_filename):
                self.display_scaled_image(self.imgMainLogo, logo_filename, self.keep_aspect, self.imgMainLogo.get_data('text-rotation'))
            else:
                self.imgMainLogo.set_from_file(None)
        #refresh list (seems necessary for rotated layouts - not sure why at the moment)
        self.on_sclGames_changed()
        self.sclGames.scroll(0)

    def pop_games_list(self):
        """populate games list"""
        #which type of list is it?
        if self.current_list_idx == 0 or self.current_list_ini.get('list_type') == 'normal':
            #normal, so sort list
            list_filename = os.path.join(
                CONFIG_DIR,
                'files',
                '%s-%s.lst' % (self.current_emu, self.current_list_idx))
            if os.path.isfile(list_filename):
                self.lsGames, self.lsGames_len = filters.read_filtered_list(list_filename)
                if self.lsGames_len == 0 and self.current_list_idx == 0 and not(self.list_creation_attempted):
                    #try re-creating list
                    print _('Please Wait. Creating initial filter...')
                    self.message.display_message(_('Please Wait'), _('Creating initial filter...'))
                    self.list_creation_attempted = True
                    self.do_events()
                    self.current_list_idx = 0
                    filters.create_initial_filter(
                        self.emu_ini.get('dat_file'),
                        os.path.join(
                            CONFIG_DIR,
                            'files',
                            '%s-0.ftr' % (self.current_emu)),
                        list_filename,
                        self.emu_ini)
                    self.load_list()
                    #hide message
                    self.message.hide()
                    return
            else:
                self.lsGames = []
                self.lsGames_len = 0
            self.lsGames.sort()
        elif self.current_list_ini.get('list_type') in ['most_played', 'longest_played']:
            #favs type, so choose sort column
            if self.current_list_ini.get('list_type') == 'most_played':
                sort_column = FAV_TIMES_PLAYED
            else:
                sort_column = FAV_MINS_PLAYED
            #use all games to gen list
            list_filename = os.path.join(
                CONFIG_DIR,
                'files',
                '%s-0.lst' % (self.current_emu))
            if os.path.isfile(list_filename):
                self.lsGames, self.lsGames_len = filters.read_filtered_list(list_filename)
            else:
                self.lsGames = []
                self.lsGames_len = 0
            #create list of roms
            flist_roms = [r[GL_ROM_NAME] for r in self.lsGames]
            #order fav dictionary by number of plays
            favs = list(self.emu_favs_list.values())
            favs.sort(key = itemgetter(sort_column), reverse=True)
            #order filtered list by favs
            flist_sorted = []
            for fav in favs:
                try:
                    idx = flist_roms.index(fav[FAV_ROM_NAME])
                    flist_sorted.append(self.lsGames[idx])
                except ValueError:
                    self.log_msg("%s not in list" % (fav[FAV_ROM_NAME]))
            self.lsGames = flist_sorted
            self.lsGames_len = len(self.lsGames)
        #setup scroll list
        if self.current_list_idx == 0:
            self.sclGames.ls = [l[0] for l in self.lsGames]
        else:
            self.sclGames.ls = []
            for l in [l[0] for l in self.lsGames]:
                #remove "(bar)" from "foo (bar)" game description
                if l[0] != '(':
                    l = l.split('(')[0]
                self.sclGames.ls.append(l)
        #select game in list
        current_game = self.current_list_ini.getint('current_game')
        if current_game >= self.lsGames_len:
            current_game = 0
        self.sclGames.set_selected(current_game)
        if not self.init:
            self.on_sclGames_changed()

    def get_random_game_idx(self):
        """pick a random game index number"""
        return random.randint(0, self.lsGames_len - 1)

    def remove_current_game(self):
        """remove currently selected game from the list"""
        item = self.sclGames.ls.pop(self.sclGames.get_selected())
        item = self.lsGames.pop(self.sclGames.get_selected())
        filters.write_filtered_list(
            os.path.join(CONFIG_DIR, 'files', '%s-%s.lst' % (
                self.current_emu, self.current_list_idx)),
            self.lsGames)
        #update displays
        self.sclGames.set_selected(self.sclGames.get_selected() - 1)
        self.sclGames.update()

    def check_music_settings(self):
        """enable music playing?"""
        self.gstMusic = None
        self.gstSound = None
        if self.gst_media_imported:
            try: 
                if self.music_enabled:
                        self.gstMusic = gst_media.MusicPlayer()
                if self.sound_enabled:
                        self.gstSound = gst_media.SoundPlayer()
                #check dir
                if not os.path.isdir(self.wahcade_ini.get('music_path')):
                    self.log_msg('Error: Music Path [%s] does not exist' % (self.musicpath))
                    return
                else:
                    #set dir
                    tracks = self.gstMusic.set_directory(self.musicpath, MUSIC_FILESPEC)
                    #set volume
                    self.gstMusic.set_volume(self.music_vol)
                    #play
                    if len(tracks) > 0:
                        self.gstMusic.load_playlist(
                            playlist = tracks,
                            play = True,
                            shuffle = self.musicshuffle)
            except:
                #playbin object creation failed
                self.log_msg('Warning: Failed to create Music gstreamer objects','0')
                return


    def check_video_settings(self):
        """enable video playing?"""
        self.video_enabled = True
        #did gst_media module import ok?
        if not self.gst_media_imported:
            self.video_enabled = False
        #movie delay
        if self.delaymovieprev == 0:
            self.video_enabled = False
        #check video path exists
        if self.emumovieprevpath != '' and not os.path.exists(self.emumovieprevpath):
            if self.debug_mode:
                self.log_msg('Error: Movie Preview Path [%s] does not exist' % self.emumovieprevpath,'0')
            self.video_enabled = False
        #check movie artwork
        if not(self.emumovieartworkno > 0):
            self.video_enabled = False
        #create gstreamer video player
        if self.video_enabled:
            try:
                self.video_player = gst_media.GstVideo(self.drwVideo)
                self.log_msg('Created Video gstreamer objects','0')
            except:
                #gstreamer object creation failed
                self.video_enabled = False
                self.log_msg('Warning: Failed to create Video gstreamer objects','0')
                return

    def start_timer(self, timer_type):
        """start given timer"""
        #screen saver
        if timer_type == 'scrsave' and self.scrsave_delay > 0:
            if self.scrsave_timer:
                gobject.source_remove(self.scrsave_timer)
            self.scrsave_timer = gobject.timeout_add(2500, self.on_scrsave_timer)
        #video
        elif timer_type == 'video' and self.video_enabled:
            #stop any playing vids first
            self.stop_video()
            #restart timer
            self.video_timer = gobject.timeout_add(
                self.delaymovieprev * 1000,
                self.on_video_timer)
        #joystick
        elif timer_type == 'joystick' and self.joy:
            self.joystick_timer = gobject.timeout_add(50, self.joy.poll, self.on_winMain_key_press)

    def display_splash(self):
        """show splash screen"""
        self.splash = gtk.Window()
        self.splash.set_decorated(False)
        self.splash.set_transient_for(self.winMain)
        self.splash.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.splash.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.splash.set_keep_above(True)
        self.splash.set_border_width(self.splash_border_width)
        vbox = gtk.VBox()
        img = gtk.Image()
        self.splash_gfx = os.path.join(CONFIG_DIR, 'layouts', self.layout, 'main-splash.png')
        if os.path.exists(self.splash_gfx):
            self.log_msg('Custom splash found, loading ' + str(self.splash_gfx))
            img.set_from_file(self.splash_gfx)
        else:
            self.splash_gfx = os.path.join(APP_PATH, 'pixmaps', 'wahcade-logo.png')
            self.log_msg('No custom splash found, loading ' + str(self.splash_gfx))
            img.set_from_file(self.splash_gfx)
        if self.splash_show_text == 1:
            lbl = gtk.Label()
            lbl.set_alignment(0.5, 0.5)
            lbl.set_justify(gtk.JUSTIFY_CENTER)
            lbl.set_use_markup(True)
            lbl.set_markup('<big><b>Wah!Cade</b></big>\n%s "%s"' % (VERSION, VERSION_NAME))
            vbox.pack_end(lbl)
        vbox.pack_start(img)
        self.splash.add(vbox)
        self.splash.show_all()
        if not self.tw_api:
            self.twitter_api = self.auth_twitter() ## Auth Twitter during startup
        self.wait_with_events(0.25)

    def get_rotated_layouts(self, angle):
        """Checks for the existence of layout file(s) for given angle.  Returns:
           (main layout filename, history viewer filename, cpviewer filename)
        """
        #main layout
        layout_path = os.path.join(CONFIG_DIR, 'layouts', self.wahcade_ini.get('layout'))
        if angle == 0:
            # The 0 degree layout angle _may_ not actually have a angle in the filename as this is the default
            # layout filename so make sure that we include this in the set.
            first_globbed_lay = ''
            glob_lays = glob.glob(os.path.join(layout_path, '*.lay'))
            if len(glob_lays) > 0:
                first_globbed_lay = glob_lays[0]
            layout_files = [
                (layout_path, '%s-%s.%s.lay' % (self.current_emu, self.current_list_idx, angle)), #0
                (layout_path, '%s-%s.lay' % (self.current_emu, self.current_list_idx)), #1
                (layout_path, '%s.%s.lay' % (self.current_emu, angle)), #2
                (layout_path, '%s.lay' % (self.current_emu)), #3
                (layout_path, 'layout.%s.lay' % (angle)), #4
                (layout_path, 'layout.lay'), #5
                ('', first_globbed_lay), #6
                (os.path.join(CONFIG_DIR, 'layouts', 'classic_640x480'), 'layout.lay')] #7
        else:
            layout_files = [
                (layout_path, '%s-%s.%s.lay' % (self.current_emu, self.current_list_idx, angle)),
                (layout_path, '%s.%s.lay' % (self.current_emu, angle)),
                (layout_path, 'layout.%s.lay' % (angle))]
        layout_file = self.get_matching_filename(layout_files, '')
        #check to see whether the returned layout matches the requested orientation
        lfp = [os.path.join(dirname, fp) for dirname, fp in layout_files]
        layout_matched = layout_file in lfp
        #history viewer layout
        hv_layout_path, hv_layout_file = os.path.split(self.histview.histview_ini.get('history_layout'))
        hv_file_base, hv_file_ext = os.path.splitext(hv_layout_file)
        if angle == 0:
            hv_layout_files = [
                (hv_layout_path, '%s.%s%s' % (hv_file_base, angle, hv_file_ext)), #0
                (hv_layout_path, '%s%s' % (hv_file_base, hv_file_ext))] #1
        else:
            hv_layout_files = [
                (hv_layout_path, '%s.%s%s' % (hv_file_base, angle, hv_file_ext))] #0
        hv_layout_file = self.get_matching_filename(hv_layout_files, '')
        #cp viewer layout
        cp_layout_path, cp_layout_file = os.path.split(self.cpviewer.cpviewer_ini.get('viewer_layout'))
        cp_file_base, cp_file_ext = os.path.splitext(cp_layout_file)
        if angle == 0:
            cp_layout_files = [
                (cp_layout_path, '%s.%s%s' % (cp_file_base, angle, cp_file_ext)), #0
                (cp_layout_path, '%s%s' % (cp_file_base, cp_file_ext))] #1
        else:
            cp_layout_files = [
                (cp_layout_path, '%s.%s%s' % (cp_file_base, angle, cp_file_ext))] #0
        cp_layout_file = self.get_matching_filename(cp_layout_files, '')
        #update ini
        if layout_matched:
            self.wahcade_ini.set('layout_orientation', angle)
            self.wahcade_ini.write()
        #done
        return layout_matched, [layout_file, hv_layout_file, cp_layout_file]

    def load_layouts(self, requested_angle):
        """switch layout to specified rotation"""
        #layout
        if requested_angle == 'toggle':
            #toggle between 0, 90, 180, 270 degree layouts
            new_angle = (self.layout_orientation + 90) % 360
            layout_matched, layout_files = False, []
            while not layout_matched:
                layout_matched, layout_files = self.get_rotated_layouts(new_angle)
                if not layout_matched:
                    new_angle = (new_angle + 90) % 360
                if new_angle == self.layout_orientation:
                    break
        else:
            #switch to specified rotation
            new_angle = requested_angle
            layout_matched, layout_files = self.get_rotated_layouts(new_angle)
        #load rotated layout(s)
        if layout_matched:
            #print "switched to:", new_angle
            self.layout_orientation = new_angle
            if os.path.isfile(layout_files[0]):
                self.load_layout_file(layout_files[0])
            if os.path.isfile(layout_files[1]):
                self.histview.load_layout(layout_files[1])
            if os.path.isfile(layout_files[2]):
                self.cpviewer.load_layout(layout_files[2])

    def show_window(self, window_name):
        """show given window"""
        child_win = None
        if window_name == 'message':
            child_win = self.message.winMessage
        elif window_name == 'options':
            child_win = self.options.winOptions
        elif window_name == 'scrsaver':
            child_win = self.scrsaver.winScrSaver
        elif window_name == 'history':
            if self.histview:
                child_win = self.histview.winHistory
        elif window_name == 'cpviewer':
            if self.cpviewer:
                child_win = self.cpviewer.winCPViewer
        #show given child window
        if child_win:
            self.stop_video()
            child_win.show()
            try:
                child_win.window.raise_()
                #child_win.window.focus() #for bug #382247
            except AttributeError:
                pass
            self.current_window = window_name

    def hide_window(self, window_name='all'):
        """hide given window"""
        #hide all child windows
        self.message.winMessage.hide()
        self.options.winOptions.hide()
        self.scrsaver.winScrSaver.hide()
        self.histview.winHistory.hide()
        self.cpviewer.winCPViewer.hide()
        #"show" main
        self.current_window = 'main'
        self.winMain.present()
        #start timers again
        self.start_timer('scrsave')
        self.start_timer('video')


    def check_ext_on_game_launch(self, romext='*'):
        if romext == '*' or len(romext) == 0:
            self.log_msg("[LAUNCH] No extension or wildcard passed trying to look up a rom extension for launch")
            if os.path.exists(self.emu_ini.get('rom_path')):
                roms = glob.glob(os.path.join(self.emu_ini.get('rom_path'), '*'))
            else:
                self.log_msg("[LAUNCH] Could not find rom path")
                return               
            if roms:
                for romname in roms:
                    if self.lsGames[self.sclGames.get_selected()][GL_ROM_NAME] in romname:
                        #Set romext to actual extension
                        romext = re.search('\.[^\.]+$',romname).group(0)[1:]
                    else:
                        romext = None
                    if romext:
                        break
                if not romext:
                    self.log_msg("[LAUNCH] No extension or wildcard passed and could no find a compatible rom for launch, try rebuilding the gameslist")                                                
            else:
                self.log_msg("[LAUNCH] ROM path exists but appears to be empty, check rom path")                
        # Multiple Extensions Specified, step through on launch
        elif ';' in romext:
            self.log_msg("[LAUNCH] Multiple extensions specified, stepping through to find first match")
            m = romext.split(";")
            for ext in m:
                if os.path.isfile(self.emu_ini.get('rom_path') + '/' + self.lsGames[self.sclGames.get_selected()][GL_ROM_NAME] + '.' + ext):
                    romext =  "." + ext
                else:
                    self.log_msg("[LAUNCH] Could not find match for: %s" % ext)
        else:
            self.log_msg("[LAUNCH] Single extension only")
            
        if romext:
            self.log_msg("[LAUNCH] Setting extension to: %s" % romext)
            return romext

    def check_params(self, check_opts):
        """check command line options"""
        if check_opts.windowed:
            self.screentype = 0
            self.log_msg("Launching in Windowed Mode")
        if check_opts.fullscreen:
            self.screentype = 1
            self.log_msg("Launching in Fullscreen Mode")
        if check_opts.debug:
            self.debug_mode = True
            self.log_msg("Debug Mode Enabled")
        if check_opts.disable_gstreamer:
            self.gst_media_imported = False
            self.log_msg("gstreamer not imported, music/movies/videos playback disabled")
        if check_opts.disable_pygame:
            self.pygame_imported = False
            self.log_msg("pyGame not imported, joysticks disabled")
        if check_opts.old_keyb_events:
            self.old_keyb_events = True
            self.log_msg("Old style keyboard events enabled")
    
    def play_clip(self, file):
        myclip = os.path.join(CONFIG_DIR, 'layouts', self.wahcade_ini.get('layout'), 'sounds', file.lower())
        for ext in MUSIC_FILESPEC_NEW:
            theclip = myclip + "." + ext
            if os.path.exists(theclip) and self.gst_media_imported and self.sound_enabled:
                self.gstSound.stop()
                self.gstSound.set_volume(self.sound_vol)
                self.gstSound.play(theclip)
            break


    def label_type(self, name, label):
        '''Set label properties based on options in emu ini'''
        if self.emu_ini.getint(name):
            label.set_line_wrap(True)
            label.set_alignment(xalign=0.0, yalign=0.0)
        else:
            label.set_line_wrap(False)
        return label

