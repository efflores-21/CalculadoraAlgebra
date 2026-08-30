from fractions import Fraction


class Clasificador:
    """
    Clasifica un sistema a partir de su matriz aumentada escalonada.
    También resuelve si es determinado.
    """

    def __init__(self, matriz_escalonada, tolerancia=1e-12):
        """
        :param matriz_escalonada: instancia de MatrizAumentada ya escalonada.
        """
        self.matriz = matriz_escalonada
        self.tolerancia = tolerancia

    def clasificar(self):
        """
        Retorna:
            - tipo: 'determinado', 'indeterminado', 'inconsistente'
            - solucion: lista de valores (solo si determinado), None en otro caso
            - variables_libres: lista de índices (solo si indeterminado), None en otro caso
        """
        for i in range(self.matriz.filas):
            es_cero_coef = all(self.matriz.datos[i][j] == 0 for j in range(self.matriz.n_variables))
            if es_cero_coef and self.matriz.datos[i][self.matriz.n_variables] != 0:
                return 'inconsistente', None, None

        rango_A = 0
        rango_A_aum = 0
        for i in range(self.matriz.filas):
            if any(self.matriz.datos[i][j] != 0 for j in range(self.matriz.n_variables)):
                rango_A += 1
            if any(self.matriz.datos[i][j] != 0 for j in range(self.matriz.columnas)):
                rango_A_aum += 1

        if rango_A < rango_A_aum:
            return 'inconsistente', None, None

        if rango_A == self.matriz.n_variables:
            sol = self._sustitucion_atras()
            return 'determinado', sol, None

        pivotes = []
        fila = 0
        for col in range(self.matriz.n_variables):
            for i in range(fila, self.matriz.filas):
                if self.matriz.datos[i][col] != 0:
                    pivotes.append(col)
                    fila = i + 1
                    break
        libres = [col for col in range(self.matriz.n_variables) if col not in pivotes]
        return 'indeterminado', None, libres

    def _sustitucion_atras(self):
        """
        Resuelve el sistema triangular superior (supone que es determinado).
        Retorna lista de valores para las variables (ordenadas).
        """
        n = self.matriz.n_variables
        sol = [Fraction(0) for _ in range(n)]
        for i in range(self.matriz.filas - 1, -1, -1):
            pivote_col = -1
            for j in range(n):
                if self.matriz.datos[i][j] != 0:
                    pivote_col = j
                    break
            if pivote_col == -1:
                continue
            suma = self.matriz.datos[i][n]
            for j in range(pivote_col + 1, n):
                suma -= self.matriz.datos[i][j] * sol[j]
            sol[pivote_col] = suma / self.matriz.datos[i][pivote_col]
        return sol

    @staticmethod
    def verificar_solucion(matriz_original, sol, tolerancia=1e-9):
        """
        Verifica la solución sustituyendo en la matriz original.
        Retorna una lista de errores (residuos) por ecuación.
        """
        if sol is None:
            return None
        errores = []
        for i in range(matriz_original.filas):
            suma = Fraction(0)
            for j in range(matriz_original.n_variables):
                suma += matriz_original.datos[i][j] * sol[j]
            error = abs(suma - matriz_original.datos[i][matriz_original.n_variables])
            errores.append(error)
        return errores
