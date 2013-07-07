#!/usr/bin/python
# coding=utf-8

from gi.repository import AppIndicator3 as AI
from gi.repository import Gtk
import os
import sys
import dbus
from dbus.mainloop.glib import DBusGMainLoop

playIcon = os.path.join(sys.path[0], "tray_playing.png")
stopIcon = os.path.join(sys.path[0], "tray_stopped.png")

APPNAME = "Rhythmbox Tray Icon"


def sayhello(item):
    print "menu item selected"

def scroll(aai, ind, steps):
    print "hello" # doesn't print anything

def makemenu():
    ' Set up the menu '
    menu = Gtk.Menu()
    check_item = Gtk.MenuItem('Check')
    exit_item = Gtk.MenuItem('Quit')
    check_item.connect('activate', sayhello)
    check_item.show()
    exit_item.connect('activate', Gtk.main_quit)
    exit_item.show()
    menu.append(check_item)
    menu.append(exit_item)
    menu.show()
    return menu

def startapp():
    ai = AI.Indicator.new(APPNAME, stopIcon, AI.IndicatorCategory.HARDWARE)
    ai.set_status(AI.IndicatorStatus.ACTIVE)
    ai.set_menu(makemenu())
    ai.connect("scroll-event", scroll)
    Gtk.main()

def filter_cb(bus, message):
    # the NameAcquired message comes through before match string gets applied
    args = message.get_args_list()
    #print args
    try:
        fulldata = args[1]
        if dbus.String(u'PlaybackStatus') in fulldata:
            print fulldata[dbus.String(u'PlaybackStatus')]
        if dbus.String(u'Metadata') in fulldata:
            metadata = fulldata[dbus.String(u'Metadata')]
            if dbus.String(u'xesam:title') in metadata:
                print metadata[dbus.String(u'xesam:title')]
            if dbus.String(u'xesam:userRating') in metadata:
                print metadata[dbus.String(u'xesam:userRating')]
    except:
        pass

    # args are
    # (app_name, notification_id, icon, summary, body, actions, hints, timeout)
    #print("Notification from app '%s'" % args[0])



DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()

bus.add_match_string_non_blocking(
    "type='signal',member='PropertiesChanged'")
bus.add_message_filter(filter_cb)
startapp()
