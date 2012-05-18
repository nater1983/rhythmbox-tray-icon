Rhythmbox tray icon plugin
==========================

Restores the tray icon functionality from the 0.x series. Requires Rhythmbox 2.9+

Tray icon, has a green 'play' when a song is playing:

![Front end screenshot](https://github.com/mendhak/flickrsignature/raw/master/flkrme.png)
![Tray Icon](http://farm8.staticflickr.com/7232/7219610460_327356b800_o.png)


When you hover over the icon, it shows the playing song:

![Hover Icon](http://farm8.staticflickr.com/7102/7219610526_a2cd6e9f18_o.png)


Install Procedure
-----------------
Copy this folder into ~/.local/share/rhythmbox/plugins.  If you want to be specific, copy all the tray_* files over:

    cp /home/mendhak/Code/rhythmbox-tray-icon/tray*.* ~/.local/share/rhythmbox/plugins/

Start Rhythmbox.  Go to Edit > Plugins.

Find 'Tray Icon' in the plugins list and enable it.  A Rhythmbox icon appears in the notification area.


Uninstall Procedure
-----------------

To uninstall, remove the tray_* files from the plugins folder.

    rm ~/.local/share/rhythmbox/plugins/tray*.*


