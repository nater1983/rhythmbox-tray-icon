#!/usr/bin/python
# coding=utf-8

from gi.repository import Gtk, Gdk, GdkPixbuf, Peas, GObject, RB
import os
import platform
import subprocess
import sys
from tray_icon_general import TrayIconGeneral


class TrayIcon(GObject.Object, Peas.Activatable):
    __gtype_name = 'TrayIconGeneral'
    object = GObject.property(type=GObject.Object)

    isUnity = False
    plugin = None

    def __init__(self):
        super(TrayIcon, self).__init__()

        if platform.dist()[0] == 'Ubuntu' and float(platform.dist()[1]) >= 13.04:
            self.isUnity = True

        print self.isUnity

    def do_activate(self):
        """
        Called when the plugin is activated
        """

        if not self.isUnity:
            self.plugin = TrayIconGeneral()
            self.plugin.do_activate()
        else:
            self.proc = subprocess.Popen(os.path.join(sys.path[0], "tray_icon_unity.py"))


    def do_deactivate(self):
        """
        Called when plugin is deactivated
        """
        if not self.isUnity:
            self.plugin.do_deactivate()
        else:
            if self.proc:
                self.proc.kill()