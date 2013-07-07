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
        self.check_item = Gtk.MenuItem('Check')
        self.check_item.set_sensitive(False)
        exit_item = Gtk.MenuItem('Quit')
        self.check_item.connect('activate', self.sayhello)
        self.check_item.show()
        exit_item.connect('activate', Gtk.main_quit)
        exit_item.show()
        menu.append(self.check_item)
        menu.append(exit_item)
        menu.show()
        return menu

    def startapp(self):
        self.ai = AI.Indicator.new(self.APPNAME, self.stopIcon, AI.IndicatorCategory.HARDWARE)
        self.ai.set_status(AI.IndicatorStatus.ACTIVE)
        self.ai.set_menu(self.makemenu())
        self.ai.connect("scroll-event", self.scroll)
        Gtk.main()

    def filter_cb(self, bus, message):
        # the NameAcquired message comes through before match string gets applied
        args = message.get_args_list()
        #print args
        try:
            if len(args) < 2:
                return
            fulldata = args[1]
            if dbus.String(u'PlaybackStatus') in fulldata:
                playing = fulldata[dbus.String(u'PlaybackStatus')]
                if playing == 'Playing':
                    self.ai.set_icon(self.playIcon)
                else:
                    self.ai.set_icon(self.stopIcon)

            if dbus.String(u'Metadata') in fulldata:
                metadata = fulldata[dbus.String(u'Metadata')]
                if dbus.String(u'xesam:title') in metadata:
                    print metadata[dbus.String(u'xesam:title')]
                    self.check_item.set_label(metadata[dbus.String(u'xesam:title')])
                if dbus.String(u'xesam:userRating') in metadata:
                    print metadata[dbus.String(u'xesam:userRating')]
        except:
            print traceback.print_exc()

        # args are
        # (app_name, notification_id, icon, summary, body, actions, hints, timeout)
        #print("Notification from app '%s'" % args[0])



DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()

bus.add_match_string_non_blocking(
    "type='signal',member='PropertiesChanged'")
tiu = TrayIconUnity()
bus.add_message_filter(tiu.filter_cb)
tiu.startapp()
