#! /usr/bin/python
# -*- coding: utf-8 -*-
# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__ = "daniel"
__date__ = "$06-mar-2012 16:25:24$"

import threading
import os
import wave
import sys
if os.name == 'nt':
    import winsound
else:
    pass
    #if sys.maxint == 2147483647:
        #import pygame
        #pygame.mixer.init()
        #pygame.mixer.pre_init(22050, -16, 2, 1024 * 3)
import gobject
import time
import Widgets




class Hilo(threading.Thread):

    def __init__(self):
        super(Hilo, self).__init__()
        self.path = os.path.abspath('sounds')
        self.event = threading.Event()
        self.lista = []
        self.UNIDADES = ('', 'UNO', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS',
            'SIETE', 'OCHO', 'NUEVE', 'DIEZ', 'ONCE', 'DOCE', 'TRECE',
            'CATORCE', 'QUINCE', 'DIECISEIS', 'DIECISIETE', 'DIECIOCHO',
            'DIECINUEVE', 'VEINTE')
        self.DECENAS = ('VEINTI', 'TREINTA', 'CUARENTA', 'CINCUENTA',
            'SESENTA', 'SETENTA', 'OCHENTA', 'NOVENTA', 'CIEN')
        self.CENTENAS = ('CIENTO', 'DOSCIENTOS', 'TRESCIENTOS',
            'CUATROCIENTOS', 'QUINIENTOS', 'SEISCIENTOS', 'SETECIENTOS',
            'OCHOCIENTOS', 'NOVECIENTOS')

    def convertir(self, numero, output, folder):
        n = str(numero).zfill(4)
        carpeta = folder + "1-99/"
        if (n == '1000'):
            output.append(carpeta + "MIL")
            return output
        elif (n == '0100'):
            output.append(carpeta + "100")
            return output
        if (n[0] != '0'):  # hay millares
            output.append(carpeta + n[0])
            output.append(carpeta + "MIL")
        if (n[1] != '0'):  # hay centenas
            output.append(carpeta + self.CENTENAS[int(n[1]) - 1])
        output.append(carpeta + str(int(n[2:])))
        return output
        k = int(n[1:])
        if(k <= 20):
            output.append(carpeta + self.UNIDADES[k])
        else:
            if((k > 30) & (n[2] != '0')):
                output.append(carpeta + self.DECENAS[int(n[1]) - 2] + 'Y')
                #output.append(carpeta + 'Y')
                if int(n[2]) > 0:
                    output.append(carpeta + self.UNIDADES[int(n[2])])
            else:
                output.append(carpeta + self.DECENAS[int(n[1]) - 2])
                if int(n[2]) > 0:
                    output.append(carpeta + self.UNIDADES[int(n[2])])
        return output

    def run(self):
        while True:
            self.event.wait()
            if len(self.lista) == 0:
                self.event.clear()
            else:
                archivo = self.lista[0]
                self.reproducir(archivo)
                self.lista = self.lista[1:]

    def play(self, lista, folder):
        self.lista.append(folder + 'Timbre')
        for l in lista:
            self.lista.append(l)
        self.event.set()

    def stop(self):
        if os.name == 'nt':
            self.lista = []
            winsound.PlaySound(None, winsound.SND_FILENAME|winsound.SND_ASYNC)
        else:
            self.lista = []
            #if sys.maxint == 2147483647:
            #pygame.mixer.music.stop()

    def preparar(self, padron, folder):
        lista = [folder + 'Unidad']
        lista = self.convertir(padron, lista, folder)
        lista.append(folder + 'Preparar')
        self.play(lista, folder)
        texto = 'Unidad %d preparar' % padron

    def ubicar(self, padron, folder):
        lista = [folder + 'Unidad']
        lista = self.convertir(padron, lista, folder)
        lista.append(folder + 'Ubicar')
        self.play(lista, folder)
        texto = 'Unidad %d ubicar' % padron

    def salir(self, padron, folder):
        lista = [folder + 'Unidad']
        lista = self.convertir(padron, lista, folder)
        lista.append(folder + 'Salir')
        self.play(lista, folder)
        texto = 'Unidad %d salir' % padron

    def ultimo(self, padron, folder):
        lista = [folder + 'Ultimo']
        lista = self.convertir(padron, lista, folder)
        lista.append(folder + 'CasoContrario')
        self.play(lista, folder)
        texto = 'Ultimo llamado  %d' % padron

    def custom(self, padron, personal, lugar, folder):
        lista = [folder + 'personal/%s' % personal]
        lista = self.convertir(padron, lista, folder)
        lista.append(folder + 'lugares/%s' % lugar)
        self.play(lista, folder)
        texto = '%s de la unidad %d acercarse a %s' % (personal, padron, lugar)

    def error(self):
        self.lista.append(self.path + '/mensajes/error')
        self.event.set()

    def normal(self):
        self.lista.append(self.path + '/mensajes/normal')
        self.event.set()

    def importante(self):
        self.lista.append(self.path + '/mensajes/importante')
        self.event.set()

    def emergencia(self):
        self.lista.append(self.path + '/mensajes/emergencia')
        self.event.set()

    def reproducir(self, archivo):
        path = archivo + '.wav'
        w = wave.open(path, 'rb')
        frames = w.getnframes()
        rate = w.getframerate()
        w.close()
        t = frames * 1. / rate
        if os.name == 'nt':
            path = path.replace('/', '\\')
            print path
            winsound.PlaySound(path, winsound.SND_FILENAME|winsound.SND_ASYNC)
        else:
            print path
            #if sys.maxint == 2147483647:
            #pygame.mixer.music.load(path)
            #pygame.mixer.music.play()
            pass
        time.sleep(t + 0.05)

if __name__ == '__main__':
    print 'inicio'
    path = os.path.abspath('sounds/H1')
    print path
    sonido = Hilo()
    sonido.start()
    lista = []
    for i in range(5):
        lista = sonido.convertir(i + 22, lista, path + '/')
    print lista
    sonido.play(lista, path + '/')
    time.sleep(2)
    sonido.stop()
