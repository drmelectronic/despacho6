# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import xlwt
import Widgets
borders = xlwt.Borders()
borders.left = xlwt.Borders.THIN
borders.right = xlwt.Borders.THIN
borders.top = xlwt.Borders.THIN
borders.bottom = xlwt.Borders.THIN
dotted = xlwt.Borders()
dotted.left = xlwt.Borders.DOTTED
dotted.right = xlwt.Borders.DOTTED
gris = xlwt.Pattern()
gris.pattern = xlwt.Pattern.SOLID_PATTERN
gris.pattern_fore_colour = 23
azul = xlwt.Pattern()
azul.pattern = xlwt.Pattern.SOLID_PATTERN
azul.pattern_fore_colour = 30
celeste = xlwt.Pattern()
celeste.pattern = xlwt.Pattern.SOLID_PATTERN
celeste.pattern_fore_colour = 44
izquierda = xlwt.Alignment()
izquierda.horz = xlwt.Alignment.HORZ_LEFT
izquierda.vert = xlwt.Alignment.VERT_CENTER
centrado = xlwt.Alignment()
centrado.horz = xlwt.Alignment.HORZ_CENTER
centrado.vert = xlwt.Alignment.VERT_CENTER
derecha = xlwt.Alignment()
derecha.horz = xlwt.Alignment.HORZ_RIGHT
derecha.vert = xlwt.Alignment.VERT_CENTER
font = xlwt.Font()
font.name = 'Arial'
font.bold = True
# titulo
estilo_titulo = xlwt.XFStyle()
estilo_titulo.alignment = centrado
estilo_titulo.font = font
estilo_titulo.pattern = azul
estilo_titulo.borders = borders
estilo_titulo.font.colour_index = 9
# subtitulo
estilo_subtitulo = xlwt.XFStyle()
estilo_subtitulo.alignment = centrado
estilo_subtitulo.font = font
estilo_subtitulo.borders = borders
estilo_subtitulo.pattern = gris
estilo_subtitulo.font.colour_index = 1
# cabeceras
estilo_bold = xlwt.XFStyle()
estilo_bold.borders = borders
estilo_bold.pattern = azul
estilo_bold.alignment = centrado
estilo_bold.font = font
estilo_bold.font.colour_index = 9
# nombre de campo
estilo_campo = xlwt.XFStyle()
estilo_campo.alignment = izquierda
estilo_campo.font = font
# campos fuera de tabla
estilo_texto = xlwt.XFStyle()
estilo_texto.alignment = derecha
# fecha campo
estilo_fecha = xlwt.XFStyle()
estilo_fecha.num_format_str = 'DD-MM-YY'
estilo_fecha.alignment = derecha
# hora campo
estilo_hora = xlwt.XFStyle()
estilo_hora.num_format_str = 'HH:MM'
estilo_hora.alignment = derecha

# TABLA
# texto en toda la tabla
estilo_par = xlwt.XFStyle()
estilo_par.borders = dotted
estilo_par.pattern = xlwt.Pattern()
estilo_par.alignment = centrado
estilo_impar = xlwt.XFStyle()
estilo_impar.borders = dotted
estilo_impar.pattern = xlwt.Pattern()
estilo_impar.alignment = centrado
estilo_impar.pattern = celeste
estilo = [estilo_par, estilo_impar]
# nombre de personal en la tabla
estilo_personal_par = xlwt.XFStyle()
estilo_personal_par.borders = dotted
estilo_personal_par.alignment = izquierda
estilo_personal_impar = xlwt.XFStyle()
estilo_personal_impar.borders = dotted
estilo_personal_impar.alignment = izquierda
estilo_personal_impar.pattern = celeste
estilo_personal = [estilo_personal_par, estilo_personal_impar]
# total
estilo_total_par = xlwt.XFStyle()
estilo_total_par.borders = dotted
estilo_total_par.alignment = centrado
estilo_total_par.font = font
estilo_total_impar = xlwt.XFStyle()
estilo_total_impar.borders = dotted
estilo_total_impar.alignment = centrado
estilo_total_impar.font = font
estilo_total_impar.pattern = celeste
estilo_total = [estilo_total_par, estilo_total_impar]
# fecha tabla
estilo_fecha_borde_par = xlwt.XFStyle()
estilo_fecha_borde_par.num_format_str = 'DD-MM-YY'
estilo_fecha_borde_par.borders = dotted
estilo_fecha_borde_par.alignment = centrado
estilo_fecha_borde_impar = xlwt.XFStyle()
estilo_fecha_borde_impar.num_format_str = 'DD-MM-YY'
estilo_fecha_borde_impar.borders = dotted
estilo_fecha_borde_impar.alignment = centrado
estilo_fecha_borde_impar.pattern = celeste
estilo_fecha_borde = [estilo_fecha_borde_par, estilo_fecha_borde_impar]
#hora_tabla
estilo_hora_borde_par = xlwt.XFStyle()
estilo_hora_borde_par.num_format_str = 'HH:MM'
estilo_hora_borde_par.borders = dotted
estilo_hora_borde_par.alignment = centrado
estilo_hora_borde_impar = xlwt.XFStyle()
estilo_hora_borde_impar.num_format_str = 'HH:MM'
estilo_hora_borde_impar.borders = dotted
estilo_hora_borde_impar.alignment = centrado
estilo_hora_borde_impar.pattern = celeste
estilo_hora_borde = [estilo_hora_borde_par, estilo_hora_borde_impar]

import datetime
from reportlab.pdfgen import canvas
import os
import json
from reportlab.lib.pagesizes import legal, A4, letter
from reportlab.lib.units import cm
import time
if os.name == 'nt':
    import win32api
    import win32print
else:
    import sh
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialBlack', 'Arial_Black.ttf'))

class Impresion:
    normal = 'Courier'
    #bold = 'FreeMonoBold'
    #normal = 'Helvetica'
    #bold = 'Helvetica'
    bold = 'Courier-Bold'

    def __init__(self, tarjeta, datos):
        self.tarjeta = tarjeta
        self.datos = datos
        self.imprimir()

    def set_font(self, s):
        if s > 16:
            self.pdf.setFont(self.bold, s)
        else:
            self.pdf.setFont(self.normal, s)

    def escribir(self, x, y, a, d):
        if a < 0:
            f = self.pdf.drawString
        elif a == 0:
            f = self.pdf.drawCentredString
        else:
            f = self.pdf.drawRightString
        f(x + self.mx, self.A4y - y - self.my, unicode(d))

    def rectangulo(self, x, y, ancho, alto, fill=False):
        self.pdf.rect(x + self.mx, self.A4y - y - self.my, ancho, alto, fill=fill)

    def decode(self, tarjeta, datos, direccion=None):
        for k in tarjeta.keys():
            if isinstance(tarjeta[k], dict):
                for f in tarjeta[k].keys():
                    if len(tarjeta[k][f]) == 6:
                        x, y, p, d, s, a = tarjeta[k][f]
                        self.set_font(s)
                        for i in datos[k]:
                            try:
                                self.escribir(x, y, a, i[f])
                            except:
                                raise
                            if d:
                                y += p
                            else:
                                x += p
            elif len(tarjeta[k]) == 3:
                x, y, s = tarjeta[k]
                self.set_font(s)
                self.escribir(x, y, -1, datos[k])
            elif len(tarjeta[k]) == 4:
                x, y, s, a = tarjeta[k]
                self.set_font(s)
                self.escribir(x, y, a, datos[k])
            elif len(tarjeta[k]) == 5:
                xi, y, p, d, fields = tarjeta[k]
                for filas in datos[k]:
                    x = xi
                    i = 0
                    for f in fields:
                        if isinstance(f, list):
                            dif, a, s = f
                            if d:
                                x += dif
                            else:
                                y += dif
                            self.set_font(s)
                            self.escribir(x, y, a, filas[i])
                        i += 1
                    if d:
                        y += p
                    else:
                        x += p
            elif len(tarjeta[k]) == 6:
                x, y, p, d, s, a = tarjeta[k]
                self.set_font(s)
                for i in datos[k]:
                    self.escribir(x, y, a, i)
                    if d:
                        y += p
                    else:
                        x += p


    def imprimir(self):
        self.metodo = self.tarjeta['metodo']
        if self.metodo == 'pdf':
            self.path = 'outs/impresion.pdf'
            x, y = self.tarjeta['hoja']#x = 22.9 #y = 16.2
            self.A4x = x * cm
            self.A4y = y * cm
            self.pdf = canvas.Canvas(self.path, pagesize=(self.A4x, self.A4y))
            self.mx, self.my = self.tarjeta['margen']
            self.decode(self.tarjeta['campos'], self.datos)
            self.pdf.showPage()
            self.pdf.save()
        elif self.metodo == 'txt':
            imp = Imp()
            self.path = 'outs/impresion.txt'
            texto = imp.metodo_escpos(self.tarjeta['campos'], self.datos, self.tarjeta['margen'])
            f = file(self.path, 'wb')
            f.write(texto)
            print texto
            f.close()
        elif self.metodo == 'ticket':
            self.path = 'outs/impresion.pdf'
            x, y = self.tarjeta['hoja']#x = 22.9 #y = 16.2
            self.A4x = x * cm
            self.A4y = y * cm
            self.pdf = canvas.Canvas(self.path, pagesize=(self.A4x, self.A4y))
            self.mx, self.my = self.tarjeta['margen']
            self.decode_ticket(self.datos)
            self.pdf.showPage()
            self.pdf.save()
        if os.name == 'nt':
            a = os.path.abspath(self.path)
            if self.metodo == 'pdf':
                win32api.ShellExecute(0, "print", a, None, ".", 0)
                os.system('taskkill /im cmd.exe /f')
            else:
                try:
                    ticket = open('outs/printer', 'rb')
                    memoria = ticket.read()
                    ticket.close()
                    printer_name = json.loads(memoria)['tarjeta']
                except:
                    print 'No hay impresora registrada'
                else:
                    hPrinter = win32print.OpenPrinter(printer_name)
                    try:
                      hJob = win32print.StartDocPrinter(hPrinter, 1, ("TCONTUR", None, "RAW"))
                      try:
                        win32print.StartPagePrinter(hPrinter)
                        win32print.WritePrinter(hPrinter, str(texto))
                        win32print.EndPagePrinter(hPrinter)
                      finally:
                        win32print.EndDocPrinter(hPrinter)
                    finally:
                      win32print.ClosePrinter(hPrinter)
        else:
            os.system("gtklp -C " + self.path)

    def decode_texto(self, tarjeta, datos):
        print tarjeta
        print datos
        formato = tarjeta['formato']
        formato_controles = tarjeta['formato_controles']
        controles = datos['controles']
        esc = chr(27)
        emph = esc + 'E'
        emphOFF = esc + 'F'
        size = {
            10: esc + 'g',
            12: esc + 'M',
            15: esc + 'P',
            17: esc + 'X' + chr(1) + chr(24) + chr(0),
            19: esc + 'X' + chr(1) + chr(28) + chr(0),
        }
        lista = []
        for l in tarjeta['lista']:
            p = ''
            if l[0] in tarjeta['lineas']:
                y = tarjeta['lineas'][l[0]]
                p += esc + '3' + chr(y)
                print 'linea', y
            p += size[l[1]]
            print 'size', l[1]
            if l[2]:
                p += emph
                print 'negrita'
            if isinstance(l[0], int):
                p += controles[l[0]]
                print controles[l[0]]
            elif l[0] == 'boletos' or l[0] == 'reservas' or l[0] == 'produccion':
                for d in datos[l[0]]:
                    if d == '':
                        d = '      '
                    p += d + tarjeta['espacio_boletos']
                    print d
            else:
                p += datos[l[0]]
                print datos[l[0]]
            if l[2]:
                p += emphOFF
            lista.append(p)
            print p
        print lista[:-1]
        texto = formato % tuple(lista[:-1])
        l = tarjeta['lista'][-1]
        controles_restantes = controles[l[0]:]
        if l[2]:
            texto += emph
        texto += size[l[1]]
        if 'controles' in tarjeta['lineas']:
            y = tarjeta['lineas']['controles']
            texto += esc + '3' + chr(y)
        for c in controles_restantes:
            texto += formato_controles % c
            print c
        if l[2]:
            texto += emphOFF
            print 'sin negrita'
        print texto
        return texto

    def decode_ticket(self, datos):
        self.escribir(self.A4x / 2, 0, 0, self.tarjeta['titulo'])
        y = 20
        self.pdf.setFont('ArialBlack', self.tarjeta['size'])
        self.escribir(10, y - 3, -1, 'UNIDAD')
        self.escribir(70, y - 3, -1, 'PAD ' + datos['padron'])
        self.escribir(120, y - 3, -1, '(%s)' % datos['placa'])

        self.rectangulo(5, y + 2, 160, 15)

        y += 15
        self.pdf.setFont(self.tarjeta['font'], self.tarjeta['size'])
        self.escribir(10, y - 3, -1, 'OPERADORES')
        self.escribir(70, y - 3, -1, 'CND ' + datos['conductor'])
        self.escribir(120, y - 3, -1, 'CBR ' + datos['cobrador'])

        self.rectangulo(5, y + 2, 160, 15)

        y += 15
        self.escribir(10, y - 3, -1, 'H. SALIDA:')
        self.escribir(70, y - 3, -1, datos['inicio'])
        self.escribir(120, y - 3, -1, datos['dia'])

        self.rectangulo(5, y + 2, 160, 15)

        y += 20
        self.escribir(10, y - 3, -1, 'CONTROLES')
        self.escribir(90, y - 3, 0, 'H.PROG')
        self.escribir(120, y - 3, -1, 'BOLETOS')

        self.rectangulo(5, y + 2, 108, 15)
        self.rectangulo(113, y + 2, 52, 15)

        y += 10
        yb = y * 1
        for c in datos['controles']:
            self.escribir(10, y, -1, c['nombre'])
            self.escribir(90, y, 0, c['hora'])
            self.rectangulo(5, y + 2, 108, 10)
            y += 10
        y = yb * 1
        for c in datos['boletos']:
            self.pdf.setFillColorCMYK(0, 0, 0, 0.2)
            self.rectangulo(113, y + 2, 52, 10, fill=True)
            self.pdf.setFillColorCMYK(0, 0, 0, 1)
            self.escribir(140, y, 0, c['nombre'])
            y += 10
            self.escribir(140, y, 0, c['boleto'])
            altura = 10
            y += 10
            for r in c['reserva']:
                self.escribir(140, y, 0, r)
                altura += 10
                y += 10
            self.rectangulo(113, y + 2 - 10, 52, altura)

class Test:
    esc = chr(27)
    sangria = 3
    x = 0
    y = 0
    factory = 45 / 19.
    factorx = 6.
    texto = ''

    def __init__(self):
        imp = Imp()
        self.path = 'outs/impresion.txt'
        texto = imp.test()
        f = file(self.path, 'wb')
        f.write(texto)
        print texto
        f.close()
        if os.name == 'nt':
            a = os.path.abspath(self.path)
            try:
                ticket = open('outs/printer', 'rb')
                memoria = ticket.read()
                ticket.close()
                printer_name = json.loads(memoria)['tarjeta']
            except:
                print 'No hay impresora registrada'
            else:
                hPrinter = win32print.OpenPrinter(printer_name)
                try:
                  hJob = win32print.StartDocPrinter(hPrinter, 1, ("TCONTUR", None, "RAW"))
                  try:
                    win32print.StartPagePrinter(hPrinter)
                    win32print.WritePrinter(hPrinter, str(texto))
                    win32print.EndPagePrinter(hPrinter)
                  finally:
                    win32print.EndDocPrinter(hPrinter)
                finally:
                  win32print.ClosePrinter(hPrinter)
        else:
            os.system("gtklp -C " + self.path)


class Excel:

    _letras = ['', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
        'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
        'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ',
        'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV',
        'AW', 'AX', 'AY', 'AZ', 'BA', 'BB', 'BC', 'BD', 'BE,' 'BF', 'BG', 'BH', 'BI', 'BJ']

    def __init__(self, titulo, subtitulo, cabeceras, filas, widths):
        self.titulo = unicode(titulo)
        self.widths = widths
        self.subtitulo = unicode(subtitulo)
        self.cabeceras = cabeceras
        self.filas = filas
        self.archivo = 'outs/reporte.xls'
        self.wb = xlwt.Workbook()
        self.ws = self.insert_ws('REPORTE')
        self.escribir(self.ws)

    def insert_ws(self, nombre):
        ws = self.wb.add_sheet(nombre)
        ws.bottom_margin = 0.4
        ws.top_margin = 0.4
        ws.right_margin = 0.4
        ws.left_margin = 0.4
        return ws

    def letras(self, i):
        primera = i / 26
        segunda = i % 26
        return self._letras[primera] + self._letras[segunda + 1]

    def terminar_xls(self, ws):
        for i, c in enumerate(self.widths):
            ws.col(i).width = int(1312 * c)
        self.wb.save(self.archivo)

    def escribir(self, ws):
        ws.write_merge(0, 0, 0, len(self.widths) - 1, self.titulo, estilo_titulo)
        ws.write_merge(1, 1, 0, len(self.widths) - 1, self.subtitulo, estilo_subtitulo)
        for i, c in enumerate(self.cabeceras):
            print c
            ws.write(3, i, unicode(c), estilo_bold)
        y = 4
        for i, r in enumerate(self.filas):
            print list(r)
            for j in range(len(self.widths)):
                c = r[j]
                print c, type(c)
                if isinstance(c, datetime.time):
                    estilo = [estilo_hora_borde_par, estilo_hora_borde_impar]
                elif isinstance(c, datetime.date):
                    estilo = [estilo_fecha_borde_par, estilo_fecha_borde_impar]
                else:
                    estilo = [estilo_par, estilo_impar]
                    c = unicode(c)
                ws.write(y + i, j, c, estilo[i % 2])
        self.terminar_xls(ws)

from serial import Serial
from escpos import printer

# epson = ESCPOS()
# print epson.log
# comandos = (
#     (('CENTER', 'b', 'bu2', 2, 2), 'TITULO\n'),
#     (('CENTER', 'a', 'b', 1, 1), 'SUBTITULO'),
#     (None),
#     (('LEFT', 'b', 'u', 1, 1), '1234567890123456789012301234567890\n'),
#     (('LEFT', 'a', 'normal', 1, 1), 'Contenido\nvarias lineas'),
#     (None),
#     (('RIGHT', 'b', 'normal', 1, 1), 'Pie de pagina\n'),
# )
# epson.imprimir(comandos)
#tarjeta, datos = [{"hoja": [21, 29], "margen": [0, 40], "campos": {"conductor": [140, 30, 10, -1], "controles": [31, 90, 17, 1, 14, -1], "inicio": [70, 56, 17, 1], "boletos": [135, 83, 53.5, 0, 14, 0], "cobrador": [140, 42, 10, -1], "dia": [520, 20, 13, -1], "placa": [45, 40, 11, 1], "produccion": [192, 57, 60, 0, 14, 1], "impresion": [520, 36, 12, -1], "padron": [55, 23, 20, 1], "vuelta": [140, 18, 16, -1], "total": [520, 57, 14, 1], "reservas": [135, 98, 53.5, 0, 14, 0]}, "metodo": "pdf"}, {"conductor": "AJALCRI\u00d1A QUISPE EDWIN JOSE", "cobrador": "AGUILAR FLORES ROLANDO", "reservas": ["", "", "", "", "", "", ""], "boletos": ["448201", "196001", "428501", "374501", "604001", "891501", "185001"], "padron": "25", "vuelta": "0.5", "total": "0.00", "controles": ["05:01", "05:16", "05:30", "05:42", "06:05", "06:13", "06:29", "06:47"], "dia": "22-08-2015", "placa": "A7Y-789", "produccion": ["0.00"], "impresion": "18:40:45", "inicio": "04:53"}]
#t = Impresion(tarjeta, datos)
#t.imprimir()

from operator import itemgetter
class Imp:
    esc = chr(27)
    sangria = 3
    x = 0
    y = 0
    factory = 45 / 19.
    factorx = 6.
    texto = ''

    def setTimes(self):
        self.texto += self.esc + chr(0x78) + chr(0x01)
        self.texto += self.esc + chr(0x6B) + chr(0x00)

    def setSerif(self):
        self.texto += self.esc + chr(0x78) + chr(0x01)
        self.texto += self.esc + chr(0x6B) + chr(0x01)

    def setDraft(self):
        self.texto += self.esc + chr(0x78) + chr(0x00)

    def test(self):
        self.definir_salto(15)
        self.normal('NORMAL ')
        self.negrita('NEGRITA')
        self.grande('GRANDE')
        self.chico('CHICO')
        self.enter()
        self.setSerif()
        self.normal('NORMAL ')
        self.negrita('NEGRITA')
        self.grande('GRANDE')
        self.chico('CHICO')
        self.enter()
        self.setDraft()
        self.normal('NORMAL ')
        self.negrita('NEGRITA')
        self.grande('GRANDE')
        self.chico('CHICO')
        self.enter()
        self.setTimes()
        self.normal('NORMAL ')
        self.negrita('NEGRITA')
        self.grande('GRANDE')
        self.chico('CHICO')
        self.enter()
        return self.texto


    def reset(self):
        self.texto += self.esc + '@'

    def definir_salto(self, n):
        self.salto = n
        print '    definir_salto(%d)' % n, int(round(n * self.factory))
        self.texto += self.esc + '3' + chr(int(round(n * self.factory)))

    def negrita(self, texto):
        self.x += 8 * len(texto)
        self.texto += self.esc + '!' + chr(8) + texto + self.esc + '!' + chr(0)

    def normal(self, texto):
        self.negrita(texto)
        return
        self.x += 8 * len(texto)
        self.texto += self.esc + '!' + chr(0) + texto

    def grande(self, texto):
        self.x += 8 * len(texto)
        #self.texto += self.esc + '!' + chr(24) + texto + self.esc + '!' + chr(0)
        self.texto += "w1" + texto + "w0"

    def chico(self, texto):
        self.x += 6 * len(texto)
        self.texto += self.esc + 'g' + texto + self.esc + '!' + chr(0)

    def enter(self):
        self.x = 0
        self.texto += '\r\n'
        self.y += self.salto
        print '      enter', self.y

    def parse(self, plantilla, dato, margen):
        if len(plantilla) == 6:  # multiple
            lista = []
            x = plantilla[0] + margen[0]
            y = plantilla[1] + margen[1]
            s = plantilla[4]
            for d in dato:
                data = [d, x, y, s]
                if plantilla[3]:  # vertical
                    y += plantilla[2]
                else:  # horizontal
                    x += plantilla[2]
                lista.append(data)
            return lista
        else:
            return [[dato, plantilla[0] + margen[0], plantilla[1] + margen[1], plantilla[2]]]

    def size(self, t, s):
        if s > 15:
            self.grande(str(t))
        elif s < 11:
            self.chico(str(t))
        else:
            self.normal(str(t))
        print '       imprimir', t, self.x, self.y

    def espaciar(self, espacio):
        if espacio:
            self.espacio = ' ' * int(espacio / self.factorx)
            self.chico(self.espacio)
            print '      espacio', espacio / self.factorx, self.x
        else:
            self.espacio = ''

            def numero_a_letras(self, n):
                number_in = int(n)
                decim = int(n * 100 - number_in * 100)
                convertido = ''
                number_str = str(number_in) if (type(number_in) != 'str') else number_in
                number_str = number_str.zfill(9)
                millones, miles, cientos = number_str[:3], number_str[3:6], number_str[6:]
                if (millones):
                    if (millones == '001'):
                        convertido += 'UN MILLON '
                    elif (int(millones) > 0):
                        convertido += '%sMILLONES ' % self.convertNumber(millones)
                if (miles):
                    if (miles == '001'):
                        convertido += 'MIL '
                    elif (int(miles) > 0):
                        convertido += '%sMIL ' % self.convertNumber(miles)
                if (cientos):
                    if (cientos == '001'):
                        convertido += 'UN '
                    elif (int(cientos) > 0):
                        convertido += '%s' % self.convertNumber(cientos)
                convertido += 'CON %s/100 ' % str(decim).zfill(2)
                return convertido

    def metodo_escpos(self, plantilla, datos, margen):
        self.setSerif()
        self.datos = datos
        lista = []
        for p in plantilla.keys():
            fila = self.parse(plantilla[p], datos[p], margen)
            print fila
            lista += fila
        lista.sort(key=itemgetter(1))
        lista.sort(key=itemgetter(2))
        self.reset()
        self.y = 0
        self.x = 0
        for l in lista:
            print l
            salto = l[2] - self.y
            if salto > 0:
                print '  calcular salto %s -> %s' % (self.y, l[2])
                self.definir_salto(salto)
                self.enter()
            espacio = l[1] - self.x
            if espacio > 0:
                print '  calcular espacio %s -> %s' % (self.x, l[1])
                self.espaciar(espacio)
            self.size(l[0], l[3])
        try:
            lineas_final = margen[2]
        except:
            lineas_final = 3
        self.texto += (self.esc + chr(13) + chr(10)) * lineas_final  # FF (fin de pagina)
        return self.texto


class ESCPOS:

    def __init__(self, data):
        self.config = data
        self.puerto = 'LPT1'
        self.log = ''
        self.buscar_serial()
        # self.config = {
        #     self.tipo: 'LPT1',
        #     'corte': True,
        #     'lineas_final': 5,
        #     'tarjeta': '-',
        #     'formato': False
        # }
        self.set_config()

    def probar(self):
        print 'probar'
        comandos = ((('CENTER', 'b', 'normal', 1, 1), '----  %s  ----' % datetime.datetime.now()),)
        self.imprimir(comandos)

    def imprimir(self, comandos, cortar=True):
        texto = json.dumps(comandos)
        ticket = open('outs/ticket.lst', 'wb')
        ticket.write(texto)
        ticket.close()

        ticket = open('outs/ticket.lpt', 'wb')
        previa = open('outs/ticket.txt', 'wb')
        vista = 'EPSON ' + str(self.epson)
        ESC = chr(27)
        GS = chr(29)
        cutpaper = GS + 'V' + chr(49)
        texto = ESC + '@'  # limpiar formatos
        texto += ESC + 't' + chr(18)  # español
        for c in comandos:
            if c is None:
                texto += '\n'
                vista += '\n'
            elif c[1] == ' \n \n \n \n':
                print('saltando final')
            else:
                if 'LEFT' == c[0][0]:
                    texto += ESC + 'a' + chr(0)
                if 'CENTER' == c[0][0]:
                    texto += ESC + 'a' + chr(1)
                if 'RIGHT' == c[0][0]:
                    texto += ESC + 'a' + chr(2)
                if 'g' in c[0][2]:
                    texto += GS + '!' + chr(17)  # fuente grande
                elif 's' in c[0][2]:
                    texto += GS + '!' + chr(1)  # fuente pequeña
                else:
                    texto += GS + '!' + chr(0)  # fuente normal
                if 'u' in c[0][2]:
                    texto += ESC + '-' + chr(2)
                if 'b' in c[0][2]:
                    texto += ESC + 'E' + chr(1)
                texto += c[1]
                vista += c[1]
                if 'u' in c[0][2]:
                    texto += ESC + '-' + chr(0)
                if 'b' in c[0][2]:
                    texto += ESC + 'E' + chr(0)
        if cortar:
            texto += '\n\nSistema de Gestion TCONTUR'
            vista += '\n\nSistema de Gestion TCONTUR'

            lineas = self.config['lineas_final'] - 2
            texto += '\n' * lineas
            vista += '\n' * lineas
            if self.config['corte'] is True:
                texto += cutpaper
                vista += cutpaper
            else:
                try:
                    byts = self.config['corte'].split(',')
                    for b in byts:
                        texto += chr(int(b))
                        vista += chr(int(b))
                except:
                    pass
        else:
            print('-- esperando siguiente parte --')
        ticket.write(texto)
        ticket.close()
        previa.write(vista)
        previa.close()
        print vista
        if os.name == 'nt':
            if self.usb:
                hprinter = win32print.OpenPrinter(self.config[self.tipo])
                try:
                    hJob = win32print.StartDocPrinter(hprinter, 1, ("TCONTUR", None, "RAW"))
                    try:
                        win32print.StartPagePrinter(hprinter)
                        if self.config['formato']:
                            win32print.WritePrinter(hprinter, str(texto))
                        else:
                            win32print.WritePrinter(hprinter, str(vista))
                        win32print.EndPagePrinter(hprinter)
                    finally:
                        win32print.EndDocPrinter(hprinter)
                finally:
                    win32print.ClosePrinter(hprinter)
                print self.config[self.tipo]
            else:
                os.system('cd outs && type ticket.lpt > ' + self.config[self.tipo])
        else:
            print 'imprimir linux', self.epson
            vista = 'EPSON NONE'
            for c in comandos:
                if c is None:
                    self.epson.control('LF')
                    vista += '\n'
                else:
                    self.epson.set(*c[0])
                    self.epson.text(c[1])
                    vista += c[1]
                print 'i'
            previa = open('outs/ticket.txt', 'wb')
            previa.write(vista)
            previa.close()
            print 'SERIAL'
            print vista
            self.epson.control('VT')
            self.epson.control('VT')
            self.epson.control('LF')
            self.epson.control('LF')

if __name__ == '__main__':
    impresora = ESCPOS('puerto')
    ticket = [
        # [["CENTER", "b", "b", 1, 1], "ECONAIN S.A.C.\n"],
        # [["CENTER", "b", "normal", 1, 1], "Jr. San Lucas 211 - Urb. Palao - S.M.P.\n"],
        # [["CENTER", "b", "normal", 1, 1], "R.U.C.: 20516318547\n"],
        # [["CENTER", "b", "b", 1, 1], "RECIBO INTERNO: 000 - 0000007\n\n"],
        # [["LEFT", "b", "normal", 1, 1], "  DIA: 02/05/2019          \n"],
        # [["LEFT", "b", "normal", 1, 1], "  PLACA:  ALW104        PADRON:  002  \n"],
        [["LEFT", "b", "normal", 1, 1], "  CLIENTE: Ñañez con tílde\n"],
        # [["LEFT", "b", "normal", 1, 1], "\n"],
        # [["LEFT", "b", "ub", 1, 1], "  DETALLE                CANT     TOTAL \n"],
        # [["LEFT", "b", "u", 1, 1], "AYUDA MUTUA 120.0         1.0     120.0\n"],
        # [["LEFT", "b", "b", 1, 1], "                  TOTAL          120.00\n\n"],
        # [["LEFT", "b", "normal", 1, 1], "SON: CIENTO VEINTE CON 00/100  NUEVOS SOLES\n"],
        # [["CENTER", "b", "normal", 1, 1], "F.PAGO: CONTADO   ID: 5629499534213120\n"],
        # [["CENTER", "b", "normal", 1, 1], "SuperAdmin          10:06:30 02/05/2019\n"],
        # [["CENTER", "b", "normal", 1, 1], "GRACIAS !!\n"]
    ]
    impresora.imprimir(ticket)

if __name__ == '__main__das':
    from escpos import *
    """ Seiko Epson Corp. Receipt Printer M129 Definitions (EPSON TM-T88IV) """
    Epson = printer.Usb(0x04b8, 0x0202)  # TM-U220
    # Epson = printer.Usb(0x067b, 0x2305)  # Prolific
    ESC = chr(27)
    GS = chr(29)
    LF = chr(10)
    raw = ESC + '@'
    raw += "IZQUIERDA"+ LF
    raw += ESC + "!" + chr(1)  # fuente pequeña
    raw += "PEQUEÑA" + LF
    raw += "1234567890"*10 + LF
    raw += "TICKET: 109 - 1262954   HORA: %s" % datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y') + LF
    raw += ESC + "!" + chr(0)  # fuente grande
    raw += "NORMAL" + LF
    raw += "1234567890"*10 + LF
    raw += GS + "!" + chr(17)  # tamaño 2x2
    raw += "GRANDE" + LF
    raw += "1234567890"*10 + LF
    raw += GS + "(L" + chr(6) + chr(0) + chr(48) + chr(69) + "B2" + chr(1) + chr(1) # boleto
    raw += GS + "!" + chr(0)  # tamaño 1x1
    raw += ESC + "a" + chr(1)  # centrado
    raw += "CENTRADO" + LF
    raw += 'IZAGUIRRE - UNI' + LF
    raw += ESC + "!" + chr(1)  # fuente pequeña
    raw += '_' * 42 + LF
    raw += 'ID Servicio: 5948521   Inicio: 09:42 16/11/2016' + LF
    raw += 'Sistema de Gestion para Transporte Urbano TCONTUR' + LF
    raw += GS + "(L" + chr(6) + chr(0) + chr(48) + chr(69) + "E1" + chr(1) + chr(1)  # ecabezado
    raw += 'PADRON: 701  PLACA A7M-895' + LF
    raw += GS + "V" + chr(49)
    Epson._raw(raw)


if __name__ == '__main__--':
    tarjeta = {
        "titulo": "HOJA DE RUTA 2411",
        "metodo": "ticket",
        "hoja": [6, 15],
        "margen": [0, 60],
        "font": 'Arial',
        "size": 8
    }
    datos = {
        "boletos": [
            {
                "nombre": "DIRECTO",
                "boleto": "500445",
                "reserva": ""
            }, {
                "nombre": "ADULTO",
                "boleto": "180182",
                "reserva": "220001"
            }, {
                "nombre": "MEDIO",
                "boleto": "187422",
                "reserva": ""
            }
        ],
        "conductor": "1410",
        "cobrador": "2883",
        "padron": "48",
        "vuelta": "2.0",
        "total": "387.00",
        "controles": [
            {
                "nombre": 'INICIO',
                "hora": "13:47",
            },
            {
                "nombre": 'PARADERO',
                "hora": "13:54",
            },
            {
                "nombre": 'MEDIO',
                "hora": "13:01",
            },
            {
                "nombre": 'FINAL',
                "hora": "14:16",
            }
        ],
        "dia": "18-12-2017",
        "placa": "B9N179",
        "impresion": "13:46:18",
        "inicio": "13:44"}
    Impresion(tarjeta, datos)
    1/0
    from escpos import *
    """ Bixolon SRP-270D """
    bixolon= printer.Usb(0x0419, 0x3c01)
    """ Epson TM-U220 """
    epson = printer.Usb(0x04b8, 0x0202)
    impresora = Epson()

    ticket = file('outs/ticket.txt', 'rb')
    raw = ticket.read()
    ticket.close()
    print raw
    Epson._raw(raw)
