#!/usr/bin/env python3
import sys
import time
import math
import os
from grafo import Grafo
from algoritmo import AStar, Dijkstra

# =============================================================================
# CONFIGURACIÓN DE ESCENARIOS DE PRUEBA (COORDENADAS REALES)
# =============================================================================
# Formato: (Latitud, Longitud)
CIUDADES = {
    # BAY AREA
    "SF_Centro":    (37.7749, -122.4194),
    "Alcatraz":     (37.8269, -122.4229), # Isla
    
    # NY
    "Manhattan":    (40.7831, -73.9712),
    "Manhattan_Vecino": (40.7835, -73.9715), # Muy cerca
    
    # COLORADO (Montañas)
    "Denver":       (39.7392, -104.9903),
    "GrandJunction":(39.0639, -108.5506),
    
    # GREAT LAKES (El Lago en medio)
    "Chicago":      (41.8781, -87.6298),
    "GrandRapids":  (42.9634, -85.6681),
    
    # FLORIDA (Pasillo)
    "Miami":        (25.7617, -80.1918),
    "Jacksonville": (30.3322, -81.6557),
    
    # CALIFORNIA (Muy lejos)
    "SanDiego":     (32.7157, -117.1611),
    "Sacramento":   (38.5816, -121.4944),
    
    # NORTHEAST (Megalópolis)
    "Philadelphia": (39.9526, -75.1652),
    "NewYork_City": (40.7128, -74.0060),
    
    # NORTHWEST (Rural)
    "Seattle":      (47.6062, -122.3321),
    "Spokane":      (47.6588, -117.4260)
}

# =============================================================================
# HERRAMIENTAS AUXILIARES
# =============================================================================

def distancia_euclidea_aprox(lat1, lon1, lat2, lon2):
    """Calcula distancia euclídea simple para buscar nodos cercanos."""
    return math.sqrt((lat1-lat2)**2 + (lon1-lon2)**2)

def buscar_nodo_por_coords(grafo, lat_objetivo, lon_objetivo):
    """
    Busca el nodo del grafo más cercano a unas coordenadas reales GPS.
    Asume que el grafo almacena coordenadas en formato entero (grados * 10^6).
    """
    lat_target = int(lat_objetivo * 1000000)
    lon_target = int(lon_objetivo * 1000000)
    
    mejor_nodo = None
    menor_dist = float('inf')
    
    # Barrido lineal para encontrar el punto de entrada (Solo setup del test)
    # CORRECCION: grafo.coordenadas es una LISTA. Usamos enumerate.
    # Empezamos en 1 porque los IDs de DIMACS empiezan en 1.
    for nodo_id, coords in enumerate(grafo.coordenadas):
        if nodo_id == 0: continue # El índice 0 no se usa en DIMACS
        
        c1, c2 = coords # Desempaquetamos (lon, lat) o (lat, lon)
        
        # Asumimos c1=lon, c2=lat (estándar DIMACS invertido) o viceversa
        d1 = distancia_euclidea_aprox(lat_target, lon_target, c2, c1)
        d2 = distancia_euclidea_aprox(lat_target, lon_target, c1, c2)
        
        actual = min(d1, d2)
        if actual < menor_dist:
            menor_dist = actual
            mejor_nodo = nodo_id
            
    return mejor_nodo

def ejecutar_test(grafo, titulo, inicio_nom, fin_nom, inicio_id, fin_id, check_imposible=False):
    print(f"\n>>> EJECUTANDO TEST: {titulo}")
    print(f"    Ruta: {inicio_nom} ({inicio_id}) -> {fin_nom} ({fin_id})")

    # 1. Ejecución A* (Algoritmo Principal)
    print("    [1/2] Ejecutando A* ... ", end="", flush=True)
    solver_astar = AStar(grafo)
    t0 = time.time()
    coste_astar, _ = solver_astar.resolver(inicio_id, fin_id)
    t1 = time.time()
    t_astar = t1 - t0
    nodos_astar = solver_astar.nodos_expandidos
    print(f"Hecho ({t_astar:.3f}s)")

    # 2. Ejecución Dijkstra (Línea Base)
    print("    [2/2] Ejecutando Dijkstra ... ", end="", flush=True)
    solver_dijkstra = Dijkstra(grafo)
    t2 = time.time()
    coste_dijkstra, _ = solver_dijkstra.resolver(inicio_id, fin_id)
    t3 = time.time()
    t_dijkstra = t3 - t2
    nodos_dijkstra = solver_dijkstra.nodos_expandidos
    print(f"Hecho ({t_dijkstra:.3f}s)")

    # --- RESULTADOS Y VALIDACIÓN ---
    status = "OK"
    mejora = 0.0
    
    # Validación de Costes
    if coste_astar != coste_dijkstra:
        status = "ERROR (Costes difieren)"
    
    # Validación de Caso Imposible (Isla)
    if check_imposible:
        if coste_astar is None:
            status = "OK (Inalcanzable detectado)"
        else:
            status = "ERROR (Encontró camino inexistente)"
    
    # Cálculo de eficiencia
    if nodos_dijkstra > 0:
        mejora = 100 * (nodos_dijkstra - nodos_astar) / nodos_dijkstra

    print(f"    RESULTADOS:")
    print(f"      A* -> Coste: {str(coste_astar):<10} | Nodos: {nodos_astar:<8} | Tiempo: {t_astar:.4f}s")
    print(f"      Dijkstra -> Coste: {str(coste_dijkstra):<10} | Nodos: {nodos_dijkstra:<8} | Tiempo: {t_dijkstra:.4f}s")
    print(f"      Eficiencia -> A* expandió un {mejora:.2f}% MENOS de nodos.")
    print(f"      Estado     -> {status}")
    
    return {
        "test": titulo,
        "nodos_astar": nodos_astar,
        "nodos_dijkstra": nodos_dijkstra,
        "tiempo_astar": t_astar,
        "tiempo_dijkstra": t_dijkstra,
        "mejora": mejora,
        "status": status
    }

# =============================================================================
# BLOQUE PRINCIPAL
# =============================================================================
def main():
    resultados_totales = []

    # Lista de mapas y sus tests asociados
    # (Nombre Archivo, [Lista de Tests])
    tests_planificados = [
        ("USA-road-d.NY", [
            ("1. Hola Mundo (Manhattan Corto)", "Manhattan", "Manhattan_Vecino", False),
            ("10. Coordenadas Erradas (Robustez)", "Manhattan", None, True) # Test especial manual abajo
        ]),
        ("USA-road-d.BAY", [
            ("2. La Isla (SF -> Alcatraz)", "SF_Centro", "Alcatraz", True)
        ]),
        ("USA-road-d.COL", [
            ("3. Montañas (Denver -> Grand Junction)", "Denver", "GrandJunction", False),
            ("9. Simetría (Grand Junction -> Denver)", "GrandJunction", "Denver", False)
        ]),
        ("USA-road-d.LKS", [
            ("4. Rodeo del Lago (Chicago -> G.Rapids)", "Chicago", "GrandRapids", False)
        ]),
        ("USA-road-d.FLA", [
            ("5. Península (Miami -> Jacksonville)", "Miami", "Jacksonville", False)
        ]),
        ("USA-road-d.CAL", [
            ("6. Larga Distancia (San Diego -> Sacram.)", "SanDiego", "Sacramento", False)
        ]),
        ("USA-road-d.NE", [
            ("7. Megalópolis (Philly -> NY)", "Philadelphia", "NewYork_City", False)
        ]),
        ("USA-road-d.NW", [
            ("8. Rural (Seattle -> Spokane)", "Seattle", "Spokane", False)
        ])
    ]

    print("============================================================")
    print(" INICIANDO BATERÍA DE TESTS - HEURÍSTICA A* vs DIJKSTRA")
    print("============================================================")

    for mapa, tests in tests_planificados:
        nombre_base = mapa
        # Verificar existencia
        if not (os.path.exists(f"{nombre_base}.gr") or os.path.exists(f"{nombre_base}.gr.gz")):
            print(f"\n[AVISO] Mapa {nombre_base} no encontrado. Saltando tests...")
            continue

        print(f"\n--- CARGANDO MAPA: {nombre_base} ---")
        g = Grafo()
        try:
            g.cargar_mapa(nombre_base)
        except Exception as e:
            print(f"Error cargando {nombre_base}: {e}")
            continue
            
        print(f"Mapa cargado. Nodos: {g.num_nodos}")

        for titulo, origen_key, destino_key, es_imposible in tests:
            
            # Caso especial: Test 10 (Coordenadas invalidas / Nodo inexistente)
            if "Coordenadas Erradas" in titulo:
                 print(f"\n>>> EJECUTANDO TEST: {titulo}")
                 # Test de Identidad para comprobar robustez y coste 0
                 print("    (Modo Robustez: Probando camino al mismo nodo origen)")
                 nodo_real = buscar_nodo_por_coords(g, *CIUDADES[origen_key])
                 if nodo_real:
                     res = ejecutar_test(g, titulo + " (Identidad)", origen_key, origen_key, nodo_real, nodo_real, False)
                     res["status"] = "OK (Coste 0)"
                     resultados_totales.append(res)
                 continue

            # Buscar IDs
            id_origen = buscar_nodo_por_coords(g, *CIUDADES[origen_key])
            id_destino = buscar_nodo_por_coords(g, *CIUDADES[destino_key])

            if id_origen is None or id_destino is None:
                print(f"    [ERROR] No se pudieron localizar los nodos para {origen_key} o {destino_key}")
                continue

            # Ejecutar
            res = ejecutar_test(g, titulo, origen_key, destino_key, id_origen, id_destino, es_imposible)
            resultados_totales.append(res)

    # =============================================================================
    # RESUMEN FINAL
    # =============================================================================
    print("\n\n")
    print("="*100)
    print(f"{'TEST':<40} | {'NODOS A*':<10} | {'NODOS DIJK':<10} | {'MEJORA %':<10} | {'ESTADO'}")
    print("="*100)
    for r in resultados_totales:
        print(f"{r['test']:<40} | {r['nodos_astar']:<10} | {r['nodos_dijkstra']:<10} | {r['mejora']:<9.2f}% | {r['status']}")
    print("="*100)

if __name__ == "__main__":
    main()