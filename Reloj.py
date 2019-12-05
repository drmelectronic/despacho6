# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import gobject
import gtk
import threading
import time


class Reloj(gtk.EventBox):
    __gsignals__ = {'tic-tac': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())}

    infinito = True

    def __init__(self):
        super(Reloj, self).__init__()
        self.hilo = threading.Thread(target=self.run)
        self.hilo.daemon = False
        self.hilo.start()

    def run(self):
        while self.infinito:
            gtk.gdk.threads_enter()
            self.emit('tic-tac')
            gtk.gdk.threads_leave()
            time.sleep(1)

    def cerrar(self):
        print('################# Finalizado')
        self.infinito = False
        self.hilo.join()
