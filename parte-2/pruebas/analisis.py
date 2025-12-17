#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import math
import os
import re
from pathlib import Path

# Ajuste del path para poder importar los modulos de la carpeta superior
# Determinar la carpeta actual del script de análisis
SCRIPT_DIR = Path(__file__).resolve().parent
# Carpeta raíz de la parte 2 (un nivel por encima)
RAIZ_PARTE2 = SCRIPT_DIR.parent
# Inyectar la ruta raíz para permitir imports relativos
if str(RAIZ_PARTE2) not in sys.path:
    sys.path.insert(0, str(RAIZ_PARTE2))

from grafo import Grafo
from algoritmo import AStar, Dijkstra

# Definimos las coordenadas de las ciudades usadas en los tests. Formato: (Latitud, Longitud)
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

    # EXTREMOS CALIFORNIA (Caso extremo)
    "CrescentCity": (41.7558, -124.2026), 
    "SanYsidro":    (32.5556, -117.0470)
}

# Configuración de rutas para mapas y salidas
MAPAS_DIR = Path(os.environ.get("MAPAS_DIR", RAIZ_PARTE2 / "mapas")).resolve()
RESULTADOS_DIR = SCRIPT_DIR / "resultados"
SALIDAS_DIR = SCRIPT_DIR / "salidas"

def localizar_mapa(nombre_base):
    """Devuelve la ruta base si existen los ficheros .gr y .co."""
    base = MAPAS_DIR / nombre_base  # carpeta donde debería estar el mapa
    ruta_gr = base.parent / f"{base.name}.gr"  # fichero de arcos
    ruta_co = base.parent / f"{base.name}.co"  # fichero de coordenadas

    # Comprobamos que ambos ficheros existen antes de usar la ruta
    if ruta_gr.exists() and ruta_co.exists():
        return str(base)

    # Avisamos en caso de mapas ausentes para poder saltar el test
    raise FileNotFoundError(
        f"Ficheros no encontrados en {MAPAS_DIR}. Se requiere .gr y .co para {nombre_base}."
    )

# Utilidades auxiliares
def distancia_euclidea_simple(lat1, lon1, lat2, lon2):
    """Calculo rapido de distancia para la aproximacion de nodos."""
    return math.sqrt((lat1-lat2)**2 + (lon1-lon2)**2)

def buscar_nodo_cercano(grafo, lat_objetivo, lon_objetivo):
    """Localiza el id del nodo mas cercano a unas coordenadas dadas."""
    # Validamos que las coordenadas tengan sentido geográfico
    if not (-90 <= lat_objetivo <= 90) or not (-180 <= lon_objetivo <= 180):
        raise ValueError("Coordenadas fuera de rango valido")

    # Convertimos a enteros porque el grafo trabaja en grados * 10^6
    lat_target = int(lat_objetivo * 1000000)
    lon_target = int(lon_objetivo * 1000000)

    mejor_nodo = None  # guardará el id mas cercano
    menor_dist = float("inf")  # valor inicial alto para comparar

    # Recorremos todos los nodos disponibles
    for nodo_id, coords in enumerate(grafo.coordenadas):
        if nodo_id == 0:
            continue  # el índice 0 no se usa en DIMACS

        # Los ficheros pueden guardar (lon, lat) o (lat, lon)
        c1, c2 = coords

        # Calculamos ambas posibilidades y nos quedamos con la menor
        d1 = distancia_euclidea_simple(lat_target, lon_target, c2, c1)
        d2 = distancia_euclidea_simple(lat_target, lon_target, c1, c2)
        actual = min(d1, d2)

        # Actualizamos el registro del nodo mas cercano
        if actual < menor_dist:
            menor_dist = actual
            mejor_nodo = nodo_id

    return mejor_nodo

def resolver_coordenadas(ref):
    """Devuelve la coordenada (lat, lon) según el tipo de referencia."""
    if isinstance(ref, str):
        if ref not in CIUDADES:
            raise KeyError(f"Ciudad '{ref}' no definida")
        return CIUDADES[ref]  # obtenemos la ciudad del diccionario
    if isinstance(ref, (tuple, list)) and len(ref) == 2:
        return float(ref[0]), float(ref[1])  # aceptamos coordenadas directas
    raise KeyError("Referencia de coordenadas no valida")

def ejecutar_comparativa(grafo, titulo, inicio_nom, fin_nom, inicio_id, fin_id):
    """Lanza A* y Dijkstra para el mismo trayecto y registra métricas."""
    reporte = []
    reporte.append(f">>> TEST: {titulo}")
    reporte.append(f"    Trayecto: {inicio_nom} ({inicio_id}) -> {fin_nom} ({fin_id})")

    # 1) Ejecucion A*
    solver_astar = AStar(grafo)
    t0 = time.time()
    coste_astar, camino_astar = solver_astar.resolver(inicio_id, fin_id)
    t1 = time.time()
    t_astar = t1 - t0
    nodos_astar = solver_astar.nodos_expandidos
    reporte.append(f"    A* completado en {t_astar:.3f}s")

    # 2) Ejecucion Dijkstra
    solver_dijkstra = Dijkstra(grafo)
    t2 = time.time()
    coste_dijkstra, _ = solver_dijkstra.resolver(inicio_id, fin_id)
    t3 = time.time()
    t_dijkstra = t3 - t2
    nodos_dijkstra = solver_dijkstra.nodos_expandidos
    reporte.append(f"    Dijkstra completado en {t_dijkstra:.3f}s")

    # 3) Analisis de resultados
    status = "OK"
    mejora = 0.0

    # Comprobamos que ambos algoritmos devuelven el mismo coste
    if coste_astar != coste_dijkstra:
        status = "FALLO: Los costes no coinciden"

    # Calculamos la mejora en nodos expandidos respecto a Dijkstra
    if nodos_dijkstra > 0:
        mejora = 100 * (nodos_dijkstra - nodos_astar) / nodos_dijkstra

    reporte.append("    METRICAS:")
    reporte.append(f"      A* -> Coste: {coste_astar} | Nodos: {nodos_astar} | Tiempo: {t_astar:.4f}s")
    reporte.append(f"      Dijkstra -> Coste: {coste_dijkstra} | Nodos: {nodos_dijkstra} | Tiempo: {t_dijkstra:.4f}s")
    reporte.append(f"      A* expandio un {mejora:.2f}% menos de nodos que Dijkstra.")
    reporte.append(f"      Resultado: {status}")

    return reporte, camino_astar

def guardar_log(titulo, lineas):
    """Guarda el log textual de un test en la carpeta de resultados."""
    RESULTADOS_DIR.mkdir(parents=True, exist_ok=True)
    ruta = RESULTADOS_DIR / f"{titulo}_resultado.txt"
    contenido = "\n".join(lineas)
    # Escribir con salto de linea final
    ruta.write_text(contenido + "\n", encoding="utf-8")

def generar_nombre_solucion(titulo):
    """Genera un nombre de archivo limpio para la solucion."""
    match = re.match(r"Test_(\d+\([^)]+\))", titulo)
    if match:
        return f"solucion_test_{match.group(1)}"
    return f"solucion_{titulo.replace(' ', '_')}"

def formatear_camino_salida(grafo, camino):
    """Genera una linea con el camino intercalando costes."""
    # Si no hay camino (lista vacía o None), devolvemos un marcador explícito.
    if not camino:
        return ["SIN SOLUCION"]
    
    # Empezamos la salida con el primer nodo del camino.
    segmentos = [str(camino[0])]  

    # Recorremos pares consecutivos (u -> v) para insertar el coste del arco entre nodos.
    for u, v in zip(camino, camino[1:]):
        # Recupera el coste del arco (u, v) desde el grafo.
        coste = grafo.coste_arco(u, v)

        # Si por algún motivo el coste es infinito, lo representamos como "INF".
        if coste == float('inf'):
            val_coste = "INF"
        else:
            val_coste = str(coste)

        segmentos.append(f"({val_coste})")
        segmentos.append(str(v))

    # Devuelve una lista de líneas.
    return [" - ".join(segmentos)]

def guardar_fichero_solucion(titulo, grafo, camino):
    """Guarda el camino final en la carpeta de salidas."""
    # Asegura que el directorio de salidas existe.
    SALIDAS_DIR.mkdir(parents=True, exist_ok=True)

    # Genera un nombre de fichero a partir del título del test.
    nombre = generar_nombre_solucion(titulo)
    ruta = SALIDAS_DIR / f"{nombre}.txt"

    # Convierte el camino (lista de nodos) a una representación en texto.
    lineas = formatear_camino_salida(grafo, camino)

    # Escribe el fichero con salto de línea final.
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")

def main():
    """Función principal que ejecuta todos los tests planificados."""

    # 1) Planificación de test agrupados por mapa
    tests_planificados = [
        ("USA-road-d.NY", [
            ("Test_1(NY)_trayecto_muy_corto", "Manhattan", "Manhattan_Vecino"),
            # Establecemos unas coordenadas inválidas
            ("Test_2(NY)_nodo_inexistente", "Manhattan", (95.0, 200.0))
        ]),
        ("USA-road-d.BAY", [
            # Estas cooredenadas corresponden a los nodos 1 y 309 utilizados en el ejemplo del enunciado
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

    # 2) Bucle principal: recorremos cada mapa y su lista de pruebas
    for mapa, tests in tests_planificados:
        # 2.1) Carga del mapa: localiza archivos y carga el grafo
        try:
            # Resuelve la ruta base del mapa (lanza FileNotFoundError si no existe).
            ruta_base = localizar_mapa(mapa) 
        except FileNotFoundError as exc:
            print(f"[AVISO] Saltando mapa {mapa}: {exc}")
            continue

        print(f"Cargando grafo: {mapa} ...")
        g = Grafo()
        try:
            # Carga de datos del mapa (nodos/aristas/coordenadas).
            g.cargar_mapa(ruta_base)
        except Exception as e:
            # Si falla la carga, no tiene sentido ejecutar tests de ese mapa.
            err_msg = f"Error critico al cargar mapa {mapa}: {e}"
            print(err_msg)

            # Registra el fallo para cada test, para que quede trazabilidad.
            for titulo, _, _ in tests:
                guardar_log(titulo, [f">>> TEST: {titulo}", f"    {err_msg}"])
            continue

        # 2.2) Ejecución de tests del mapa ya cargado
        for titulo, origen_ref, destino_ref in tests:
            # Buffer local para registrar eventos/errores de este test.
            log_buffer = [f">>> INICIANDO: {titulo}"]

            # 2.2.1) Resolución de referencias a coordenadas y a IDs de nodo
            try:
                # Convierte "Nombre" -> (lat, lon) o valida tuplas (lat, lon).
                coord_origen = resolver_coordenadas(origen_ref)
                coord_destino = resolver_coordenadas(destino_ref)

                # Busca el vértice más cercano del grafo a cada coordenada.
                id_origen = buscar_nodo_cercano(g, *coord_origen)
                id_destino = buscar_nodo_cercano(g, *coord_destino)

                # Si no se pudo mapear, abortamos el test con error controlado.
                if id_origen is None or id_destino is None:
                    raise ValueError("No se encontraron nodos cercanos validos.")

            except Exception as e:
                # Errores típicos: coordenadas fuera de rango, ciudad no definida,
                # o fallo en la búsqueda del nodo más cercano.
                log_buffer.append(f"    [ERROR] Fallo en preparacion del test: {e}")
                guardar_log(titulo, log_buffer)
                continue

            # 2.2.2) Ejecución de la comparativa A* vs Dijkstra y guardado de resultados
            print(f"  -> Ejecutando {titulo}...")
            # Ejecuta ambos algoritmos, devuelve líneas de log y el camino
            lineas_res, camino = ejecutar_comparativa(g, titulo, origen_ref, destino_ref, id_origen, id_destino)

            # Guarda log detallado del test
            guardar_log(titulo, lineas_res)

            # Guarda el camino final
            guardar_fichero_solucion(titulo, g, camino)

    print("\n--- Ejecucion de pruebas finalizada ---")

if __name__ == "__main__":
    main()