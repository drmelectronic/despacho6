#! /usr/bin/python
# -*- encoding: utf-8 -*-

import datetime
import json

import gobject
import threading
import time

import Widgets
import gtk

from Http import Http
DIA_SEMANA = [
    'LUNES',
    'MARTES',
    'MIÉRCOLES',
    'JUEVES',
    'VIERNES',
    'SÁBADO',
    'DOMINGO'
]

COMBO_LIST_MESES = [
    ('Enero', 1),
    ('Febrero', 2),
    ('Marzo', 3),
    ('Abril', 4),
    ('Mayo', 5),
    ('Junio', 6),
    ('Julio', 7),
    ('Agosto', 8),
    ('Setiembre', 9),
    ('Octubre', 10),
    ('Noviembre', 11),
    ('Diciembre', 12)
]

class Adelantos(Widgets.Alerta_TreeView):

    def __init__(self, http, data):
        self.http = http
        self.clave = data['clave']
        self.unidad = data['unidad']
        self.nombre = data['nombre']
        self.dia = data['dia']
        self.ruta = data['ruta']
        respuesta = self.http.load('ver-adelantos', {
            'json': json.dumps({
                'clave': data['clave'],
                'unidad': data['unidad'],
                'dia': data['dia']
            })
        })
        tabla = []
        total = 0
        self.limitar_adelanto = False
        self.maximo_adelanto = 0
        self.tiene_saldos_pendientes = False
        hoy = datetime.date.today()
        self.dias_anteriores = {}
        if respuesta:
            for r in respuesta:
                dia = datetime.datetime.strptime(r['dia'], '%Y-%m-%d').date()
                if dia != hoy:
                    if r['dia'] not in self.dias_anteriores:
                        self.dias_anteriores[r['dia']] = []
                    self.dias_anteriores[r['dia']].append(r)
                    self.tiene_saldos_pendientes = True
            for r in respuesta:
                dia = datetime.datetime.strptime(r['dia'], '%Y-%m-%d').date()
                mostrar = False
                if self.tiene_saldos_pendientes:
                    if dia < hoy:
                        mostrar = True
                else:
                    mostrar =True
                if mostrar:
                    tabla.append((r['dia'], r['hora'], r['numero'], r['concepto'], r['monto'] / 100., r['despachador'], r['id']))
                    total += r['monto']
                    if r['monto'] > 0:
                        self.limitar_adelanto = True
                    self.maximo_adelanto = r['monto'] / 100.
                    print('maximo adelanto', self.maximo_adelanto)

        super(Adelantos, self).__init__(
            'Reporte de Adelantos',
            '<b>TRABAJADOR: %s\nDIA: %s</b>' % (data['nombre'], data['dia']),
            'Balance',
            ('DIA', 'HORA', 'NUMERO', 'CONCEPTO', 'MONTO', 'DESPACHADOR'),
            tabla
        )
        self.set_size_request(420, 500)
        hbox = gtk.HBox(False, 0)
        self.vbox.pack_start(hbox, False, False, 10)

        self.entry_saldo = Widgets.Entry(7)
        self.entry_saldo.set_text(str(total / 100.))
        self.entry_saldo.set_property('editable', False)

        hbox.pack_end(self.entry_saldo, False, False, 5)
        label = gtk.Label()
        if total > 0:
            label.set_markup('<span color="#0B0">Saldo a Favor</span>')
        else:
            label.set_markup('<span color="#B00">Adelantado</span>')
        hbox.pack_end(label, False, False, 5)
        hbox.show_all()

        self.but_ok.hide_all()

        if self.tiene_saldos_pendientes:
            self.set_title('Saldo Días Anteriores')
            self.set_background('#900')
            self.set_mensaje('\nSALDO DÍAS ANTERIORES\n')
            self.set_text_color('#FFF')

            button = Widgets.Button('caja.png', 'Completar')
            self.action_area.pack_end(button, False, False, 10)
            button.connect('clicked', self.completar)
            button.show_all()
        else:
            button = Widgets.Button('dinero.png', '_Adelantar')
            self.action_area.pack_end(button, False, False, 10)
            button.connect('clicked', self.adelantar)
            button.show_all()

    def completar(self, *args):
        contador = 0
        suma = 0
        for dia in self.dias_anteriores:
            contador += 1
            inicio = False
            fin = False
            if contador == 1:
                inicio = True
            if contador == len(self.dias_anteriores):
                fin = True
            monto = 0
            for i in self.dias_anteriores[dia]:
                monto += i['monto']
            datos = {
                'json': json.dumps({
                    'nombre': self.nombre,
                    'clave': self.clave,
                    'unidad': self.unidad,
                    'adelantos': self.dias_anteriores[dia],
                    'monto': monto,
                    'dia': dia,
                    'ruta': self.ruta,
                    'inicio': inicio,
                    'fin': fin,
                    'suma': suma
                })
            }
            respuesta = self.http.load('completar-pago', datos)
            if respuesta:
                suma += respuesta['entregado']
                continue
            else:
                break
        self.destroy()

    def adelantar(self, *args):
        dialogo = Widgets.Alerta_Numero(
            'Adelantar Pago',
            'dinero.png', 'Escriba la cantidad de dinero a entregar', 10, False)
        monto = dialogo.iniciar()
        dialogo.cerrar()

        data = {
            'json': json.dumps({
                'monto': monto,
                'clave': self.clave,
                'unidad': self.unidad,
                'nombre': self.nombre,
                'dia': self.dia,
                'ruta': self.ruta
            })
        }
        if self.limitar_adelanto:
            print(self.maximo_adelanto, '<', monto, self.maximo_adelanto < monto)
            if self.maximo_adelanto < monto:
                Widgets.Alerta('Límite de Adelanto', 'error.png', 'No puede entregar más del Saldo a Favor')
                return
        else:
            if self.maximo_adelanto - float(monto) < -30:
                Widgets.Alerta('Límite de Adelanto', 'error.png', 'No puede adelantar más de 50 soles en total')
                return

        if monto:
            respuesta = self.http.load('adelantar-pago', data)
            if respuesta:
                self.but_ok.clicked()


class Produccion(gtk.Window):

    def __init__(self, http, datos):

        super(Produccion, self).__init__(gtk.WINDOW_TOPLEVEL)
        self.http = http
        self.ruta = datos['ruta']
        self.set_title('Producciones de Flota')

        vbox_main = gtk.VBox(False, 5)
        self.add(vbox_main)

        hbox = gtk.HBox(False, 5)
        vbox_main.pack_start(hbox, False, False, 5)

        hbox.pack_start(gtk.Label('Año'), False, False, 5)
        self.combo_year = Widgets.ComboBox()
        lista = []
        inicio = 2016
        actual = datetime.datetime.now().year
        while inicio <= actual:
            lista.append((str(actual), actual))
            actual -= 1
        self.combo_year.set_lista(lista)
        hbox.pack_start(self.combo_year, False, False, 5)

        hbox.pack_start(gtk.Label('Mes'), False, False, 5)
        self.combo_month = Widgets.ComboBox()
        self.combo_month.set_lista(COMBO_LIST_MESES)
        self.combo_month.set_id(datetime.datetime.now().month)
        hbox.pack_start(self.combo_month, False, False, 5)

        button = Widgets.Button('buscar.png', 'Cargar')
        button.connect('clicked', self.cargar_mes)
        hbox.pack_start(button, False, False, 5)
        button = Widgets.Button('nuevo.png', 'Crear Nuevo Día')
        button.connect('clicked', self.nueva_produccion)
        hbox.pack_start(button, False, False, 5)

        self.treeview = Widgets.TreeViewId('Producciones',
                                           ('DIA', 'D/S', 'PRODUCCION', 'VIAJES', '%', '#UNID', '#COND', '#COBR', 'BLOQ', 'DISTR', 'PAGADO'))

        self.treeview.set_size_request(620, 250)
        self.treeview.set_border_width(5)
        self.treeview.set_liststore(
            (str, str, str, str, str, str, str, str, bool, bool, bool, gobject.TYPE_PYOBJECT)
        )
        self.treeview.treeview.connect('cursor-changed', self.row_selected)
        vbox_main.pack_start(self.treeview, True, True, 5)

        hbox = gtk.HBox(False, 5)
        vbox_main.pack_start(hbox, False, False, 5)

        self.saldarBtn = Widgets.Button('dinero.png', 'Saldar Pagos')
        self.saldarBtn.connect('clicked', self.saldar)
        hbox.pack_end(self.saldarBtn, False, False, 5)

        self.generarBtn = Widgets.Button('cuenta.png', 'Generar Pagos')
        self.generarBtn.connect('clicked', self.generar)
        hbox.pack_end(self.generarBtn, False, False, 5)

        self.actualizarBtn = Widgets.Button('actualizar.png', 'Actualizar')
        self.actualizarBtn.connect('clicked', self.actualizar)
        hbox.pack_end(self.actualizarBtn, False, False, 5)

        self.show_all()

        self.generarBtn.hide_all()
        self.saldarBtn.hide_all()
        self.actualizarBtn.hide_all()

    def saldar(self, *args):
        p = self.get_row()
        if p:
            if p['guardado']:
                Saldar(self, p)

    def row_selected(self, *args):
        selected = self.get_row()
        if selected:
            if selected['guardado']:
                self.generarBtn.hide_all()
                self.saldarBtn.show_all()
            else:
                self.generarBtn.show_all()
                self.saldarBtn.hide_all()
            if selected['bloqueado']:
                self.actualizarBtn.hide_all()
            else:
                self.generarBtn.hide_all()
                self.actualizarBtn.show_all()
            if selected['cancelado']:
                self.saldarBtn.set_text('Ver Pagos')
            else:
                self.saldarBtn.set_text('Saldar Pagos')

    def get_row(self):
        selected = self.treeview.get_selected()
        if selected:
            return selected[len(selected) - 1]

    def replace_row(self, prod):
        if prod:
            model = self.treeview.get_model()
            for p in model:
                if prod['id'] == p[11]['id']:
                    p[0] = prod['dia']
                    p[1] = DIA_SEMANA[datetime.datetime.strptime(prod['dia'], '%Y-%m-%d').weekday()]
                    p[2] = prod['produccion']
                    p[3] = prod['vueltas']
                    p[4] = prod['porcentaje']
                    p[5] = prod['num_unidades']
                    p[6] = prod['num_conductores']
                    p[7] = prod['num_cobradores']
                    p[8] = prod['bloqueado']
                    p[9] = prod['guardado']
                    p[10] = prod['cancelado']
                    p[11] = prod

    def actualizar(self, *args):
        p = self.get_row()
        if p:
            datos = {
                'json': json.dumps({
                    'id': p['id']
                })
            }
            prod = self.http.load('actualizar-produccion', datos)
            if prod['porcentaje'] == 100:
                dialogo = Widgets.Alerta_SINO('Bloquear', 'bloqueado.png', 'La producción ya está completa,\nquiere bloquear el día?')
                bloquear = dialogo.iniciar()
                dialogo.cerrar()
                if bloquear:
                    prod = self.http.load('bloquear-produccion', datos)
                    self.generarBtn.show_all()
                    self.actualizarBtn.hide_all()
            self.replace_row(prod)

    def generar(self, *args):
        prod = self.get_row()
        if prod:
            if not prod['bloqueado']:
                Widgets.Alerta('Error', 'error.png', 'Debe bloquear el día para que no hayan modificaciones')
                return
            if prod['guardado']:
                Widgets.Alerta('Error', 'error.png', 'Ya ha sido hecha la distribución de la producción')
                return
            if prod['porcentaje'] < 100:
                Widgets.Alerta('Error', 'error.png', 'Todavía hay viajes sin boletaje')
                return
            Distribucion(self, prod)

    def get_month(self):
        return self.combo_month.get_id()

    def get_year(self):
        return self.combo_year.get_id()

    def create_row(self, p):
        return p['dia'], DIA_SEMANA[datetime.datetime.strptime(p['dia'], '%Y-%m-%d').weekday()],p['produccion'], p['vueltas'], p['porcentaje'], p['num_unidades'], p['num_conductores'],\
               p['num_cobradores'], p['bloqueado'], p['guardado'], p['cancelado'], p

    def llenar_tabla(self, producciones):
        if producciones:
            model = self.treeview.get_model()
            model.clear()
            for p in producciones:
                model.append(self.create_row(p))

    def add_row(self, p):
        if p:
            model = self.treeview.get_model()
            model.append(self.create_row(p))

    def cargar_mes(self, *args):
        datos = {
            'json': json.dumps({
                'month': self.get_month(),
                'year': self.get_year(),
                'ruta': self.ruta
            })
        }
        producciones = self.http.load('ver-producciones', datos)
        self.llenar_tabla(producciones)

    def nueva_produccion(self, *args):
        datos = {
            'json': json.dumps({
                'month': self.get_month(),
                'year': self.get_year(),
                'ruta': self.ruta
            })
        }
        produccion = self.http.load('crear-produccion', datos)
        self.add_row(produccion)


class Distribucion(gtk.Window):

    def __init__(self, padre, prod):
        super(Distribucion, self).__init__(gtk.WINDOW_TOPLEVEL)
        self.produccion = prod
        self.padre = padre
        self.produccion_reemplazar = None
        self.http = padre.http
        self.set_size_request(500, 120)
        self.set_title('Procesando...')

        vbox_main = gtk.VBox(False, 5)
        self.add(vbox_main)

        hbox = gtk.HBox(False, 10)
        vbox_main.pack_start(hbox, False, False, 15)
        self.progress_bar = gtk.ProgressBar()
        hbox.pack_start(self.progress_bar, True, True, 10)

        hbox = gtk.HBox(False, 10)
        vbox_main.pack_start(hbox, False, False, 10)

        self.cancelarBtn = Widgets.Button('cancelar.png', 'Cancelar')
        self.cancelarBtn.connect('clicked', self.cancelar)
        hbox.pack_end(self.cancelarBtn, False, False, 5)

        self.reintentarBtn = Widgets.Button('actualizar.png', 'Reintentar')
        self.reintentarBtn.connect('clicked', self.reintentar)
        hbox.pack_end(self.reintentarBtn, False, False, 5)

        self.worker = WorkerPago(self)
        self.worker.start()
        self.show_all()

    def update_progress(self):
        progress = 100. * self.worker.counter / self.worker.total
        self.progress_bar.set_fraction(progress / 100)
        self.progress_bar.set_text('%d%%' % progress)
        if self.worker.error:
            self.reintentarBtn.show_all()
        return False

    def reintentar(self, *args):
        self.worker.error = False
        self.reintentarBtn.hide_all()

    def cancelar(self, *args):
        self.worker.done = True
        self.destroy()

    def on_quit(self, *args):
        self.worker.done = True

    def actualizar_produccion(self):
        if self.produccion_reemplazar:
            self.padre.replace_row(self.produccion_reemplazar)
            if self.produccion_reemplazar['guardado']:
                self.padre.generarBtn.hide_all()
                self.padre.saldarBtn.show_all()


class WorkerPago(threading.Thread):

    def __init__(self, window):
        super(WorkerPago, self).__init__()
        self.window = window
        self.http = window.http

    def run(self):
        data = {
            'json': json.dumps(self.window.produccion)
        }
        reporte = self.http.load('cargar-reporte-produccion', data)
        if reporte:
            self.items = reporte
            self.counter = 3
            self.total = len(self.items) + 4
            self.done = False
            self.error = False
            gobject.idle_add(self.window.update_progress)

            data = {
                'json': json.dumps(self.window.produccion)
            }
            respuesta = self.http.load('borrar-produccion-dia', data)
            print('borrar', data, respuesta)
            if respuesta:
                print('items', len(self.items))
                self.counter += 1
                gobject.idle_add(self.window.update_progress)
                while len(self.items):
                    if self.done:
                        break
                    if self.error:
                        time.sleep(1)  # esperar accion del usuario

                    item = dict(self.items[0])
                    item['ruta'] = self.window.produccion['ruta']
                    data = {
                        'json': json.dumps(item)
                    }
                    print('item', item)
                    respuesta = self.http.load('generar-pago-produccion', data)
                    if respuesta:
                        self.counter += 1
                    else:
                        self.error = True
                    self.items = self.items[1:]
                    gobject.idle_add(self.window.update_progress)

                print('items', len(self.items))
                if len(self.items) == 0:
                    print('terminar')
                    data = {
                        'json': json.dumps({
                            'id': self.window.produccion['id']
                        })
                    }
                    respuesta = self.http.load('guardar-produccion-dia', data)
                    print('guardar-produccion-dia', data, respuesta)
                    if respuesta:
                        self.window.produccion_reemplazar = respuesta
                        gobject.idle_add(self.window.actualizar_produccion)
                    else:
                        self.error = True
                    print('finalizado')
        gobject.idle_add(self.window.cancelar)


class Saldar(gtk.Window):

    def __init__(self, padre, produccion):

        super(Saldar, self).__init__(gtk.WINDOW_TOPLEVEL)
        self.http = padre.http
        self.produccion = produccion

        self.set_title('Distribución Día %s' % produccion['dia'])

        vbox_main = gtk.VBox(False, 5)
        self.add(vbox_main)

        hbox = gtk.HBox(False, 5)
        vbox_main.pack_start(hbox, False, False, 5)

        self.por_pagar = Widgets.TreeViewId('', ('NOMBRE', 'TOTAL', 'ADELANTADO', 'SALDO'))

        self.por_pagar.set_size_request(500, 300)
        self.por_pagar.set_border_width(5)
        self.por_pagar.set_liststore(
            (str, str, str, str, gobject.TYPE_PYOBJECT)
        )
        self.por_pagar.get_model().set_sort_column_id(0, gtk.SORT_ASCENDING)
        self.por_pagar.connect('activado', self.row_selected)

        self.pagados = Widgets.TreeViewId('', ('NOMBRE', 'TOTAL', 'PAGADO', 'SALDO'))

        self.pagados.set_size_request(500, 300)
        self.pagados.set_border_width(5)
        self.pagados.set_liststore(
            (str, str, str, str, gobject.TYPE_PYOBJECT)
        )
        self.pagados.get_model().set_sort_column_id(0, gtk.SORT_ASCENDING)

        self.notebook = Widgets.Notebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.notebook.insert_page(self.por_pagar, gtk.Label('POR PAGAR'))
        self.notebook.insert_page(self.pagados, gtk.Label('PAGADOS'))
        self.notebook.set_homogeneous_tabs(True)
        self.notebook.child_set_property(self.por_pagar, 'tab-expand', True)

        hbox.pack_start(self.notebook, True, True, 10)

        hbox = gtk.HBox(False, 5)
        vbox_main.pack_start(hbox, False, False, 5)

        label = gtk.Label()
        label.set_markup('<b>SALDO POR PAGAR</b>')
        hbox.pack_start(label, False, False, 5)

        hbox = gtk.HBox(False, 5)
        vbox_main.pack_start(hbox, False, False, 5)

        self.entry_total_unidades = Widgets.Entry(7)
        self.entry_total_unidades.set_property('editable', False)
        hbox.pack_end(self.entry_total_unidades, False, False, 5)
        hbox.pack_end(gtk.Label('Unidades'), False, False, 5)

        self.entry_total_trabajadores = Widgets.Entry(7)
        self.entry_total_trabajadores.set_property('editable', False)
        hbox.pack_end(self.entry_total_trabajadores, False, False, 5)
        hbox.pack_end(gtk.Label('Trabajadores'), False, False, 5)


        self.show_all()

        data = {
            'json': json.dumps(self.produccion)
        }
        adelantos = self.http.load('ver-adelantos-dia', data)
        if adelantos:
            self.compilar_adelantos(adelantos)

        self.menu = gtk.Menu()
        item1 = gtk.MenuItem('Ver Pagos')
        item1.connect('activate', self.ver_pagos)
        self.menu.append(item1)
        self.por_pagar.connect('button-release-event', self.on_release_button)
        self.pagados.connect('button-release-event', self.on_release_button)

    def on_release_button(self, treeview, event):
        self.cliente_selected = self.get_row(treeview)
        print('cliente', self.cliente_selected)
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            t = event.time
            pthinfo = treeview.treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.treeview.grab_focus()
                treeview.treeview.set_cursor(path, col, 0)
                self.menu.popup(None, None, None, event.button, t)
                self.menu.show_all()
            return True

    def ver_pagos(self, *args):
        data = {
            'clave': self.cliente_selected['clave'],
            'unidad': self.cliente_selected['unidad'],
            'nombre': self.cliente_selected['nombre'],
            'dia': self.produccion['dia'],
            'ruta': self.produccion['ruta']
        }
        dialog = Adelantos(self.http, data)
        dialog.action_area.hide_all()
        dialog.iniciar()
        dialog.cerrar()

    def row_selected(self, *args):
        selected = self.get_row(self.por_pagar)
        if selected:
            print('pagar', selected['saldo'])
            dialogo = Widgets.Alerta_SINO('Completar Pago', 'dinero.png', 'Confirme que va a pagar a\n' +
                                          '%s\nMonto: <b>%s</b>' % (selected['nombre'], selected['saldo'] / 100.))
            respuesta = dialogo.iniciar()
            dialogo.cerrar()
            if respuesta:
                datos = {
                    'json': json.dumps({
                        'nombre': selected['nombre'],
                        'clave': selected['clave'],
                        'unidad': selected['unidad'],
                        'adelantos': None,
                        'monto': selected['saldo'],
                        'dia': self.produccion['dia'],
                        'ruta': self.produccion['ruta'],
                        'inicio': True,
                        'fin': True
                    })
                }
                adelanto = self.http.load('completar-pago', datos)
                if adelanto:
                    pagado = self.delete_row(self.por_pagar, selected)
                    pagado['pagado'] = pagado['total']
                    pagado['saldo'] = 0
                    self.add_row(self.pagados, pagado)
                    if len(self.por_pagar.get_model()) == 0:
                        print('finalizar-produccion')
                        datos = {
                            'json': json.dumps(self.produccion)
                        }
                        respuesta = self.http.load('finalizar-produccion', datos)
                        if respuesta:
                            self.produccion['cancelado'] = True
                            self.padre.replace_row(self.produccion)
                            self.destroy()

    def get_row(self, treeview):
        selected = treeview.get_selected()
        if selected:
            return selected[len(selected) - 1]

    def replace_row(self, treeview, cliente):
        if cliente:
            model = treeview.get_model()
            for p in model:
                if cliente['id'] == p[6]['id']:
                    p[0] = cliente['nombre']
                    p[1] = cliente['total'] / 100.
                    p[2] = cliente['pagado'] / 100.
                    p[3] = cliente['saldo'] / 100.
                    p[4] = cliente

    def create_row(self, p):
        return p['nombre'], p['total'] / 100., p['pagado'] / 100., p['saldo'] / 100., p

    def llenar_tabla(self, treeview, producciones):
        if producciones:
            model = treeview.get_model()
            model.clear()
            for p in producciones:
                model.append(self.create_row(p))

    def delete_row(self, treeview, cliente):
        if cliente:
            print('borrar', cliente)
            model = treeview.get_model()
            i = 0
            for p in model:
                print('comparar', p[4])
                if cliente['clave'] == p[4]['clave'] and cliente['unidad'] == p[4]['unidad']:
                    c = p[4]
                    treeiter = model.get_iter(i)
                    model.remove(treeiter)
                    return c
                i += 1

    def add_row(self, treeview, p):
        if p:
            model = treeview.get_model()
            model.append(self.create_row(p))

    def compilar_adelantos(self, adelantos):
        unidades = {}
        trabajadores = {}
        for a in adelantos:
            if a['unidad']:
                if a['clave'] not in unidades:
                    unidades[a['clave']] = {
                        'total': 0,
                        'pagado': 0,
                        'saldo': 0,
                        'nombre': 'PAD %s' % a['nombre'],
                        'clave': a['clave'],
                        'unidad': True,
                        'cancelado': False
                    }
                u = unidades[a['clave']]
                if a['concepto'] == 'PAGO DEL DIA':
                    print('pago del dia', a['concepto'], a['monto'])
                    u['total'] += a['monto']
                    u['saldo'] += a['monto']
                    u['cancelado'] = u['cancelado'] or a['cancelado']
                else:
                    print('adelanto', a['concepto'], a['monto'])
                    u['saldo'] += a['monto']
                    u['pagado'] -= a['monto']
                    u['cancelado'] = u['cancelado'] or a['cancelado']
            else:
                if a['clave'] not in trabajadores:
                    trabajadores[a['clave']] = {
                        'total': 0,
                        'pagado': 0,
                        'saldo': 0,
                        'nombre': a['nombre'],
                        'clave': a['clave'],
                        'unidad': False,
                        'cancelado': False
                    }
                u = trabajadores[a['clave']]
                if a['concepto'] == 'PAGO DEL DIA':
                    u['total'] += a['monto']
                    u['saldo'] += a['monto']
                    u['cancelado'] = u['cancelado'] or a['cancelado']
                else:
                    u['saldo'] += a['monto']
                    u['pagado'] -= a['monto']
                    u['cancelado'] = u['cancelado'] or a['cancelado']
        pagados = []
        por_pagar = []
        total_unidades = 0
        total_trabajadores = 0
        for k in unidades:
            if unidades[k]['saldo']:
                por_pagar.append(unidades[k])
                total_unidades += unidades[k]['saldo']
            else:
                pagados.append(unidades[k])
                if not unidades[k]['cancelado']:
                    print('cancelar', unidades[k]['unidad'], unidades[k]['clave'])
                    datos = {
                        'json': json.dumps({
                            'ruta': self.produccion['ruta'],
                            'dia': self.produccion['dia'],
                            'unidad': unidades[k]['unidad'],
                            'clave': unidades[k]['clave']
                        })
                    }
                    self.http.load('cancelar-pagos', datos)
        for k in trabajadores:
            if trabajadores[k]['saldo']:
                por_pagar.append(trabajadores[k])
                total_trabajadores += trabajadores[k]['saldo']
            else:
                pagados.append(trabajadores[k])
                if not trabajadores[k]['cancelado']:
                    print('cancelar', trabajadores[k]['unidad'], trabajadores[k]['clave'])
                    datos = {
                        'json': json.dumps({
                            'ruta': self.produccion['ruta'],
                            'dia': self.produccion['dia'],
                            'unidad': trabajadores[k]['unidad'],
                            'clave': trabajadores[k]['clave']
                        })
                    }
                    self.http.load('cancelar-pagos', datos)
        self.llenar_tabla(self.por_pagar, por_pagar)
        self.llenar_tabla(self.pagados, pagados)

        self.entry_total_trabajadores.set_text(str(total_trabajadores / 100.))
        self.entry_total_unidades.set_text(str(total_unidades / 100.))

        if len(self.por_pagar.get_model()) == 0:
            if not self.produccion['cancelado']:
                print('finalizar-produccion')
                datos = {
                    'json': json.dumps(self.produccion)
                }
                self.http.load('finalizar-produccion', datos)


if __name__ == '__main__':
    data = {
        'nombre': 'TEMPORAL',
        'id': 1,
        'dia': '2019-01-31'
    }

    datos = {
        'ruta': 1,
    }
    http = Principal.Http([])
    a = Produccion(http, datos)
    gtk.main()