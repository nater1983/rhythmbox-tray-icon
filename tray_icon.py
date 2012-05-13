from gi.repository import GObject, Peas
import subprocess


class TrayIcon(GObject.Object, Peas.Activatable):
    proc = None
    __gtype_name = 'TrayIcon'
    object = GObject.property(type=GObject.Object)

    def do_activate(self):
        #Invoke the actual application
        #This is done because the actual rhythmbox environment is too restrictive
        self.proc = subprocess.Popen("/home/mendhak/.local/share/rhythmbox/plugins/statusicon.py")

    def do_deactivate(self):
        if self.proc:
            self.proc.kill()
