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

    # Conversión de los IDs de nodos a enteros
    try:
        start_node = int(sys.argv[1])  # Nodo de inicio
        end_node = int(sys.argv[2])    # Nodo de destino
    except ValueError:
        print("Error: Los IDs de los vértices deben ser enteros.")
        sys.exit(1)

    # Obtención de rutas de archivos
    ruta_mapa = sys.argv[3]           # Ruta base del mapa (sin extensión)
    fichero_salida = sys.argv[4]      # Ruta del fichero de salida

    # 2)Carga del Grafo
    print(f"Cargando grafo desde {ruta_mapa}...")

    # Instanciación del objeto Grafo
    grafo = Grafo()  
    
    # El nombre del mapa puede ser una ruta absoluta o relativa
    # El método cargar_mapa() buscará automáticamente los ficheros .gr y .co
    try:
        t_carga_inicio = time.time()
        # Carga de los ficheros .gr (arcos) y .co (coordenadas)
        grafo.cargar_mapa(ruta_mapa)
        t_carga_fin = time.time()
    except Exception as e:
        print(f"Error cargando el grafo: {e}")
        sys.exit(1)

    # 3) Ejecución del Algoritmo A*
    print(f"Calculando ruta de {start_node} a {end_node}...")
    
    # Creación del objeto solver con el algoritmo A*
    solver = AStar(grafo)
    
    # Medición del tiempo de ejecución del algoritmo
    t_algo_inicio = time.time()
    coste_total, camino = solver.resolver(start_node, end_node)
    t_algo_fin = time.time()
    
    tiempo_total = t_algo_fin - t_algo_inicio

    # 4) Presentación de resultados en pantalla
    if camino:
        # Si se encontró un camino válido, mostramos las estadísticas
        print(f"# vertices: {grafo.num_nodos}")
        print(f"# arcos : {grafo.num_arcos}")
        print(f"Solución óptima encontrada con coste {coste_total}")
        print(f"Tiempo de ejecución: {tiempo_total:.4f} segundos")
        
        # Cálculo de la tasa de nodos expandidos por segundo
        rate = 0
        if tiempo_total > 0:
            rate = solver.nodos_expandidos / tiempo_total
        print(f"# expansiones : {solver.nodos_expandidos} ({rate:.2f} nodes/sec)")
        
        # 5) Escritura del fichero de salida-
        # Formato requerido: <inicio> - (coste) - <nodo_i> - (coste) - <nodo_i+1> - ... - <fin>
        try:
            with open(fichero_salida, 'w') as f:
                # Construcción de la línea de salida con el formato especificado
                linea_salida = f"{camino[0]}"  # Comenzamos con el nodo inicial
                
                # Iteramos sobre cada par de nodos consecutivos en el camino
                for i in range(len(camino) - 1):
                    u = camino[i]       # Nodo actual
                    v = camino[i+1]     # Nodo siguiente
                    
                    # Obtenemos el coste del arco entre u y v
                    coste_arco = grafo.coste_arco(u, v)
                    
                    # Añadimos el formato: - (coste) - nodo_siguiente
                    linea_salida += f" - ({coste_arco}) - {v}"
                
                # Escribimos la línea completa en el fichero
                f.write(linea_salida + "\n")
            
            print(f"Solución guardada en {fichero_salida}")
            
        except IOError as e:
            print(f"Error escribiendo fichero de salida: {e}")
    else:
        # No se encontró ningún camino entre los nodos especificados
        print("No se encontró solución o los nodos no están conectados.")

if __name__ == "__main__":
    main()
    