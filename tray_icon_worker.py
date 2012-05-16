#!/usr/bin/python
# coding=utf-8
import dbus
from gi.repository import Gio, GLib
import gtk
import os
import subprocess
import sys
import math
import gobject
import dbus.mainloop.glib
import glib

class StatusIcon:

    """
    A Python application which sits in the system tray and can control Rhythmbox.
    Features: previous, next, play/pause, quit
    Rate a song using the stars menu item
    Scrolling over the icon increases or decreases the volume.
    Mouseover the icon and it dispays a tooltip with the current song name.
    Changes Rhythmbox tray icon when a song is playing.
    """
    starValue = 0

    iconsPath = "/usr/share/icons/"
    rhythmboxIcon = iconsPath + "hicolor/32x32/apps/rhythmbox.png"
    #playIcon = iconsPath + "gnome/32x32/actions/media-playback-start.png"
    playIcon = os.path.join(sys.path[0], "tray_playing.png")

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
        """
        Method called when the mousewheel is scrolled over the icon. Changes the volume.
        """

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
        """
        Method called when the icon is left clicked. Launches rhythmbox.
        """
        if event.button == 1: # left button
            subprocess.call("rhythmbox")


    def GetSongURI(self):
        """
        Gets the file URI of the current song in Rhythmbox.
        """
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
        """
        Gets the current song's user rating from Rhythmbox.
        """
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
        """
        Sets the current song rating in Rhythmbox.
        """

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


    def OnPlayPauseClick(self, widget):
        """
        Method called when the playpause menu item is clicked. Toggles the play-pause state of Rhythmbox.
        """
        try:
            session_bus = dbus.SessionBus()
            player = session_bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
            playeriface = dbus.Interface(player, dbus_interface='org.mpris.MediaPlayer2.Player')
            playeriface.PlayPause()
        except:
            print "Unable to play/pause, are you sure Rhythmbox is running?"


    def OnNextClick(self, widget):
        """
        Method called when the next menu item is clicked.  Pays next song.
        """
        try:
            session_bus = dbus.SessionBus()
            player = session_bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
            playeriface = dbus.Interface(player, dbus_interface='org.mpris.MediaPlayer2.Player')
            playeriface.Next()
        except:
            print "Unable to go to next item, are you sure Rhythmbox is running?"

    def OnPreviousClick(self, widget):
        """
        Method called when the previous menu item is clicked. Plays previous song.
        """
        try:

            session_bus = dbus.SessionBus()
            player = session_bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
            playeriface = dbus.Interface(player, dbus_interface='org.mpris.MediaPlayer2.Player')
            playeriface.Previous()
        except:
            print "Unable to go to previous item, are you sure Rhythmbox is running?"

    def OnQuitClick(self, widget):
        """
        Method called when the quit menu item is clicked. Quits rhythmbox.
        """
        try:
            session_bus = dbus.SessionBus()
            player = session_bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
            mplayeriface = dbus.Interface(player, dbus_interface='org.mpris.MediaPlayer2')
            mplayeriface.Quit()
        except:
            sys.exit()

    def GetChosenStarsFromMousePosition(self, label, mouseX):
        """
        Calculates the number of chosen stars to show based on the mouse's X position
        """
        starWidth = int(label.get_layout().get_pixel_size()[0]/5)
        chosen = math.ceil((mouseX-label.allocation.x)/starWidth)
        if chosen <= 0:
            chosen = 0

        if chosen >= 5:
            chosen = 5

        return chosen

    def OnStarClick(self, widget, event):
        """
        Method called when stars are clicked on. Determines chosen stars and sets song rating.
        """
        label = widget.get_children()[0]
        self.starValue = self.GetChosenStarsFromMousePosition(label, event.x)
        self.SetSongRating(self.starValue)

    def OnStarMouseOut(self, widget, event):
        """
        Method called when mouse leaves the rating stars. Resets stars to original value.
        """
        label = widget.get_children()[0]
        label.set_markup(self.GetStarsMarkup(self.starValue, 5))


    def OnStarMouseOver(self, widget, event):
        """
        Method called when mouse hovers over the rating stars. Shows filled stars as mouse hovers.
        """
        label = widget.get_children()[0]
        label.set_markup(self.GetStarsMarkup(self.GetChosenStarsFromMousePosition(label,event.x), 5))

    def GetStarsMarkup(self, filledStars, totalStars):
        """
        Gets the Pango Markup for the star rating label
        """

        if filledStars is None or filledStars <= 0:
                    filledStars = 0

        if filledStars >= totalStars:
            filledStars = totalStars

        filledStars = int(math.ceil(filledStars))
        totalStars = int(totalStars)

        starString = '★' * filledStars + '☆' * (totalStars-filledStars)
        return "<span size='x-large'>" + starString + "</span>"


    def OnShowPopupMenu(self, icon, button, time):
        """
        Called when the icon is right clicked, displays the menu
        """
        menu = gtk.Menu()

        playpause = gtk.MenuItem("Play/Pause")
        next = gtk.MenuItem("Next")
        prev = gtk.MenuItem("Prev")
        quit = gtk.MenuItem("Quit")


        starItem = self.GetRatingStar()
        if starItem:
            menu.append(starItem)

        playpause.connect("activate", self.OnPlayPauseClick)
        next.connect("activate", self.OnNextClick)
        prev.connect("activate", self.OnPreviousClick)
        quit.connect("activate", self.OnQuitClick)

        menu.append(playpause)
        menu.append(next)
        menu.append(prev)
        menu.append(quit)
        menu.show_all()

        menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusicon)

    def GetRatingStar(self):
        """ Gets a gtk.MenuItem with the current song's ratings in filled stars """
        starItem = gtk.MenuItem(self.GetStarsMarkup(0,5))
        self.starValue =  self.GetSongRating()
        label = starItem.get_children()[0]
        label.set_markup(self.GetStarsMarkup(self.starValue,5))

        starItem.connect("motion_notify_event", self.OnStarMouseOver)
        starItem.connect("button_press_event", self.OnStarClick)
        starItem.connect("leave_notify_event", self.OnStarMouseOut)

        if self.starValue >= 0:
            return starItem
        else:
            return None



    def SetPlayingIcon(self, isPlaying):
        """
        Sets the current icon to rhythmbox or a playing icon
        """
        if isPlaying:
            self.statusicon.set_from_file(self.playIcon)
        else:
            self.statusicon.set_from_file(self.rhythmboxIcon)

    def SetTooltip(self, message):
        """ Sets the tooltip of the icon """
        self.statusicon.set_tooltip(message)



def OnPlaybackStatusChanged (sender, properties, sig):
    """
    Reads the current song title and sets the icon tooltip.
    Reads the PlaybackStatus and changes the icon depending on play/pause status
    """

    if properties and "Metadata" in properties:
        if "xesam:title" in properties["Metadata"]:
            s.SetTooltip(properties["Metadata"]["xesam:title"])

    if properties and "PlaybackStatus" in properties:
        if properties["PlaybackStatus"] == "Playing":
            s.SetPlayingIcon(True)
        else:
            s.SetPlayingIcon(False)
            s.SetTooltip("")



def SetupPlaybackStatusListener():
    """
        Sets up a playback status listener from Rhythmbox, which runs in a glib.MainLoop().
        Calls OnPlaybackStatusChanged when the status changes
    """
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




gobject.timeout_add(1000, SetupPlaybackStatusListener)

s = StatusIcon()
gtk.main()


