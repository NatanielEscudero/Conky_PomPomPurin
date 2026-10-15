#!/bin/bash

# Esperar a que XFCE termine de cargar el escritorio
sleep 4

# Iniciar Conky con tu configuración
conky -c "$HOME/.config/conky/conky.conf" &

# Darle tiempo a Conky para aparecer
sleep 9

# Iniciar los botones interactivos
python3 "$HOME/.config/conky/botones_conky.py" &