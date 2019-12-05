# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
from urllib3.exceptions import MaxRetryError

import Impresion
import Sonido
import Widgets
import urllib3
import os
import json
import DataLocal
import Reloj


class Http(object):

    local = 1
    version = 6.00
    dia = 'Actualización martes 29 de octubre de 2019'

    __instance = None
    dataLocal = None
    # exclusiones = [
    #     'Error Digitación',
    #     'Sin Personal',
    #     'Combustible',
    #     'Taller',
    #     'Almuerzo'
    # ]
    usuario = None
    conn = None
    ventanas = []
    server = 'localhost:8000'
    titulo = 'MODO LOCAL v%s' % version
    ventanas = ventanas
    base_url = '/desktop/'
    login_ok = False
    username = ''
    sessionid = ''
    nombre = ''
    user_id = None
    sonido = None
    reloj = None
    ticketera = None
    ticketera_sunat = None
    headers = None

    def __new__(cls):
        if Http.__instance is None:
            Http.__instance = object.__new__(cls)
        return Http.__instance

    def test_server(self):
        test = urllib3.HTTPSConnectionPool(self.dataLocal.server)
        try:
            test.urlopen('HEAD', '/', assert_same_host=False)
        except:
            print('TEST SERVER OK', self.dataLocal.server)
            self.server = self.dataLocal.server
        else:
            print('TEST SERVER FAIL', self.dataLocal.server, 'USE', self.dataLocal.sin_dns)
            self.server = self.dataLocal.sin_dns

    def construir(self, ventanas):
        self.dataLocal = DataLocal.DataLocal()
        if os.name == 'nt':
            self.local = 0
        print 'LOCAL', self.local
        if self.local:
            self.conn = urllib3.HTTPConnectionPool(self.server, timeout=30)
        else:
            self.server = 'api.tcontur.com'
            self.sin_dns = 'api.tcontur.com'
            self.titulo = 'Sistema de Despacho TCONTUR v%s' % self.version
            self.test_server()
            self.conn = urllib3.HTTPSConnectionPool(self.server, timeout=30)
        self.sonido = Sonido.Hilo()
        self.sonido.start()
        self.reloj = Reloj.Reloj()
        ticketera_data = self.dataLocal.get_config('ticketera')
        if ticketera_data:
            self.ticketera = Impresion.ESCPOS(ticketera_data)
        ticketera_data = self.dataLocal.get_config('ticketera_sunat')
        if ticketera_data:
            self.ticketera_sunat = Impresion.ESCPOS(ticketera_data)
        self.headers = {
            'Cookie': '',
            'User-Agent': 'DesktopTCONTUR/%s' % self.version,
            'Accept': '*/*',
            'Cache-Control': 'no-cache',
            'Host': self.server,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive'
        }
        self.login_ok = False
        self.dataLocal.load_data_file()

    def set_usuario(self, usuario):
        self.usuario = usuario
        self.dataLocal.set_main(self.username, self.password, usuario)

    def login(self, username, password, clave):
        self.username = username
        self.password = password
        data = {
            'username': username,
            'password': password,
            'clave': clave
        }
        login = self.load('token-auth', data)
        if login:
            self.headers['Authorization'] = 'Token ' + login['token']
            self.headers['Content-Type'] = 'application/x-www-form-urlencoded'
            self.username = login['username']
            self.nombre = login['nombre']
            self.user_id = login['id']
            self.sessionid = login['token']
            self.login_ok = True
            return login

    def set_cookie(self, key):
        try:
            cookies = self.req.getheaders()['set-cookie']
        except:
            return None
        i = cookies.find(key)
        if i == -1:
            return False
        cook = cookies[i:]
        n = cook.find('=')
        m = cook.find(';')
        cookie = cook[n + 1:m]
        self.headers['Cookie'] += '%s=%s; ' % (key, cook[n + 1:m])
        return cookie

    def load(self, consulta, datos={}, log=True, method='POST'):
        if log:
            print('**********************************')
            print('load', consulta, datos, method)
            print('++++++++++++++++++++++++++++++++++')
        post_data = ''
        if method == 'POST':
            datos['version'] = self.version
            datos['username'] = self.username
            datos['user_id'] = self.user_id
            keys = datos.keys()
            keys.sort()
            for k in keys:
                if datos[k] is None:
                    pass
                elif isinstance(datos[k], tuple) or isinstance(datos[k], list):
                    for d in datos[k]:
                        post_data += '%s=%s&' % (k, d)

                else:
                    post_data += '%s=%s&' % (k, datos[k])

            post_data = post_data[:-1]
        if consulta[0] == '/':
            url = consulta
        else:
            url = '/desktop/%s/' % consulta

        l = len(str(post_data))
        self.headers['Content-Length'] = str(l)
        try:
            r = self.conn.urlopen(method, url, body=post_data, headers=self.headers, assert_same_host=False)
        except MaxRetryError:
            print('********************************')
            print(url)
            print('********************************')
            Widgets.Alerta('Error', 'error_http.png', 'No es posible conectarse al servidor,\n' + 'asegúrese de estar conectado a internet\n' + 'e intente de nuevo.')
            return False
        except:
            print('********************************')
            print(url)
            print('********************************')
            Widgets.Alerta('Error', 'error_http.png', 'No es posible conectarse al servidor,\n' + 'asegúrese de estar conectado a internet\n' + 'e intente de nuevo.')
            return False

        self.req = r
        if log:
            a = os.path.abspath('outs/index.html')
            f = open(a, 'wb')
            f.write(r.data)
            f.close()

        try:
            js = json.loads(r.data)
        except:
            print('********************************')
            print(url)
            print('********************************')
            print 'json', url, post_data, self.headers
            print r.status
            if self.local:
                Widgets.Alerta('Error 500', 'error_http.png', 'Hubo un error en la operación.')
            else:
                for v in self.ventanas:
                    v.status_bar.push('Error de conexion')

            return False

        if log:
            print(js)

        if 200 <= r.status < 300:
            return self.ejecutar(js)
        else:
            print(json.dumps(js, indent=4))
            Widgets.Alerta('Error %s' % r.status, 'error_http.png', json.dumps(js, indent=4))
            return False

    def ejecutar(self, js):
        if isinstance(js, dict):
            if 'error' in js:
                self.sonido.error()
                Widgets.Alerta('Error', 'error_dialogo.png', js['mensaje'])
                for v in self.ventanas:
                    v.status_bar.push(js['mensaje'].split('\n')[0])
                return False
        return js

    def ejecutar_antiguo(self, js):
        if len(js) < 2:
            return False
        primero = js[0]
        segundo = js[1]
        if primero == 'Json':
            return segundo
        elif primero == 'Dialogo':
            Widgets.Alerta('Aviso', 'info.png', segundo)
            for v in self.ventanas:
                v.status_bar.push(segundo.split('\n')[0])

            return self.ejecutar(js[2:])
        elif primero == 'Comando':
            self.comando(segundo)
            return self.ejecutar(js[2:])
        elif primero == 'OK':
            for v in self.ventanas:
                v.status_bar.push(segundo)

            return self.ejecutar(js[2:])
        elif primero == 'Error':
            self.sonido.error()
            print segundo
            Widgets.Alerta('Error', 'error_dialogo.png', segundo)
            for v in self.ventanas:
                v.status_bar.push(segundo.split('\n')[0])
            return False
        elif primero == 'print':
            print 'imprimiendo'
            self.imprimir(segundo)
            return self.ejecutar(js[2:])
        elif primero == 'ticket':
            self.ticket(segundo, cortar=True)
            return self.ejecutar(js[2:])
        elif primero == 'ticket_uncut':
            self.ticket(segundo, cortar=False)
            return self.ejecutar(js[2:])
        elif primero == 'open':
            self.open(segundo)
            return self.ejecutar(js[2:])
        elif primero == 'image':
            self.imagen(segundo)
            return self.ejecutar(js[2:])
        else:
            return self.ejecutar(js[2:])

    def imprimir(self, datos):
        Impresion.Impresion(datos[0], datos[1])

    def open(self, consulta):
        url = '/%s' % consulta
        self.headers.pop('Content-Length')
        r = self.conn.urlopen('GET', url, headers=self.headers, assert_same_host=False)
        self.req = r
        a = 'outs/reporte.pdf'
        f = open(a, 'wb')
        f.write(r.data)
        f.close()
        a = os.path.abspath(a)
        if os.name == 'nt':
            com = 'cd "%s" & start reporte.pdf' % a[:-12]
            os.system(com)
        else:
            os.system('xdg-open outs/reporte.pdf')
        return True

    def imagen(self, consulta):
        url = '/%s' % consulta
        self.headers.pop('Content-Length')
        r = self.conn.urlopen('GET', url, headers=self.headers, assert_same_host=False)
        self.req = r
        a = 'outs/imagen.png'
        f = open(a, 'wb')
        f.write(r.data)
        f.close()
        return True

    def ticket(self, comandos, cortar=True):
        for c in comandos:
            if 'AUTORIZACION:' in c[1]:
                self.ticketera_sunat.imprimir(comandos, cortar)
                return
        self.ticketera.imprimir(comandos, cortar)

    def connect(self, string, funcion):
        self.signals[string].append(funcion)

    def emit(self, string):
        for f in self.signals[string]:
            f()

    def nada(self, *args):
        pass

    def get_pagos(self, ruta):
        if ruta in self.pagos:
            return self.pagos[ruta]
        else:
            data = self.load('pagos-por-tipo', {
                'ruta': ruta,
                'lado': 0,
                'padron': 0
            })
            print 'pagos', data
            if data:
                self.pagos[ruta] = data
                return data
            else:
                return []

    def comando(self, params):
        funcion = params['funcion']
        default = params['default']
        dialogo = self.http_funciones[funcion](self)
        dialogo.set_defaults(default)
        if dialogo.iniciar():
            self.load(funcion, dialogo.datos)
        dialogo.cerrar()

    def webbrowser(self, url, backup=False):
        uri = 'http://%s/desktop/ingresar?sessionid=%s&next=%s' % (self.web, self.sessionid, url)
        self.config.open_url(uri)