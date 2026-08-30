import sys
from fractions import Fraction

SUPERSCRIPTS = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵',
    '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', '-': '⁻'
}
SUBSCRIPTS = {
    '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅',
    '6': '₆', '7': '₇', '8': '₈', '9': '₉', '-': '₋'
}


def _soporta_unicode():
    try:
        encoding = sys.stdout.encoding or 'utf-8'
        '⁷⁄₅'.encode(encoding)
        return True
    except Exception:
        return False


def formatear_valor(valor):
    """Devuelve una fracción compacta con estilo visual, con fallback seguro."""
    if isinstance(valor, Fraction):
        fraccion = valor
    elif isinstance(valor, float):
        if valor.is_integer():
            return str(int(valor))
        fraccion = Fraction(str(valor)).limit_denominator()
    else:
        return str(valor)

    if fraccion.denominator == 1:
        return str(fraccion.numerator)

    num = str(fraccion.numerator)
    den = str(fraccion.denominator)
    if abs(fraccion.numerator) <= 9 and abs(fraccion.denominator) <= 9 and _soporta_unicode():
        num_txt = ''.join(SUPERSCRIPTS.get(ch, ch) for ch in num)
        den_txt = ''.join(SUBSCRIPTS.get(ch, ch) for ch in den)
        return f"{num_txt}⁄{den_txt}"

    return f"{fraccion.numerator}/{fraccion.denominator}"


class MatrizAumentada:
    """
    Representa la matriz aumentada [A | b].
    Proporciona métodos para copiar, formatear, y realizar operaciones elementales.
    """

    def __init__(self, datos):
        """
        :param datos: lista de listas (m x (n+1)) con coeficientes y términos independientes.
        """
        self.datos = self._copiar(self._normalizar_matriz(datos))
        self.filas = len(self.datos)
        self.columnas = len(self.datos[0]) if self.filas > 0 else 0
        self.n_variables = self.columnas - 1
        self.tolerancia = 1e-12

    @staticmethod
    def _normalizar_valor(valor):
        if isinstance(valor, Fraction):
            return valor
        if isinstance(valor, int):
            return Fraction(valor, 1)
        if isinstance(valor, float):
            return Fraction(str(valor))
        if isinstance(valor, str):
            texto = valor.strip().replace(',', '.')
            return Fraction(texto)
        return Fraction(str(valor))

    @classmethod
    def _normalizar_matriz(cls, datos):
        return [[cls._normalizar_valor(valor) for valor in fila] for fila in datos]

    @staticmethod
    def _copiar(mat):
        """Copia profunda de una matriz."""
        return [fila[:] for fila in mat]

    def copiar(self):
        """Retorna una copia de la matriz actual."""
        return MatrizAumentada(self.datos)

    def redondear(self):
        """Elimina errores de redondeo manteniendo valores exactos cuando corresponden."""
        for i in range(self.filas):
            for j in range(self.columnas):
                if self.datos[i][j] == 0:
                    self.datos[i][j] = Fraction(0)

    # ----- Operaciones elementales -----
    def intercambiar_filas(self, i, j):
        """Intercambia la fila i con la fila j."""
        self.datos[i], self.datos[j] = self.datos[j], self.datos[i]

    def escalar_fila(self, i, escalar):
        """Multiplica la fila i por un escalar (distinto de 0)."""
        if abs(escalar) < self.tolerancia:
            raise ValueError("El escalar no puede ser cero.")
        self.datos[i] = [elem * escalar for elem in self.datos[i]]

    def sumar_multiplo_fila(self, i, j, escalar):
        """Fila i = Fila i + escalar * Fila j."""
        if i == j:
            raise ValueError("No se puede sumar una fila a sí misma.")
        self.datos[i] = [self.datos[i][k] + escalar * self.datos[j][k]
                         for k in range(self.columnas)]

    # ----- Formateo para mostrar -----
    def mostrar(self, decimales=4):
        """Devuelve una matriz alineada, fácil de leer, con fracciones compactas."""
        if self.filas == 0:
            return ""

        filas = [[formatear_valor(elem) for elem in fila] for fila in self.datos]
        anchos = [max(len(fila[i]) for fila in filas) for i in range(self.columnas)]

        lineas = []
        for fila in filas:
            celdas = [valor.center(anchos[i]) for i, valor in enumerate(fila)]
            lineas.append("[ " + " | ".join(celdas) + " ]")
        return "\n".join(lineas)


# Compatibilidad con la versión antigua del proyecto

def intercambiar_filas(matriz, i, j):
    matriz[i], matriz[j] = matriz[j], matriz[i]


def multiplicar_fila(matriz, i, escalar):
    matriz[i] = [elem * escalar for elem in matriz[i]]


def sumar_filas(matriz, i, j, escalar):
    matriz[i] = [matriz[i][k] + escalar * matriz[j][k] for k in range(len(matriz[i]))]


def es_cero(valor):
    if isinstance(valor, Fraction):
        return valor == 0
    try:
        return abs(float(valor)) < 1e-12
    except (TypeError, ValueError):
        return valor == 0


def mostrar_matriz(matriz, titulo=None):
    if titulo:
        print(titulo)
    for fila in matriz:
        print("[ " + "  ".join(formatear_valor(elem) for elem in fila) + " ]")
