#!/usr/bin/python
# coding=utf-8

from gi.repository import AppIndicator3 as AI
from gi.repository import Gtk
import os
import sys
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import traceback

class TrayIconUnity():
    playIcon = os.path.join(sys.path[0], "tray_playing.png")
    stopIcon = os.path.join(sys.path[0], "tray_stopped.png")


    APPNAME = "Rhythmbox Tray Icon"


    def sayhello(self, item):
        print "menu item selected"


    def scroll(self, aai, ind, steps):
        print "hello" # doesn't print anything

    def makemenu(self):
        ' Set up the menu '
        menu = Gtk.Menu()

        self.currentsong_menuitem = Gtk.MenuItem('')
        self.currentsong_menuitem.set_sensitive(False)
        self.currentsong_menuitem.connect('activate', self.sayhello)
        self.currentsong_menuitem.show()

        self.rating_menuitem = Gtk.MenuItem('☆☆☆☆☆')
        self.rating_menuitem.show()

        submenu = Gtk.Menu()
        for i in [5,4,3,2,1,0]:
            starString = '★' * i + '☆' * (5-i)
            ratingsubmenuitem = Gtk.MenuItem(starString)
            ratingsubmenuitem.show()
            submenu.append(ratingsubmenuitem)

        self.rating_menuitem.set_submenu(submenu)



        exit_item = Gtk.MenuItem('Quit')
        exit_item.connect('activate', Gtk.main_quit)
        exit_item.show()

        menu.append(self.currentsong_menuitem)
        menu.append(self.rating_menuitem)
        menu.append(exit_item)
        menu.show()
        return menu

    def startapp(self):

        self.ai = AI.Indicator.new(self.APPNAME, self.stopIcon, AI.IndicatorCategory.HARDWARE)
        self.ai.set_status(AI.IndicatorStatus.ACTIVE)
        self.ai.set_menu(self.makemenu())
        self.ai.connect("scroll-event", self.scroll)

        self.set_menu_values()
        Gtk.main()

    def set_menu_values(self):
        if self.is_playing():
            self.ai.set_icon(self.playIcon)
        else:
            self.ai.set_icon(self.stopIcon)

        self.currentsong_menuitem.set_label(self.get_current_track())

        rating = self.get_current_rating()
        starString = '★' * rating + '☆' * (5-rating)
        self.rating_menuitem.set_label(starString)

    def filter_cb(self, bus, message):
        # the NameAcquired message comes through before match string gets applied
        args = message.get_args_list()
        print args
        try:
            self.set_menu_values()
        except:
            print traceback.print_exc()


    def is_playing(self):
        bus = dbus.SessionBus()
        mplayer = bus.get_object('org.mpris.MediaPlayer2.rhythmbox', '/org/mpris/MediaPlayer2')
        iface = dbus.Interface(mplayer, dbus.PROPERTIES_IFACE)
        return iface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus') == 'Playing'

    def get_current_track(self):
        bus = dbus.SessionBus()
        mplayer = bus.get_object('org.mpris.MediaPlayer2.rhythmbox', '/org/mpris/MediaPlayer2')
        iface = dbus.Interface(mplayer, dbus.PROPERTIES_IFACE)
        return iface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')[dbus.String(u'xesam:title')]

    def get_current_rating(self):
        bus = dbus.SessionBus()
        mplayer = bus.get_object('org.mpris.MediaPlayer2.rhythmbox', '/org/mpris/MediaPlayer2')
        iface = dbus.Interface(mplayer, dbus.PROPERTIES_IFACE)
        return int(iface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')[dbus.String(u'xesam:userRating')] * 5)


DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()

bus.add_match_string_non_blocking("type='signal',member='PropertiesChanged',path='/org/mpris/MediaPlayer2'")
tiu = TrayIconUnity()
bus.add_message_filter(tiu.filter_cb)

tiu.startapp()
