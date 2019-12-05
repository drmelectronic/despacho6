#! /usr/bin/python
# -*- encoding: utf-8 -*-
import datetime
import gobject
import json
import os

import Impresion
import Widgets
import gtk

import models
from Http import Http


class Cobranza(gtk.Window):

    documento = None
    cliente = None
    moneda = None
    movimiento = None

    def __init__(self):
        super(Cobranza, self).__init__()

        acgroup = gtk.AccelGroup()
        self.add_accel_group(acgroup)

        mb = gtk.MenuBar()

        menu1 = gtk.Menu()

        file = gtk.MenuItem("_Reportes")
        file.set_submenu(menu1)
        mb.append(file)

        por_cobrar = gtk.ImageMenuItem('Por Cobrar', acgroup)
        por_cobrar.add_accelerator("activate", acgroup, ord('R'), gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        por_cobrar.connect('activate', self.por_cobrar)
        menu1.append(por_cobrar)

        self.http = Http()
        self.dataLocal = self.http.dataLocal
        self.dataLocal.get_clientes()

        self.set_title('Módulo de Cobranza')
        self.set_size_request(720, 400)

        vbox_main = gtk.VBox(False, 0)
        self.add(vbox_main)

        vbox_main.pack_start(mb, False, False, )

        hbox_main = gtk.HBox(False, 0)
        vbox_main.pack_start(hbox_main, False, False, 0)

        vbox_form = gtk.VBox(False, 0)
        hbox_main.pack_start(vbox_form, True, True, 0)

        hbox_form = gtk.HBox(False, 0)
        vbox_form.pack_start(hbox_form, False, False, 10)

        frame1 = gtk.Frame('Documento')
        frame1.set_size_request(200, 130)
        hbox_form.pack_start(frame1, True, True, 10)

        hbox = gtk.HBox(False, 0)
        frame1.add(hbox)
        tabla = gtk.Table(3, 3)
        tabla.set_row_spacings(5)
        tabla.set_col_spacings(5)
        hbox.pack_start(tabla, False, False, 10)

        label = gtk.Label('TIPO:')
        label.set_alignment(0, 0.5)
        tabla.attach(label, 0, 1, 0, 1)
        self.entry_tipo_doc = Widgets.Numero(4)
        tabla.attach(self.entry_tipo_doc, 1, 2, 0, 1)
        self.label_tipo_doc = gtk.Label('Escoja un tipo')
        self.label_tipo_doc.set_alignment(0, 0.5)
        tabla.attach(self.label_tipo_doc, 2, 3, 0, 1)
        self.entry_tipo_doc.connect('activate', self.tipo_documento)

        label = gtk.Label('SERIE:')
        label.set_alignment(0, 0.5)
        tabla.attach(label, 0, 1, 1, 2)
        self.entry_serie = Widgets.Numero(4)
        tabla.attach(self.entry_serie, 1, 2, 1, 2)
        self.label_serie = gtk.Label('Escoja una serie')
        self.label_serie.set_alignment(0, 0.5)
        tabla.attach(self.label_serie, 2, 3, 1, 2)
        self.entry_serie.connect('activate', self.buscar_documento)

        label = gtk.Label('MONEDA:')
        label.set_alignment(0, 0.5)
        tabla.attach(label, 0, 1, 2, 3)
        self.entry_moneda = Widgets.Numero(4)
        tabla.attach(self.entry_moneda, 1, 2, 2, 3)
        self.label_moneda = gtk.Label('Escoja una moneda')
        self.label_moneda.set_alignment(0, 0.5)
        tabla.attach(self.label_moneda, 2, 3, 2, 3)
        self.entry_moneda.connect('activate', self.buscar_moneda)

        # tabla.attach(gtk.Label('NUMERO:'), 0, 1, 1, 2)
        # self.entry_serie = gtk.Entry()
        # tabla.attach(self.entry_serie, 1, 2, 1, 2)
        # tabla.attach(gtk.Label('Escoja una serie'), 2, 3, 1, 2)

        frame2 = gtk.Frame('Cliente')
        frame2.set_size_request(200, 90)
        hbox_form.pack_start(frame2, True, True, 10)

        hbox = gtk.HBox(False, 0)
        frame2.add(hbox)
        tabla = gtk.Table(3, 3)
        tabla.set_row_spacings(10)
        tabla.set_col_spacings(10)
        hbox.pack_start(tabla, False, False, 10)

        label = gtk.Label('MOV:')
        label.set_alignment(0, 0.5)
        tabla.attach(label, 0, 1, 0, 1)
        self.entry_tipo_mov = Widgets.Texto(4)
        tabla.attach(self.entry_tipo_mov, 1, 2, 0, 1)
        self.label_tipo_mov = gtk.Label('Escoja un tipo')
        self.label_tipo_mov.set_alignment(0, 0.5)
        tabla.attach(self.label_tipo_mov, 2, 3, 0, 1)
        self.entry_tipo_mov.connect('activate', self.tipo_movimiento)

        # label = gtk.Label('TIPO:')
        # label.set_alignment(0, 0.5)
        # tabla.attach(label, 0, 1, 1, 2)
        # self.entry_tipo_cli = Widgets.Texto(4)
        # tabla.attach(self.entry_tipo_cli, 1, 2, 1, 2)
        # self.label_tipo_cliente = gtk.Label('Escoja un tipo')
        # self.label_tipo_cliente.set_alignment(0, 0.5)
        # tabla.attach(self.label_tipo_cliente, 2, 3, 1, 2)
        # self.entry_tipo_cli.connect('activate', self.tipo_cliente)

        label = gtk.Label('CODIGO:')
        label.set_alignment(0, 0.5)
        tabla.attach(label, 0, 1, 2, 3)
        self.entry_cliente = Widgets.Texto(11)
        tabla.attach(self.entry_cliente, 1, 3, 2, 3)
        self.entry_cliente.connect('activate', self.buscar_cliente)

        hbox = gtk.HBox(False, 0)
        vbox_form.pack_start(hbox, False, False, 10)
        self.label_cliente = gtk.Label('<b><big>CLIENTE: </big></b>')
        # self.label_cliente.set_size_request(500, 20)
        self.label_cliente.set_alignment(0, 0.5)
        self.label_cliente.set_use_markup(True)
        hbox.pack_start(self.label_cliente, False, False, 20)


        vbox_buttons = gtk.VBox(False, 0)
        hbox_main.pack_start(vbox_buttons, False, False, 10)

        vbox_buttons.pack_start(gtk.HBox(), False, False, 3)

        button_cargar = Widgets.Button('credito.png', "Buscar\nDeudas", 48)
        vbox_buttons.pack_start(button_cargar, False, False, 10)
        button_cargar.connect('clicked', self.buscar_cliente)

        self.but_pagar = Widgets.Button('cash-register.png',
                                        '<b><big><span foreground="#2196f3">PAGAR\nS/ 0.00</span></big></b>',
                                        48)
        # self.but_pagar.set_size_request(180, 100)
        self.but_pagar.connect('clicked', self.pagar)
        vbox_buttons.pack_start(self.but_pagar, False, False, 0)

        hbox_search = gtk.HBox(False, 0)
        vbox_buttons.pack_start(hbox_search, False, False, 10)

        hbox_search.pack_start(gtk.Label('Nuevo Prod: '), False, False, 20)
        self.entry_search = Widgets.Texto(10, DIR_TAB=False)
        hbox_search.pack_start(self.entry_search, False, False, 10)
        self.set_productos()
        button = Widgets.Button('mas.png', 'Buscar')
        button.set_size_request(180, 100)
        self.entry_search.connect('activate', self.buscar_codigo)
        button.connect('clicked', self.buscar_codigo)

        hbox = gtk.HBox(False, 0)
        vbox_main.pack_start(hbox, True, True, 10)

        sw = gtk.ScrolledWindow()
        hbox.pack_start(sw, True, True, 10)
        sw.set_size_request(560, 10)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        model = gtk.ListStore(str, str, str, str, str, str, str, gobject.TYPE_PYOBJECT)
        self.treeview = Widgets.TreeView(model)
        self.columnas = ['Nº', 'REF', 'DETALLE', 'CANT.', 'P.UNIT.', 'IGV', 'PAGAR']
        for i, columna in enumerate(self.columnas):
            cell_text = gtk.CellRendererText()
            tvcolumn = Widgets.TreeViewColumn(columna)
            tvcolumn.pack_start(cell_text, True)
            tvcolumn.set_attributes(cell_text, text=i)
            self.treeview.append_column(tvcolumn)
            tvcolumn.encabezado()
            if i == 2:
                tvcolumn.set_expand(True)
        sw.add(self.treeview)
        self.connect('key-press-event', self.on_key_pressed)
        self.treeview.connect('row-activated', self.delete_row)
        self.show_all()

    def delete_row(self, *args):
        path, column = self.treeview.get_cursor()
        path = int(path[0])
        model = self.treeview.get_model()
        dialogo = Widgets.Alerta_SINO('Eliminar Concepto', 'warning.png',
                                      'Confirme que desea eliminar el concepto:\n<b><big>Nº%s %s</big></b>' %
                                      (model[path][0], model[path][1]))
        respuesta = dialogo.iniciar()
        dialogo.cerrar()
        if respuesta:
            treeiter = model.get_iter(path)
            model.remove(treeiter)
            i = 0
            for row in model:
                i += 1
                row[0] = str(i)

    def buscar_moneda(self, *args):
        moneda = self.entry_moneda.get_text()
        self.treeview.get_model().clear()
        if moneda == '1':
            self.label_moneda.set_text('US$')
            self.moneda = False
            self.moneda_str = 'US$'
        elif moneda == '' or moneda == '0':
            self.label_moneda.set_text('S/')
            self.moneda_str = 'S/'
            self.moneda = True
        else:
            self.label_moneda.set_text('Moneda inválida')
            self.moneda = None
            self.moneda_str = ''


    def set_productos(self):
        liststore = gtk.ListStore(str)
        for p in self.dataLocal.get_productos():
            liststore.append([p['codigo']])
        completion = gtk.EntryCompletion()
        completion.set_model(liststore)
        completion.set_text_column(0)
        self.entry_search.set_completion(completion)

    def on_key_pressed(self, widget, event):
        k = event.keyval
        print('key', k)
        if k == 65307:  # Escape
            dialogo = Widgets.Alerta_SINO('Cancelar Cobranza', 'warning.png', 'Confirme si desea borrar todos los campos')
            respuesta = dialogo.iniciar()
            dialogo.cerrar()
            if respuesta:
                self.limpiar_form()
            else:
                if len(self.treeview.get_model()):
                    self.entry_search.grab_focus()
                else:
                    self.entry_tipo_doc.grab_focus()

    def limpiar_form(self):
        # self.entry_tipo_cli.set_text('')
        self.label_tipo_cliente.set_text('Escoja un tipo')
        self.entry_serie.set_text('')
        self.label_serie.set_text('Escoja una serie')
        # self.entry_tipo_cli.set_text('')
        self.label_tipo_cliente.set_text('Escoja un tipo')
        self.entry_cliente.set_text('')
        self.label_cliente.set_text('Escoja un código')
        self.documento = None
        self.cliente = None
        self.moneda = None
        self.treeview.get_model().clear()
        self.but_pagar.set_text('<b><big><span foreground="#2196f3">PAGAR\nS/ 0.00</span></big></b>')
        self.entry_tipo_doc.grab_focus()

    def tipo_documento(self, *args):
        tipo = self.entry_tipo_doc.get_int()
        if tipo == 0:
            doc = 'RECIBO INTERNO'
        elif tipo == 1:
            doc = 'FACTURA'
        elif tipo == 3:
            doc = 'BOLETA'
        else:
            doc = 'TIPO INVÁLIDO'
        self.label_tipo_doc.set_text(doc)

    def buscar_documento(self, *args):
        tipo = self.entry_tipo_doc.get_int()
        serie = unicode(self.entry_serie.get_text())

        self.documento = None
        if tipo == 0:
            doc = 'RECIBO INTERNO'
        elif tipo == 1:
            doc = 'FACTURA'
        elif tipo == 3:
            doc = 'BOLETA'
        else:
            return Widgets.Alerta('Error de Formulario', 'error.png', 'Tipo de Documento inválido')

        documentos = self.dataLocal.get_tipos_documento()
        print documentos
        for d in documentos:
            if d.tipo == tipo and d.serie == serie:
                self.label_serie.set_text(doc[0] + serie.zfill(3))
                self.documento = d
                return d

        dialogo = Widgets.Alerta_SINO('Crear Nueva Serie', 'warning.png', 'Confirme si desea crear la serie:\n%s %s' %
                                      (doc, serie))
        respuesta = dialogo.iniciar()
        if respuesta:
            data = {
                'tipo': tipo,
                'serie': serie
            }
            creado = self.http.load('/api/tiposDocumento', data)
            if creado:
                self.dataLocal.get_tipos_documento(actualizar=True)
                self.buscar_documento()
        dialogo.cerrar()

    def tipo_movimiento(self, *args):
        self.movimiento = None
        self.treeview.get_model().clear()
        tipo = self.entry_tipo_mov.get_text().upper()
        self.entry_tipo_mov.set_text(tipo)
        print('tipo movimiento', tipo)
        if tipo == '0' or tipo == 'A' or tipo == '':
            cli = 'ABONO'
            self.movimiento = 'A'
        elif tipo == '1' or tipo == 'R':
            cli = 'RETIRO'
            self.movimiento = 'R'
        elif tipo == '2' or tipo == 'D':
            cli = 'GENERAR DEUDA'
            self.movimiento = 'D'
        else:
            cli = 'ABONO'
            self.movimiento = 'A'
        self.label_tipo_mov.set_text(cli)

    # def tipo_cliente(self, *args):
    #     tipo = self.entry_tipo_cli.get_text().upper()
    #     self.entry_tipo_cli.set_text(tipo)
    #     self.treeview.get_model().clear()
    #     print('tipo cliente', tipo)
    #     if tipo == '0':
    #         cli = 'PERSONAL x ID'
    #     elif tipo == '1' or tipo == 'U' or tipo == '':
    #         cli = 'UNIDAD'
    #     elif tipo == 'F':
    #         cli = 'CONDUCTOR'
    #     elif tipo == 'C':
    #         cli = 'COBRADOR'
    #     else:
    #         cli = 'TIPO INVÁLIDO'
    #     self.label_tipo_cliente.set_text(cli)

    def buscar_cliente(self, *args):
        if self.documento is None:
            Widgets.Alerta('Formulario Incompleto', 'road-closure.png', 'Escoja un Documento Válido')

            self.entry_serie.grab_focus()
            self.label_serie.set_markup('<span foreground="#aa1111">Escoja una serie</span>')
            self.entry_serie.grab_focus()
            self.label_tipo_doc.set_markup('<span foreground="#aa1111">Escoja un tipo</span>')
            self.entry_tipo_doc.grab_focus()
            return
        # tipo = self.entry_tipo_cli.get_text()
        codigo = self.entry_cliente.get_text()

        if codigo == '':
            Widgets.Alerta('Error de Formulario', 'error.png', 'Código de Cliente Vacío')
            self.entry_cliente.grab_focus()
            return
        self.cliente = None
        self.treeview.get_model().clear()
        self.deudas = None

        for c in self.dataLocal.get_clientes():
            if c.codigo == codigo:
                self.cliente = c
                break

        if self.cliente is None:
            data = {'codigo': codigo}
            respuesta = self.http.load('buscar-cliente', data)
            if respuesta:
                self.cliente = respuesta['cliente']
                self.dataLocal.add_dato('clientes', self.cliente)
            else:
                dialog = ClienteDialogo()
                dialog.entry_codigo.set_text(codigo)
                cliente = dialog.iniciar()
                data = {
                    'codigo': dialog.entry_codigo.get_text(),
                    'referencia': dialog.entry_corto.get_text(),
                    'nombre': dialog.entry_nombre.get_text(),
                }
                dialog.cerrar()
                if cliente:
                    respuesta = self.http.load('/api/clientes', data)
                    if respuesta:
                        self.cliente = self.dataLocal.add_cliente(respuesta)

        if self.cliente:
            label_cliente = '<b><big>CLIENTE: %s</big></b>' % self.cliente.nombre
            self.label_cliente.set_markup(label_cliente)
            self.abrir_deudas()
        else:
            self.entry_cliente.grab_focus()

    def get_deudas(self):
        if self.deudas is None:
            data = {
                'cliente': self.cliente.id
            }
            respuesta = self.http.load('buscar-deudas', data)
            if respuesta:
                self.deudas = []
                for d in respuesta['deudas']:
                    self.deudas.append(models.Deuda(d))

    def abrir_deudas(self, *args):
        if self.documento is None:
            Widgets.Alerta('Formulario Incompleto', 'road-closure.png', 'Escoja una Serie Válida')
        elif self.cliente is None:
            Widgets.Alerta('Formulario Incompleto', 'road-closure.png', 'Escoja un Cliente Válido')
        elif self.moneda is None:
            Widgets.Alerta('Formulario Incompleto', 'road-closure.png', 'Escoja una Moneda')
        else:
            self.get_deudas()
            deudas = []
            for d in self.deudas:
                if d['moneda'] == self.moneda:
                    deudas.append(d)
            if deudas:
                dialogo = Deudas(self, {'cliente': self.cliente, 'deudas': deudas})
                dialogo.iniciar()
                dialogo.cerrar()
            else:
                if self.deudas:
                    Widgets.Alerta('La unidad tiene deudas', 'info.png', 'La unidad tiene deudas, pero no están en %s' % self.moneda_str)

            self.entry_search.grab_focus()


    def buscar_codigo(self, *args):
        codigo = self.entry_search.get_text()
        if codigo:
            for prod in self.dataLocal.get_productos():
                p = prod.copy()
                print(p['codigo'], p['nombre'])
                if p['codigo'] == codigo:
                    if self.movimiento == 'D':
                        self.generar_deuda(p)
                        return
                    if p['cliente'] is True:  # Unidad
                        if self.cliente['tipo'] != 'Unidad':
                            Widgets.Alerta('Concepto Inválido', 'road-closure.png', 'El concepto sólo está permitido para Unidades')
                            self.entry_search.set_text('')
                            self.entry_search.grab_focus()
                            return
                    elif p['cliente'] is False:  # Trabajador
                        if self.cliente['tipo'] != 'Trabajador':
                            Widgets.Alerta('Concepto Inválido', 'road-closure.png', 'El concepto sólo está permitido para Trabajadores')
                            self.entry_search.set_text('')
                            self.entry_search.grab_focus()
                            return
                    if p['moneda'] != self.moneda:
                        if self.moneda is None:
                            Widgets.Alerta('Formulario Incompleto', 'road-closure.png', 'Escoja una Serie Válida')
                            self.entry_serie.grab_focus()
                            self.label_serie.set_text('<span foreground="#aa1111">Escoja una serie</span>')
                            return
                        Widgets.Alerta('Error', 'error.png', 'La deuda a pagar debe estar en %s' % self.moneda_str)
                        self.entry_search.set_text('')
                        self.entry_search.grab_focus()
                        return False

                    if p['variable']:
                        if self.movimiento == 'A':
                            dialogo = Widgets.Alerta_Numero('Pagar', 'money.png',
                                                            'Escriba la cantidad a cobrar\n<b>%s</b>' % p['nombre'],
                                                            10, True)
                        else:
                            dialogo = Widgets.Alerta_Numero('Pagar', 'money.png',
                                                            'Escriba la cantidad a retirar\n<b>%s</b>' % p['nombre'],
                                                            10, True)
                        print('venta', p['venta'])
                        dialogo.entry.set_text(Widgets.currency(p['venta']))
                        monto = dialogo.iniciar()
                        dialogo.cerrar()
                        if monto:
                            p['pagar'] = int(float(monto) * 100)
                            p['precio'] = int(float(monto) * 1000)
                        else:
                            p['pagar'] = 0
                        p['cantidad'] = 1000
                    else:
                        if self.movimiento == 'A':
                            dialogo = Widgets.Alerta_Numero('Pagar', 'money.png',
                                                            'Escriba la cantidad de unidades a vender\n<b>CONCEPTO: %s\nPRECIO UNIT.: %s %s</b>' % (p['nombre'], self.moneda_str, Widgets.currency(p['precio'])),
                                                            10, True)
                        else:
                            dialogo = Widgets.Alerta_Numero('Pagar', 'money.png',
                                                            'Escriba la cantidad de unidades a retirar\n<b>CONCEPTO: %s\nPRECIO UNIT.: %s %s</b>' % (p['nombre'], self.moneda_str, Widgets.currency(p['precio'])),
                                                            10, True)
                        dialogo.entry.set_text('1')
                        cantidad = dialogo.iniciar()
                        dialogo.cerrar()
                        p['cantidad'] = 1
                        if cantidad:
                            p['pagar'] = p['precio'] * float(cantidad)
                            p['cantidad'] = float(cantidad) * 1000
                            p['precio'] = p['precio'] * 10
                        else:
                            p['pagar'] = 0
                    if p['pagar']:
                        p['referencia'] = p['tipo'][0] + codigo.zfill(5)
                        p['detalle'] = p['nombre']
                        if self.movimiento != 'A':
                            p['pagar'] = - p['pagar']
                        self.add_concepto(p)
                        print(p)
                    break
            self.entry_search.set_text('')
            self.entry_search.grab_focus()
        else:
            self.pagar()

    def add_concepto(self, concepto):
        model = self.treeview.get_model()
        print('concepto', concepto)
        if concepto['moneda'] != self.moneda:
            Widgets.Alerta('Error', 'error.png', 'La concepto a pagar debe estar en %s' % self.moneda_str)
            return False
        fila = [
            len(model) + 1,
            concepto['referencia'],
            concepto['detalle'],
            Widgets.quantity(concepto['cantidad']),
            Widgets.quantity(concepto['precio']),
            'SI' if concepto['afecto'] else '',
            Widgets.currency(concepto['pagar']),
            dict(concepto)
        ]
        model.append(fila)
        total = 0
        for row in model:
            total += row[len(self.columnas)]['pagar']
        for i, d in enumerate(self.deudas):
            print(d)
            if d['id'] == concepto['id']:
                self.deudas.pop(i)
                break
        self.but_pagar.set_text('<b><big><span foreground="#2196f3">PAGAR\n%s %s</span></big></b>' %
                                (self.moneda_str, Widgets.currency(total)))
        return True

    def pagar(self, *args):
        model = self.treeview.get_model()
        total = 0
        for row in model:
            total += row[len(self.columnas)]['pagar']
        # if total <= 0:
        #     Widgets.Alerta('Error de Digitación', 'error.png', 'Debe pagar un monto positivo')
        #     return
        if self.movimiento is None:
            Widgets.Alerta('Error de Digitación', 'error.png', 'Debe definir un tipo de Movimiento')
            return
        dialogo = Widgets.Alerta_SINO('Pagar', 'cash-register.png', 'Confirme que va a cobrar\n<b><big><span foreground="#2196f3">%s %s</span></big></b>' % (self.moneda_str, Widgets.currency(total)))
        dialogo.label.set_alignment(0.5, 0.5)
        respuesta = dialogo.iniciar()
        dialogo.cerrar()
        if respuesta:
            pagos = []
            base = 0
            igv = 0
            inafecta = 0
            total = 0
            for concepto in self.treeview.get_model():
                c = concepto[len(self.columnas)]
                if c['tipoCobro'] == 'X':  # Antes era 'F' para cobrar fondos ticket x ticket
                    if c['afecto']:
                        i = round(c['pagar'] * 0.18)
                        b = c['pagar'] - i
                        ina = 0
                    else:
                        ina = c['pagar']
                        b = 0
                        i = 0
                    data = {
                        'json': json.dumps({
                            'pagos': [c],
                            'cliente': self.cliente,
                            'documento': self.documento,
                            'movimiento': self.movimiento,
                            'venta': {
                                'moneda': self.moneda,
                                'base': b,
                                'igv': i,
                                'inafecta': ina,
                                'total': c['pagar'],
                            }
                        })
                    }
                    pagado = self.http.load('pagar-modulo-cobranza', data)
                    if pagado:
                        print('pagado Fondo OK')
                else:
                    pagos.append(c)
                    if c['afecto']:
                        i = round(c['pagar'] * 0.18)
                        b = c['pagar'] - i
                        base += b
                        igv += i
                    else:
                        inafecta += c['pagar']
                    total += c['pagar']
            if len(pagos):
                data = {
                    'json': json.dumps({
                        'pagos': pagos,
                        'cliente': self.cliente,
                        'documento': self.documento,
                        'movimiento': self.movimiento,
                        'venta': {
                            'moneda': self.moneda,
                            'base': base,
                            'igv': igv,
                            'inafecta': inafecta,
                            'total': total,
                        }
                    })
                }
                pagado = self.http.load('pagar-modulo-cobranza', data)
            if pagado:
                print('pagado OK')
                self.limpiar_form()
            else:
                self.entry_search.grab_focus()

        else:
            self.entry_search.grab_focus()

    def por_cobrar(self, *args):
        print('Por Cobrar')
        PorCobrar(self.http)

    def generar_deuda(self, p):
        GenerarDeuda(self.http, self.cliente, p)



class Deudas(gtk.Dialog):

    def __init__(self, parent, data):
        super(Deudas, self).__init__(flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        ventanas = gtk.window_list_toplevels()
        self.padre = parent
        self.http = parent.http
        parent = ventanas[0]
        for v in ventanas:
            if v.is_active():
                parent = v
                break
        self.set_modal(True)
        self.set_transient_for(parent)
        self.cliente = data['cliente']
        self.deudas = data['deudas']
        self.set_title('Deudas del Cliente: %s' % self.cliente['nombre'])
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect('delete_event', self.cerrar)
        sw = gtk.ScrolledWindow()
        sw.set_size_request(400, 300)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.vbox.pack_start(sw, False, False, 0)
        self.model = gtk.ListStore(str, str, str, str, gobject.TYPE_PYOBJECT)
        self.treeview = gtk.TreeView(self.model)
        self.columnas = ('DIA', 'DETALLE', 'MONEDA', 'MONTO')
        sw.add(self.treeview)
        for i, columna in enumerate(self.columnas):
            cell_text = gtk.CellRendererText()
            tvcolumn = Widgets.TreeViewColumn(columna)
            tvcolumn.pack_start(cell_text, True)
            tvcolumn.set_attributes(cell_text, markup=i)
            self.treeview.append_column(tvcolumn)
            if i == 1:
                tvcolumn.set_expand(True)
            tvcolumn.encabezado()

        for l in self.deudas:
            if l['moneda']:
                moneda = 'S/'
            else:
                moneda = 'US$'
            if l['total'] > 0:
                self.model.append((l['dia'], '%s-%s' % (l['numero'], l['detalle']), moneda, Widgets.currency(l['total']), l))

        self.menu = gtk.Menu()
        item1 = gtk.MenuItem('Conciliar Deuda')
        item2 = gtk.MenuItem('Eliminar Deuda')
        item3 = gtk.MenuItem('Editar Deuda')
        item4 = gtk.MenuItem('Historial Deuda')
        item1.connect('activate', self.conciliar)
        item2.connect('activate', self.eliminar)
        item3.connect('activate', self.editar)
        item4.connect('activate', self.historial)
        self.menu.append(item1)
        self.menu.append(item2)
        self.menu.append(item3)
        self.menu.append(item4)
        self.treeview.connect('button-release-event', self.on_release_button)
        but_pagar_todo = Widgets.Button('dinero.png', '_Pagar Todo')
        self.action_area.pack_start(but_pagar_todo, False, False, 0)
        but_pagar_todo.connect('clicked', self.pagar_todo)

        but_salir = Widgets.Button('cancelar.png', '_Salir')
        self.add_action_widget(but_salir, gtk.RESPONSE_CANCEL)
        self.treeview.connect('row-activated', self.pagar)
        self.treeview.set_enable_search(False)

    def on_release_button(self, treeview, event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            t = event.time
            pthinfo = treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.grab_focus()
                treeview.set_cursor(path, col, 0)
                self.menu.popup(None, None, None, event.button, t)
                self.menu.show_all()
            return True

    def conciliar(self, *args):
        path, column = self.treeview.get_cursor()
        path = int(path[0])
        row = self.model[path]
        pregunta = Widgets.Alerta_Entry(
            'Monto de CONCILIACIÓN',
            'editar.png', 'Escriba el monto final de la deuda'
        )
        monto = pregunta.iniciar()
        pregunta.cerrar()
        try:
            float(monto)
        except:
            return Widgets.Alerta('Error en formulario', 'error.png', 'Monto inválido')
        if monto:
            pregunta = Widgets.Alerta_Entry(
                'Motivo de CONCILIACIÓN',
                'editar.png', 'Escriba el motivo de la Conciliación'
            )
            motivo = pregunta.iniciar()
            pregunta.cerrar()
            datos = {'json': json.dumps({'deuda': row[-1],
                         'monto': monto,
                         'motivo': motivo,
                         })
                     }
            respuesta = self.http.load('conciliar-deuda', datos)
            if respuesta:
                self.cerrar()
        return

    def eliminar(self, *args):
        path, column = self.treeview.get_cursor()
        path = int(path[0])
        row = self.model[path]
        pregunta = Widgets.Alerta_Entry(
            'Motivo de CONCILIACIÓN',
            'editar.png', 'Escriba el motivo de la Conciliación'
        )
        motivo = pregunta.iniciar()
        pregunta.cerrar()
        if motivo:
            datos = {'json': json.dumps({'deuda': row[-1],
                         'motivo': motivo})
                     }
            respuesta = self.http.load('eliminar-deuda', datos)
            if respuesta:
                self.cerrar()
        return

    def historial(self, *args):
        path, column = self.treeview.get_cursor()
        path = int(path[0])
        row = self.model[path]
        datos = {'json': json.dumps({'deuda': row[-1]})
                 }
        respuesta = self.http.load('historial-deuda', datos)
        if respuesta:
            tabla = []
            for r in respuesta:
                tabla.append([r['dia'], r['monto'], r['usuario'], r['id']])
            tabla.sort(key=lambda k: k[0])
            dialog = Widgets.Alerta_TreeView('Historial de pagos', '', 'Pagos', ('DIA', 'MONTO', 'USUARIO'), tabla)
            dialog.set_default_size(350, 300)
            dialog.iniciar()
            dialog.cerrar()
        else:
            Widgets.Alerta('No hay elementos', 'warning.png', 'No se encontraron pagos hechos a esta deuda')

    def editar(self, *args):
        path, column = self.treeview.get_cursor()
        path = int(path[0])
        row = self.model[path]
        dialog = EditarDeuda(self, row[-1])
        dialog.iniciar()

    def pagar_todo(self, *args):
        for r in self.model:
            deuda = r[len(self.columnas)]
            deuda['pagar'] = deuda['total']
            deuda['referencia'] = 'D' + str(deuda['numero']).zfill(5)
            deuda['saldo'] = (deuda['total'] - deuda['pagar'])
            deuda['detalle'] = deuda['dia'][2:] + ' ' + deuda['detalle']
            deuda['cantidad'] = 1000
            self.padre.add_concepto(deuda)
            self.cerrar()

    def pagar(self, *args):
        try:
            path, column = self.treeview.get_cursor()
            path = int(path[0])
        except:
            return

        deuda = self.model[path][len(self.columnas)]
        dialogo = Widgets.Alerta_Numero('Pagar', 'dinero.png',
                                                    'Escriba la cantidad a cobrar\n<b>%s</b>' % deuda['detalle'],
                                                    10, True)
        monto = dialogo.iniciar()
        dialogo.cerrar()
        pagar = int(float(monto) * 100)
        print('pagar', pagar, deuda['total'])
        if 0 < pagar <= deuda['total']:
            deuda['pagar'] = pagar
            deuda['referencia'] = 'D' + str(deuda['numero']).zfill(5)
            deuda['saldo'] = (deuda['total'] - deuda['pagar'])
            deuda['detalle'] = '%s-%s %s' % (deuda['numero'], deuda['dia'][2:], deuda['detalle'])
            deuda['cantidad'] = 1000
            if self.padre.add_concepto(deuda):
                model = self.treeview.get_model()
                treeiter = model.get_iter(path)
                model.remove(treeiter)
        # elif pagar < 0:
        #     Widgets.Alerta('Error de Digitación', 'error.png', 'Debe pagar un monto positivo')
        elif pagar > deuda['total']:
            Widgets.Alerta('Error de Digitación', 'error.png', 'Debe pagar un monto menor o igual a la deuda')


    def iniciar(self):
        self.show_all()
        self.run()
        return

    def cerrar(self, *args):
        self.destroy()



class PorCobrar(gtk.Window):

    concepto = None
    tipo = None

    def __init__(self, http):
        super(PorCobrar, self).__init__()

        self.http = http

        self.set_title('Reporte General de Fondos')
        self.set_size_request(900, 400)

        vbox_main = gtk.VBox(False, 0)
        self.add(vbox_main)

        hbox_main = gtk.HBox(False, 0)
        vbox_main.pack_start(hbox_main, False, False, 0)


        frame1 = gtk.Frame('Búsqueda')
        frame1.set_size_request(200, 60)
        hbox_main.pack_start(frame1, True, True, 10)

        hbox = gtk.HBox(False, 0)
        frame1.add(hbox)

        label = gtk.Label('TIPO DE BÚSQUEDA:')
        label.set_alignment(0, 0.5)
        hbox.pack_start(label, False, False, 10)
        self.entry_tipo = Widgets.Texto(2, DIR_TAB=False)
        self.entry_tipo.connect('activate', self.buscar_tipo)
        hbox.pack_start(self.entry_tipo, False, False, 20)
        self.label_tipo = gtk.Label('Seleccione un tipo')
        self.label_tipo.set_alignment(0, 0.5)
        hbox.pack_start(self.label_tipo, True, True, 10)

        label = gtk.Label('CONCEPTO:')
        label.set_alignment(0, 0.5)
        hbox.pack_start(label, False, False, 10)
        self.entry_codigo = Widgets.Texto(4, DIR_TAB=False)
        self.entry_codigo.connect('activate', self.buscar_codigo)
        hbox.pack_start(self.entry_codigo, False, False, 20)

        self.button_cargar = Widgets.Button('buscar.png', "Buscar Fondos", 24)
        hbox.pack_end(self.button_cargar, False, False, 10)
        self.button_cargar.connect('clicked', self.cargar_deudas)

        hbox = gtk.HBox(True, 10)
        vbox_main.pack_start(hbox, True, True, 10)

        vbox = gtk.VBox(False, 0)
        hbox.pack_start(vbox, True, True, 10)

        hbox_fondos = gtk.HBox(False, 0)
        vbox.pack_start(hbox_fondos, False, False, 0)

        self.label_codigo = gtk.Label()
        self.label_codigo.set_markup('<big><b>Escoja un código</b></big>')
        self.label_codigo.set_alignment(0, 0.5)
        hbox_fondos.pack_start(self.label_codigo, False, False, 10)

        self.button_excel = Widgets.Button('excel.png', None, 24, 'Exportar a Excel')
        self.button_excel.connect('clicked', self.imprimir)
        hbox_fondos.pack_end(self.button_excel, False, False, 0)

        sw = gtk.ScrolledWindow()
        vbox.pack_start(sw, True, True, 10)
        sw.set_size_request(560, 10)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        model = gtk.ListStore(str, str, str, str, str, gobject.TYPE_PYOBJECT)
        self.treeview_fondo = Widgets.TreeView(model)
        self.columnas = ['Nº', 'CODIGO', 'REF', 'CLIENTE', 'SALDO']
        for i, columna in enumerate(self.columnas):
            cell_text = gtk.CellRendererText()
            tvcolumn = Widgets.TreeViewColumn(columna)
            tvcolumn.pack_start(cell_text, True)
            tvcolumn.set_attributes(cell_text, text=i)
            self.treeview_fondo.append_column(tvcolumn)
            tvcolumn.encabezado()
            if i == 3:
                tvcolumn.set_expand(True)
        sw.add(self.treeview_fondo)
        self.treeview_fondo.connect('row-activated', self.abrir_deuda)

        vbox = gtk.VBox(False, 0)
        hbox.pack_start(vbox, True, True, 10)

        self.label_fondo = gtk.Label()
        self.label_fondo.set_markup('<big><b>Escoja un fondo</b></big>')
        self.label_fondo.set_alignment(0, 0.5)
        vbox.pack_start(self.label_fondo, False, False, 10)

        sw = gtk.ScrolledWindow()
        vbox.pack_start(sw, True, True, 10)
        sw.set_size_request(560, 10)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        model = gtk.ListStore(str, str, str, str, gobject.TYPE_PYOBJECT)
        self.treeview_deposito = Widgets.TreeView(model)
        self.columnas = ['DIA', 'CONCEPTO', 'MONTO', 'ACUMULADO']
        for i, columna in enumerate(self.columnas):
            cell_text = gtk.CellRendererText()
            tvcolumn = Widgets.TreeViewColumn(columna)
            tvcolumn.pack_start(cell_text, True)
            tvcolumn.set_attributes(cell_text, text=i)
            self.treeview_deposito.append_column(tvcolumn)
            tvcolumn.encabezado()
            if i == 1:
                tvcolumn.set_expand(True)
        sw.add(self.treeview_deposito)
        self.show_all()

    def buscar_tipo(self, *args):
        tipo = self.entry_tipo.get_text()
        self.label_tipo.set_text('')
        self.tipo = None
        if tipo == 'D' or tipo == '0':
            self.tipo = 'D'
            self.label_tipo.set_text('DEUDAS POR COBRAR (-)')
        elif tipo == 'A' or tipo == '1':
            self.tipo = 'A'
            self.label_tipo.set_text('ABONOS POR PROCESAR (+)')
        else:
            self.tipo = 'DA'
            self.label_tipo.set_text('DEUDAS y ABONOS (+/-)')

    def buscar_codigo(self, *args):
        codigo = self.entry_codigo.get_text()
        self.label_codigo.set_text('')
        self.concepto = None
        if codigo:
            for p in self.dataLocal.get_productos():
                if p['codigo'] == codigo:
                    if p['tipo'] != 'FONDO':
                        print('concepto', p)
                        Widgets.Alerta('Error de Consulta', 'error.png', 'El concepto "%s" no es un Fondo' % p['nombre'])
                        break
                    self.label_codigo.set_markup('<big><b>%s</b></big>' % p['nombre'])
                    self.concepto = p
                    break
            if self.concepto:
                self.cargar_deudas()
                self.treeview_fondo.grab_focus()
                return
        self.entry_codigo.set_text('')
        self.entry_codigo.grab_focus()

    def cargar_deudas(self, *args):
        data = {
            'json': json.dumps({
                'concepto': self.concepto,
                'tipo': self.tipo
            })
        }
        respuesta = self.http.load('deudas-global', data)
        if respuesta:
            if 'deudas' in respuesta:
                i = 0
                model = self.treeview_fondo.get_model()
                model.clear()
                for d in respuesta['deudas']:
                    i += 1
                    if d['cliente'][:3] == 'PAD':
                        n = d['cliente'].find('(')
                        codigo = d['cliente'][4:n - 1]
                        m = d['cliente'].find(')')
                        referencia = d['cliente'][n + 1:m]
                        cliente = d['cliente'][m + 2:]
                    else:
                        n = d['cliente'].find(' ')
                        referencia = d['cliente'][:n]
                        m = d['cliente'].find('(')
                        codigo = d['cliente'][m + 1: -1]
                        cliente = d['cliente'][n + 1:m]

                    model.append([i, codigo, referencia, cliente, Widgets.currency(d['monto']), d])

                model = self.treeview_deposito.get_model()
                model.clear()

    def abrir_deuda(self, *args):
        print('abrir deuda')
        path, column = self.treeview_fondo.get_cursor()
        path = int(path[0])
        model = self.treeview_fondo.get_model()
        data = {
            'json': json.dumps({
                'fondo': model[path][len(model[path]) - 1]
            })
        }
        respuesta = self.http.load('deudas-detalle', data)
        if respuesta:
            if 'deudas' in respuesta:
                self.label_fondo.set_markup('<big><b>%s</b></big>' % model[path][1])
                model = self.treeview_deposito.get_model()
                i = 0
                acumulado = 0
                model.clear()
                for d in respuesta['deudas']:
                    i += 1
                    acumulado += d['currency']
                    model.prepend([d['dia'], d['concepto'], Widgets.currency(d['currency']), Widgets.currency(acumulado), d])

    def imprimir(self, *args):
        cabeceras = ['Nº', 'CODIGO', 'REF', 'CLIENTE', 'SALDO']
        widths = [1.2, 2, 3, 10, 2]
        filas = []
        for row in self.treeview_fondo.get_model():
            print(row)
            filas.append(list(row)[:-1])
        reporte = Impresion.Excel('Reporte de %s' % self.label_tipo.get_text(),
                                  'Hora de Impresión: %s' % (datetime.datetime.now().strftime('%H:%M:%S %d/%m/%Y')),
                                  cabeceras, filas, widths)
        a = os.path.abspath(reporte.archivo)
        if os.name == 'nt':
            com = 'cd "%s" & start reporte.xls' % a[:-12]
            print com
            os.system(com)
        else:
            os.system('xdg-open ' + a)



class GenerarDeuda(gtk.Window):

    concepto = None
    tipo = None
    DIAS = ['', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

    def __init__(self, http, cliente, concepto):
        super(GenerarDeuda, self).__init__()

        self.http = http
        self.cliente = cliente
        self.concepto = concepto.copy()

        self.set_title('Generar Deuda: ')
        self.set_size_request(400, 500)

        vbox_main = gtk.VBox(False, 0)
        self.add(vbox_main)

        hbox = gtk.HBox(False, 10)
        vbox_main.pack_start(hbox, False, False, 5)

        frame = gtk.Frame('Información de Cŕedito')
        hbox.pack_start(frame, True, True, 10)

        vbox = gtk.VBox(True, 0)
        frame.add(vbox)

        hbox = gtk.HBox(False, 10)
        vbox.pack_start(hbox, False, False, 5)

        label = gtk.Label('CLIENTE:')
        label.set_alignment(0, 0.5)
        hbox.pack_start(label, False, False, 10)
        label = gtk.Label(self.cliente['nombre'])
        label.set_alignment(0, 0.5)
        hbox.pack_end(label, False, False, 10)

        hbox = gtk.HBox(False, 10)
        vbox.pack_start(hbox, False, False, 5)

        label = gtk.Label('CONCEPTO:')
        label.set_alignment(0, 0.5)
        hbox.pack_start(label, False, False, 10)
        self.entry_detalle = Widgets.Texto(12)
        hbox.pack_end(self.entry_detalle, False, False, 10)
        label = gtk.Label(self.concepto['nombre'])
        label.set_alignment(0, 0.5)
        hbox.pack_end(label, False, False, 10)

        hbox_main = gtk.HBox(False, 0)
        vbox_main.pack_start(hbox_main, False, False, 0)


        frame1 = gtk.Frame('Plan de Pago')
        frame1.set_size_request(200, 180)
        hbox_main.pack_start(frame1, True, True, 10)

        vbox = gtk.VBox(True, 0)
        frame1.add(vbox)

        hbox = gtk.HBox(False, 10)
        vbox.pack_start(hbox, False, False, 5)

        label = gtk.Label('INICIO:')
        label.set_alignment(0, 0.5)
        hbox.pack_start(label, False, False, 10)
        self.entry_fecha = Widgets.FechaSpin()
        self.entry_fecha.connect('changed', self.cambiar_dias)
        hbox.pack_end(self.entry_fecha, False, False, 10)

        hbox = gtk.HBox(False, 10)
        vbox.pack_start(hbox, False, False, 5)

        label = gtk.Label('TOTAL:')
        label.set_alignment(0, 0.5)
        hbox.pack_start(label, False, False, 10)
        self.entry_total = Widgets.Numero(10, null=False)
        self.entry_total.connect('activate', self.set_total)
        hbox.pack_end(self.entry_total, False, False, 10)

        hbox = gtk.HBox(False, 10)
        vbox.pack_start(hbox, False, False, 5)

        self.label_cuota = gtk.Label('CUOTA 1:')
        self.label_cuota.set_alignment(0, 0.5)
        hbox.pack_start(self.label_cuota, False, False, 10)
        self.entry_cuota = Widgets.Numero(10)
        hbox.pack_end(self.entry_cuota, False, False, 10)
        self.entry_cuota.connect('activate', self.add_cuota)

        hbox = gtk.HBox(False, 10)
        vbox.pack_start(hbox, False, False, 5)

        label = gtk.Label('SALDO:')
        label.set_alignment(0, 0.5)
        hbox.pack_start(label, False, False, 10)
        self.label_saldo = gtk.Label('')
        label.set_alignment(0, 0.5)
        hbox.pack_end(self.label_saldo, False, False, 10)



        frame1 = gtk.Frame('Días para cobrar')
        frame1.set_size_request(110, 180)
        hbox_main.pack_start(frame1, False, False, 10)

        vbox = gtk.VBox(True, 0)
        frame1.add(vbox)

        self.check_dias = []

        check_lunes = gtk.CheckButton('Lunes')
        vbox.pack_start(check_lunes, False, False, 5)
        check_lunes.set_active(True)
        self.check_dias.append(check_lunes)

        check_martes = gtk.CheckButton('Martes')
        vbox.pack_start(check_martes, False, False, 5)
        check_martes.set_active(True)
        self.check_dias.append(check_martes)

        check_miercoles = gtk.CheckButton('Miércoles')
        vbox.pack_start(check_miercoles, False, False, 5)
        check_miercoles.set_active(True)
        self.check_dias.append(check_miercoles)

        check_jueves = gtk.CheckButton('Jueves')
        vbox.pack_start(check_jueves, False, False, 5)
        check_jueves.set_active(True)
        self.check_dias.append(check_jueves)

        check_viernes = gtk.CheckButton('Viernes')
        vbox.pack_start(check_viernes, False, False, 5)
        check_viernes.set_active(True)
        self.check_dias.append(check_viernes)

        check_sabado = gtk.CheckButton('Sábado')
        vbox.pack_start(check_sabado, False, False, 5)
        check_sabado.set_active(True)
        self.check_dias.append(check_sabado)

        check_domingo = gtk.CheckButton('Domingo')
        vbox.pack_start(check_domingo, False, False, 5)
        self.check_dias.append(check_domingo)

        hbox = gtk.HBox(True, 10)
        vbox_main.pack_start(hbox, True, True, 10)

        vbox = gtk.VBox(False, 0)
        hbox.pack_start(vbox, True, True, 10)

        sw = gtk.ScrolledWindow()
        vbox.pack_start(sw, True, True, 10)
        sw.set_size_request(560, 10)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        model = gtk.ListStore(int, str, str, str)
        self.treeview = Widgets.TreeView(model)
        self.columnas = ['CUOTA', 'FECHA', 'DIA', 'MONTO']
        for i, columna in enumerate(self.columnas):
            cell_text = gtk.CellRendererText()
            tvcolumn = Widgets.TreeViewColumn(columna)
            tvcolumn.pack_start(cell_text, True)
            tvcolumn.set_attributes(cell_text, text=i)
            self.treeview.append_column(tvcolumn)
            tvcolumn.encabezado()
            if i == 1:
                tvcolumn.set_expand(True)
        sw.add(self.treeview)

        check_lunes.connect('toggled', self.cambiar_dias)
        check_martes.connect('toggled', self.cambiar_dias)
        check_miercoles.connect('toggled', self.cambiar_dias)
        check_jueves.connect('toggled', self.cambiar_dias)
        check_viernes.connect('toggled', self.cambiar_dias)
        check_sabado.connect('toggled', self.cambiar_dias)
        check_domingo.connect('toggled', self.cambiar_dias)

        self.show_all()
        self.entry_fecha.hide_clear_button()

        # self.entry_total.grab_focus()

    def set_total(self, *args):
        total = self.entry_total.get_text()
        self.entry_cuota.set_text(total)
        self.label_saldo.set_markup('<b>%s</b>' % total)
        model = self.treeview.get_model()
        model.clear()
        self.entry_cuota.set_text('')

    def add_cuota(self, *args):
        cuota = self.entry_cuota.get_text()

        model = self.treeview.get_model()
        n = len(model)
        acumulado = 0
        for row in model:
            acumulado += float(row[3])
        total = float(self.entry_total.get_text())
        falta = total - acumulado
        if cuota == '':
            if falta == 0:
                self.guardar()
            else:
                Widgets.Alerta('Error de Formulario', 'error.png', 'Aún no ha terminado de fraccionar el crédito')
            return
        cuota = float(cuota)
        if falta == 0:
            Widgets.Alerta('Fin de Cronograma', 'error.png', 'Ya se terminó de fraccionar el crédito')
            self.entry_cuota.set_text('')
            self.entry_cuota.grab_focus()
            return
        if cuota > falta:
            return Widgets.Alerta('Error de Formulario', 'error.png', 'La cuota supera el saldo restante')
        saldo = falta - cuota
        model.append((n + 1, '', '', cuota))
        self.label_cuota.set_markup('CUOTA %s:' % (n + 2))
        self.label_saldo.set_markup('<b>%s</b>' % saldo)
        self.cambiar_dias()
        self.entry_total.grab_focus()
        return True

    def guardar(self):
        cronograma = []
        model = self.treeview.get_model()
        print('antes', self.concepto['nombre'])
        for row in model:
            dia = datetime.datetime.strptime(row[1], '%d/%m/%Y').strftime('%Y-%m-%d')
            if len(model) > 1:
                detalle = '%s %s (%s/%s)' % (self.concepto['nombre'], self.entry_detalle.get_text(), row[0], len(model))
            else:
                detalle = '%s %s' % (self.concepto['nombre'], self.entry_detalle.get_text())
            print('detalle', detalle)
            cronograma.append({
                'cuota': row[0],
                'dia': dia,
                'total': int(float(row[3]) * 100),
                'precio': int(float(row[3]) * 100),
                'detalle': detalle,
                'cantidad': 1000
            })

        self.concepto['nombre'] += ' ' + self.entry_detalle.get_text()
        print('concepto', self.concepto['nombre'])

        data = {
            'json': json.dumps({
                'cronograma': cronograma,
                'cliente': self.cliente,
                'concepto': self.concepto
            })
        }
        print('crear-cronograma', data)
        respuesta = self.http.load('crear-cronograma', data)
        if respuesta:
            print('cronograma OK')
            self.destroy()

    def cambiar_dias(self, *args):
        permitidos = []
        for i, c in enumerate(self.check_dias):
            if c.get_active():
                permitidos.append(i + 1)

        model = self.treeview.get_model()
        if permitidos:
            inicio = self.entry_fecha.get_date()
            for row in model:
                while not (inicio.isoweekday() in permitidos):
                    inicio += datetime.timedelta(1)

                row[1] = inicio.strftime('%d/%m/%Y')
                row[2] = self.DIAS[inicio.isoweekday()]
                inicio += datetime.timedelta(1)
        else:
            for row in model:
                row[1] = ''
                row[2] = ''


class EditarDeuda(gtk.Dialog):

    def __init__(self, padre, deuda):
        super(EditarDeuda, self).__init__(flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        ventanas = gtk.window_list_toplevels()
        self.padre = padre
        self.http = padre.http
        self.deuda = deuda
        parent = ventanas[0]
        for v in ventanas:
            if v.is_active():
                parent = v
                break
        self.set_modal(True)
        self.set_transient_for(parent)
        self.set_title('Editar Deuda')
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect('delete_event', self.cerrar)

        main_hbox = gtk.HBox(False, 0)

        self.vbox.pack_start(main_hbox, False, False, 10)

        frame2 = gtk.Frame('Cliente')
        frame2.set_size_request(200, 135)
        main_hbox.pack_start(frame2, True, True, 10)

        hbox = gtk.HBox(False, 0)
        frame2.add(hbox)
        tabla = gtk.Table(3, 3)
        tabla.set_row_spacings(10)
        tabla.set_col_spacings(10)
        hbox.pack_start(tabla, False, False, 10)

        label = gtk.Label('TIPO:')
        label.set_alignment(0, 0.5)
        tabla.attach(label, 0, 1, 0, 1)
        self.entry_tipo_cli = Widgets.Texto(4)
        tabla.attach(self.entry_tipo_cli, 1, 2, 0, 1)

        label = gtk.Label('CODIGO:')
        label.set_alignment(0, 0.5)
        tabla.attach(label, 0, 1, 1, 2)
        self.entry_cliente = Widgets.Texto(11)
        tabla.attach(self.entry_cliente, 1, 3, 1, 2)

        label = gtk.Label('DIA:')
        label.set_alignment(0, 0.5)
        tabla.attach(label, 0, 1, 2, 3)
        self.entry_fecha = Widgets.Fecha()
        tabla.attach(self.entry_fecha, 1, 3, 2, 3)

        but_ok = Widgets.Button('aceptar.png', 'EDITAR')
        but_cancel = Widgets.Button('cancelar.png', 'CANCELAR')

        self.add_action_widget(but_ok, gtk.RESPONSE_OK)
        self.add_action_widget(but_cancel, gtk.RESPONSE_CANCEL)

    def iniciar(self):
        self.show_all()
        if self.run() == gtk.RESPONSE_OK:
            tipo = self.entry_tipo_cli.get_text()
            if tipo == '':
                tipo = 'PAD'
            data = {
                'json': json.dumps({
                    'tipo': tipo,
                    'codigo': self.entry_cliente.get_text(),
                    'dia': self.entry_fecha.get_date().strftime('%Y-%m-%d'),
                    'deuda': self.deuda
                })
            }
            print('editar deuda ', data)
            self.http.load('editar-deuda', data)
        self.cerrar()

    def cerrar(self, *args):
        self.destroy()


class ClienteDialogo(Widgets.Dialogo):

    def __init__(self):
        super(ClienteDialogo, self).__init__('Crear Nuevo Cliente')

        frame = gtk.Frame()
        frame.set_border_width(5)
        frame.set_label('')

        self.vbox.pack_start(frame, True, True, 0)

        vbox = gtk.VBox(True, 0)
        frame.add(vbox)

        hbox = gtk.HBox(False, 5)
        label = gtk.Label('Código:')
        self.entry_codigo = Widgets.Texto(32)

        hbox.pack_start(label, False, False, 15)
        hbox.pack_start(self.entry_codigo, True, True, 15)

        vbox.pack_start(hbox, False, False, 15)

        hbox = gtk.HBox(False, 0)
        label = gtk.Label('Nombre Corto:')
        self.entry_corto = Widgets.Texto(256)

        hbox.pack_start(label, False, False, 15)
        hbox.pack_start(self.entry_corto, True, True, 15)

        vbox.pack_start(hbox, False, False, 15)

        hbox = gtk.HBox(False, 0)
        label = gtk.Label('Nombre:')
        self.entry_nombre = Widgets.Texto(256)

        hbox.pack_start(label, False, False, 15)
        hbox.pack_start(self.entry_nombre, True, True, 15)

        vbox.pack_start(hbox, False, False, 15)

        self.entry_corto.connect('key-release-event', self.repetir)

    def repetir(self, *args):
        self.entry_nombre.set_text(self.entry_corto.get_text())


if __name__ == '__main__':
    from Http import Http
    # http = Http([])
    # http.login('daniel', 'ontralog', 'clave')
    c = ClienteDialogo()
    c.iniciar()

    gtk.main()