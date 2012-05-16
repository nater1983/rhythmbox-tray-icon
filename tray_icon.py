from gi.repository import GObject, Peas
import subprocess


class TrayIcon(GObject.Object, Peas.Activatable):
    """
    This is an 'empty' Rhythmbox plugin which invokes another Python script to control Rhythmbox.
    """

    proc = None
    __gtype_name = 'TrayIcon'
    object = GObject.property(type=GObject.Object)

    def do_activate(self):
        """
        Invokes tray_icon_worker.py as the Rhythmbox environment is too restrictive to perform all the required functions.
        """
        self.proc = subprocess.Popen("/home/mendhak/.local/share/rhythmbox/plugins/tray_icon_worker.py")

    def do_deactivate(self):
        """
        Kills the tray_icon_worker.py script.
        """
        if self.proc:
            self.proc.kill()
