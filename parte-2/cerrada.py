"""
Implementación de la Lista Cerrada para el algoritmo A*.

Esta clase gestiona el conjunto de nodos ya visitados/expandidos durante
la búsqueda, evitando reexpansiones innecesarias y garantizando la
terminación del algoritmo en grafos finitos.
"""
# -----------------------------------------------------------------------------
# Clase ListaCerrada: Gestión de nodos ya explorados en A*
# -----------------------------------------------------------------------------

class ListaCerrada:
    """Clase que implementa la lista cerrada del algoritmo A*."""
    
    def __init__(self):
        """Inicializa una lista cerrada vacía."""
        # Conjunto que almacena los IDs de los nodos ya visitados/expandidos
        self.visitados = set()
    
    def add(self, nodo):
        """Añade un nodo a la lista cerrada."""
        # Insertamos el nodo en el conjunto de visitados
        self.visitados.add(nodo)
    
    def contains(self, nodo):
        """Verifica si un nodo ya ha sido visitado/expandido."""
        # Comprobamos si el nodo pertenece al conjunto de visitados
        return nodo in self.visitados