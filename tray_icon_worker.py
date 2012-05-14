#!/usr/bin/python
import dbus
from gi.repository import Gio, GLib
import gtk
import subprocess
import sys

import tray_icon_starwidget

import dbus.mainloop.glib
import glib

class StatusIcon:

    star = None
    starValue = 0

    iconsPath = "/usr/share/icons/"
    rhythmboxIcon = iconsPath + "hicolor/32x32/apps/rhythmbox.png"
    playIcon = iconsPath + "gnome/32x32/actions/media-playback-start.png"

    def __init__(self):

        self.statusicon = gtk.StatusIcon()
        #self.statusicon.set_from_stock(gtk.STOCK_MEDIA_PLAY)
        self.statusicon.set_from_file(self.rhythmboxIcon)
        self.statusicon.connect("popup-menu", self.OnShowPopupMenu)
        self.statusicon.connect("button-press-event", self.OnIconClick)
        self.statusicon.connect("scroll-event", self.OnIconScroll)

        window = gtk.Window()
        window.connect("destroy", lambda w: gtk.main_quit())
        #window.show_all()

    def OnIconScroll(self, widget, event):

        if event.direction == 0:
            session_bus = dbus.SessionBus()
            player = session_bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
            dbuspropiface = dbus.Interface(player,dbus_interface='org.freedesktop.DBus.Properties')
            vol=dbuspropiface.Get("org.mpris.MediaPlayer2.Player","Volume")
            vol+=(0.1*vol)
            dbuspropiface.Set("org.mpris.MediaPlayer2.Player","Volume",vol)
        elif event.direction == 1:
            session_bus = dbus.SessionBus()
            player = session_bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
            dbuspropiface = dbus.Interface(player,dbus_interface='org.freedesktop.DBus.Properties')
            vol=dbuspropiface.Get("org.mpris.MediaPlayer2.Player","Volume")
            vol-=(0.1*vol)
            dbuspropiface.Set("org.mpris.MediaPlayer2.Player","Volume",vol)

    def OnIconClick(self, icon, event, data = None):
        if event.button == 1: # left button
            subprocess.call("rhythmbox")


    def GetSongURI(self):
        try:
            bus = dbus.SessionBus()
            proxy = bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
            properties_manager = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
            currentSongURI = str(properties_manager
                        .Get("org.mpris.MediaPlayer2.Player","Metadata").get(dbus.String(u'xesam:url')))
            return currentSongURI
        except:
            return None

    def GetSongRating(self):
        try:
            bus = dbus.SessionBus()
            proxy = bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
            properties_manager = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
            currentRating = int(float(properties_manager
                        .Get('org.mpris.MediaPlayer2.Player','Metadata').get(dbus.String(u'xesam:userRating')))*5)
        except:
            currentRating = -1

        if currentRating:
            return currentRating
        else:
            return 0

    def SetSongRating(self, rating):

            try:
                currentSongURI = self.GetSongURI()

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
            except:
                print "Failed to set a rating"


    def OnRatingMouseOver(self, widget, event):
        # User moving over the stars, highlight stars accordingly
        if event.is_hint:
           x, y, state = event.window.get_pointer()
        else:
           x = event.x
           y = event.y

        self.star.check_for_new_stars(x-self.star.allocation.x)

    def OnRatingClick(self, widget, event):
        # User clicked on a star. Set the rating.
        event.x = event.x - self.star.allocation.x
        self.star.do_button_press_event(event)

        self.starValue = self.star.stars
        self.SetSongRating(self.starValue)

    def OnRatingMouseOut(self, widget, event):
        # Mouse left the star area, restore to original rating
        self.star.set_value(self.starValue)

    def OnPlayPauseClick(self, widget):
        try:
            session_bus = dbus.SessionBus()
            player = session_bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
            playeriface = dbus.Interface(player, dbus_interface='org.mpris.MediaPlayer2.Player')
            playeriface.PlayPause()
        except:
            print "Unable to play/pause, are you sure Rhythmbox is running?"


    def OnNextClick(self, widget):
        try:
            session_bus = dbus.SessionBus()
            player = session_bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
            playeriface = dbus.Interface(player, dbus_interface='org.mpris.MediaPlayer2.Player')
            playeriface.Next()
        except:
            print "Unable to go to next item, are you sure Rhythmbox is running?"

    def OnPreviousClick(self, widget):
        try:

            session_bus = dbus.SessionBus()
            player = session_bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
            playeriface = dbus.Interface(player, dbus_interface='org.mpris.MediaPlayer2.Player')
            playeriface.Previous()
        except:
            print "Unable to go to previous item, are you sure Rhythmbox is running?"

    def OnQuitClick(self, widget):
        try:
            session_bus = dbus.SessionBus()
            player = session_bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
            mplayeriface = dbus.Interface(player, dbus_interface='org.mpris.MediaPlayer2')
            mplayeriface.Quit()
        except:
            sys.exit()


    def OnShowPopupMenu(self, icon, button, time):
        menu = gtk.Menu()

        playpause = gtk.MenuItem("Play/Pause")
        next = gtk.MenuItem("Next")
        prev = gtk.MenuItem("Prev")
        quit = gtk.MenuItem("Quit")

        ratingItem = self.GetRatingWidget()
        if ratingItem:
            menu.append(ratingItem)

        playpause.connect("activate", self.OnPlayPauseClick)
        next.connect("activate", self.OnNextClick)
        prev.connect("activate", self.OnPreviousClick)
        quit.connect("activate", self.OnQuitClick)

        menu.append(playpause)
        menu.append(next)
        menu.append(prev)
        menu.append(quit)
        menu.show_all()

        #TODO, get DBus listener working
        #self.SetupPlaybackStatusListener()

        menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusicon)

    def GetRatingWidget(self):
        ratingItem = gtk.MenuItem()
        self.starValue =  self.GetSongRating()

        if self.starValue >= 0:
            self.star = tray_icon_starwidget.StarHScale(5, self.starValue)

            ratingItem.add(self.star)
            ratingItem.connect("motion_notify_event", self.OnRatingMouseOver)
            ratingItem.connect("button_press_event", self.OnRatingClick)
            ratingItem.connect("leave_notify_event", self.OnRatingMouseOut)

            style = ratingItem.get_style().copy()
            ratingItem.set_style(style)

            return ratingItem
        else:
            return None

    def SetPlayingIcon(self, isPlaying):
        print isPlaying



def OnPlaybackStatusChanged (sender, properties, sig):
    if properties and "PlaybackStatus" in properties:
        if properties["PlaybackStatus"] == "Playing":
            s.SetPlayingIcon(True)
        else:
            s.SetPlayingIcon(False)


def SetupPlaybackStatusListener():
    try:
        print "Setup Playback Status Listener"
        dbus.mainloop.glib.DBusGMainLoop (set_as_default = True)

        bus = dbus.SessionBus ()

        proxy = bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
        player = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
        player.connect_to_signal("PropertiesChanged", OnPlaybackStatusChanged)

        mainloop = glib.MainLoop ()
        mainloop.run ()
    except:
        print "Status Listener error"
        print sys.exc_info()
        pass

    return False



import gobject
gobject.timeout_add(1000, SetupPlaybackStatusListener)

s = StatusIcon()
gtk.main()


