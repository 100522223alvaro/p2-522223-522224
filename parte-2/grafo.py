import os

class Grafo:
    def __init__(self):
        # indices 1-based, usamos size + 1.
        # adj[u] = {v: coste, ...}
        self.adyacencia = [] 
        self.coordenadas = [] # [(lon, lat), ...]
        self.num_nodos = 0
        self.num_arcos = 0

    def cargar_mapa(self, ruta_base):
        """Carga los ficheros .gr y .co basándose en el nombre base."""
        ruta_gr = ruta_base + ".gr"
        ruta_co = ruta_base + ".co"

        if not os.path.exists(ruta_gr) or not os.path.exists(ruta_co):
            raise FileNotFoundError(f"No se encontraron los ficheros {ruta_gr} o {ruta_co}")

        self._cargar_coordenadas(ruta_co)
        self._cargar_arcos(ruta_gr)

    def _cargar_coordenadas(self, ruta):
        """Lee el fichero de coordenadas (formato DIMACS)."""
        max_id = 0
        temp_coords = {}
        
        with open(ruta, 'r') as f:
            for linea in f:
                if linea.startswith('v'):
                    partes = linea.split()
                    # v <id> <longitud> <latitud>
                    nid = int(partes[1])
                    lon = int(partes[2])
                    lat = int(partes[3])
                    temp_coords[nid] = (lon, lat)
                    if nid > max_id:
                        max_id = nid
        
        self.num_nodos = max_id
        # Inicializamos listas con tamaño fijo para acceso directo por índice
        # +1 porque los IDs de DIMACS empiezan en 1
        self.coordenadas = [(0, 0)] * (max_id + 1)
        self.adyacencia = [{} for _ in range(max_id + 1)]

        for nid, coord in temp_coords.items():
            self.coordenadas[nid] = coord

    def _cargar_arcos(self, ruta):
        """Lee el fichero de distancias/arcos."""
        count = 0
        with open(ruta, 'r') as f:
            for linea in f:
                if linea.startswith('a'):
                    # a <uIdx> <vIdx> <weight>
                    partes = linea.split()
                    u = int(partes[1])
                    v = int(partes[2])
                    w = int(partes[3])
                    
                    # Guardamos en la lista de adyacencia
                    # Si existen arcos duplicados, nos quedamos con el menor (o sobreescribimos)
                    self.adyacencia[u][v] = w
                    count += 1
        self.num_arcos = count

    def get_vecinos(self, nodo):
        """Devuelve un iterable de (vecino, coste)."""
        return self.adyacencia[nodo].items()

    def get_coordenadas(self, nodo):
        return self.coordenadas[nodo]

    def coste_arco(self, u, v):
        return self.adyacencia[u].get(v, float('inf'))