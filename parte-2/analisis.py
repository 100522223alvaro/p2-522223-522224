#!/usr/bin/env python3
import sys
import time
import random
from grafo import Grafo
from algoritmo import AStar, Dijkstra

def ejecutar_caso(grafo, nombre_caso, inicio, fin):
    print(f"\n--- {nombre_caso} (Nodos {inicio} -> {fin}) ---")
    
    # 1. Ejecución A* (Con Heurística)
    solver_astar = AStar(grafo)
    t0 = time.time()
    coste, _ = solver_astar.resolver(inicio, fin)
    t1 = time.time()
    
    if coste is None:
        print("No hay camino accesible.")
        return

    # 2. Ejecución Fuerza Bruta (Sin Heurística)
    solver_dijkstra = Dijkstra(grafo)
    t2 = time.time()
    _, _ = solver_dijkstra.resolver(inicio, fin) # Ignoramos camino, solo queremos stats
    t3 = time.time()

    # Resultados
    nodos_astar = solver_astar.nodos_expandidos
    nodos_dijkstra = solver_dijkstra.nodos_expandidos
    tiempo_astar = t1 - t0
    tiempo_dijkstra = t3 - t2
    
    mejora = 100 * (nodos_dijkstra - nodos_astar) / nodos_dijkstra if nodos_dijkstra else 0

    print(f"Coste Ruta    : {coste}")
    print(f"A* (Heuríst.) : {nodos_astar} nodos expandidos ({tiempo_astar:.4f} s)")
    print(f"Fuerza Bruta  : {nodos_dijkstra} nodos expandidos ({tiempo_dijkstra:.4f} s)")
    print(f"Eficiencia    : A* expandió un {mejora:.2f}% menos de nodos.")

def main():
    if len(sys.argv) != 2:
        print("Uso: python analisis.py <nombre_mapa>")
        print("Ejemplo: python analisis.py USA-road-d.BAY")
        sys.exit(1)

    ruta_mapa = sys.argv[1]
    
    print(f"Cargando mapa {ruta_mapa}...")
    g = Grafo()
    g.cargar_mapa(ruta_mapa)
    print(f"Mapa cargado. Nodos: {g.num_nodos}, Arcos: {g.num_arcos}")

    # Casos de prueba seleccionados (basados en el mapa BAY)
    # Estos pares tienen distancias variadas
    casos = [
        ("Caso Muy Corto", 58370, 73159),
        ("Caso Corto    ", 58370, 16664),
        ("Caso Medio    ", 58370, 100815),
        ("Caso Largo    ", 58370, 139974),
        ("Caso Extremo  ", 58370, 110616) 
    ]

    for nombre, inicio, fin in casos:
        ejecutar_caso(g, nombre, inicio, fin)

if __name__ == "__main__":
    main()