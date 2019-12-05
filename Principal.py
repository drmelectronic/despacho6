#! /usr/bin/python
# -*- encoding: utf-8 -*-

import gtk
import Salidas
import Widgets
import Chrome
import gobject
import os
import DataLocal
from Http import Http


if __name__ == '__main__':
    gobject.threads_init()


class Splash(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.show_all()
        path = os.path.join('images', 'splash.png')
        pixbuf = gtk.gdk.pixbuf_new_from_file(path)
        pixmap, mask = pixbuf.render_pixmap_and_mask()
        width, height = pixmap.get_size()
        del pixbuf
        self.set_app_paintable(True)
        self.resize(width, height)
        self.realize()
        self.window.set_back_pixmap(pixmap, False)
        self.show_all()
        gobject.idle_add(self.aplicacion)

    def aplicacion(self, *args):
        self.a = Aplicacion()
        self.hide_all()
        self.a.login()


class Aplicacion:

    def __init__(self):
        d = DataLocal.DataLocal()
        d.load_main()
        d.load_config()
        self.grupo = gtk.WindowGroup()
        self.ventanas = []
        self.http = Http()
        self.http.construir(self.ventanas)
        d.http = self.http
        self.ventana = self.nueva_ventana()

    def login(self, *args):
        dialog = Widgets.Login()
        s.hide_all()

        respuesta = dialog.iniciar()
        if respuesta:
            self.ventana.login()
            dialog.cerrar()
        else:
            dialog.cerrar()

    def nueva_ventana(self, *args):
        ventana = Salidas.Ventana()
        self.grupo.add_window(ventana)
        ventana.present()
        self.ventanas.append(ventana)
        ventana.connect('cerrar', self.cerrar)
        ventana.connect('login', self.login)
        ventana.connect('nueva-ventana', self.nueva_ventana)
        if len(self.ventanas) > 1:
            ventana.login()
        ventana.grab_focus()
        return ventana

    def ticketera(self, widgets, event):
        dialogo = Widgets.Configuracion(self.http)
        self.http.dataLocal.limpiar_data()
        dialogo.cerrar()

    def cerrar(self, ventana):
        self.ventanas.remove(ventana)
        del ventana
        if len(self.ventanas) == 0:
            print('cerrar ventana')
            self.http.reloj.infinito = False
            gtk.main_quit()


if __name__ == '__main__':
    s = Splash()
    try:
        gtk.main()
    except BaseException:
        s.a.http.reloj.cerrar()
    if os.name == 'nt':
        os.system('taskkill /im TCONTUR5.exe /f')
