#!/usr/bin/python
import dbus
from gi.repository import Gio, GLib
import gtk
import traceback
import starhscale


class StatusIcon:

    star = None
    starValue = 0

    def __init__(self):
        self.statusicon = gtk.StatusIcon()
        self.statusicon.set_from_stock(gtk.STOCK_HOME)
        self.statusicon.connect("popup-menu", self.right_click_event)
        self.statusicon.set_tooltip("StatusIcon Example")

        window = gtk.Window()
        window.connect("destroy", lambda w: gtk.main_quit())
        #window.show_all()

    def get_song_uri(self):

        bus = dbus.SessionBus()
        proxy = bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
        properties_manager = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
        currentSongURI = str(properties_manager.Get("org.mpris.MediaPlayer2.Player","Metadata").get(dbus.String(u'xesam:url')))
        return currentSongURI

    def get_song_rating(self):
        bus = dbus.SessionBus()
        proxy = bus.get_object('org.mpris.MediaPlayer2.rhythmbox','/org/mpris/MediaPlayer2')
        properties_manager = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
        currentRating = int(float(properties_manager.Get
                    ('org.mpris.MediaPlayer2.Player','Metadata').get(dbus.String(u'xesam:userRating')))*5)

        if currentRating:
            return currentRating
        else:
            return 0

    def set_song_rating(self, rating):
            tb = ''
            try:
                #currentSongURI = shell.props.shell_player.get_playing_entry().get_playback_uri()
                currentSongURI = self.get_song_uri()

                bus_type = Gio.BusType.SESSION
                flags = 0
                iface_info = None


                proxy = Gio.DBusProxy.new_for_bus_sync(bus_type, flags, iface_info,
                                                       "org.gnome.Rhythmbox3",
                                                       "/org/gnome/Rhythmbox3/RhythmDB",
                                                       "org.gnome.Rhythmbox3.RhythmDB", None)

                vrating = GLib.Variant("d", float(rating))
                proxy.SetEntryProperties("(sa{sv})", currentSongURI, {"rating": vrating})
            except:
                tb = traceback.format_exc()
            finally:
                print tb

            return False


    def motion_notify_event(self, widget, event):
        if event.is_hint:
           x, y, state = event.window.get_pointer()
        else:
           x = event.x
           y = event.y

        self.star.check_for_new_stars(x-self.star.allocation.x)

    def click_notify_event(self, widget, event):
        event.x = event.x - self.star.allocation.x
        self.star.do_button_press_event(event)
        self.starValue = self.star.stars
        self.set_song_rating(self.starValue)


    def leave_notify_event(self, widget, event):
        self.star.set_value(self.starValue)

    def right_click_event(self, icon, button, time):
        menu = gtk.Menu()

        about = gtk.MenuItem("About")
        quit = gtk.MenuItem("Quit")

        ### MODIFIED PART!! ###

        item = gtk.MenuItem()


        ####gobject.type_register(starhscale.StarHScale)

        self.starValue =  self.get_song_rating()
        self.star = starhscale.StarHScale(5, self.starValue)

        item.add(self.star)
        item.connect("motion_notify_event", self.motion_notify_event)
        item.connect("button_press_event", self.click_notify_event)
        item.connect("leave_notify_event", self.leave_notify_event)


        style = item.get_style().copy()
        item.set_style(style)

        menu.append(item)
        #### END MODIFIED PART ####

        about.connect("activate", self.show_about_dialog)
        quit.connect("activate", gtk.main_quit)

        menu.append(about)
        menu.append(quit)
        menu.show_all()


        menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusicon)

    def show_about_dialog(self, widget):
        about_dialog = gtk.AboutDialog()

        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_name("StatusIcon Example")
        about_dialog.set_version("1.0")
        about_dialog.set_authors(["Andrew Steele"])

        about_dialog.run()
        about_dialog.destroy()

StatusIcon()
gtk.main()