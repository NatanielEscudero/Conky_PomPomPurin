#!/usr/bin/env python3

import subprocess
import threading
import time
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

# Tamaño de cada botón
ANCHO = 20
ALTO = 20

# Posiciones RELATIVAS a la esquina superior izquierda de Conky
BOTONES = [
    {"nombre": "Volumen", "x": 27, "y": 260,
     "comando": ["pavucontrol"]},
    {"nombre": "Wi-Fi", "x": 27, "y": 230,
     "comando": ["nm-connection-editor"]},
    {"nombre": "Bluetooth", "x": 27, "y": 290,
     "comando": ["blueman-manager"]},

    {"nombre": "Archivos", "x": 27, "y": 200,
     "comando": ["thunar"]},

    {"nombre": "Tareas", "x": 27, "y": 320,
     "comando": ["xfce4-taskmanager"]},
]

VENTANAS = []


PROCESOS = {}
ULTIMO_CLIC = {}

def ejecutar(comando):
    nombre = comando[0]
    ahora = time.monotonic()

    if ahora - ULTIMO_CLIC.get(nombre, 0) < 0.8:
        print(f"Clic ignorado por repetición: {nombre}", flush=True)
        return

    ULTIMO_CLIC[nombre] = ahora

    print(f"Ejecutando: {nombre}", flush=True)

    try:
        proceso = subprocess.Popen(comando)
        print(f"Proceso iniciado: {nombre}, PID: {proceso.pid}", flush=True)
    except Exception as e:
        print(f"Error al abrir {comando}: {e}", flush=True)


class BotonConky:
    def __init__(self, datos):
        self.datos = datos

        self.ventana = Gtk.Window(
            title=f"Botón Conky - {datos['nombre']}"
        )
        self.ventana.set_default_size(ANCHO, ALTO)
        self.ventana.set_size_request(ANCHO, ALTO)
        self.ventana.set_resizable(False)
        self.ventana.set_decorated(False)
        self.ventana.set_app_paintable(True)
        self.ventana.set_keep_above(False)
        self.ventana.set_skip_taskbar_hint(True)
        self.ventana.set_skip_pager_hint(True)
        self.ventana.set_accept_focus(False)
        self.ventana.set_type_hint(Gdk.WindowTypeHint.NORMAL)

        visual = self.ventana.get_screen().get_rgba_visual()
        if visual:
            self.ventana.set_visual(visual)

        caja = Gtk.EventBox()
        caja.set_visible_window(True)
        caja.set_size_request(ANCHO, ALTO)

        etiqueta = Gtk.Label(label="")
        caja.add(etiqueta)

        css = Gtk.CssProvider()
        css.load_from_data(b"""
            eventbox,
            eventbox:hover,
            eventbox:active {
                background-color: transparent;
                background-image: none;
                border: none;
                box-shadow: none;
            }

            label {
                color: transparent;
                background-color: transparent;
            }
        """)


        caja.get_style_context().add_provider(
            css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        caja.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        caja.connect("button-press-event", self.al_clic)

        self.ventana.add(caja)
        self.ventana.show_all()

    def al_clic(self, widget, evento):
        if evento.button == 1:
            print(f"Clic recibido: {self.datos['nombre']}", flush=True)
            ejecutar(self.datos["comando"])
            return True
        return False

    def mover(self, x, y):
        self.ventana.move(int(x), int(y))


def geometria_conky():
    try:
        salida = subprocess.run(
            ["xdotool", "search", "--class", "conky"],
            capture_output=True,
            text=True,
            timeout=2
        )

        if salida.returncode != 0:
            return None

        for wid in salida.stdout.splitlines():
            wid = wid.strip()
            if not wid:
                continue

            try:
                info = subprocess.run(
                    ["xdotool", "getwindowgeometry", "--shell", wid],
                    capture_output=True,
                    text=True,
                    timeout=2
                )

                if info.returncode != 0:
                    continue

                datos = {}
                for linea in info.stdout.splitlines():
                    if "=" in linea:
                        clave, valor = linea.split("=", 1)
                        datos[clave] = valor

                x = int(datos["X"])
                y = int(datos["Y"])
                ancho = int(datos["WIDTH"])
                alto = int(datos["HEIGHT"])

                if ancho >= 400 and alto >= 500:
                    return x, y, ancho, alto

            except (subprocess.SubprocessError, ValueError, KeyError):
                continue

    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    return None

def recuperar_ventanas():
    for boton in VENTANAS:
        try:
            boton.ventana.set_keep_above(False)
            boton.ventana.set_keep_below(False)
            boton.ventana.set_keep_above(True)
            boton.ventana.set_keep_above(False)
        except Exception as e:
            print(
                f"Error recuperando {boton.datos['nombre']}: {e}",
                flush=True
            )

    return True

def actualizar_posiciones():
    geo = geometria_conky()

    if geo:
        cx, cy, cw, ch = geo

        for boton in VENTANAS:
            datos = boton.datos

            # Limitar el botón para que quede dentro de Conky
            rx = max(0, min(datos["x"], cw - ANCHO))
            ry = max(0, min(datos["y"], ch - ALTO))

            boton.mover(cx + rx, cy + ry)

    return True


for datos in BOTONES:
    VENTANAS.append(BotonConky(datos))

GLib.timeout_add(500, actualizar_posiciones)
GLib.timeout_add(5000, recuperar_ventanas)

actualizar_posiciones()
Gtk.main()