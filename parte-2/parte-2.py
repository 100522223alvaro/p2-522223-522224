#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import os
from grafo import Grafo
from algoritmo import AStar

# -----------------------------------------------------------------------------
# Parte 2: Algoritmo de búsqueda óptimo (A*)
# -----------------------------------------------------------------------------

def main():

    # 1) Validar argumentos
    # Nota: Para ejecutar el scirpt con ./parte-2.py en Linux, se debe dar permisos de ejecución con chmod +x parte-2.py
    if len(sys.argv) != 5:
        print("Uso: ./parte-2.py <id_inicio> <id_fin> <nombre_mapa> <fichero_salida>")
        sys.exit(1)

    try:
        start_node = int(sys.argv[1])
        end_node = int(sys.argv[2])
    except ValueError:
        print("Error: Los IDs de los vértices deben ser enteros.")
        sys.exit(1)

    ruta_mapa = sys.argv[3]
    fichero_salida = sys.argv[4]

    # Manejo de rutas para el mapa (si no tiene extensión, asumimos que es el prefijo)
    # El enunciado dice que se recibe "USA-road-d.BAY" y hay que buscar .gr y .co
    # Verificamos si el usuario pasó ruta absoluta o relativa
    
    # 2. Carga del Grafo
    print(f"Cargando grafo desde {ruta_mapa}...")
    grafo = Grafo()
    try:
        t_carga_inicio = time.time()
        grafo.cargar_mapa(ruta_mapa)
        t_carga_fin = time.time()
    except Exception as e:
        print(f"Error cargando el grafo: {e}")
        sys.exit(1)

    # 3. Ejecución del Algoritmo
    print(f"Calculando ruta de {start_node} a {end_node}...")
    solver = AStar(grafo)
    
    t_algo_inicio = time.time()
    coste_total, camino = solver.resolver(start_node, end_node)
    t_algo_fin = time.time()
    
    tiempo_total = t_algo_fin - t_algo_inicio
    
    # 4. Mostrar resultados en pantalla
    if camino:
        print(f"# vertices: {grafo.num_nodos}")
        print(f"# arcos : {grafo.num_arcos}")
        print(f"Solución óptima encontrada con coste {coste_total}")
        print(f"Tiempo de ejecución: {tiempo_total:.4f} segundos")
        
        rate = 0
        if tiempo_total > 0:
            rate = solver.nodos_expandidos / tiempo_total
        print(f"# expansiones : {solver.nodos_expandidos} ({rate:.2f} nodes/sec)")
        
        # 5. Escribir fichero de salida
        # Formato: <inicio> - (coste) - <sig> - (coste) ...
        try:
            with open(fichero_salida, 'w') as f:
                linea_salida = f"{camino[0]}"
                for i in range(len(camino) - 1):
                    u = camino[i]
                    v = camino[i+1]
                    coste_arco = grafo.coste_arco(u, v)
                    linea_salida += f" - ({coste_arco}) - {v}"
                f.write(linea_salida + "\n")
            print(f"Solución guardada en {fichero_salida}")
            
        except IOError as e:
            print(f"Error escribiendo fichero de salida: {e}")
    else:
        print("No se encontró solución o los nodos no están conectados.")

if __name__ == "__main__":
    main()