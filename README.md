Rhythmbox tray icon plugin
==========================

Restores the tray icon functionality from the 0.x series. Requires Rhythmbox 2.9+

Tray icon, has a green 'play' when a song is playing.

![Tray Icon](http://farm8.staticflickr.com/7232/7219610460_327356b800_o.png)

You can rate the song, play/pause, go previous, go next, or quit.

Clicking directly on the tray icon will attempt to show the Rhythmbox window.

When you hover over the icon, it shows the playing song:

![Hover Icon](http://farm8.staticflickr.com/7102/7219610526_a2cd6e9f18_o.png)


Install Procedure
-----------------
Copy this folder into ~/.local/share/rhythmbox/plugins.  If you want to be specific, copy all the tray_* files over:

    cp /home/mendhak/Code/rhythmbox-tray-icon/tray*.* ~/.local/share/rhythmbox/plugins/

Start Rhythmbox.  Go to Edit > Plugins.

Find 'Tray Icon' in the plugins list and enable it.  A Rhythmbox icon appears in the notification area.

![Edit Plugins in Rhythmbox](http://farm6.staticflickr.com/5197/7219640336_a97b998f63_o.png)


Uninstall Procedure
-----------------

To uninstall, remove the tray_* files from the plugins folder.

    rm ~/.local/share/rhythmbox/plugins/tray*.*


