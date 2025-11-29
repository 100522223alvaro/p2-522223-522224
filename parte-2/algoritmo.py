"""
Implementación del algoritmo A* para búsqueda de caminos óptimos.

Este módulo contiene la implementación del algoritmo A* que utiliza la
distancia Haversine como heurística admisible para encontrar el camino
más corto en grafos de carreteras con coordenadas geográficas.

"""

import math
from abierta import ListaAbierta
from cerrada import ListaCerrada

# -----------------------------------------------------------------------------
# Clase AStar: Algoritmo de búsqueda heurística A*
# -----------------------------------------------------------------------------

class AStar:
    """
    Implementación del algoritmo A* para búsqueda de camino óptimo.
    
    A* es un algoritmo de búsqueda informada que utiliza una función de
    evaluación f(n) = g(n) + h(n), donde g(n) es el coste real desde el
    inicio hasta n, y h(n) es una estimación heurística hasta el objetivo.
    
    Atributos:
        grafo: Instancia de la clase Grafo con el mapa a explorar
        nodos_expandidos: Contador de nodos expandidos durante la búsqueda
    """
    
    def __init__(self, grafo):
        """Inicializa el algoritmo A* con un grafo."""
        self.grafo = grafo
        self.nodos_expandidos = 0  # Contador de estadísticas

    def _heuristica(self, nodo_actual, nodo_objetivo):
        """
        Calcula la distancia Haversine entre dos nodos.
        
        La distancia Haversine es una heurística admisible (nunca sobreestima)
        para calcular la distancia más corta sobre la superficie de una esfera.
        
        Args:
            nodo_actual: ID del nodo desde el que se calcula la distancia
            nodo_objetivo: ID del nodo objetivo
        
        Las coordenadas en el grafo vienen multiplicadas por 10^6.
        Radio de la Tierra: aproximadamente 6.371.000 metros.
        """
        
        # Obtener coordenadas de ambos nodos
        lon1, lat1 = self.grafo.get_coordenadas(nodo_actual)
        lon2, lat2 = self.grafo.get_coordenadas(nodo_objetivo)

        # Convertir coordenadas a grados reales (dividir por 10^6) y luego a radianes
        rlat1 = math.radians(lat1 / 1000000.0)
        rlon1 = math.radians(lon1 / 1000000.0)
        rlat2 = math.radians(lat2 / 1000000.0)
        rlon2 = math.radians(lon2 / 1000000.0)

        # Diferencias de latitud y longitud
        dlat = rlat2 - rlat1
        dlon = rlon2 - rlon1

        # Aplicación de la fórmula de Haversine
        # a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
        a = math.sin(dlat / 2)**2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2)**2
        
        # c = 2 * atan2(√a, √(1-a))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        # Distancia = Radio * c
        R = 6371000  # Radio de la Tierra en metros
        return R * c

    def resolver(self, inicio, fin):
        """
        Ejecuta el algoritmo A* para encontrar el camino más corto.
        
        Args:
            inicio: ID del nodo de inicio
            fin: ID del nodo objetivo
        """
        # Inicialización de estructuras de datos
        abierta = ListaAbierta()    # Nodos por explorar (frontera)
        cerrada = ListaCerrada()    # Nodos ya expandidos
        
        # g_score: diccionario que almacena el coste real desde inicio hasta cada nodo
        # Usamos dict para flexibilidad (IDs no siempre son densos)
        g_score = {inicio: 0}
        
        # came_from: diccionario para reconstruir el camino {nodo_hijo: nodo_padre}
        came_from = {}

        # Insertar nodo inicial en la lista abierta con f(n) = g(n) + h(n)
        h_inicial = self._heuristica(inicio, fin)
        abierta.push(inicio, h_inicial)  # f(inicio) = 0 + h(inicio)

        # Reiniciar contador de expansiones
        self.nodos_expandidos = 0

        # Bucle principal de A*: explorar hasta encontrar solución o agotar opciones
        while not abierta.is_empty():
            # Extraer el nodo con menor f(n) de la lista abierta
            f_actual, u = abierta.pop()

            # Condición de éxito: hemos alcanzado el nodo objetivo
            if u == fin:
                return g_score[u], self._reconstruir_camino(came_from, inicio, fin)

            # Lazy deletion: ignorar nodos ya expandidos
            # (pueden aparecer duplicados en el heap con diferentes f_scores)
            if cerrada.contains(u):
                continue
            
            # Marcar nodo como expandido
            cerrada.add(u)
            self.nodos_expandidos += 1

            # Expansión: explorar todos los vecinos del nodo actual
            for v, peso in self.grafo.get_vecinos(u):
                # Saltar vecinos ya expandidos
                if cerrada.contains(v):
                    continue

                # Calcular coste tentativo de llegar a v a través de u
                tentative_g = g_score[u] + peso
                
                # Si encontramos un camino mejor hacia v (o es la primera vez que lo visitamos)
                if v not in g_score or tentative_g < g_score[v]:
                    # Actualizar mejor camino conocido hacia v
                    g_score[v] = tentative_g
                    
                    # Calcular f(v) = g(v) + h(v)
                    h_v = self._heuristica(v, fin)
                    f_v = tentative_g + h_v
                    
                    # Insertar v en la lista abierta con su nuevo f_score
                    abierta.push(v, f_v)
                    
                    # Registrar el predecesor para reconstruir el camino
                    came_from[v] = u

        # Si llegamos aquí, no hay camino entre inicio y fin
        return None, []

    def _reconstruir_camino(self, came_from, inicio, fin):
        """
        Reconstruye el camino desde el inicio hasta el fin.
        
        Args:
            came_from: Diccionario {nodo_hijo: nodo_padre} con los predecesores
            inicio: ID del nodo inicial
            fin: ID del nodo final
        
        Returns:
            list: Lista ordenada de IDs de nodos desde inicio hasta fin
        
        """
        # Construir camino en orden inverso (de fin a inicio)
        camino = [fin]
        actual = fin
        
        # Retroceder siguiendo los predecesores hasta llegar al inicio
        while actual != inicio:
            actual = came_from[actual]
            camino.append(actual)
        
        # Invertir para obtener el camino de inicio a fin
        camino.reverse()
        return camino