#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
###
# Application: wah!cade
# File:        wc_common.py
# Description: common code to wahcade windows
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
import os
import sys
import webbrowser
import shutil
import time
import re
import glob
import StringIO
pil_imported = False
try:
    import PIL.Image
    pil_imported = True
except ImportError:
    print 'Warning: PIL module not found.  Rotated images not supported'

## GTK import
import gtk

#project modules
from constants import *
from mamewah_ini import MameWahIni
from key_consts import mamewah_keys
from filters import walk_dir
_ = gettext.gettext


# TWITTER support
twitter_enabled = False
try:
    import tweepy
    twitter_enabled = True
    print 'Twitter Support Enabled'
except:
    print 'Twitter Support Disabled, install tweepy (pip install tweepy)'

class WahCade:
    """Common functions for Wah!Cade"""

    def __init__(self):
        """initialise common wahcade class"""
        #set default icon for windows
        gtk.window_set_default_icon_from_file(
            os.path.join(APP_PATH, 'pixmaps', 'wahcade.png'))
        ### LOGFILE
        if os.path.exists(CONFIG_DIR):
            self.log_filename = os.path.join(CONFIG_DIR, 'wahcade.log')
            try:
                f = open(self.log_filename, 'w')
                self.log_msg("//======================= NEW LOG RUN =======================//")
                f.close
            except:
                print "ERROR opening LOG FILE, %s, check for orphaned processes" % self.log_filename

    def hide_mouse_cursor(self, win):
        """hide mouse cursor"""
        gtk_col = gtk.gdk.Color()
        pixmap = gtk.gdk.Pixmap(None, 1, 1, 1)
        invisible_cursor = gtk.gdk.Cursor(
            pixmap, pixmap, gtk_col, gtk_col, 0, 0)
        win.window.set_cursor(invisible_cursor)

    def get_layout_item_properties(self, lines, offset):
        """get properties for item in layout"""
        d={}
        d['visible'] = (lines[offset].lower() == 'true')
        d['transparent'] = (lines[offset + 1] == '1')
        d['background-col'] = self.get_colour(int(lines[offset + 2]))
        d['text-col'] = self.get_colour(int(lines[offset + 3]))
        d['font'] = lines[offset + 4]
        d['font-bold'] = (lines[offset + 5].lower() == 'true')
        d['font-italic'] = (lines[offset + 6].lower() == 'true')
        d['font-size'] = float(lines[offset + 7])
        align_rot = lines[offset + 8].split(';')
        d['text-align'] = int(align_rot[0])
        d['text-rotation'] = 0
        if len(align_rot) > 1:
            d['text-rotation'] = int(align_rot[1])
        d['x'] = int(lines[offset + 9])
        d['y'] = int(lines[offset + 10])
        d['width'] = int(lines[offset + 11])
        d['height'] = int(lines[offset + 12])
        #done
        return d

    def get_colorbutton_info(self, clr_widget):
        """get gtk.ColorButton widgets current colour in gdk and hex format"""
        clr = clr_widget.get_color()
        hex_clr = '#%s%s%s' % (
            hex(clr.red/256)[2:].rjust(2, '0'),
            hex(clr.green/256)[2:].rjust(2, '0'),
            hex(clr.blue/256)[2:].rjust(2, '0'))
        return clr, hex_clr

    def get_colour(self, col):
        """convert decimal colour into format suitable for gtk colour"""
        hex_col = hex(col)[2:].rjust(6, '0').upper()
        #re-arrange
        hex_col = '#%s%s%s' % (hex_col[4:6], hex_col[2:4], hex_col[0:2])
        return hex_col

    def reverse_get_colour(self, hex_col):
        """reverse get_colour method - convert hex colour (#RRGGBB) into
           wahcade's decimal format"""
        r = int(hex_col[1:3], 16)
        g = int(hex_col[3:5], 16)
        b = int(hex_col[5:7], 16)
        col = (b * 256 * 256) + (g * 256) + r
        return col

    def get_matching_filename(self, file_prefixes, file_formats):
        """return the filename if it exists from given formats & path
              file_prefixes = [(dir_name, filename), ...]
              file_formats = [file_ext1, file_ext2, ...]
        """
        p = re.compile('(\.[^\.]+$)|(\s(\(|\[).+(?<=(\)|\]|\s))\.[^\.]+$)')
        self.wahcade_ini = MameWahIni(os.path.join(CONFIG_DIR, 'wahcade.ini'))
        l = self.wahcade_ini.get('layout')
        fz = self.wahcade_ini.getint('fuzzy_artwork_search')
        #check lower & upper case filenames for each given prefix & format
        for dirname, fp in file_prefixes:
            if fp == '##random##':
                for ff in file_formats:
                    fnl = walk_dir(dirname, False, '*.%s' % ff.lower(), False) + \
                        walk_dir(dirname, False, '*.%s' % ff.upper(), False)
                    #return first valid match
                    for filename in fnl:
                        if os.path.isfile(filename):
                            return filename
            elif fp != '':
                if file_formats != '':
                    # Check if this is a layout
                    if l not in dirname:
                        if fz:
                            # NB: we append a fake extension here to support the regex currently - sairuk
                            #     handles . appearing in filename being treated as an ext
                            fileset = glob.iglob(os.path.join(CONFIG_DIR, dirname, re.sub(p,'',fp + ".fix") + "*"))
                            for filename in fileset:
                                fn = os.path.basename(filename.lower())
                                f = re.sub(p,'',fn)
                                g = re.search(re.escape(f),fp.lower())
                                if f and g is not None:
                                    if f == g.group(0):
                                        return filename
                                else:
                                    self.log_msg(" [ARTWORK] No match for " + fp + " in " + dirname, 1)
                        else:
                            for ff in file_formats:
                                basename = '%s.%s' % (fp, ff)
                                #build list of possible filenames
                                fnl = [os.path.join(dirname, basename),
                                       os.path.join(dirname, basename.lower()),
                                       os.path.join(dirname, basename.upper())]
                                #return first valid match
                                for filename in fnl:
                                    if os.path.isfile(filename):
                                        return filename
                    else:
                        for ff in file_formats:
                            basename = '%s.%s' % (fp, ff)
                            #build list of possible filenames
                            fnl = [os.path.join(dirname, basename),
                                   os.path.join(dirname, basename.lower()),
                                   os.path.join(dirname, basename.upper())]
                            #return first valid match
                            for filename in fnl:
                                if os.path.isfile(filename):
                                    return filename
                                
                else:
                    filename = os.path.join(dirname, fp)
                    if os.path.isfile(filename):
                        return filename
        #done - nothing found
        return ''

    def get_artwork_image(self, img_path, layout_path, game_info, emu_name, artwork_num):
        """check various permutations of file name and return img filename"""
        #list of files to check for
        image_files = [
            (img_path, game_info['rom_name']),
            (img_path, game_info['clone_of']),
            (os.path.join(img_path, game_info['rom_name'].upper()), '##random##'),
            (os.path.join(img_path, game_info['rom_name'].lower()), '##random##'),
            (layout_path, '%s-art%s' % (emu_name, artwork_num)),
            (layout_path, '%s-art' % (emu_name)),
            (layout_path, 'art%s' % artwork_num),
            (layout_path, 'art')]
        #get artwork filename
        art_filename = self.get_matching_filename(
            image_files,
            IMAGE_FILETYPES)
        #still not found an image?
        if art_filename == '':
            #use default empty image
            art_filename = os.path.join(APP_PATH, 'pixmaps', 'empty.png')
        #done
        return art_filename

    def get_video_file(self, video_path, game_info):
        """check various permutations of file name and return video filename"""
        #list of files to check for
        video_files = [
            (video_path, game_info['rom_name']),
            (video_path, game_info['clone_of'])]
        #get vid filename
        vid_filename = self.get_matching_filename(
            video_files,
            MOVIE_FILETYPES)
        #done
        return vid_filename

    def get_scaled_pixbuf(self, img, img_filename, keep_aspect, missing_img=None, rotate=0):
        """get a pixbuf with image from filename (scaled to fit)"""
        #get image widget size
        img_width, img_height = img.size_request()
        #load image
        self.anim = 0
        try:
            if rotate is not 0 and pil_imported:
                pb = self.pil_image_to_pixbuf(img_filename, rotate)
            else:
                pb = gtk.gdk.PixbufAnimation(img_filename)
                self.anim = 1
                if pb.is_static_image():
                    del pb
                    pb = gtk.gdk.pixbuf_new_from_file(img_filename)
                    self.anim = 0
        except IOError or glib.GError as e:
            self.log_msg("[ERROR] %s" % e)
            #load empty image
            if not missing_img:
                self.log_msg("[INFO] Loading default image")
                missing_img = os.path.join(APP_PATH, 'pixmaps', 'empty.png')
            pb = gtk.gdk.pixbuf_new_from_file(missing_img)
        #calc image scale
        img_scale_x = float(img_width) / float(pb.get_width())
        img_scale_y = float(img_height) / float(pb.get_height())
        #scale to width or height
        if keep_aspect:
            if (pb.get_height()) * img_scale_x > img_height:
                #scale to height
                new_pb_width = int(float(pb.get_width()) * img_scale_y)
                new_pb_height = int(float(pb.get_height()) * img_scale_y)
            else:
                #scale to width
                new_pb_width = int(float(pb.get_width()) * img_scale_x)
                new_pb_height = int(float(pb.get_height()) * img_scale_x)
        else:
            new_pb_width = img_width
            new_pb_height = img_height
        #scale artwork to display size
        if self.anim == 1:
            scaled_pb = pb
        else:
            scaled_pb = pb.scale_simple(new_pb_width, new_pb_height, gtk.gdk.INTERP_HYPER)
        #set video width & height
        if img == self.video_artwork_widget:
            self.video_width = new_pb_width
            self.video_height = new_pb_height
        #done
        del pb
        return scaled_pb

    def display_scaled_image(self, img, img_filename, keep_aspect, rotate=0):
        """load given image widget with filename (scaled to fit)"""
        pb = self.get_scaled_pixbuf(img, img_filename, keep_aspect, rotate=rotate)
        if self.anim == 1:
            img.set_from_animation(pb)
        else:
            img.set_from_pixbuf(pb)
        del pb

    def do_events(self):
        """process any outstanding gtk events"""
        while gtk.events_pending():
            gtk.main_iteration(False)

    def get_path(self, check_path):
        """return a given path, with user expansion"""
        if check_path:
            if os.path.exists(os.path.expanduser(check_path)):
                check_path = os.path.normcase(os.path.expanduser(check_path))
        #done
        return check_path

    def show_about_dialog(self, app_name, config_dir):
        """about dialog"""
        #open controller ini file
        self.ctrlr_ini = MameWahIni(os.path.join(config_dir, 'ctrlr', 'default.ini'), 'ctrlr')
        #create about dialog
        dlg = gtk.AboutDialog()
        dlg.set_name(app_name)
        dlg.set_version('\n%s "%s"' % (VERSION, VERSION_NAME))
        dlg.set_logo(gtk.gdk.pixbuf_new_from_file(
            os.path.join(APP_PATH, 'pixmaps', 'wahcade-logo.png')))
        gtk.about_dialog_set_url_hook(self.show_website, None)
        dlg.set_website('http:///www.anti-particle.com/wahcade.shtml')
        dlg.set_website_label('www.anti-particle.com/wahcade')
        dlg.set_authors([
            'Andy Balcombe', 'sairuk',
            'Bug Reports and Patches:',
                '  Sylvain Fauveau', '  Robbforce', '  Jim Merullo',
                '  SeTTleR', '  Mike Crawford', '  Mike Schwartz',
                '  Nellistc', '  Captbaritone', '  Delphipool', '  3NF',
                '  Zerodiv', '  Natrix', '  Bonzo', '  Battlecat', '  Krisbee',
                '  Buks', '  KillsTheWeak', '  Martin Kalitis', '  Zerojay',
                '  Dave Baer', '  Spudgunman', '  RomKnight', '  Jason Carter',
                '  Zombie', '  Pinball Wizard', '  hamelg', '  3vi1',
                '  Vítor Baptista', '  Enrico Magrella', 'zagadka',
                '  and anyone I\'ve forgotten...', '',
            'Translations:',
                '  de: SeTTleR', '  es: Nicolás Álvarez',
                '  fr: Sylvain Faveau', '  it: Diego Pierotto',
                '  sv: Daniel Nylander', '',
            'bdist_debian.py: Gene Cash', '',
            ])
        dlg.set_artists(['Andy Balcombe', 'Buks', 'Battlecat'])
        dlg.set_copyright('%s 2005-2010 Andy Balcombe' % (
            unichr(169)).encode("utf-8"))
        dlg.set_comments('Thanks to:\nMinWah and also the Mame / xMame team')
        dlg.set_translator_credits(_('translator-credits'))
        dlg.set_license(open(os.path.join(APP_PATH, 'doc', 'COPYING')).read())
        dlg.connect('key_press_event', self.on_dlgAbout_key_press)
        dlg.run()
        dlg.hide()

    def on_dlgAbout_key_press(self, dlg, event, *args):
        """keyboard pressed on about dialog - close it"""
        if event.type == gtk.gdk.KEY_PRESS:
            #keyboard pressed, get gtk keyname
            keyname = gtk.gdk.keyval_name(event.keyval).lower()
            if keyname not in mamewah_keys:
                return
            #get mamewah keyname
            mw_keys = mamewah_keys[keyname]
            if mw_keys == []:
                return
            #get mamewah function from key
            for mw_key in mw_keys:
                mw_functions = self.ctrlr_ini.reverse_get(mw_key)
                if mw_functions:
                    break
            #check key
            for mw_func in mw_functions:
                if mw_func in ['LAUNCH_GAME', 'EXIT_TO_WINDOWS']:
                    #send close signal
                    dlg.response(gtk.RESPONSE_CLOSE)

    def show_website(self, dlg, link, data):
        """display web site from about dialog"""
        webbrowser.open(link)

    def invert_dictionary_with_lists(self, d):
        """inverts a dictionary that contains lists"""
        return dict((v, k) for k in d for v in d[k])

    def make_evb_widget(self, widget):
        """create an event box and add the given widget to it"""
        evb = gtk.EventBox()
        #evb.show()
        evb.add(widget)
        return evb

    def copy_user_config(self, copymode='update'):
        """update the user's config dir (e.g. ~/.wahcade) with any missing
           files from wahcade/config.dist"""
        if copymode == 'all':
            #copy ALL config files
            shutil.copytree(
                os.path.join(APP_PATH, 'config.dist'),
                CONFIG_DIR)
        else:
            #update the config files
            self._copytree(
                os.path.join(APP_PATH, 'config.dist'),
                CONFIG_DIR)

    def _copytree(self, src, dst):
        """copy files from src to dst"""
        names = os.listdir(src)
        if not os.path.exists(dst):
            os.mkdir(dst)
        for name in names:
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            try:
                if os.path.isdir(srcname):
                    self._copytree(srcname, dstname)
                else:
                    if not os.path.exists(dstname):
                        if 'config.dist/ini/' not in srcname:
                            #create file if it doesn't exist already
                            shutil.copy2(srcname, dstname)
            except IOError:
                pass

    def pil_image_to_pixbuf(self, image_fn, angle):
        """use Python Image Library (PIL) to load an image, rotate it, and return as a pixbuf)
        """
        pixbuf = None
        if os.path.isfile(image_fn):
            pil_image = PIL.Image.open(image_fn)
            if angle is not 0:
                pil_image = pil_image.rotate(angle,PIL.Image.BICUBIC,1)
            fd = StringIO.StringIO()
            pil_image.save(fd, "png")
            contents = fd.getvalue()
            fd.close()
            loader = gtk.gdk.PixbufLoader("png")
            loader.write(contents, len(contents))
            pixbuf = loader.get_pixbuf()
            loader.close()
        #done
        return pixbuf

    def set_busy_cursor(self, win):
        """set mouse to busy cursor"""
        win.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
        self.do_events()

    def set_normal_cursor(self, win):
        """set mouse to arrow cursor"""
        win.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.ARROW))
        self.do_events()

    def wait_with_events(self, num_seconds):
        """pause for a given amount of time"""
        time_start = time.time()
        while True:
            self.do_events()
            if (time_start + num_seconds) < time.time():
                break

    # return_listnum
    # returns digits included in string after a dash
    #
    def return_listnum(self, str, regex="(?<=-)\d+"):
        """return regex result from string"""
        m = re.search(regex,str)
        if m is not None:
            return int(m.group(0))

    # build_filelist
    # returns sorted array of files numbers matching regex.
    #
    # defaults
    # type, type of list, required
    # ext, *.ini
    # regex, (?<=-)\d+ [matches 0 in mame-0.ini]
    # emu, current emu name
    # sep, sparator used in file, default is none
    #
    def build_filelist(self, type, ext="ini", regex="(?<=-)\d+", emu="", sep=""):
        """return array of files numbers matching regex value"""
        filelist = []
        fileset = glob.glob(os.path.join(CONFIG_DIR, ext, emu + sep + '*.' + ext))
        for file in fileset:
            m = re.search(regex,file)
            if m is not None:
                if type == "int":
                    filelist.append(self.return_listnum(file))
                elif type == "glist":
                    if os.path.isfile(file):
                        list_ini = MameWahIni(file)
                        filelist.append('%s: %s' % (self.return_listnum(file),list_ini.get('list_title')))
                else:
                    filelist.append(file)
        filelist.sort()
        return filelist
    
    
    # buildemulist
    # returns array of available emulators
    #
    def buildemulist(self):
        emu_lists = []
        emu_ini_files = self.build_filelist("", "ini", "(.*(?<!=-))")
        for emu_ini in emu_ini_files:
            ini = MameWahIni(emu_ini)
            if not ini.has_option('list_title'):
                emu_lists.append(
                    [ini.get('emulator_title'),
                     os.path.splitext(os.path.basename(emu_ini))[0],ini])
        return emu_lists
    
    # buildartlist
    # returns array of available artwork
    #
    def buildartlist(self, dirname):
        art_lists = []
        art_lists = glob.glob(os.path.join(CONFIG_DIR, dirname, "*"))
        return art_lists
    

    # log_msg
    # writes log files
    #
    def log_msg(self, message, type='X'):
        """writing application log file"""
        # To be used to write log files in the future
        # Set Date & Time        
        mytime = time.asctime( time.localtime(time.time()) )
        pmessage = "[" + str(mytime) + "]: " + str(message)
        
        # Print message to location
        #    0 = stdout
        #    1 = debug messages
        if type == 0:
            print(message)   
        elif type == 1:
            pmessage = "[" + str(mytime) + "]: [DEBUG] " + str(message)
        else:
            pass
        # All messages are written to wahcade.log
        try:
            f = open(self.log_filename, 'a')
            f.write(pmessage + '\n')
            f.close()
        except:
            pass 


    def auth_twitter(self):
        tw_error = []
        if self.tw_oath_ckey == '':
            tw_error.append('consumer_key')
        if self.tw_oath_csecret == '':
            tw_error.append('consumer_secret')
        if self.tw_oath_akey == '':
            tw_error.append('access_key')
        if self.tw_oath_asecret == '':
            tw_error.append('access_key')

        if len(tw_error) > 0:
            twitter_enabled = False
            self.log_msg('[TWITTER] support disabled due to missing options')
            for tw_error in tw_error:
                self.log_msg('[TWITTER] %s cannot be blank in wahcade.ini, details available at https://dev.twitter.com/' % tw_error)
            return

        self.log_msg(('[TWITTER] Beginning OAuthentication'))
        auth = tweepy.OAuthHandler(self.tw_oath_ckey,self.tw_oath_csecret)
        auth.set_access_token(self.tw_oath_akey, self.tw_oath_asecret)
        self.tw_api = tweepy.API(auth)
        if not self.tw_api.verify_credentials():
            self.log_msg('[TWITTER] Error! OAuthentication failure')
            self.tw_api = None
        else:
            self.log_msg('[TWITTER] Logged in as: %s' % self.tw_api.me().name)
        return self.tw_api

    def post_tweet(self,msg):
        try:
            self.tw_api.update_status(msg)
            self.log_msg('[TWITTER] tweeting: %s' % msg)
            return 'Post Tweet Success!'
        except tweepy.TweepError:
            return 'Post Tweet Failed!'

    def procmsg(self,msg):
        if msg:
            # Build Message based on data available
            msg_opts = {}
            msg_opts["%r"]= self.lsGames[self.sclGames.get_selected()][GL_ROM_NAME]
            msg_opts["%n"]= self.lsGames[self.sclGames.get_selected()][GL_GAME_NAME]
            msg_opts["%y"]= self.lsGames[self.sclGames.get_selected()][GL_YEAR]
            msg_opts["%m"]= self.lsGames[self.sclGames.get_selected()][GL_MANUFACTURER]
            msg_opts["%c"]= self.lsGames[self.sclGames.get_selected()][GL_CATEGORY]
            msg_opts["%d"]= self.lsGames[self.sclGames.get_selected()][GL_DISPLAY_TYPE]
            msg_opts["%s"]= self.lsGames[self.sclGames.get_selected()][GL_SCREEN_TYPE]
            msg_opts["%e"]= self.emu_ini.get('emulator_title')
            msg_opts["%g"]= self.current_list_ini.get('list_title')
            # Make substitution in msg string
            for i in msg_opts.iteritems():
                msg = msg.replace(i[0],i[1])
            msg = msg + " #mahcade " + self.tw_ctags
        return msg
