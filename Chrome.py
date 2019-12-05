import sys
import os
import ctypes
if os.name == 'nt':
    from cefpython1 import cefpython_py27 as cefpython
#else:
#    import webkit
#    import jswebkit
import gobject
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import re
import platform
import Widgets


def GetApplicationPath(file=None):
    import re, os
    # If file is None return current directory without trailing slash.
    if file is None:
        file = ""
    # Only when relative path.
    if not file.startswith("/") and not file.startswith("\\") and (
            not re.search(r"^[\w-]+:", file)):
        if hasattr(sys, "frozen"):
            path = os.path.dirname(sys.executable)
        elif "__file__" in globals():
            path = os.path.dirname(os.path.realpath(__file__))
        else:
            path = os.getcwd()
        path = path + os.sep + file
        path = re.sub(r"[/\\]+", re.escape(os.sep), path)
        path = re.sub(r"[/\\]+$", "", path)
        return path
    return str(file)

def ExceptHook(type, value, traceObject):
    import traceback, os, time
    # This hook does the following: in case of exception display it,
    # write to error.log, shutdown CEF and exit application.
    error = "\n".join(traceback.format_exception(type, value, traceObject))
    a = os.path.abspath("outs/error.log")
    with open(a, "a") as file:
        file.write("\n[%s] %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), error))
    print("\n"+error+"\n")
    return
    cefpython.QuitMessageLoop()
    cefpython.Shutdown()
    # So that "finally" does not execute.
    os._exit(1)

def init():
    if os.name == 'nt':
        sys.excepthook = ExceptHook
        a = os.path.abspath("outs/debug.log")
        settings = {
            "log_severity": cefpython.LOGSEVERITY_INFO,
            "log_file": GetApplicationPath(a),
            "release_dcheck_enabled": True # Enable only when debugging.
        }
        cefpython.Initialize(settings)

def close():
    os._exit(1)

class Window(gtk.Window):

    def __init__(self, url):
        super(Window, self).__init__(gtk.WINDOW_TOPLEVEL)
        self.set_size_request(400, 590)
        if os.name == 'nt':
            self.www = Browser(url, 550, 100)
        else:
            self.www = IFrame(url, 550, 100)
        hbox = gtk.VBox()
        self.add(hbox)
        hbox.pack_start(self.www)
        self.show_all()
        self.realize()
        self.set_url(url)
        self.connect('delete-event', self.esconder)

    def set_url(self, url):
        self.www.open(url)
        self.show_all()

    def esconder(self, *args):
        self.hide_all()
        return True


class Browser(gtk.DrawingArea): # Windows

    __gsignals__ = {'mostrar': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
        ())
        }

    def __init__(self, url, x, y):
        gobject.threads_init() # timer for messageloop
        super(Browser, self).__init__()
        self.exiting = False
        self.url = url
        self.mapa = True
        gobject.timeout_add(10, self.OnTimer)
        self.set_property('can-focus', True)
        self.connect_after('realize', self.mostrar)
        self.set_size_request(x, y)

    def mostrar(self, *args):
        print 'BROWSER MOSTRAR'
        windowID = self.get_window().handle
        windowInfo = cefpython.WindowInfo()
        windowInfo.SetAsChild(windowID)
        self.browser = cefpython.CreateBrowserSync(windowInfo,
                browserSettings={},
                navigateUrl=self.url)
        self.frame = self.browser.GetFocusedFrame()
        self.w = self.get_window()
        self.connect('size-allocate', self.OnSize)
        #cefpython.WindowUtils.OnSize(self.w.handle, 0, 0, 0)
        self.emit('mostrar')
        self.show_all()

    def OnTimer(self):
        if self.exiting:
            return False
        cefpython.MessageLoopWork()
        return True

    def OnFocusIn(self, widget, data):
        # This function is currently not called by any of code, but if you would like
        # for browser to have automatic focus add such line:
        # self.mainWindow.connect('focus-in-event', self.OnFocusIn)
        cefpython.WindowUtils.OnSetFocus(self.w.handle, 0, 0, 0)

    def OnSize(self, widget, sizeAlloc):
        cefpython.WindowUtils.OnSize(self.w.handle, 0, 0, 0)
        self.emit('mostrar')

    def open(self, url):
        print url
        self.frame.LoadUrl(url)
        self.emit('mostrar')

    def execute_script(self, url):
        if self.mapa:
            print url
            self.frame.ExecuteJavascript(url)

    def switch(self, server):
        lista = ((0, 'Mapa'), (1, 'Claro'), (2, 'Movistar'), (3, 'Ayuda'))
        enlaces = ((0, self.url), (1, 'http://www.internetclaro.com.pe'),
            (2, 'http://www.movistar.com.pe/im'), (3, server + '/ayuda'))
        dialogo = Alerta_Combo('Navegador', 'internet.png', 'Seleccione el enlace que desea ver:', lista)
        respuesta = dialogo.iniciar()
        self.frame.LoadUrl(enlaces[respuesta][1])

class IFrame(gtk.ScrolledWindow): # Ubuntu

    def __init__(self, url, x, y):
        super(IFrame, self).__init__()
        try:
            self.exiting = False
            self.url = url
            self.mapa = False
            self.connect_after('realize', self.mostrar)
            self.set_size_request(x, y)
            self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
            self.browser = webkit.WebView()
            self.browser_frame = self.browser.get_main_frame()
            self.add(self.browser)
            self.browser.open(url)
        except:
            pass

    def mostrar(self, *args):
        m = re.search("GtkScrolledWindow at 0x(\w+)", str(self))
        hexID = m.group(1)
        windowID = int(hexID, 16)
        #print 'windowID', windowID, hexID, self.get_window().xid
        #windowID = self.get_window().xid

    def OnTimer(self):
        if self.exiting:
            return False
        cefpython.MessageLoopWork()
        return True

    def OnFocusIn(self, widget, data):
        cefpython.WindowUtils.OnSetFocus(self.w.handle, 0, 0, 0)

    def open(self, url):
        print 'browser', url
        #self.browser.open(url)

    def execute_script(self, url):
        print url
        # self.browser.execute_script(url)
        try:
            ctx = jswebkit.JSContext(self.browser_frame.get_global_context())
            ctx.EvaluateScript(url)
        except:
            pass

    def switch(self, server):
        lista = (('Mapa', 0), ('Claro', 1), ('Movistar', 2), ('Ayuda', 3))
        enlaces = (self.url, 'http://www.internetclaro.com.pe',
            'http://www.movistar.com.pe/im', server + '/ayuda')
        dialogo = Widgets.Alerta_Combo('Navegador', 'internet.png', 'Seleccione el enlace que desea ver:', lista)
        respuesta = dialogo.iniciar()
        dialogo.cerrar()
        self.open(enlaces[respuesta])
        print enlaces[respuesta]


class Navegador(gtk.Window):

    def __init__(self, parent):
        super(Navegador, self).__init__(gtk.WINDOW_TOPLEVEL)
        self.http = parent.http
        url = 'http://%s/despacho/ingresar?sessionid=%s&next=pantalla%s' % (self.http.dominio,
            self.http.sessionid)
        if os.name == 'nt':
            self.www = Chrome.Browser(url, 550, 100)
        else:
            self.www = Chrome.IFrame(url, 550, 100)
        vbox = gtk.VBox(False, 0)
        self.add(vbox)
        hbox = gtk.HBox(False, 0)
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(self.www, True, True, 0)
        #but_exportar = Widgets.Button('excel.png', 'Exportar a Excel')
        #hbox.pack_start(but_exportar, True, True, 0)
        #but_exportar.connect('clicked', 'self.exportar')

    #def exportar(self, *args):
    #    url = self.frame.GetUrl()



if __name__ == '__main__':
    # init()
    # url = 'http://tracking.tcontur.com/despacho/login-mapa?usuario=None&password=None'
    # w = Window(url)

    #w = gtk.Window(gtk.WINDOW_TOPLEVEL)
    #if os.name == 'nt':
    #    www = Browser(url, 150, 150)
    #else:
    #    www = IFrame(url, 150, 150)
    #hbox = gtk.VBox()
    #w.add(hbox)
    #hbox.pack_start(www)
    #w.realize()
    #print 'realize'
    #www.mostrar()
    #w.show_all()
    ##www.open('tracking.tcontur.com')

    # gtk.main()

    #close()
    import webbrowser
    webbrowser.get()
    webbrowser.open('http://urbano.tcontur.com')
