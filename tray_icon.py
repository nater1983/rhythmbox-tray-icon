#!/usr/bin/python3
# coding=utf-8

import gi
gi.require_version('XApp', '1.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Peas, GObject, RB, XApp, GLib
from pathlib import Path
import math


class TrayIcon(GObject.Object, Peas.Activatable):
    __gtype_name = 'TrayIcon'
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        super(TrayIcon, self).__init__()
        base_path = Path(__file__).parent
        self.rhythmbox_icon = base_path / "tray_stopped.png"
        self.play_icon = base_path / "tray_playing.png"

    def do_activate(self) -> None:
        """
        Called when the plugin is activated.
        """
        self.shell = self.object
        self.player = self.shell.props.shell_player
        self.wind = self.shell.get_property("window")
        self.status_win = StatusWindow(self.shell)

        self.icon = XApp.StatusIcon()
        self.icon.set_icon_name(str(self.rhythmbox_icon))
        self.icon.connect("scroll-event", self.on_scroll)
        self.icon.connect("button-press-event", self.on_btn_press)
        self.player.connect("playing-changed", self.on_playing_changed)
        self.wind.connect("delete-event", self.hide_on_delete)

    def do_deactivate(self) -> None:
        """
        Called when the plugin is deactivated.
        """
        self.icon.disconnect_by_func(self.on_scroll)
        self.icon.disconnect_by_func(self.on_btn_press)
        self.player.disconnect_by_func(self.on_playing_changed)
        self.icon.set_visible(False)
        del self.icon

    def toggle_player_visibility(self, *args) -> None:
        """
        Toggles visibility of Rhythmbox player.
        """
        if self.wind.get_visible():
            self.wind.hide()
        else:
            self.wind.show()
            self.wind.present()

    def hide_on_delete(self, widget, event) -> bool:
        """
        Hide Rhythmbox on window close.
        """
        self.wind.hide()
        return True  # don't actually delete

    def on_btn_press(self, status_icon: XApp.StatusIcon, x: int, y: int, button: int, time: int) -> None:
        """
        Handle mouse button presses.
        """
        if button == 1:  # left button
            self.toggle_player_visibility()
        elif button == 2:  # middle button
            self.player.do_next()
        elif button == 3:  # right button
            self.status_win.popup(x, y)

    def on_playing_changed(self, player, playing: bool) -> None:
        """
        Sets icon and tooltip when playing status changes.
        """
        if playing:
            self.icon.set_icon_name(str(self.play_icon))
        else:
            self.icon.set_icon_name(str(self.rhythmbox_icon))

    def on_scroll(self, status_icon: XApp.StatusIcon, amount: int, direction: XApp.ScrollDirection, time: int) -> None:
        """
        Lowers or raises Rhythmbox's volume.
        """
        vol = round(self.player.get_volume()[1], 1)

        if direction == XApp.ScrollDirection.UP:
            vol += 0.1
        elif direction == XApp.ScrollDirection.DOWN:
            vol -= 0.1
        vol = max(0, min(1, vol))

        self.player.set_volume(vol)


class StatusWindow(Gtk.Window):
    def __init__(self, shell):
        super().__init__()
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_keep_above(True)
        self.set_border_width(5)

        self.icon_theme = Gtk.IconTheme.get_default()
        self.shell = shell
        self.player = self.shell.props.shell_player
        self.db = self.shell.props.db

        self.album_image = Gtk.Image()
        self.album_image.set_size_request(70, 70)

        self.title = Gtk.Label("Title")
        self.album = Gtk.Label("Album")
        self.artist = Gtk.Label("Artist")

        rating_event_box = Gtk.EventBox()
        self.rating = Gtk.Label()
        rating_event_box.add(self.rating)
        rating_event_box.set_events(Gdk.EventMask.POINTER_MOTION_MASK)
        rating_event_box.connect("motion_notify_event", self.on_star_mouseover)
        rating_event_box.connect("button_press_event", self.on_star_click)
        rating_event_box.connect("leave_notify_event", self.on_star_mouseout)
        self._star_value = -1

        self.play_pause_btn = Gtk.Button()
        self.next_btn = Gtk.Button()
        self.set_button_icon(self.next_btn, ["media-skip-forward"], 24, _("Next"))
        self.prev_btn = Gtk.Button()
        self.set_button_icon(self.prev_btn, ["media-skip-backward"], 24, _("Previous"))
        self.play_pause_btn.connect("clicked", self.play)
        self.next_btn.connect("clicked", self.next)
        self.prev_btn.connect("clicked", self.previous)
        box = Gtk.Box(halign=Gtk.Align.CENTER, spacing=5)
        box.add(self.prev_btn)
        box.add(self.play_pause_btn)
        box.add(self.next_btn)
        self.update_play_button_image()

        quit_btn = Gtk.Button()
        self.set_button_icon(quit_btn, ["gnome-logout", "exit"], 22, _("Quit Rhythmbox"))
        quit_btn.connect("clicked", self.quit)

        grid = Gtk.Grid(column_spacing=5, row_spacing=5)
        grid.attach(self.album_image, 0, 0, 1, 3)
        grid.attach(self.title, 1, 0, 1, 1)
        grid.attach(self.album, 1, 1, 1, 1)
        grid.attach(self.artist, 1, 2, 1, 1)
        grid.attach(rating_event_box, 0, 3, 1, 1)
        grid.attach(box, 1, 3, 1, 1)
        grid.attach(quit_btn, 2, 0, 1, 1)

        self.add(grid)
        self.player.get_property("player").connect("image", self.set_image)
        self.player.connect("playing-changed", self.update_items)

        self.connect("focus-out-event", self.focus_changed)
        self.connect("draw", self.on_draw)

    def popup(self, x: int, y: int) -> None:
        """
        Show window.
        """
        self.x_pos = x
        self.y_pos = y
        self.update_items()
        self.show_all()

    def focus_changed(self, window, widget) -> None:
        """
        Hide window on lose focus.
        """
        self.hide()

    def set_image(self, player=None, stream_data=None, image=None) -> None:
        """
        Set album image.
        """
        if image is None:
            image = self.find_cover() or self.icon_theme.load_icon('image-missing', 64, 0)
        self.album_image.set_from_pixbuf(image.scale_simple(70, 70, GdkPixbuf.InterpType.BILINEAR))

    def find_cover(self):
        """
        Find album cover in AlbumArt plugin.
        """
        db_entry = self.player.get_playing_entry()
        if db_entry is None:
            return None
        key = db_entry.create_ext_db_key(RB.RhythmDBPropType.ALBUM)
        cover_db = RB.ExtDB(name='album-art')
        art_location = cover_db.lookup(key)[0]
        if art_location and Path(art_location).exists():
            if Path(art_location).is_file():
                cover_pixbuf = GdkPixbuf.Pixbuf.new_from_file(art_location)
                return cover_pixbuf
        return None

    def set_button_icon(self, widget, icon_names, size, tooltip="") -> None:
        """
        Set button icon and tooltip.
        """
        icon_pixbuf = None
        for icon_name in icon_names:
            try:
                icon_pixbuf = self.icon_theme.load_icon(icon_name, size, 0)
                break
            except GLib.Error:
                continue
        if icon_pixbuf:
            widget.set_image(Gtk.Image.new_from_pixbuf(icon_pixbuf))
        widget.set_tooltip_text(tooltip)

    def update_play_button_image(self) -> None:
        """
        Update play button icon and tooltip depending on playing status.
        """
        playing = self.player.get_property("playing")
        icon_name = ["media-pause", "stock-media-pause"] if playing else ["media-play", "stock-media-play"]
        tooltip = _("Pause") if playing else _("Play")
        self.set_button_icon(self.play_pause_btn, icon_name, 32, tooltip)

        self.prev_btn.set_sensitive(self.player.get_property("has-prev"))
        self.next_btn.set_sensitive(self.player.get_property("has-next"))

    def update_items(self, player=None, playing=None) -> None:
        """
        Update window items (song info).
        """
        self.set_image()
        self.update_play_button_image()

        current_entry = self.player.get_playing_entry()
        if current_entry is not None:
            self.artist.set_text(current_entry.get_string(RB.RhythmDBPropType.ARTIST))
            self.album.set_text(current_entry.get_string(RB.RhythmDBPropType.ALBUM))
            self.title.set_text(current_entry.get_string(RB.RhythmDBPropType.TITLE))
        else:
            self.artist.set_text(_("Artist"))
            self.album.set_text(_("Album"))
            self.title.set_text(_("Title"))

    def on_star_mouseover(self, widget, event) -> None:
        """
        Show star rating on mouse over.
        """
        self.rating.set_text(self._star_value)

    def on_star_click(self, widget, event) -> None:
        """
        Set star rating on click.
        """
        self._star_value = (event.x // 20) + 1
        self.rating.set_text(str(self._star_value))

    def on_star_mouseout(self, widget, event) -> None:
        """
        Hide star rating on mouse out.
        """
        self.rating.set_text("")

    def play(self, button) -> None:
        """
        Toggle play/pause.
        """
        if self.player.get_property("playing"):
            self.player.do_pause()
        else:
            self.player.do_play()

    def next(self, button) -> None:
        """
        Play next song.
        """
        self.player.do_next()

    def previous(self, button) -> None:
        """
        Play previous song.
        """
        self.player.do_previous()

    def quit(self, button) -> None:
        """
        Quit Rhythmbox.
        """
        Gtk.main_quit()

    def on_draw(self, widget, cr) -> bool:
        """
        Handle custom drawing.
        """
        cr.set_source_rgb(0, 0, 0)
        cr.paint()
        return False

# End of TrayIcon and StatusWindow class
