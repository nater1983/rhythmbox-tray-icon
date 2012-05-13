#!/usr/bin/python
import gobject

import gtk
import starhscale

class StatusIcon:

    star = None
    starValue = 0

    def __init__(self):
        self.statusicon = gtk.StatusIcon()
        self.statusicon.set_from_stock(gtk.STOCK_HOME)
        self.statusicon.connect("popup-menu", self.right_click_event)
        self.statusicon.set_tooltip("StatusIcon Example")

        window = gtk.Window()
        window.connect("destroy", lambda w: gtk.main_quit())
        window.show_all()

    def motion_notify_event(self, widget, event):
        # if this is a hint, then let's get all the necessary
        # information, if not it's all we need.
        if event.is_hint:
           x, y, state = event.window.get_pointer()
        else:
           x = event.x
           y = event.y

        self.star.check_for_new_stars(x-self.star.allocation.x)

    def click_notify_event(self, widget, event):
        event.x = event.x - self.star.allocation.x
        self.star.do_button_press_event(event)
        self.starValue = self.star.stars


    def leave_notify_event(self, widget, event):
        self.star.set_value(self.starValue)

    def right_click_event(self, icon, button, time):
        menu = gtk.Menu()

        about = gtk.MenuItem("About")
        quit = gtk.MenuItem("Quit")

        ### MODIFIED PART!! ###
        item = gtk.MenuItem()

        prog = gtk.ProgressBar()
        prog.pulse()
        prog.show()
        prog.set_fraction(0.5)

        gobject.type_register(starhscale.StarHScale)
        self.star = starhscale.StarHScale(5, self.starValue)

        lbl = gtk.Label("Test")

        item.add(self.star)
        item.connect("motion_notify_event", self.motion_notify_event)
        item.connect("button_press_event", self.click_notify_event)
        item.connect("leave_notify_event", self.leave_notify_event)


        style = item.get_style().copy()
        item.set_style(style)

        menu.append(item)
        #### END MODIFIED PART ####

        about.connect("activate", self.show_about_dialog)
        quit.connect("activate", gtk.main_quit)

        menu.append(about)
        menu.append(quit)
        menu.show_all()


        menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.statusicon)

    def show_about_dialog(self, widget):
        about_dialog = gtk.AboutDialog()

        about_dialog.set_destroy_with_parent(True)
        about_dialog.set_name("StatusIcon Example")
        about_dialog.set_version("1.0")
        about_dialog.set_authors(["Andrew Steele"])

        about_dialog.run()
        about_dialog.destroy()

StatusIcon()
gtk.main()