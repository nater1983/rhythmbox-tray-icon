#!/usr/bin/python3
# coding=utf-8

import gi
gi.require_version('XApp', '1.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Peas, GObject, RB, XApp
import os
import sys
import math


class TrayIcon(GObject.Object, Peas.Activatable):

    __gtype_name = 'TrayIcon'
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        super(TrayIcon, self).__init__()

        # tray icons
        self.rhythmbox_icon = os.path.join(sys.path[0], "tray_stopped.png")
        self.play_icon = os.path.join(sys.path[0], "tray_playing.png")

    def toggle_player_visibility(self, *args):
        """
        Toggles visibility of Rhythmbox player
        """
        if self.wind.get_visible():
            self.wind.hide()
        else:
            self.wind.show()
            self.wind.present()

    def hide_on_delete(self, widget, event):
        """
        Hide Rhythmbox on window close.
        """
        self.wind.hide()
        return True # don't actually delete

    def on_playing_changed(self, player, playing):
        """
        Sets icon and tooltip when playing status changes
        """
        if playing:
            self.icon.set_icon_name(self.play_icon)
            current_entry = self.player.get_playing_entry()
            self.set_tooltip_text(
                current_entry.get_string(RB.RhythmDBPropType.ARTIST) +
                " - " + current_entry.get_string(RB.RhythmDBPropType.TITLE))
        else:
            self.icon.set_icon_name(self.rhythmbox_icon)
            self.set_tooltip_text()

        self.status_win.set_image()
        self.status_win.update_play_button_image(playing)
        self.status_win.update_items()

    def set_tooltip_text(self, message=""):
        """
        Sets tooltip to given message
        """
        prepend = ""
        info = "(Scroll = volume, click = visibility, middle click = next)"
        if message:
            prepend = "\r\n"
        tooltip_text = message + prepend + info
        self.icon.set_tooltip_text(tooltip_text)

    def do_activate(self):
        """
        Called when the plugin is activated
        """
        self.shell = self.object
        self.player = self.shell.props.shell_player
        self.wind = self.shell.get_property("window")

        self.status_win = StatusWindow(self.shell)

        self.icon = XApp.StatusIcon()
        self.icon.set_icon_name(self.rhythmbox_icon)
        self.icon.connect("scroll-event", self.on_scroll)
        self.icon.connect("button-press-event", self.on_btn_press)
        self.player.connect("playing-changed", self.on_playing_changed)
        self.wind.connect("delete-event", self.hide_on_delete)

        self.set_tooltip_text()

    def on_btn_press(self, status_icon, x, y, button, time, panel_position):
        """
        Handle mouse buttons press.
        """
        if button == 1:    # left button
            self.toggle_player_visibility()
        elif button == 2:  # middle button
            self.player.do_next()
        elif button == 3:  # right button
            self.status_win.popup(x, y)

    def on_scroll(self, status_icon, amount, direction, time):
        """
        Lowers or raises Rhythmbox's volume
        """
        vol = round(self.player.get_volume()[1],1)

        if direction == XApp.ScrollDirection.UP:
            vol += 0.1
        elif direction == XApp.ScrollDirection.DOWN:
            vol -= 0.1
        # correct vol to span: 0 <= vol <= 1
        vol = 0 if vol < 0 else 1 if vol > 1 else vol

        self.player.set_volume(vol)

    def do_deactivate(self):
        """
        Called when plugin is deactivated
        """
        self.icon.set_visible(False)
        del self.icon


class StatusWindow(Gtk.Window):

    def __init__(self, shell):
        Gtk.Window.__init__(self)
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_keep_above(True)

        self.icon_theme = Gtk.IconTheme.get_default()

        self.shell = shell
        self.player = self.shell.props.shell_player
        self.db = self.shell.props.db

        self.album_image = Gtk.Image()
        self.album_image.set_size_request(70, 70)

        self.title = Gtk.Label("Title")
        self.album = Gtk.Label("Album")
        self.artist = Gtk.Label("Artist")

        # pack Label to EventBox to catch motion event
        rating_event_box = Gtk.EventBox()
        self.rating = Gtk.Label()
        rating_event_box.add(self.rating)
        rating_event_box.set_events(Gdk.EventMask.POINTER_MOTION_MASK)
        rating_event_box.connect("motion_notify_event", self.on_star_mouseover)
        rating_event_box.connect("button_press_event", self.on_star_click)
        rating_event_box.connect("leave_notify_event", self.on_star_mouseout)
        self.star_value = -1

        self.play_pause_btn = Gtk.Button()
        self.update_play_button_image(False)
        self.next_btn = Gtk.Button()
        self.set_button_icon(self.next_btn, "media-skip-forward", 24, _("Next"))
        self.prev_btn = Gtk.Button()
        self.set_button_icon(self.prev_btn,
                             "media-skip-backward", 24, _("Previous"))
        self.play_pause_btn.connect("clicked", self.play)
        self.next_btn.connect("clicked", self.next)
        self.prev_btn.connect("clicked", self.previous)
        box = Gtk.Box(halign=Gtk.Align.CENTER, spacing=5)
        box.add(self.prev_btn)
        box.add(self.play_pause_btn)
        box.add(self.next_btn)

        quit_btn = Gtk.Button()
        self.set_button_icon(quit_btn, "gnome-logout", 22, _("Quit Rhythmbox"))
        quit_btn.connect("clicked", self.quit)

        grid = Gtk.Grid(column_spacing=5, row_spacing=5)
        # attach(child, left, top, width, height)
        grid.attach(self.album_image, 0, 0, 1, 3)
        grid.attach(self.title, 1, 0, 1, 1)
        grid.attach(self.album, 1, 1, 1, 1)
        grid.attach(self.artist, 1, 2, 1, 1)
        grid.attach(rating_event_box, 0, 3, 1, 1)
        grid.attach(box, 1, 3, 1, 1)
        grid.attach(quit_btn, 2, 0, 1, 1)

        self.add(grid)

        self.player.get_property("player").connect("image", self.set_image)
        self.connect("focus-out-event", self.focus_changed)
        self.connect("draw", self.on_draw)

    def focus_changed(self, window, widget):
        """
        Hide window on lose focus.
        """
        self.hide()

    def set_image(self, player=None, stream_data=None, image=None):
        """
        Set album image.
        """
        if image is None:
            image = self.icon_theme.load_icon('image-missing', 64, 0)
        self.album_image.set_from_pixbuf(
                image.scale_simple(70, 70, GdkPixbuf.InterpType.BILINEAR))

    def set_button_icon(self, widget, icon_name, size, tooltip=""):
        """
        Set button icon and tooltip.
        """
        widget.set_image(Gtk.Image.new_from_pixbuf(
            self.icon_theme.load_icon(icon_name, size, 0)))
        widget.set_tooltip_text(tooltip)

    def popup(self, x, y):
        """
        Show window.
        """
        # remember icon position
        self.x_pos = x
        self.y_pos = y
        self.update_items()
        self.show_all()

    def update_items(self):
        """
        Update window items (song info).
        """
        if not self.get_visible():
            return

        # updates title menu item with the current song's info.
        current_entry = self.player.get_playing_entry()
        if current_entry is not None:
            self.artist.set_text(
                current_entry.get_string(RB.RhythmDBPropType.ARTIST))
            self.album.set_text(
                current_entry.get_string(RB.RhythmDBPropType.ALBUM))
            self.title.set_text(
                current_entry.get_string(RB.RhythmDBPropType.TITLE))
        else:
            self.artist.set_text(_("Artist"))
            self.album.set_text(_("Album"))
            self.title.set_text(_("Title"))

        # update stars menu with the current song's ratings in filled stars
        self.star_value = self.get_song_rating()
        self.rating.set_markup(self.get_stars_markup(self.star_value, 5))

        # shrink window
        self.resize(50, 50)

    def on_draw(self, widget, cr):
        """
        Handle "draw" event. Try to center window on icon position.
        Prevent overlap to side screen.
        """
        gdk_win = self.get_window()
        if gdk_win is not None:
            monitor = Gdk.Display.get_default().get_monitor_at_window(gdk_win)
            scr_width = monitor.get_workarea().width
            if scr_width < (self.x_pos + self.get_size().width / 2):
                self.move(scr_width - self.get_size().width, self.y_pos)
            else:
                self.move(self.x_pos - self.get_size().width / 2, self.y_pos)

    def get_song_rating(self):
        """
        Gets the current song's user rating from Rhythmbox.
        """
        current_entry = self.player.get_playing_entry()

        if current_entry:
            return int(current_entry.get_double(RB.RhythmDBPropType.RATING))
        else:
            return -1

    def on_star_click(self, widget, event):
        """
        Method called when stars are clicked on.
        Determines chosen stars and sets song rating.
        """
        if self.star_value < 0:
            return
        self.star_value = self.get_chosen_stars(self.rating, event.x)
        self.set_song_rating(self.star_value)

    def set_song_rating(self, rating):
        """
        Sets the current song rating in Rhythmbox.
        """
        current_entry = self.player.get_playing_entry()
        self.db.entry_set(current_entry, RB.RhythmDBPropType.RATING, rating)

    def get_chosen_stars(self, label, mouseX):
        """
        Calculates the number of chosen stars to show.
        Based on the mouse's X position.
        """
        star_width = int(label.get_layout().get_pixel_size()[0]/5)
        if star_width == 0:
            return 0
        chosen = math.ceil((mouseX-label.get_layout_offsets()[0])/star_width)
        # correct chosen to span: 0 <= vol <= 5
        chosen = 0 if chosen < 0 else 5 if chosen > 5 else chosen

        return chosen

    def on_star_mouseout(self, widget, event):
        """
        Method called when mouse leaves the rating stars.
        Resets stars to original value.
        """
        self.rating.set_markup(self.get_stars_markup(self.star_value, 5))

    def on_star_mouseover(self, widget, event):
        """
        Method called when mouse hovers over the rating stars.
        Shows filled stars as mouse hovers.
        """
        if self.star_value < 0:
            return
        chosen_stars = self.get_chosen_stars(self.rating, event.x)
        self.rating.set_markup(self.get_stars_markup(chosen_stars, 5))

    def get_stars_markup(self, filled_stars, total_stars):
        """
        Gets the Pango Markup for the star rating label
        """
        if filled_stars is None or filled_stars < 0:
            return ""

        if filled_stars >= total_stars:
            filled_stars = total_stars

        filled_stars = int(math.ceil(filled_stars))
        total_stars = int(total_stars)

        starString = '★' * filled_stars + '☆' * (total_stars-filled_stars)
        return ("<span size='x-large' foreground='yellow'>" +
                starString + "</span>")

    def play(self, widget):
        """
        Starts playing
        """
        self.player.playpause()

    def update_play_button_image(self, playing):
        """
        Update play button icon and tooltip depending on playing status.
        """
        if playing:
            icon_name = "media-pause"
            tooltip = _("Pause")
        else:
            icon_name = "media-play"
            tooltip = _("Play")
        self.set_button_icon(self.play_pause_btn, icon_name, 32, tooltip)

    def next(self, widget):
        """
        Goes to next song
        """
        self.player.do_next()

    def previous(self, widget):
        """
        Goes to previous song
        """
        try:
            self.player.do_previous()
        except:
            pass

    def quit(self, widget):
        """
        Exits Rhythmbox
        """
        self.shell.quit()
