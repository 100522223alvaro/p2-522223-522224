#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import subprocess

# Directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ruta a parte-1.py 
PARTE1 = os.path.join(os.path.dirname(BASE_DIR), "parte-1.py")

# Definición de carpetas para organizar el flujo de trabajo
INPUT_DIR = os.path.join(BASE_DIR, "entradas")
SALIDA_DIR = os.path.join(BASE_DIR, "salidas")
TIEMPOS_DIR = os.path.join(BASE_DIR, "tiempos")

# Nos aseguramos de que las carpetas de destino existan; si no, las crea.
os.makedirs(SALIDA_DIR, exist_ok=True)
os.makedirs(TIEMPOS_DIR, exist_ok=True)

def extraer_num_soluciones(salida):
    """
    Busca en la salida del script la línea 'X soluciones encontradas'
    y devuelve el número X.
    """
    for linea in salida.splitlines():
        linea = linea.strip()
        if "soluciones encontradas" in linea:
            try:
                # Toma el primer elemento (el número) y lo convierte a entero
                return int(linea.split()[0])
            except Exception:
                return None
    return None

def main():

    # 1) Obtener lista de ficheros de entrada
    entradas = sorted(
        f for f in os.listdir(INPUT_DIR)
        if f.endswith(".in") and os.path.isfile(os.path.join(INPUT_DIR, f))
    )

    # Si no encuentra ficheros, avisa y termina el programa
    if not entradas:
        print("No hay ficheros .in en la carpeta de pruebas.")
        print(f"Carpeta esperada: {INPUT_DIR}")
        return
    
    # 2) Bucle de ejecución de pruebas
    for nombre in entradas:
        ruta_in = os.path.join(INPUT_DIR, nombre)
        # Extraemos el nombre base
        base, _ = os.path.splitext(nombre)
        # Definimos dónde se guardará la solución (.out) y el tiempo (.out)
        ruta_out = os.path.join(SALIDA_DIR, base + ".out")
        ruta_tiempos = os.path.join(TIEMPOS_DIR, base + "_tiempo.out")

        # 3) Ejecución y Medición
        # Iniciamos el cronómetro
        t0 = time.perf_counter()

        proc = subprocess.run(
            [sys.executable, PARTE1, ruta_in, ruta_out],
            capture_output=True,
            text=True
        )
        
        # Paramos el cronómetro
        t1 = time.perf_counter()

        # Calculamos la diferencia
        dt = t1 - t0

        # Extraemos cuántas soluciones encontró leyendo lo que imprimió parte-1.py
        num_sol = extraer_num_soluciones(proc.stdout)

        # 4) Guardar en el fichero de tiempos
        with open(ruta_tiempos, "a", encoding="utf-8") as ft:
            ft.write(f"Soluciones encontradas: {num_sol}\nTiempo de ejecución: {dt:.6f}\n")

if __name__ == "__main__":
    main()

