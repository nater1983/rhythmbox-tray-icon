Rhythmbox tray icon plugin
==========================

A tray icon to control basic Rhythmbox features. Requires Rhythmbox 2.9+

You can rate the track, play/pause, go previous, go next, or quit.

![Tray Icon](http://farm8.staticflickr.com/7232/7219610460_327356b800_o.png)

Scroll up and down over the tray icon to adjust Rhythmbox's volume.

Clicking directly on the tray icon will attempt to show the Rhythmbox window.

The tray icon has a green 'play' overlay when a track is playing.

When you hover over the icon, it shows the playing track:

![Hover Icon](http://farm8.staticflickr.com/7102/7219610526_a2cd6e9f18_o.png)


How to install
-----------------

To install, run these commands in a terminal window:

    wget https://github.com/mendhak/rhythmbox-tray-icon/raw/master/rhythmbox-tray-icon.zip
    unzip -u rhythmbox-tray-icon.zip -d ~/.local/share/rhythmbox/plugins

To do it manually, download [rhythmbox-tray-icon.zip](https://github.com/mendhak/rhythmbox-tray-icon/raw/master/rhythmbox-tray-icon.zip) and extract its contents into ~/.local/share/rhythmbox/plugins.

Start Rhythmbox.  Go to Edit > Plugins.

Find 'Tray Icon' in the plugins list and enable it.  A Rhythmbox icon appears in the notification area.

![Edit Plugins in Rhythmbox](http://farm6.staticflickr.com/5197/7219640336_a97b998f63_o.png)


How to uninstall
-----------------

To uninstall, run this command in a terminal window:

    rm ~/.local/share/rhythmbox/plugins/tray_*.*

It will remove the tray_* files from the plugins folder.

**Notes**

There is no .deb package yet.

Heavily modified from [palfrey's original](https://github.com/palfrey/rhythmbox-tray-icon) plugin.
