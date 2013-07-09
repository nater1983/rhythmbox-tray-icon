#!/usr/bin/python
# coding=utf-8

from gi.repository import AppIndicator3 as AI
from gi.repository import Gtk, Gio, GLib
import os
import sys
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import traceback

class TrayIconUnity():
    playIcon = os.path.join(sys.path[0], "tray_playing.png")
    stopIcon = os.path.join(sys.path[0], "tray_stopped.png")


    APPNAME = "Rhythmbox Tray Icon"


    def quit(self, item):
        print "Quitting"
        try:
            session_bus = dbus.SessionBus()
            player = session_bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
            mplayeriface = dbus.Interface(player, dbus_interface='org.mpris.MediaPlayer2')
            mplayeriface.Quit()
            Gtk.main_quit()
        except:
            sys.exit()

    def next(self, item):
        print "Next"
        try:
            session_bus = dbus.SessionBus()
            player = session_bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
            mplayeriface = dbus.Interface(player, dbus_interface='org.mpris.MediaPlayer2.Player')
            mplayeriface.Next()
        except:
            pass

    def previous(self, item):
        print "Previous"
        try:
            session_bus = dbus.SessionBus()
            player = session_bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
            mplayeriface = dbus.Interface(player, dbus_interface='org.mpris.MediaPlayer2.Player')
            mplayeriface.Previous()
        except:
            pass

    def playpause(self, item):
        print "Play/Pause"
        try:
            session_bus = dbus.SessionBus()
            player = session_bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
            mplayeriface = dbus.Interface(player, dbus_interface='org.mpris.MediaPlayer2.Player')
            mplayeriface.PlayPause()
        except:
            pass

    def rate(self, item, *data):
        print "Setting rating to " + str(data[0])
        self.set_track_rating(data[0])

    def scroll(self, aai, ind, steps):
        pass
        #Not working due to this bug: https://bugs.launchpad.net/indicator-application/+bug/1075152
        #bus = dbus.SessionBus()
        #mplayer = bus.get_object('org.mpris.MediaPlayer2.rhythmbox', '/org/mpris/MediaPlayer2')
        #iface = dbus.Interface(mplayer, dbus.PROPERTIES_IFACE)
        #current_volume = iface.Get('org.mpris.MediaPlayer2.Player', 'Volume')
        #iface.Set('org.mpris.MediaPlayer2.Player', 'Volume', 0.5)



    def makemenu(self):
        print "Creating menu items"
        menu = Gtk.Menu()

        self.currentsong_menuitem = Gtk.MenuItem('')
        self.currentsong_menuitem.set_sensitive(False)
        self.currentsong_menuitem.show()

        self.rating_menuitem = Gtk.MenuItem('☆☆☆☆☆')
        self.rating_menuitem.show()

        submenu = Gtk.Menu()
        for i in [5,4,3,2,1,0]:
            starString = '★' * i + '☆' * (5-i)
            ratingsubmenuitem = Gtk.MenuItem(starString)
            ratingsubmenuitem.connect('activate', self.rate, i)
            ratingsubmenuitem.show()
            submenu.append(ratingsubmenuitem)

        self.rating_menuitem.set_submenu(submenu)

        playpause_item = Gtk.MenuItem('Play/Pause')
        playpause_item.connect('activate', self.playpause)
        playpause_item.show()


        next_item = Gtk.MenuItem('Next')
        next_item.connect('activate', self.next)
        next_item.show()

        prev_item = Gtk.MenuItem('Previous')
        prev_item.connect('activate', self.previous)
        prev_item.show()

        exit_item = Gtk.MenuItem('Quit')
        exit_item.connect('activate', self.quit)
        exit_item.show()

        menu.append(self.currentsong_menuitem)
        menu.append(self.rating_menuitem)
        menu.append(playpause_item)
        menu.append(next_item)
        menu.append(prev_item)
        menu.append(exit_item)
        menu.show()
        return menu

    def startapp(self):
        print "Starting app"
        self.ai = AI.Indicator.new(self.APPNAME, self.stopIcon, AI.IndicatorCategory.HARDWARE)
        self.ai.set_status(AI.IndicatorStatus.ACTIVE)
        self.ai.set_menu(self.makemenu())
        self.ai.connect("scroll-event", self.scroll)

        self.set_menu_values()
        Gtk.main()

    def set_menu_values(self):
        print "Setting menu values"
        if self.is_playing():
            self.ai.set_icon(self.playIcon)
        else:
            self.ai.set_icon(self.stopIcon)

        currentTrack = self.get_current_track()
        if currentTrack:
            self.currentsong_menuitem.set_label(self.get_current_track())

        rating = self.get_current_rating()
        if rating:
            starString = '★' * rating + '☆' * (5-rating)
            self.rating_menuitem.set_label(starString)

    def filter_cb(self, bus, message):
        print "Filter event raised"
        # the NameAcquired message comes through before match string gets applied
        # args = message.get_args_list()
        try:
            self.set_menu_values()
        except:
            print traceback.print_exc()

    def is_playing(self):
        try:
            bus = dbus.SessionBus()
            mplayer = bus.get_object('org.mpris.MediaPlayer2.rhythmbox', '/org/mpris/MediaPlayer2')
            iface = dbus.Interface(mplayer, dbus.PROPERTIES_IFACE)
            return iface.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus') == 'Playing'
        except:
            return False

    def get_current_track(self):
        try:
            bus = dbus.SessionBus()
            mplayer = bus.get_object('org.mpris.MediaPlayer2.rhythmbox', '/org/mpris/MediaPlayer2')
            iface = dbus.Interface(mplayer, dbus.PROPERTIES_IFACE)
            return iface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')[dbus.String(u'xesam:title')]
        except:
            return None

    def get_current_track_url(self):
        try:
            bus = dbus.SessionBus()
            mplayer = bus.get_object('org.mpris.MediaPlayer2.rhythmbox', '/org/mpris/MediaPlayer2')
            iface = dbus.Interface(mplayer, dbus.PROPERTIES_IFACE)
            return iface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')[dbus.String(u'xesam:url')]
        except:
            return None

    def get_current_rating(self):
        try:
            bus = dbus.SessionBus()
            mplayer = bus.get_object('org.mpris.MediaPlayer2.rhythmbox', '/org/mpris/MediaPlayer2')
            iface = dbus.Interface(mplayer, dbus.PROPERTIES_IFACE)
            return int(iface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')[dbus.String(u'xesam:userRating')] * 5)
        except:
            return None


    def set_track_rating(self, rating):
        """
        Sets the current song rating in Rhythmbox.
        """

        try:
            currentSongURI = self.get_current_track_url()

            if currentSongURI:

                busType = Gio.BusType.SESSION
                flags = 0
                ratingInterface = None

                proxy = Gio.DBusProxy.new_for_bus_sync(busType, flags, ratingInterface,
                                                       "org.gnome.Rhythmbox3",
                                                       "/org/gnome/Rhythmbox3/RhythmDB",
                                                       "org.gnome.Rhythmbox3.RhythmDB", None)

                variantRating = GLib.Variant("d", float(rating))
                proxy.SetEntryProperties("(sa{sv})", currentSongURI, {"rating": variantRating})
                self.set_menu_values()
        except:
                print traceback.print_exc()


DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
bus.add_match_string_non_blocking("type='signal',member='PropertiesChanged',path='/org/mpris/MediaPlayer2'")
tiu = TrayIconUnity()
bus.add_message_filter(tiu.filter_cb)

# sbus = dbus.SessionBus()
# sbus.add_match_string_non_blocking("type='method_call'")
# sbus.add_message_filter(tiu.filter_scroll)


tiu.startapp()
