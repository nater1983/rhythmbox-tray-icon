#!/usr/bin/python
# coding=utf-8

from gi.repository import Gtk, Gdk, GdkPixbuf, Peas, GObject
import os
import sys
import math

iconsPath = "/usr/share/icons/"
rhythmboxIcon = iconsPath + "hicolor/32x32/apps/rhythmbox.png"
playIcon = iconsPath + "gnome/32x32/actions/media-playback-start.png"

class TrayIcon(GObject.Object, Peas.Activatable):

    __gtype_name = 'TrayIcon'
    object = GObject.property(type=GObject.Object)

    iconsPath = "/usr/share/icons/"
    rhythmboxIcon = iconsPath + "hicolor/32x32/apps/rhythmbox.png"
    #playIcon = iconsPath + "gnome/32x32/actions/media-playback-start.png"
    playIcon = os.path.join(sys.path[0], "tray_playing.png")
    menu = None


    def popup_menu(self, icon, button, time, data = None):
        #self.popup.popup(None, None, None, None, button, time)
        """
        Called when the icon is right clicked, displays the menu
        """

        if not self.menu:
            self.menu = Gtk.Menu()

            playpause = Gtk.MenuItem("Play/Pause")
            next = Gtk.MenuItem("Nexto")
            prev = Gtk.MenuItem("Prevo")
            quit = Gtk.MenuItem("Quito")

            starItem = self.GetRatingStar()
            if starItem:
               self.menu.append(starItem)

            playpause.connect("activate", self.play)
            next.connect("activate", self.nextItem)
            prev.connect("activate", self.previous)
            quit.connect("activate", self.quit)

            self.menu.append(playpause)
            self.menu.append(next)
            self.menu.append(prev)
            self.menu.append(quit)
            self.menu.show_all()

            self.SetMenuCss()

        self.menu.popup(None, None, lambda w,x: self.icon.position_menu(self.menu, self.icon), self.icon, 3, time)



    def SetMenuCss(self):
        #Prevent background color when mouse hovers
        screen = Gdk.Screen.get_default()
        css_provider = Gtk.CssProvider()

        #The only way I could do it: Re-set bg, border colors, causing menuitem to 'expand', then set the :hover colors with unico
        #Also strange, background-color is ignored, but background is not.
        css_provider.load_from_data("GtkMenuItem { border:@bg_color; background:@bg_color; } GtkMenuItem:hover { background:@selected_bg_color; } GtkWidget{ border: @bg_color; } #starMenu:hover { color:@fg_color;background: @bg_color; -unico-inner-stroke-width: 0; }")

        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


    def GetRatingStar(self):
        """ Gets a Gtk.MenuItem with the current song's ratings in filled stars """
        starItem = Gtk.MenuItem(self.GetStarsMarkup(0,5))
        self.starValue =  5
        label = starItem.get_children()[0]
        label.set_markup(self.GetStarsMarkup(self.starValue,5))

        starItem.set_name('starMenu')

        starItem.connect("motion_notify_event", self.OnStarMouseOver)
        starItem.connect("button_press_event", self.OnStarClick)
        starItem.connect("leave_notify_event", self.OnStarMouseOut)

        if self.starValue >= 0:
            return starItem
        else:
            return None

    def OnStarClick(self, widget, event):
        """
        Method called when stars are clicked on. Determines chosen stars and sets song rating.
        """
        label = widget.get_children()[0]
        self.starValue = self.GetChosenStarsFromMousePosition(label, event.x)
        self.SetSongRating(self.starValue)

    def SetSongRating(self, rating):
        """
        Sets the current song rating in Rhythmbox.
        """
        print "Rating:", rating
#        try:
#            currentSongURI = self.GetSongURI()
#
#            if currentSongURI:
#
#                busType = Gio.BusType.SESSION
#                flags = 0
#                ratingInterface = None
#
#                proxy = Gio.DBusProxy.new_for_bus_sync(busType, flags, ratingInterface,
#                                                       "org.gnome.Rhythmbox3",
#                                                       "/org/gnome/Rhythmbox3/RhythmDB",
#                                                       "org.gnome.Rhythmbox3.RhythmDB", None)
#
#                variantRating = GLib.Variant("d", float(rating))
#                proxy.SetEntryProperties("(sa{sv})", currentSongURI, {"rating": variantRating})
#        except:
#            print "Failed to set a rating"


    def GetChosenStarsFromMousePosition(self, label, mouseX):
        """
        Calculates the number of chosen stars to show based on the mouse's X position
        """
        starWidth = int(label.get_layout().get_pixel_size()[0]/5)
        chosen = math.ceil((mouseX-label.get_layout_offsets()[0])/starWidth)
        if chosen <= 0:
            chosen = 0

        if chosen >= 5:
            chosen = 5

        return chosen

    def OnStarMouseOut(self, widget, event):
        """
        Method called when mouse leaves the rating stars. Resets stars to original value.
        """
        label = widget.get_children()[0]
        label.set_markup(self.GetStarsMarkup(self.starValue, 5))


    def OnStarMouseOver(self, widget, event):
        """
        Method called when mouse hovers over the rating stars. Shows filled stars as mouse hovers.
        """
        label = widget.get_children()[0]
        label.set_markup(self.GetStarsMarkup(self.GetChosenStarsFromMousePosition(label,event.x), 5))

    def GetStarsMarkup(self, filledStars, totalStars):
        """
        Gets the Pango Markup for the star rating label
        """

        if filledStars is None or filledStars <= 0:
                    filledStars = 0

        if filledStars >= totalStars:
            filledStars = totalStars

        filledStars = int(math.ceil(filledStars))
        totalStars = int(totalStars)

        starString = '★' * filledStars + '☆' * (totalStars-filledStars)
        return "<span size='x-large' foreground='#000000'>" + starString + "</span>"

    def toggle(self, icon, event, data = None):
        if event.button == 1: # left button
            if self.wind.get_visible():
                self.wind.hide()
            else:
                self.wind.show()
                self.wind.present()

    def play(self, widget):
        self.player.playpause(True) # does nothing argument

    def nextItem(self, widget):
        self.player.do_next()

    def previous(self, widget):
        self.player.do_previous()

    def quit(self, widget):
        self.shell.quit()

    def hide_on_delete(self, widget, event):
        self.wind.hide()
        return True # don't actually delete

    def set_playing_icon(self, player, playing):
        if playing:
            self.icon.set_from_file(self.playIcon)
        else:
            self.icon.set_from_file(self.rhythmboxIcon)

    def do_activate(self):
        self.shell = self.object
        self.wind = self.shell.get_property("window")
        self.player = self.shell.props.shell_player

        self.wind.connect("delete-event", self.hide_on_delete)

#        ui = Gtk.UIManager()
#        ui.add_ui_from_string(
#        """
#        <ui>
#          <popup name='PopupMenu'>
#            <menuitem action='PlayPause' />
#            <menuitem action='Next' />
#            <menuitem action='Previous' />
#            <separator />
#            <menuitem action='Quit' />
#          </popup>
#        </ui>
#        """)

#        ag = Gtk.ActionGroup("actions")
#        ag.add_actions([
#                ("PlayPause",Gtk.STOCK_MEDIA_PLAY,"Play/Pause",None, None, self.play),
#                ("Next",Gtk.STOCK_MEDIA_NEXT,"Next",None, None, self.nextItem),
#                ("Previous",Gtk.STOCK_MEDIA_PREVIOUS,"Previous",None, None, self.previous),
#                ("Quit",None,"Quit",None, None, self.quit)
#                ])
#        ui.insert_action_group(ag)
#        self.popup = ui.get_widget("/PopupMenu")

#        s1 = cairo.ImageSurface.create_from_png(rhythmboxIcon)
#        s2 = cairo.ImageSurface.create_from_png(playIcon)
#        ctx = cairo.Context(s1)
#        ctx.set_source_surface(s2, 0, 0)
#        ctx.paint()
#        self.playIcon = Gdk.pixbuf_get_from_surface(s1, 0, 0, s1.get_width(), s1.get_height())

        self.normalIcon = GdkPixbuf.Pixbuf.new_from_file(rhythmboxIcon)
        self.icon =  Gtk.StatusIcon()
        self.icon.set_from_file(self.rhythmboxIcon)
        self.icon.connect("scroll-event", self.scroll)
        self.icon.connect("popup-menu", self.popup_menu)
        self.icon.connect("button-press-event", self.toggle)
        self.player.connect("playing-changed", self.set_playing_icon)

    def scroll(self, widget, event):
        if self.player.playpause(True):
            # scroll up for previous track
            if event.direction == Gdk.ScrollDirection.UP:
                self.previous(widget)
            # scroll down for next track
            elif event.direction == Gdk.ScrollDirection.DOWN:
                self.nextItem(widget)

    def do_deactivate(self):
        self.icon.set_visible(False)
        del self.icon