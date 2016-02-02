# -*- coding: utf-8 -*-
#
# Copyright (c) 2001-2006   Andy Balcombe <http://www.anti-particle.com>
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
import new
import types

import pygtk
#this is needed for py2exe
if sys.platform != 'win32':
    #not win32, ensure version 2 of pygtk is imported
    pygtk.require('2.0')
import gtk
assert gtk.pygtk_version >= (2, 12, 0), 'pygtk should be >= 2.12.0'
import gtk.glade
import gobject
import pango


class GladeSupport:
    """ Superclass for glade2 based applications
    Parameters:
        glade_filename : name of .glade filename
        window_name    : name of window / dialog / menu to be created
    """

    def __init__(self, glade_filename, window_name, app_name=None):
        #load glade file
        if app_name:
            self.xml = gtk.glade.XML(glade_filename, window_name, app_name)
        else:
            self.xml = gtk.glade.XML(glade_filename, window_name)
        #find and store methods as bound callbacks
        callbacks = {}
        class_methods = self.__class__.__dict__
        for method_name in class_methods.keys():
            method = class_methods[method_name]
            if type(method) == types.FunctionType:
                callbacks[method_name] = new.instancemethod(method, self, self.__class__)
        #autoconnect signals
        self.xml.signal_autoconnect(callbacks)

    def __getattr__(self, key):
        """returns reference to a widget"""
        w = self.xml.get_widget(key)
        if w is None:
            raise AttributeError('Widget %s not found' % (key))
        self.__dict__[key] = w
        return w

    def setup_treeview(self, columns, column_types, container, changed_callback=None, highlight_rows=True, resizeable_cols=True, sortable_cols=True, text_style='text', edit_cell_cb=None):
        """ Create a ready-to-use (list based) treeview widget
        Parameters:
            columns          : List of column names
            column_types     : List of variable types for each column
                               (eg. [gobject.TYPE_STRING, gobject.TYPE_LONG])
            container        : reference to widget that is to contain list,
                               almost always a scrolled window - gtk.ScrolledWindow()
            changed_callback : the callback function for the "changed" signal (ie. row selected)
            highlight_rows   : True to force highlighted rows (rendered with alternating row colours)
            resizeable_cols  : True to allow columns to be resizable by user
            sortable_cols    : True to allow user to sort columns
            text_style       : 'text' for normail plain text,
                               'markup' for pango marked-up text
            edit_cell_cb     : a function thats called when a cell is edited (None for uneditable view)
        Returns:
            Reference to TreeView, ListStore and TreeViewSelection widgets

        e.g. to create a three column (first two displayed, third hidden) list view...
            self.tvwProjects, self.lsProjects, self.tvwsProjects = self.setup_treeview(
                ['Project', 'Number of Files'],
                [gobject.TYPE_STRING, gobject.TYPE_LONG, gobject.TYPE_STRING],
                self.scwProjects,
                self.on_tvwProjects_changed,
                True,
                False)
        """
        #create the ListStore and Treeview objects
        ls = gtk.ListStore(*column_types)
        tvw = gtk.TreeView(ls)
        #set columns
        for i in range(len(columns)):
            if column_types[i] != gtk.gdk.Pixbuf:
                #create text renderer
                tvwRendererText = gtk.CellRendererText()
                tvwRendererText.set_property('yalign', 0.0)
                if edit_cell_cb:
                    tvwRendererText.set_property('editable', True)
                    tvwRendererText.connect('edited', edit_cell_cb, (ls, i))
                if text_style == 'markup':
                    #markup text rendering
                    column = gtk.TreeViewColumn(columns[i], tvwRendererText, markup=i)
                else:
                    #default text rendering
                    column = gtk.TreeViewColumn(columns[i], tvwRendererText, text=i)
                if sortable_cols:
                    column.set_sort_column_id(i)
            else:
                #create pixbuf renderer
                tvwRendererPixbuf = gtk.CellRendererPixbuf()
                column = gtk.TreeViewColumn(columns[i], tvwRendererPixbuf, pixbuf=i)
            if resizeable_cols:
                column.set_resizable(True)
            tvw.append_column(column)
        #highlight rows
        if highlight_rows:
            tvw.set_rules_hint(True)
        #display it (add treeview to given widget)
        container.add(tvw)
        tvw.show()
        #selection object
        tvws = tvw.get_selection()
        #connect callback
        if changed_callback:
            tvws.connect('changed', changed_callback)
        #done
        return tvw, ls, tvws

    def setup_iconview(self, columns, column_types, container, changed_cb=None, activate_cb=None, text_style='text'):
        """ Create a ready-to-use (list based) iconview widget (GTK+2.6 and baove)
        Parameters:
            columns      : List of column names (should only be two - one for icon & one for description)
            column_types : List of variable types for each column
                           (eg. [gobject.TYPE_STRING, gobject.TYPE_LONG])
            container    : reference to widget that is to contain list,
                           almost always a scrolled window - gtk.ScrolledWindow()
            changed_cb   : the callback function for the "changed" TreeViewSelection signal
            activate_cb  : the callback function for the "changed" TreeViewSelection signal
            text_style   : 'text' for normail plain text,
                           'markup' for pango marked-up text
        Returns:
            Reference to IconView and ListStore widgets

        e.g. to create a four column (first two displayed, rest hidden) icon view...
            self.tvwProjects, self.lsProjects, self.tvwsProjects = self.setup_treeview(
                ['Picture', 'Desc'],
                [gtk.gdk.Pixbuf, gobject.TYPE_STRING, gobject.TYPE_LONG, gobject.TYPE_STRING],
                self.scwPictures,
                self.on_tvwsPictures_changed,
                None
                'text')
        """
        #create the ListStore and IconView objects
        ls = gtk.ListStore(*column_types)
        ivw = gtk.IconView(ls)
        #set columns
        for i in range(len(columns)):
            if column_types[i] != gtk.gdk.Pixbuf:
                #create text renderer
                tvwRendererText = gtk.CellRendererText()
                tvwRendererText.set_property('yalign', 0.0)
                if text_style == 'markup':
                    #markup text rendering
                    column = gtk.TreeViewColumn(columns[i], tvwRendererText, markup=i)
                    ivw.set_markup_column(i)
                else:
                    #default text rendering
                    column = gtk.TreeViewColumn(columns[i], tvwRendererText, text=i)
                    ivw.set_text_column(i)
            else:
                #create pixbuf renderer
                tvwRendererPixbuf = gtk.CellRendererPixbuf()
                column = gtk.TreeViewColumn(columns[i], tvwRendererPixbuf, pixbuf=i)
                ivw.set_pixbuf_column(i)
        #display it (add iconview to given widget)
        container.add(ivw)
        ivw.show()
        #connect callbacks
        if changed_cb:
            ivw.connect('selection_changed', changed_cb)
        if activate_cb:
            ivw.connect('item_activated', activate_cb)
        #done
        return ivw, ls

    def setup_combo_box(self, cbo, items, initial_item=None):
        """initialise a given ComboBox"""
        #create items list
        cbo.clear()
        ls = gtk.ListStore(gobject.TYPE_STRING)
        cbo.set_model(ls)
        cell = gtk.CellRendererText()
        cbo.pack_start(cell, True)
        cbo.add_attribute(cell, 'text', 0)
        #populate items
        if items:
            for item in items:
                cbo.append_text(item)
            #set initial item?
            if initial_item:
                cbo.set_active(initial_item)

    def setup_combo_box_entry(self, cboe, initial_text=None):
        """initialise a given ComboBoxEntry"""
        #create items list
        ls = gtk.ListStore(gobject.TYPE_STRING)
        cboe.set_model(ls)
        cboe.set_text_column(0)
        #populate with text?
        if initial_text:
            ls.append((initial_text, ))
            cboe.child.set_text(initial_text)

    def setup_menu(self, mnu_items, mnu_pixmaps, activate_cb):
        """returns a gtk menu object
        Parameters:
            mnu_items   : List of menu item names (either a string, a gtk stock item or '_sep_' for a separator)
            mnu_pixmaps : List of pixmaps (filename, a gtk stock icon or None)
            activate_cb : Callback function for menu activation
        Returns:
            Reference to the constructed gtk.Menu
        """
        mnu = gtk.Menu()
        for i in range(len(mnu_items)):
            #separator or menu item?
            if mnu_items[i] != '_sep_':
                #menu item
                mnuItem = gtk.ImageMenuItem(stock_id=mnu_items[i])
                img = gtk.Image()
                if mnu_pixmaps[i]:
                    if mnu_pixmaps[i][:4] == 'gtk-' and '.' not in mnu_pixmaps[i]:
                        #stock icon
                        img.set_from_stock(mnu_pixmaps[i], gtk.ICON_SIZE_MENU)
                    else:
                        #file icon
                        img.set_from_pixbuf(self.get_pixbuf(mnu_pixmaps[i], gtk.ICON_SIZE_MENU))
                    img.show()
                    mnuItem.set_image(img)
                mnuItem.connect('activate', activate_cb)
                mnuItem.set_name(mnu_items[i])
            else:
                #separator
                mnuItem = gtk.SeparatorMenuItem()
            #add item to menu
            mnuItem.show()
            mnu.append(mnuItem)
        #done
        return mnu

    def get_pixbuf(self, filename, width, height=None):
        """returns a scaled pixbuf from a given filename"""
        if height is None:
            height = width
        pb = gtk.gdk.pixbuf_new_from_file(os.path.join(os.path.abspath(sys.path[0]), 'pixmaps', filename))
        return pb.scale_simple(width, height, gtk.gdk.INTERP_HYPER)

    def show_msg_dialog(self, dlg_type=gtk.MESSAGE_INFO, dlg_buttons=gtk.BUTTONS_OK, msg=None):
        """display a MessageDialog"""
        mdlg = gtk.MessageDialog(type=dlg_type, buttons=dlg_buttons, message_format=msg)
        resp = mdlg.run()
        mdlg.destroy()
        #done
        return resp

    #map getitem to getattr
    __getitem__ = __getattr__
