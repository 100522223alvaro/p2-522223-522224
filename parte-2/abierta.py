import heapq

class ListaAbierta:
    def __init__(self):
        # Elementos: (f_score, nodo_id)
        self.heap = []
    
    def push(self, nodo, f_score):
        heapq.heappush(self.heap, (f_score, nodo))
        
    def pop(self):
        # Devuelve (f_score, nodo)
        if not self.heap:
            return None
        return heapq.heappop(self.heap)
        
    def is_empty(self):
        return len(self.heap) == 0