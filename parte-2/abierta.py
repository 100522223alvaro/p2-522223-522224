"""
Implementación de la Lista Abierta para el algoritmo A*.

Esta clase gestiona el conjunto de nodos pendientes de explorar,
ordenados por su valor f(n) = g(n) + h(n)
"""

import heapq

# -----------------------------------------------------------------------------
# Clase ListaAbierta: Gestión de nodos a explorar en A*
# -----------------------------------------------------------------------------

class ListaAbierta:
    """Clase que implementa la lista abierta (frontera) del algoritmo A*."""
    
    def __init__(self):
        """Inicializa una lista abierta vacía."""
        # Heap que almacena elementos como (f_score, nodo_id)
        # El heap se ordena automáticamente por el primer elemento de la tupla (f_score), menor valor = mayor prioridad
        self.heap = []
    
    def push(self, nodo, f_score):
        """Inserta un nodo en la lista abierta con su valor f(n)."""
        heapq.heappush(self.heap, (f_score, nodo))
        
    def pop(self):
        """Extrae y retorna el nodo con menor valor f(n) de la lista abierta."""
        # Verificamos si el heap está vacío
        if not self.heap:
            return None
        
        # Extraemos y retornamos el elemento con menor f_score
        return heapq.heappop(self.heap)
        
    def is_empty(self):
        """Verifica si la lista abierta está vacía."""
        return len(self.heap) == 0