"""Cálculo didáctico de polinomios de Maclaurin con expresiones seguras."""

import ast
import math

try:
    import sympy as sp
except ImportError:
    sp = None

from backend.funciones import compilar_funcion

MAX_TERMINOS_MACLAURIN = 30


def _real_finito(valor, nombre):
    if isinstance(valor, bool):
        raise ValueError(f"{nombre} debe ser un número real finito.")
    try:
        resultado = float(valor)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{nombre} debe ser un número real finito.") from error
    if not math.isfinite(resultado):
        raise ValueError(f"{nombre} debe ser un número real finito.")
    return resultado


def _a_simpy(nodo, x):
    """Convierte exclusivamente el AST aprobado por backend.funciones."""
    if isinstance(nodo, ast.Expression):
        return _a_simpy(nodo.body, x)
    if isinstance(nodo, ast.Constant):
        return sp.Integer(nodo.value) if isinstance(nodo.value, int) else sp.Rational(str(nodo.value))
    if isinstance(nodo, ast.Name):
        return x if nodo.id == "x" else {"pi": sp.pi, "e": sp.E}[nodo.id]
    if isinstance(nodo, ast.UnaryOp):
        valor = _a_simpy(nodo.operand, x)
        return valor if isinstance(nodo.op, ast.UAdd) else -valor
    if isinstance(nodo, ast.BinOp):
        izquierda, derecha = _a_simpy(nodo.left, x), _a_simpy(nodo.right, x)
        if isinstance(nodo.op, ast.Add):
            return izquierda + derecha
        if isinstance(nodo.op, ast.Sub):
            return izquierda - derecha
        if isinstance(nodo.op, ast.Mult):
            return izquierda * derecha
        if isinstance(nodo.op, ast.Div):
            return izquierda / derecha
        if isinstance(nodo.op, ast.Pow):
            return izquierda ** derecha
    if isinstance(nodo, ast.Call):
        argumentos = [_a_simpy(arg, x) for arg in nodo.args]
        funciones = {
            "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
            "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
            "sqrt": sp.sqrt, "log": sp.log, "log10": lambda valor: sp.log(valor, 10),
            "exp": sp.exp, "abs": sp.Abs,
        }
        if nodo.func.id == "log" and len(argumentos) == 2:
            return sp.log(argumentos[0]) / sp.log(argumentos[1])
        return funciones[nodo.func.id](*argumentos)
    raise ValueError("La expresión contiene una operación no permitida.")


def _valor_simbolico(valor, nombre):
    valor = sp.simplify(valor)
    if valor.has(sp.zoo, sp.nan, sp.oo, -sp.oo) or valor.is_finite is False:
        raise ValueError(f"{nombre} no tiene un valor finito en x = 0.")
    numerico = sp.N(valor, 17)
    if numerico.is_real is not True or numerico.is_finite is not True:
        raise ValueError(f"{nombre} no puede evaluarse como un número real finito en x = 0.")
    return valor


def _aviso_convergencia(funcion, variable, x):
    """Advierte fuera del radio solo cuando SymPy identifica singularidades finitas."""
    try:
        singularidades = sp.singularities(funcion, variable)
        if not isinstance(singularidades, sp.FiniteSet):
            return ""
        distancias = []
        for punto in singularidades:
            distancia = sp.N(sp.Abs(punto), 17)
            if distancia.is_real is True and distancia.is_finite is True:
                radio_candidato = float(distancia)
                if radio_candidato > 0:
                    distancias.append(radio_candidato)
        if not distancias:
            return ""
        radio = min(distancias)
        if abs(x) > radio + 1e-12 * max(1, radio):
            return (f"El análisis simbólico detecta radio de convergencia R = {radio:.8g}; "
                    f"|x| = {abs(x):.8g} > R, por lo que la serie no converge en este punto. "
                    "El polinomio truncado aún se evalúa como aproximación polinómica.")
        if math.isclose(abs(x), radio, rel_tol=1e-12, abs_tol=1e-12):
            return (f"|x| = {radio:.8g} está en la frontera del radio detectado; "
                    "la convergencia en la frontera no se determina automáticamente.")
    except (NotImplementedError, TypeError, ValueError, OverflowError):
        return ""
    return ""


def calcular_maclaurin(expresion, x_evaluacion, numero_terminos):
    """Calcula P_N y devuelve coeficientes, traza simbólica, aproximación y errores."""
    if sp is None:
        raise ValueError("Series de Maclaurin necesita SymPy para calcular derivadas simbólicas.")
    if isinstance(numero_terminos, bool) or not isinstance(numero_terminos, int) \
            or not 1 <= numero_terminos <= MAX_TERMINOS_MACLAURIN:
        raise ValueError(f"La cantidad de términos debe ser un entero entre 1 y {MAX_TERMINOS_MACLAURIN}.")
    x_evaluacion = _real_finito(x_evaluacion, "El valor de x")
    funcion = compilar_funcion(expresion)
    variable = sp.Symbol("x", real=True)
    try:
        simbolica = sp.simplify(_a_simpy(funcion._arbol, variable))
        # La función original debe estar definida en cero; no se sustituye por una extensión continua.
        funcion(0)
    except (ValueError, OverflowError, ZeroDivisionError) as error:
        raise ValueError(f"La función no está definida en el punto de desarrollo x = 0: {error}") from error

    terminos = []
    polinomio = sp.Integer(0)
    derivada = simbolica
    valor_derivada_anterior = None
    for orden in range(numero_terminos):
        if orden:
            try:
                derivada = sp.simplify(sp.diff(derivada, variable))
                limites = (
                    sp.limit((terminos[-1]["derivada"] - valor_derivada_anterior) / variable,
                             variable, 0, dir="-"),
                    sp.limit((terminos[-1]["derivada"] - valor_derivada_anterior) / variable,
                             variable, 0, dir="+"),
                )
            except Exception as error:
                raise ValueError(f"No se pudo calcular la derivada de orden {orden}.") from error
            if sp.simplify(limites[0] - limites[1]) != 0:
                raise ValueError(f"La derivada de orden {orden} no existe en x = 0.")
        en_cero = _valor_simbolico(derivada.subs(variable, 0), f"La derivada de orden {orden}")
        valor_derivada_anterior = en_cero
        factorial = math.factorial(orden)
        coeficiente = sp.simplify(en_cero / factorial)
        termino = sp.simplify(coeficiente * variable ** orden)
        polinomio += termino
        terminos.append({
            "orden": orden,
            "derivada": derivada,
            "derivada_en_cero": en_cero,
            "factorial": factorial,
            "coeficiente": coeficiente,
            "termino": termino,
        })
    polinomio = sp.simplify(polinomio)
    try:
        aproximacion_sp = sp.N(polinomio.subs(variable, sp.Float(x_evaluacion, 17)), 17)
        if aproximacion_sp.is_real is not True or aproximacion_sp.is_finite is not True:
            raise ValueError("La aproximación del polinomio no es un número real finito.")
        aproximacion = float(aproximacion_sp)
        if not math.isfinite(aproximacion):
            raise ValueError("La aproximación del polinomio excede el rango numérico finito.")
    except (TypeError, OverflowError, ZeroDivisionError) as error:
        raise ValueError("No se pudo evaluar el polinomio en el valor de x indicado.") from error

    valor_real = error_absoluto = error_relativo_porcentual = None
    aviso_evaluacion = aviso_error = ""
    try:
        valor_real = funcion(x_evaluacion)
        error_absoluto = abs(valor_real - aproximacion)
        if not math.isfinite(error_absoluto):
            error_absoluto = None
            aviso_error = "El error absoluto excede el rango numérico finito."
        elif valor_real != 0:
            error_relativo_porcentual = error_absoluto / abs(valor_real) * 100
            if not math.isfinite(error_relativo_porcentual):
                error_relativo_porcentual = None
                aviso_error = "El error relativo porcentual excede el rango numérico finito."
    except ValueError as error:
        aviso_evaluacion = f"La función original no se pudo evaluar en x = {x_evaluacion:g}: {error}"

    aviso_convergencia = _aviso_convergencia(simbolica, variable, x_evaluacion)
    return {
        "expresion": funcion.expresion,
        "funcion_simbolica": simbolica,
        "x": x_evaluacion,
        "numero_terminos": numero_terminos,
        "polinomio": polinomio,
        "aproximacion": aproximacion,
        "valor_real": valor_real,
        "error_absoluto": error_absoluto,
        "error_relativo_porcentual": error_relativo_porcentual,
        "terminos": terminos,
        "aviso_evaluacion": aviso_evaluacion,
        "aviso_error": aviso_error,
        "aviso_convergencia": aviso_convergencia,
        "nota_convergencia": (
            "Se muestra el polinomio truncado. Que la serie infinita converja a f(x) depende de la función "
            "y de su radio de convergencia; no se presupone convergencia para todo x."
        ),
    }
