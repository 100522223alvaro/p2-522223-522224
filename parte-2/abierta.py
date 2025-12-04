"""
Implementación de la Lista Abierta para el algoritmo A*.

Esta clase gestiona el conjunto de nodos pendientes de explorar,
ordenados por su valor f(n) = g(n) + h(n)
"""

# -----------------------------------------------------------------------------
# Clase ListaAbierta: Gestión de nodos a explorar en A*
# -----------------------------------------------------------------------------

class ListaAbierta:
    """Clase que implementa la lista abierta (frontera) del algoritmo A*."""
    
    def __init__(self):
        """Inicializa una lista abierta vacía."""
        self.lista = []
    
    def push(self, nodo, f_score):
        """Inserta un nodo en la lista abierta con su valor f(n)."""
        self.lista.append((f_score, nodo))
        
    def pop(self):
        """Extrae y retorna el nodo con menor valor f(n) de la lista abierta."""
        if not self.lista:
            return None
        
        # Búsqueda lineal del elemento con menor f_score
        # Encontramos el índice del elemento con menor f_score
        idx_min = 0
        for i in range(1, len(self.lista)):
            if self.lista[i][0] < self.lista[idx_min][0]:
                idx_min = i
        
        # Extraemos el elemento
        return self.lista.pop(idx_min)
        
    def is_empty(self):
        """Verifica si la lista abierta está vacía."""
        return len(self.lista) == 0