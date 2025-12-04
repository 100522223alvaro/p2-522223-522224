"""
Implementación de la clase Grafo para representar mapas de carreteras.

Esta clase carga y almacena grafos dirigidos con coordenadas geográficas
desde ficheros en formato DIMACS, permitiendo consultas eficientes de
vecindad y costes de arcos.
"""

import os

# -----------------------------------------------------------------------------
# Clase Grafo: Representación de mapas de carreteras
# -----------------------------------------------------------------------------

class Grafo:
    """
    Clase que representa un grafo dirigido con coordenadas geográficas.
    
    Utiliza listas de adyacencia para representación eficiente en memoria
    y acceso directo por índice para nodos (indexación basada en 1).
    
    Atributos:
        adyacencia: Lista de diccionarios donde adyacencia[u][v] = coste del arco u->v
        coordenadas: Lista de tuplas (longitud, latitud) para cada nodo
        num_nodos: Número total de nodos en el grafo
        num_arcos: Número total de arcos en el grafo
    """
    
    def __init__(self):
        """Inicializa un grafo vacío.."""
        # Lista de adyacencia: adyacencia[u] = {v: coste, ...}
        self.adyacencia = [] 
        
        # Lista de coordenadas: coordenadas[nodo_id] = (longitud, latitud)
        self.coordenadas = []
        
        # Contadores de elementos del grafo
        self.num_nodos = 0
        self.num_arcos = 0

    def cargar_mapa(self, ruta_base):
        """Carga un mapa desde los ficheros .gr y .co de DIMACS."""
        # Construcción de las rutas completas a los ficheros
        ruta_gr = ruta_base + ".gr"  # Fichero de arcos/distancias
        ruta_co = ruta_base + ".co"  # Fichero de coordenadas

        # Verificación de existencia de ficheros
        if not os.path.exists(ruta_gr) or not os.path.exists(ruta_co):
            raise FileNotFoundError(f"No se encontraron los ficheros {ruta_gr} o {ruta_co}")

        # Carga de datos en orden: primero coordenadas (para dimensionar), luego arcos
        self._cargar_coordenadas(ruta_co)
        self._cargar_arcos(ruta_gr)

    def _cargar_coordenadas(self, ruta):
        """
        Lee el fichero de coordenadas en formato DIMACS.
        Formato de línea: v <id> <longitud> <latitud>
        """
        max_id = 0
        temp_coords = {}
        
        # Primera pasada: leer todas las coordenadas y encontrar el ID máximo
        with open(ruta, 'r') as f:
            for linea in f:
                # Procesamos solo las líneas que empiezan con 'v'
                if linea.startswith('v'):
                    partes = linea.split()
                    # Formato: v <id> <longitud> <latitud>
                    nid = int(partes[1])      # ID del nodo
                    lon = int(partes[2])      # Longitud * 10^6
                    lat = int(partes[3])      # Latitud * 10^6
                    
                    temp_coords[nid] = (lon, lat)
                    
                    # Actualizamos el ID máximo para dimensionar las listas
                    if nid > max_id:
                        max_id = nid
        
        self.num_nodos = max_id
        
        # Inicializamos listas con tamaño fijo para acceso directo por índice
        # +1 porque los IDs de DIMACS empiezan en 1 (no en 0)
        for i in range(max_id + 1):
            self.coordenadas.append((0, 0))

        for i in range(max_id + 1):
            self.adyacencia.append({})

        # Segunda pasada: asignar coordenadas a sus posiciones en la lista
        for nid, coord in temp_coords.items():
            self.coordenadas[nid] = coord

    def _cargar_arcos(self, ruta):
        """
        Lee el fichero de arcos/distancias en formato DIMACS.
        Formato de línea: a <id_origen> <id_destino> <coste>
        El coste representa distancia en metros.
        """
        count = 0
        
        with open(ruta, 'r') as f:
            for linea in f:
                # Procesamos solo las líneas que empiezan con 'a'
                if linea.startswith('a'):
                    # Formato: a <id_origen> <id_destino> <peso>
                    partes = linea.split()
                    u = int(partes[1])  # Nodo origen
                    v = int(partes[2])  # Nodo destino
                    w = int(partes[3])  # Coste del arco en metros
                    
                    # Guardamos el arco en la lista de adyacencia
                    # Si hay arcos duplicados, se sobrescribe (quedamos con el último)
                    self.adyacencia[u][v] = w
                    count += 1
        
        self.num_arcos = count

    def get_vecinos(self, nodo):
        """Obtiene los vecinos de un nodo con sus costes."""
        return self.adyacencia[nodo].items()

    def get_coordenadas(self, nodo):
        """Obtiene las coordenadas geográficas de un nodo."""
        return self.coordenadas[nodo]

    def coste_arco(self, u, v):
        """Obtiene el coste del arco entre dos nodos."""
        return self.adyacencia[u].get(v, float('inf'))