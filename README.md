Rhythmbox tray icon plugin
==========================

A tray icon to control basic Rhythmbox features.

You can rate the track, play/pause, go previous, go next, or quit.

This is fork from [mendhak/rhythmbox-tray-icon](https://github.com/mendhak/rhythmbox-tray-icon).

![Tray Icon](https://user-images.githubusercontent.com/8698003/163804315-da04932c-dd32-493a-85fd-c93b09df040c.png)

Scroll up and down over the tray icon to adjust Rhythmbox's volume (doesn't work in Gnome 42).

Click on the tray icon to show or hide the Rhythmbox window.

The tray icon has a green 'play' overlay when a track is playing.


How to install
-----------------

To install, run these commands in a terminal window:

    git clone https://github.com/vantu5z/rhythmbox-tray-icon.git
    cd rhythmbox-tray-icon
    ./install.sh

To do it manually, download [ziped repo](https://github.com/vantu5z/rhythmbox-tray-icon/archive/refs/heads/master.zip) and extract its contents into ~/.local/share/rhythmbox/plugins/tray_icon.

Start Rhythmbox.  Go to Edit > Plugins.

Find 'Tray Icon' in the plugins list and enable it.  A Rhythmbox icon appears in the notification area.

![Edit Plugins in Rhythmbox](http://farm6.staticflickr.com/5197/7219640336_a97b998f63_o.png)


How to uninstall
-----------------

To uninstall, run this command in a terminal window:

    rm -r ~/.local/share/rhythmbox/plugins/tray_icon

It will remove the tray_icon folder from the plugins folder.

Dependencies
----------------

[xapp](https://github.com/linuxmint/xapp)

[gnome-shell-extension-appindicator](https://github.com/ubuntu/gnome-shell-extension-appindicator) (or similar, to enable tray icons in Gnome Shell)

In Arch Linux you can install them by:

    pacman -S xapp gnome-shell-extension-appindicator
