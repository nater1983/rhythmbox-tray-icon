# Rhythmbox: Edit > Plugins > Python Console enabled
# Play a song
# Open Rhythmbox Python Console
# execfile('/path/to/rate.py')
import sys
import rb
from gi.repository import Gtk, Gdk
import traceback

def rateThread(rating):
		tb = ''
		try:
			currentSongURI = shell.props.shell_player.get_playing_entry().get_playback_uri()
			print "Setting rating for " + currentSongURI

			from gi.repository import GLib, Gio
			bus_type = Gio.BusType.SESSION
			flags = 0
			iface_info = None

			print "Get Proxy"
			proxy = Gio.DBusProxy.new_for_bus_sync(bus_type, flags, iface_info,
												   "org.gnome.Rhythmbox3",
												   "/org/gnome/Rhythmbox3/RhythmDB",
												   "org.gnome.Rhythmbox3.RhythmDB", None)

			print "Got proxy"
			rating = float(rating)
			vrating = GLib.Variant("d", rating)
			print "SetEntryProperties"
			proxy.SetEntryProperties("(sa{sv})", currentSongURI, {"rating": vrating})
			print "Done"
		except:
			tb = traceback.format_exc()
		finally:
			print tb

		return False

def rate():
		if shell.props.shell_player.get_playing_entry():
			Gdk.threads_add_idle(100, rateThread, 3)

rate()