import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from ui.ventana import Ventana

if __name__ == "__main__":
    Ventana()
    Gtk.main()
