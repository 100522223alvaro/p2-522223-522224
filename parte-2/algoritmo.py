import math
from abierta import ListaAbierta
from cerrada import ListaCerrada

class AStar:
    def __init__(self, grafo):
        self.grafo = grafo
        self.nodos_expandidos = 0

    def _heuristica(self, nodo_actual, nodo_objetivo):
        """
        Calcula la distancia Haversine entre dos nodos.
        Las coordenadas vienen multiplicadas por 10^6 en los ficheros.
        Radio Tierra ~ 6371000 metros.
        """
        lon1, lat1 = self.grafo.get_coordenadas(nodo_actual)
        lon2, lat2 = self.grafo.get_coordenadas(nodo_objetivo)

        # Convertir a grados reales y luego a radianes
        # lat/lon en archivo están * 10^6
        rlat1 = math.radians(lat1 / 1000000.0)
        rlon1 = math.radians(lon1 / 1000000.0)
        rlat2 = math.radians(lat2 / 1000000.0)
        rlon2 = math.radians(lon2 / 1000000.0)

        dlat = rlat2 - rlat1
        dlon = rlon2 - rlon1

        # Fórmula de Haversine
        a = math.sin(dlat / 2)**2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        R = 6371000 # Radio de la tierra en metros
        return R * c

    def resolver(self, inicio, fin):
        """
        Ejecuta A* para encontrar el camino más corto.
        Retorna: (coste_total, camino_lista) o (None, []) si no hay camino.
        """
        abierta = ListaAbierta()
        cerrada = ListaCerrada()
        
        # g_score: coste real desde inicio hasta n
        # Inicializamos con infinito, usando dict o array. 
        # Como los IDs son densos, un array es ligeramente más rápido, 
        # pero un dict es más seguro si hubiera huecos. Usaremos dict por flexibilidad.
        g_score = {inicio: 0}
        
        # came_from: para reconstruir el camino {hijo: padre}
        came_from = {}

        # f_score inicial
        h_inicial = self._heuristica(inicio, fin)
        abierta.push(inicio, h_inicial)

        self.nodos_expandidos = 0

        while not abierta.is_empty():
            f_actual, u = abierta.pop()

            # Si llegamos al destino
            if u == fin:
                return g_score[u], self._reconstruir_camino(came_from, inicio, fin)

            # Si ya visitamos este nodo con un coste menor o igual, lo ignoramos
            # (Lazy deletion en heap)
            if cerrada.contains(u):
                continue
            
            cerrada.add(u)
            self.nodos_expandidos += 1

            # Expansión de vecinos
            for v, peso in self.grafo.get_vecinos(u):
                if cerrada.contains(v):
                    continue

                tentative_g = g_score[u] + peso
                
                # Si encontramos un camino mejor hacia v
                if v not in g_score or tentative_g < g_score[v]:
                    g_score[v] = tentative_g
                    h_v = self._heuristica(v, fin)
                    f_v = tentative_g + h_v
                    abierta.push(v, f_v)
                    came_from[v] = u

        return None, []

    def _reconstruir_camino(self, came_from, inicio, fin):
        camino = [fin]
        actual = fin
        while actual != inicio:
            actual = came_from[actual]
            camino.append(actual)
        camino.reverse()
        return camino