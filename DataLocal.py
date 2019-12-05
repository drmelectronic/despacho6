# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import base64
import json
import os

import models


class DataLocal(object):
    __instance = None
    http = None
    dataServer = {}
    dataDump = {}
    username = None
    password = None
    server = None
    sin_dns = None
    empresa = None
    empresa_id = None
    config_data = None
    EMPRESAS = [
        {
            'id': 1,
            'codigo': 'ECONAIN',
            'server': 'api.tcontur.com',
            'sin_dns': 'django-4eyifataca-uc.a.run.app'
        }
    ]

    def __new__(cls):
        if DataLocal.__instance is None:
            DataLocal.__instance = object.__new__(cls)
        return DataLocal.__instance

    def get_empresas(self):
        lista = []
        for e in self.EMPRESAS:
            lista.append([e['codigo'], e['id']])
        print('empresas', lista)
        return lista

    def set_empresa(self, i):
        for e in self.EMPRESAS:
            if e['id'] == i:
                self.server = e['server']
                self.sin_dns = e['sin_dns']
                self.empresa_id = e['id']
                self.empresa = e['codigo']
                break

    def load_config(self):
        try:
            a = os.path.abspath('outs/config.txt')
            f = open(a, 'r')
            data = f.read()
            f.close()
            js = json.loads(data)
        except:
            self.config_data = {}
        else:
            self.config_data = js

    def get_config(self, key):
        if key in self.config_data:
            return self.config_data[key]

    def load_main(self):
        try:
            a = os.path.abspath("outs/pdfcreator.dll")
            archivo = open(a, 'r')
            content = archivo.read()
            archivo.close()
            js = base64.b64decode(content)
            d = json.loads(js)
            self.username = d[u'username']
            self.password = d[u'password']
            self.set_empresa(d[u'empresa'])
        except:
            js = json.dumps({
                'username': '',
                'password': '',
                'empresa': ''
            })
            content = base64.b64encode(js)
            a = os.path.abspath("outs/pdfcreator.dll")
            archivo = open(a, 'w')
            archivo.write(content)
            archivo.close()
            self.usuario = ''
            self.password = ''
            self.empresa = None

    def set_main(self, username, password, usuario):
        empresa = usuario.get_empresa()
        if self.empresa is None and empresa is None:
            js = json.dumps({
                'username': username,
                'password': password,
                'empresa': empresa
            })
            content = base64.b64encode(js)
            a = os.path.abspath("outs/pdfcreator.dll")
            archivo = open(a, 'w')
            archivo.write(content)
            archivo.close()
        self.usuario = username
        self.password = password
        self.empresa = usuario.get_empresa()

    def load_data_file(self):
        try:
            a = os.path.abspath('outs/data.bkp')
            f = open(a, 'r')
            data = f.read()
            f.close()
            js = json.loads(data)
        except:
            self.dataDump = {}
        else:
            self.dataDump = js
        self.load_data_server()

    def load_data_server(self):
        keys = self.dataDump.keys()
        for k in keys:
            modelo = models.MODELOS[k]
            datos = self.dataDump[k]
            if datos:
                print('DATA LOADED:', k)
                self.dataServer[k] = []
                for d in datos:
                    if modelo:
                        try:
                            self.dataServer[k].append(modelo(d))
                        except KeyError:
                            del self.dataDump[k]
                            self.save_data_file()
                            print('NUEVA VERSION DE ' + k)
                            break
                    else:
                        self.dataServer[k].append(d)

    def save_data_file(self):
        print('DATA SAVED')
        a = os.path.abspath('outs/data.bkp')
        f = open(a, 'w')
        f.write(json.dumps(self.dataDump))
        f.close()

    def limpiar_data(self):
        self.dataServer = {}
        self.dataDump = {}
        self.save_data_file()

    def get_datos(self, key, actualizar=False):
        if not (key in self.dataServer):
            actualizar = True
        modelo = models.MODELOS[key]

        if actualizar:
            print('ACTUALIZAR DATOS', key)
            datos = self.http.load('/api/' + key, method='GET')
            self.dataDump[key] = datos
            self.save_data_file()

            if datos:
                self.dataServer[key] = []
                for d in datos:
                    if modelo:
                        objeto = modelo(d)
                        self.dataServer[key].append(objeto)
                    else:
                        self.dataServer[key].append(d)
            else:
                return []
        return self.dataServer[key]

    def get_dato(self, key, _id):
        if key not in self.dataServer:
            self.get_datos(key, True)
        for d in self.dataServer[key]:
            if isinstance(d, models.model_base):
                if d.id == _id:
                    return d
            else:
                if d['id'] == _id:
                    return d
        return None

    # LOAD DATA

    def get_recibo(self, actualizar=False):
        return self.get_datos('recibos', actualizar)

    def get_item(self, actualizar=False):
        return self.get_datos('items', actualizar)

    def get_tipos_documento(self, actualizar=False):
        return self.get_datos('tiposDocumento', actualizar)

    def get_productos(self, actualizar=False):
        return self.get_datos('productos', actualizar)

    def get_boletos(self, actualizar=False):
        return self.get_datos('boletos', actualizar)

    def get_rutas(self, actualizar=False):
        rutas = self.get_datos('rutas', actualizar)
        for r in rutas:
            if r.plantilla is None:
                plantillas = self.get_plantillas()
                frecuencias = self.get_frecuencias()
                self.get_tiempos()
                self.get_geocercas()
                self.get_trabajadores()
                r.set_plantilla(plantillas)
                r.configurar_frecuencias(frecuencias)
        return rutas

    def get_tiempos(self, actualizar=False):
        return self.get_datos('tiempos', actualizar)

    def get_plantillas(self, actualizar=False):
        return self.get_datos('plantillas', actualizar)

    def get_frecuencias(self, actualizar=False):
        return self.get_datos('frecuencias', actualizar)

    def get_geocercas(self, actualizar=False):
        return self.get_datos('geocercas', actualizar)

    def get_trabajadores(self, actualizar=False):
        return self.get_datos('trabajadores', actualizar)

    def get_propietarios(self, actualizar=False):
        return self.get_datos('propietarios', actualizar)

    def get_configuraciones(self, actualizar=False):
        return self.get_datos('configuraciones', actualizar)

    def get_stocks(self, actualizar=False):
        return self.get_datos('stocks', actualizar)

    def get_clientes(self, actualizar=False):
        return self.get_datos('clientes', actualizar)

    # get objeto

    def get_recibo(self, _id):
        return self.get_dato('recibos', _id)

    def get_item(self, _id):
        return self.get_dato('items', _id)

    def get_documento(self, _id):
        return self.get_dato('documentos', _id)

    def get_producto(self, _id):
        return self.get_dato('productos', _id)

    def get_boleto(self, _id):
        return self.get_dato('boletos', _id)

    def get_ruta(self, _id):
        return self.get_dato('rutas', _id)

    def get_tiempo(self, _id):
        return self.get_dato('tiempos', _id)

    def get_plantilla(self, _id):
        return self.get_dato('plantillas', _id)

    def get_frecuencia(self, _id):
        return self.get_dato('frecuencias', _id)

    def get_geocerca(self, _id):
        return self.get_dato('geocercas', _id)

    def get_trabajador(self, _id):
        return self.get_dato('trabajadores', _id)

    def get_propietario(self, _id):
        return self.get_dato('propietarios', _id)

    def get_configuracion(self, _id):
        return self.get_dato('configuraciones', _id)

    def get_stock(self, _id):
        return self.get_dato('stocks', _id)

    def get_cliente(self, _id):
        return self.get_dato('clientes', _id)

    # ADD METHODS

    def add_dato(self, key, value):
        objeto = models.MODELOS[key](self, value)
        self.dataServer[key].append(objeto)
        if key in self.dataDump:
            del self.dataDump[key]
            self.save_data_file()
        return objeto

    def add_tipo_documento(self, value):
        self.add_dato('documentos', value)

    def add_cliente(self, value):
        self.add_dato('clientes', value)

    def filtrar(self, lista, filter):
        query = []
        for l in lista:
            if self.cumple(l, filter):
                query.append(l)
        return query

    def cumple(self, item, filter):
        for f in filter:
            if item.get_param(f) == filter[f]:
                continue
            else:
                return False
        return True

    def ordenar(self, lista, sort):
        sort.reverse()
        for k, orden in sort:
            lista.sort(key=lambda x: x.__getattribute__(k))
            if orden < 0:
                lista.reverse()
