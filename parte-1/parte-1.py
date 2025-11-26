#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from constraint import Problem, ExactSumConstraint

# -----------------------------------------------------------------------------
# Parte 1: Satisfacción de Restricciones (Binairo)
# -----------------------------------------------------------------------------

def leer_fichero(ruta):
    """Lee el fichero de entrada y devuelve la matriz del tablero y el tamaño n."""
    try:
        # Leemos todas las líneas no vacías, eliminando el salto de línea final
        with open(ruta, 'r',encoding="utf-8") as f:
            lineas = [l.strip() for l in f.readlines() if l.strip()]
        
        if len(lineas) == 0:
            raise ValueError("El fichero de entrada está vacío.")
        
        n = len(lineas)

        # El tablero debe tener al menos tamaño 2x2
        if n < 2:
            raise ValueError("El tamaño del tablero debe ser al menos 2x2.")
        
        # Para Binairo n debe ser par (para que haya el mismo número de X y O)
        if n % 2 != 0:
            raise ValueError("El tamaño del tablero debe ser par.")
        
        tablero = []
        for line in lineas:
            fila = list(line)
            # Comprobamos que todas las filas tienen longitud n
            if len(fila) != n:
                raise ValueError("El tablero no es n x n.")
            # Comprobamos que los símbolos son válidos
            for char in fila:
                if char not in ('.', 'O', 'X'):
                    raise ValueError("Símbolo inválido en el tablero.")
            tablero.append(fila)

        return tablero, n
    
    except FileNotFoundError:
        # Si el fichero no existe, mostramos un mensaje y salimos
        print(f"Error: No se encontró el fichero {ruta}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error de formato en el fichero de entrada: {e}")
        sys.exit(1)

def imprimir_tablero_str(tablero):
    """
    Devuelve una cadena con la representación del tablero.
    Cada casilla se muestra enmarcada entre barras y separadores.
    """
    n = len(tablero)
    tablero_str = []
    
    # Línea separadora horizontal
    separador = "+---"*n + "+"
    tablero_str.append(separador)

    # Recorremos fila a fila
    for fila in tablero:
        fila_str = "|"
        for celda in fila:
            # Convertir . a espacio para la visualización 
            if celda == '.':
                valor = " "
            else:
                valor = celda
            fila_str += f" {valor} |"
        tablero_str.append(fila_str)
        tablero_str.append(separador)

    # Unimos todas las líneas en una única cadena
    return "\n".join(tablero_str)

def resolver_binairo(tablero_inicial, n):
    """
    Crea y resuelve el problema Binairo como un CSP.

    Restricciones:
      1) Respetar casillas ya preasignadas en la instancia inicial.
      2) En cada fila y cada columna, debe haber exactamente n/2 discos negros (y n/2 blancos).
      3) No puede haber tres discos consecutivos del mismo color ni en filas ni en columnas.

    Devuelve una lista con todas las soluciones encontradas.
    """
    
    # Creamos el problema de satisfacción de restricciones
    problem = Problem()
    
    # Definimos las variables: una por casilla, identificada por la tupla (fila i, columna j)
    # Dominio general: 0 para 'O' (Blanco), 1 para 'X' (Negro)
    coords = []
    domain = [0, 1]
    for i in range(n):
        for j in range(n):
            coords.append((i, j))

    # Añadimos todas las variables con el dominio [0, 1]
    problem.addVariables(coords, domain)
    
  
    # 1) Restricción unaria: Respetar casillas preasignadas en la instancia inicial.
    #   - Si una casilla es 'O', su variable solo puede valer 0.
    #   - Si es 'X', su variable solo puede valer 1.
    for i in range(n):
        for j in range(n):
            variable = tablero_inicial[i][j]
            if variable == 'O':
                # Restricción unaria: x == 0
                problem.addConstraint(lambda x: x == 0, [(i, j)])
            elif variable == 'X':
                # Restricción unaria: x == 1
                problem.addConstraint(lambda x: x == 1, [(i, j)])

    # 2) Restricción: Mismo número de blancos y negros en filas y columnas.
    # Como O=0 y X=1, la suma de cada fila/columna debe ser n/2.
    cantidad_necesaria = n // 2

    # Restricción de suma en cada fila
    for i in range(n):
        fila_vars = []
        for j in range(n):
            fila_vars.append((i, j))
        problem.addConstraint(ExactSumConstraint(cantidad_necesaria), fila_vars)

    # Restricción de suma en cada columna
    for j in range(n):
        col_vars = []
        for i in range(n):
            col_vars.append((i, j))
        problem.addConstraint(ExactSumConstraint(cantidad_necesaria), col_vars)

    # 3) Restricción: No más de dos discos consecutivos del mismo color.
    # Se aplica a cualquier secuencia de 3 casillas en fila o columna.
    # No puede ocurrir que a == b == c.
    def no_tres_iguales(a, b, c):
        return not (a == b == c)

    # Aplicamos la restricción a todos los tríos consecutivos de cada fila
    for i in range(n):
        for j in range(n - 2):
            problem.addConstraint(no_tres_iguales, [(i, j), (i, j+1), (i, j+2)])
            
    # Aplicamos la restricción a todos los tríos consecutivos de cada columna
    for j in range(n):
        for i in range(n - 2):
            problem.addConstraint(no_tres_iguales, [(i, j), (i+1, j), (i+2, j)])

    # Devolvemos todas las soluciones encontradas
    return problem.getSolutions()

def guardar_salida(ruta_salida, tablero_inicial, solucion, n):
    """
    Escribe la salida en el fichero indicado.

    Formato:
    - Primero el tablero inicial.
    - Luego la solución encontrada (si existe).
    """

    # Convertimos el tablero inicial a texto
    contenido_inicial = imprimir_tablero_str(tablero_inicial)
    
    contenido_solucion = ""

    # Convertir solución numérica (0/1) a caracteres (O/X)
    if solucion:
        tablero_resuelto = []
        for i in range(n):
            fila = []
            for j in range(n):
                if solucion[(i, j)] == 0:
                    fila.append('O')
                else:
                    fila.append('X')
            tablero_resuelto.append(fila)

        # Convertimos a texto la solución
        contenido_solucion = imprimir_tablero_str(tablero_resuelto)
    
    # Escribimos instancia y solución en el fichero de salida
    with open(ruta_salida, 'w', encoding="utf-8") as f:
        f.write(contenido_inicial + "\n")
        if contenido_solucion:
            f.write(contenido_solucion + "\n")

def main():
    """
    Función principal del programa.
    Gestiona la lectura de argumentos, la resolución del problema y la escritura de la salida.
    """

    # 1) Validar argumentos
    # Nota: Para ejecutar el scirpt con ./parte-1.py en Linux, se debe dar permisos de ejecución con chmod +x parte-1.py
    if len(sys.argv) != 3:
        print("Uso: ./parte-1.py <fichero-entrada.in> <fichero-salida.out>")
        sys.exit(1)
        
    # 2) Lectura de argumentos de línea de comandos  
    entrada = sys.argv[1]
    salida = sys.argv[2]
    
    # 3) Leer entrada
    tablero_inicial, n = leer_fichero(entrada)
    
    # 4) Mostrar instancia inicial en pantalla
    str_inicial = imprimir_tablero_str(tablero_inicial)
    print(str_inicial)
    
    # 5) Resolver el problema
    soluciones = resolver_binairo(tablero_inicial, n)
    num_soluciones = len(soluciones)
    
    print(f"{num_soluciones} soluciones encontradas")
    
    # 6) Escribir fichero de salida
    # Se toma la primera solución de la lista si existe.
    if num_soluciones > 0:
        primera_solucion = soluciones[0]
    else:
        primera_solucion = None
    guardar_salida(salida, tablero_inicial, primera_solucion, n)

if __name__ == "__main__":
    main()
