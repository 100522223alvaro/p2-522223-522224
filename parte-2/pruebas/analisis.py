#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import math
import os
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
RAIZ_PARTE2 = SCRIPT_DIR.parent
if str(RAIZ_PARTE2) not in sys.path:
    sys.path.insert(0, str(RAIZ_PARTE2))

from grafo import Grafo
from algoritmo import AStar, Dijkstra

# =============================================================================
# CONFIGURACIÓN DE ESCENARIOS DE PRUEBA (COORDENADAS REALES)
# =============================================================================
# Formato: (Latitud, Longitud)
CIUDADES = {
    # NY (Camino muy corto)
    "Manhattan":    (40.7831, -73.9712),
    "Manhattan_Vecino": (40.7835, -73.9715), 
    
    # COLORADO (Montañas)
    "Denver":       (39.738386, -104.990336),
    "GrandJunction":(39.064381, -108.550848),
    
    # GREAT LAKES (El Lago en medio)
    "Milwaukee":    (43.0389, -87.9065),
    "GrandRapids":  (42.963226, -85.668130),
    
    # FLORIDA (Pasillo)
    "Miami":        (25.761477, -80.191869),
    "Jacksonville": (30.332439, -81.656017),
    
    # CALIFORNIA (Muy lejos)
    "SanDiego":     (32.715851, -117.161166),
    "Sacramento":   (38.581705, -121.494366),
    
    # NORTHEAST (Megalópolis)
    "Philadelphia": (39.9526, -75.1652),
    "NewYork_City": (40.7128, -74.0060),
    
    # NORTHWEST (Rural)
    "Seattle":      (47.6062, -122.3321),
    "Spokane":      (47.6588, -117.4260),

    # ISLAS desconectadas 
    "IslaA": (0.0, -100.0),
    "IslaB": (0.0, 100.0)
}

# =============================================================================
# LOCALIZACIÓN DE FICHEROS
# =============================================================================

MAPAS_DIR = Path(os.environ.get("MAPAS_DIR", RAIZ_PARTE2 / "mapas")).resolve()
RESULTADOS_DIR = SCRIPT_DIR / "resultados"
SALIDAS_DIR = SCRIPT_DIR / "salidas"


def localizar_mapa(nombre_base):
    """Devuelve la ruta base (sin extensión) dentro de MAPAS_DIR."""
    base = MAPAS_DIR / nombre_base
    ruta_gr = base.parent / f"{base.name}.gr"
    ruta_co = base.parent / f"{base.name}.co"

    if ruta_gr.exists() and ruta_co.exists():
        return str(base)

    raise FileNotFoundError(
        f"No se encuentran {ruta_gr} o {ruta_co}. Ajusta MAPAS_DIR o copia los ficheros."
    )


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
    if not isinstance(lat_objetivo, (int, float)) or not isinstance(lon_objetivo, (int, float)):
        raise ValueError("Coordenadas inválidas")
    if not math.isfinite(lat_objetivo) or not math.isfinite(lon_objetivo):
        raise ValueError("Coordenadas inválidas")
    if abs(lat_objetivo) > 90 or abs(lon_objetivo) > 180:
        raise ValueError("Coordenadas fuera de rango")

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


def obtener_coordenadas(ref):
    """Devuelve (lat, lon) a partir de una clave o una tupla literal."""
    if isinstance(ref, str):
        if ref not in CIUDADES:
            raise KeyError(ref)
        return CIUDADES[ref]
    if isinstance(ref, (tuple, list)) and len(ref) == 2:
        return float(ref[0]), float(ref[1])
    raise KeyError(str(ref))

def ejecutar_test(grafo, titulo, inicio_nom, fin_nom, inicio_id, fin_id):
    lineas = []
    lineas.append(f">>> EJECUTANDO TEST: {titulo}")
    lineas.append(f"    Ruta: {inicio_nom} ({inicio_id}) -> {fin_nom} ({fin_id})")

    solver_astar = AStar(grafo)
    t0 = time.time()
    coste_astar, camino_astar = solver_astar.resolver(inicio_id, fin_id)
    t1 = time.time()
    t_astar = t1 - t0
    nodos_astar = solver_astar.nodos_expandidos
    lineas.append(f"    [1/2] Ejecutando A* ... Hecho ({t_astar:.3f}s)")

    solver_dijkstra = Dijkstra(grafo)
    t2 = time.time()
    coste_dijkstra, _ = solver_dijkstra.resolver(inicio_id, fin_id)
    t3 = time.time()
    t_dijkstra = t3 - t2
    nodos_dijkstra = solver_dijkstra.nodos_expandidos
    lineas.append(f"    [2/2] Ejecutando Dijkstra ... Hecho ({t_dijkstra:.3f}s)")

    status = "OK"
    mejora = 0.0
    if coste_astar != coste_dijkstra:
        status = "ERROR (Costes difieren)"
    if nodos_dijkstra > 0:
        mejora = 100 * (nodos_dijkstra - nodos_astar) / nodos_dijkstra

    lineas.append("    RESULTADOS:")
    lineas.append(f"      A* -> Coste: {str(coste_astar)}; Nodos: {nodos_astar}; Tiempo: {t_astar:.4f}s")
    lineas.append(f"      Dijkstra -> Coste: {str(coste_dijkstra)}; Nodos: {nodos_dijkstra}; Tiempo: {t_dijkstra:.4f}s")
    lineas.append(f"      Eficiencia: A* expandió un {mejora:.2f}% MENOS de nodos.")
    lineas.append(f"      Estado: {status}")
    
    return lineas, {
        "test": titulo,
        "nodos_astar": nodos_astar,
        "nodos_dijkstra": nodos_dijkstra,
        "tiempo_astar": t_astar,
        "tiempo_dijkstra": t_dijkstra,
        "mejora": mejora,
        "status": status
    }, camino_astar


def guardar_resultado(titulo, lineas):
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
    ruta = RESULTADOS_DIR / f"{titulo}_resultado.txt"
    contenido = "\n".join(lineas)
    ruta.write_text(contenido + ("\n" if not contenido.endswith("\n") else ""), encoding="utf-8")


def _nombre_solucion(titulo):
    match = re.match(r"Test_(\d+\([^)]+\))", titulo)
    if match:
        return f"solucion_test_{match.group(1)}"
    return f"solucion_{titulo.replace(' ', '_')}"


def _formatear_camino(grafo, camino):
    if not camino:
        return ["SIN SOLUCION"]

    segmentos = [str(camino[0])]
    for u, v in zip(camino, camino[1:]):
        coste = grafo.coste_arco(u, v)
        if coste == float('inf'):
            coste = "INF"
        segmentos.append(f"({coste})")
        segmentos.append(str(v))

    linea_camino = " - ".join(segmentos)
    return [linea_camino]


def guardar_solucion(titulo, grafo, camino):
    SALIDAS_DIR.mkdir(parents=True, exist_ok=True)
    nombre = _nombre_solucion(titulo)
    ruta = SALIDAS_DIR / f"{nombre}.txt"
    contenido = _formatear_camino(grafo, camino)
    texto = "\n".join(contenido)
    ruta.write_text(texto + ("\n" if not texto.endswith("\n") else ""), encoding="utf-8")

def main():
    resultados_totales = []

    # Lista de mapas y sus tests asociados
    # (Nombre Archivo, [Lista de Tests])
    tests_planificados = [
        ("USA-road-d.NY", [
            ("Test_1(NY)_trayecto_muy_corto", "Manhattan", "Manhattan_Vecino"),
            ("Test_2(NY)_nodo_inexistente", "Manhattan", (95.0, 200.0))
        ]),
        ("USA-road-d.BAY", [
            # Ejemplo del enunciado. Se ha convertido a coordenadas los nodos 1 y 309
            ("Test_3(BAY)_caso_normal", (37.608914, -121.745853), (37.614648, -121.750370))
        ]),
        ("USA-road-d.COL", [
            ("Test_4(COL)_travesia_montanosa", "Denver", "GrandJunction"),
            ("Test_5(COL)_travesia_montanosa_inversa", "GrandJunction", "Denver")
        ]),
        ("USA-road-d.LKS", [
            ("Test_6(LKS)_rodeo_lago", "Milwaukee", "GrandRapids")
        ]),
        ("USA-road-d.FLA", [
            ("Test_7(FLA)_corredor_peninsular", "Miami", "Jacksonville")
        ]),
        ("USA-road-d.CAL", [
            ("Test_8(CAL)_larga_distancia", "SanDiego", "Sacramento")
        ]),
        ("USA-road-d.NE", [
            ("Test_9(NE)_trayecto_urbano", "Philadelphia", "NewYork_City")
        ]),
        ("USA-road-d.NW", [
            ("Test_10(NW)_trayecto_rural", "Seattle", "Spokane")
        ]),
        ("ISLAS-road-d", [
            ("Test_11(ISLAS)_islas_desconectadas", "IslaA", "IslaB")
        ])
    ]

    for mapa, tests in tests_planificados:
        try:
            ruta_base = localizar_mapa(mapa)
        except FileNotFoundError as exc:
            aviso = f"[AVISO] {exc}"
            for titulo, _, _ in tests:
                guardar_resultado(titulo, [f">>> EJECUTANDO TEST: {titulo}", f"    {aviso}"])
            continue

        g = Grafo()
        try:
            g.cargar_mapa(ruta_base)
        except Exception as e:
            aviso = f"[ERROR] Falló la carga del mapa {mapa}: {e}"
            for titulo, _, _ in tests:
                guardar_resultado(titulo, [f">>> EJECUTANDO TEST: {titulo}", f"    {aviso}"])
            continue

        for titulo, origen_key, destino_key in tests:
            log = [f">>> EJECUTANDO TEST: {titulo}"]

            try:
                coord_origen = obtener_coordenadas(origen_key)
            except KeyError:
                log.append(f"    [ERROR] No existe el nodo '{origen_key}' en la lista de ciudades")
                guardar_resultado(titulo, log)
                continue

            try:
                coord_destino = obtener_coordenadas(destino_key)
            except KeyError:
                log.append(f"    [ERROR] No existe el nodo '{destino_key}' en la lista de ciudades")
                guardar_resultado(titulo, log)
                continue

            try:
                id_origen = buscar_nodo_por_coords(g, *coord_origen)
            except ValueError:
                log.append(f"    [ERROR] Coordenadas inválidas para '{origen_key}'")
                guardar_resultado(titulo, log)
                continue

            try:
                id_destino = buscar_nodo_por_coords(g, *coord_destino)
            except ValueError:
                log.append(f"    [ERROR] Coordenadas inválidas para '{destino_key}'")
                guardar_resultado(titulo, log)
                continue

            if id_origen is None or id_destino is None:
                log.append(f"    [ERROR] No se pudieron localizar los nodos para {origen_key} o {destino_key}")
                guardar_resultado(titulo, log)
                continue

            lineas_test, res, camino = ejecutar_test(g, titulo, origen_key, destino_key, id_origen, id_destino)
            guardar_resultado(titulo, lineas_test)
            guardar_solucion(titulo, g, camino)
            resultados_totales.append(res)

if __name__ == "__main__":
    main()