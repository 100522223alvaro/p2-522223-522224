#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import math
import os
import re
from pathlib import Path

# Ajuste del path para poder importar los modulos de la carpeta superior
SCRIPT_DIR = Path(__file__).resolve().parent
RAIZ_PARTE2 = SCRIPT_DIR.parent
if str(RAIZ_PARTE2) not in sys.path:
    sys.path.insert(0, str(RAIZ_PARTE2))

from grafo import Grafo
from algoritmo import AStar, Dijkstra

# =============================================================================
# DEFINICION DE COORDENADAS (CIUDADES Y PUNTOS DE INTERES)
# =============================================================================
# Formato: (Latitud, Longitud)
CIUDADES = {
    # NY (Camino muy corto para pruebas basicas)
    "Manhattan":    (40.7831, -73.9712),
    "Manhattan_Vecino": (40.7835, -73.9715), 
    
    # COLORADO (Terreno montañoso)
    "Denver":       (39.738386, -104.990336),
    "GrandJunction":(39.064381, -108.550848),
    
    # GREAT LAKES (Obstaculo natural)
    "Milwaukee":    (43.0389, -87.9065),
    "GrandRapids":  (42.963226, -85.668130),
    
    # FLORIDA (Ruta lineal norte-sur)
    "Miami":        (25.761477, -80.191869),
    "Jacksonville": (30.332439, -81.656017),
    
    # CALIFORNIA (Distancias largas)
    "SanDiego":     (32.715851, -117.161166),
    "Sacramento":   (38.581705, -121.494366),
    
    # NORTHEAST (Alta densidad de nodos)
    "Philadelphia": (39.9526, -75.1652),
    "NewYork_City": (40.7128, -74.0060),
    
    # NORTHWEST (Baja densidad, rural)
    "Seattle":      (47.6062, -122.3321),
    "Spokane":      (47.6588, -117.4260),

    # ISLAS (Grafo desconexo) 
    "IslaA": (0.0, -100.0),
    "IslaB": (0.0, 100.0),

    # EXTREMOS CALIFORNIA (Test de carga / El mas costoso)
    # De Crescent City (Norte) a San Ysidro (Frontera Sur)
    "CrescentCity": (41.7558, -124.2026), 
    "SanYsidro":    (32.5556, -117.0470)
}

# =============================================================================
# CONFIGURACION DE RUTAS
# =============================================================================

MAPAS_DIR = Path(os.environ.get("MAPAS_DIR", RAIZ_PARTE2 / "mapas")).resolve()
RESULTADOS_DIR = SCRIPT_DIR / "resultados"
SALIDAS_DIR = SCRIPT_DIR / "salidas"


def localizar_mapa(nombre_base):
    """
    Busca los ficheros .gr y .co en el directorio de mapas.
    Retorna la ruta base si ambos existen.
    """
    base = MAPAS_DIR / nombre_base
    ruta_gr = base.parent / f"{base.name}.gr"
    ruta_co = base.parent / f"{base.name}.co"

    if ruta_gr.exists() and ruta_co.exists():
        return str(base)

    raise FileNotFoundError(
        f"Ficheros no encontrados en {MAPAS_DIR}. Se requiere .gr y .co para {nombre_base}."
    )


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def distancia_euclidea_simple(lat1, lon1, lat2, lon2):
    """Calculo rapido de distancia para la aproximacion de nodos."""
    return math.sqrt((lat1-lat2)**2 + (lon1-lon2)**2)

def buscar_nodo_cercano(grafo, lat_objetivo, lon_objetivo):
    """
    Localiza el ID del nodo mas cercano a unas coordenadas dadas.
    Recorre linealmente los nodos cargados en memoria.
    """
    # Validacion basica de coordenadas
    if not (-90 <= lat_objetivo <= 90) or not (-180 <= lon_objetivo <= 180):
        raise ValueError("Coordenadas fuera de rango valido")

    # El grafo almacena coordenadas como enteros (grados * 10^6)
    lat_target = int(lat_objetivo * 1000000)
    lon_target = int(lon_objetivo * 1000000)
    
    mejor_nodo = None
    menor_dist = float('inf')
    
    # Iteramos sobre todos los nodos del grafo para encontrar el mas proximo
    # Nota: grafo.coordenadas es una lista donde el indice es el ID del nodo
    for nodo_id, coords in enumerate(grafo.coordenadas):
        if nodo_id == 0: continue # Saltamos el indice 0 (no usado en DIMACS)
        
        # Las coordenadas pueden venir en orden (lat, lon) o (lon, lat) dependiendo del fichero
        c1, c2 = coords 
        
        # Probamos ambas combinaciones para asegurar la distancia minima real
        d1 = distancia_euclidea_simple(lat_target, lon_target, c2, c1)
        d2 = distancia_euclidea_simple(lat_target, lon_target, c1, c2)
        
        actual = min(d1, d2)
        if actual < menor_dist:
            menor_dist = actual
            mejor_nodo = nodo_id
            
    return mejor_nodo


def resolver_coordenadas(ref):
    """Obtiene la tupla (lat, lon) desde el diccionario o directamente."""
    if isinstance(ref, str):
        if ref not in CIUDADES:
            raise KeyError(f"Ciudad '{ref}' no definida")
        return CIUDADES[ref]
    if isinstance(ref, (tuple, list)) and len(ref) == 2:
        return float(ref[0]), float(ref[1])
    raise KeyError("Referencia de coordenadas no valida")

def ejecutar_comparativa(grafo, titulo, inicio_nom, fin_nom, inicio_id, fin_id):
    """
    Ejecuta A* y Dijkstra para el mismo trayecto y compara metricas.
    """
    reporte = []
    reporte.append(f">>> TEST: {titulo}")
    reporte.append(f"    Trayecto: {inicio_nom} ({inicio_id}) -> {fin_nom} ({fin_id})")

    # 1. Ejecucion A*
    solver_astar = AStar(grafo)
    t0 = time.time()
    coste_astar, camino_astar = solver_astar.resolver(inicio_id, fin_id)
    t1 = time.time()
    t_astar = t1 - t0
    nodos_astar = solver_astar.nodos_expandidos
    reporte.append(f"    A* completado en {t_astar:.3f}s")

    # 2. Ejecucion Dijkstra (Fuerza Bruta / Oraculo)
    solver_dijkstra = Dijkstra(grafo)
    t2 = time.time()
    coste_dijkstra, _ = solver_dijkstra.resolver(inicio_id, fin_id)
    t3 = time.time()
    t_dijkstra = t3 - t2
    nodos_dijkstra = solver_dijkstra.nodos_expandidos
    reporte.append(f"    Dijkstra completado en {t_dijkstra:.3f}s")

    # 3. Analisis de resultados
    status = "OK"
    mejora = 0.0
    
    # Verificacion de optimalidad
    if coste_astar != coste_dijkstra:
        status = "FALLO: Los costes no coinciden"
        
    # Calculo de eficiencia
    if nodos_dijkstra > 0:
        mejora = 100 * (nodos_dijkstra - nodos_astar) / nodos_dijkstra

    reporte.append("    METRICAS:")
    reporte.append(f"      A* -> Coste: {coste_astar} | Nodos: {nodos_astar} | Tiempo: {t_astar:.4f}s")
    reporte.append(f"      Dijkstra -> Coste: {coste_dijkstra} | Nodos: {nodos_dijkstra} | Tiempo: {t_dijkstra:.4f}s")
    reporte.append(f"      A* expandio un {mejora:.2f}% menos de nodos que Dijkstra.")
    reporte.append(f"      Resultado: {status}")
    
    datos_estructurados = {
        "test": titulo,
        "nodos_astar": nodos_astar,
        "nodos_dijkstra": nodos_dijkstra,
        "tiempo_astar": t_astar,
        "tiempo_dijkstra": t_dijkstra,
        "mejora": mejora,
        "status": status
    }
    
    return reporte, datos_estructurados, camino_astar


def guardar_log(titulo, lineas):
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
    ruta = RESULTADOS_DIR / f"{titulo}_resultado.txt"
    contenido = "\n".join(lineas)
    # Escribir con salto de linea final estilo UNIX
    ruta.write_text(contenido + "\n", encoding="utf-8")


def generar_nombre_solucion(titulo):
    """Genera un nombre de archivo limpio para la solucion."""
    match = re.match(r"Test_(\d+\([^)]+\))", titulo)
    if match:
        return f"solucion_test_{match.group(1)}"
    return f"solucion_{titulo.replace(' ', '_')}"


def formatear_camino_salida(grafo, camino):
    """Formatea el camino segun especificaciones de la practica."""
    if not camino:
        return ["SIN SOLUCION"]

    # Formato: nodo - (coste) - nodo ...
    segmentos = [str(camino[0])]
    for u, v in zip(camino, camino[1:]):
        coste = grafo.coste_arco(u, v)
        val_coste = "INF" if coste == float('inf') else str(coste)
        segmentos.append(f"({val_coste})")
        segmentos.append(str(v))

    return [" - ".join(segmentos)]


def guardar_fichero_solucion(titulo, grafo, camino):
    SALIDAS_DIR.mkdir(parents=True, exist_ok=True)
    nombre = generar_nombre_solucion(titulo)
    ruta = SALIDAS_DIR / f"{nombre}.txt"
    lineas = formatear_camino_salida(grafo, camino)
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")

def main():
    resultados_globales = []

    # =========================================================================
    # PLANIFICACION DE TESTS
    # Estructura: (Nombre_Mapa, [Lista_de_Tests])
    # =========================================================================
    tests_planificados = [
        ("USA-road-d.NY", [
            ("Test_1(NY)_trayecto_muy_corto", "Manhattan", "Manhattan_Vecino"),
            ("Test_2(NY)_nodo_inexistente", "Manhattan", (95.0, 200.0))
        ]),
        ("USA-road-d.BAY", [
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
            ("Test_8(CAL)_larga_distancia", "SanDiego", "Sacramento"),
            # NUEVO TEST: El mas costoso (Extremo a Extremo)
            ("Test_12(CAL)_extremo_norte_sur", "CrescentCity", "SanYsidro")
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

    # Bucle principal de ejecucion
    for mapa, tests in tests_planificados:
        # 1. Carga del mapa
        try:
            ruta_base = localizar_mapa(mapa)
        except FileNotFoundError as exc:
            print(f"[AVISO] Saltando mapa {mapa}: {exc}")
            continue

        print(f"Cargando grafo: {mapa} ...")
        g = Grafo()
        try:
            g.cargar_mapa(ruta_base)
        except Exception as e:
            err_msg = f"Error critico al cargar mapa {mapa}: {e}"
            print(err_msg)
            # Registramos el error en los logs de los tests afectados
            for titulo, _, _ in tests:
                guardar_log(titulo, [f">>> TEST: {titulo}", f"    {err_msg}"])
            continue

        # 2. Ejecucion de los tests asociados al mapa
        for titulo, origen_ref, destino_ref in tests:
            log_buffer = [f">>> INICIANDO: {titulo}"]

            # Resolucion de coordenadas y nodos
            try:
                coord_origen = resolver_coordenadas(origen_ref)
                coord_destino = resolver_coordenadas(destino_ref)
                
                id_origen = buscar_nodo_cercano(g, *coord_origen)
                id_destino = buscar_nodo_cercano(g, *coord_destino)

                if id_origen is None or id_destino is None:
                    raise ValueError("No se encontraron nodos cercanos validos.")

            except Exception as e:
                log_buffer.append(f"    [ERROR] Fallo en preparacion del test: {e}")
                guardar_log(titulo, log_buffer)
                continue

            # Ejecucion y guardado
            print(f"  -> Ejecutando {titulo}...")
            lineas_res, metricas, camino = ejecutar_comparativa(g, titulo, origen_ref, destino_ref, id_origen, id_destino)
            
            guardar_log(titulo, lineas_res)
            guardar_fichero_solucion(titulo, g, camino)
            resultados_globales.append(metricas)

    print("\n--- Ejecucion de pruebas finalizada ---")

if __name__ == "__main__":
    main()