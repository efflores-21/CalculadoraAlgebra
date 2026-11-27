"""Propagación de incertidumbres para expresiones seguras de una o más variables."""

import ast
import math

try:
    import sympy as sp
except ImportError:
    sp = None

from backend.funciones import compilar_funcion_multivariable


def _a_simpy(nodo, simbolos):
    """Traduce el AST después de que el parser seguro haya validado la expresión."""
    if isinstance(nodo, ast.Expression):
        return _a_simpy(nodo.body, simbolos)
    if isinstance(nodo, ast.Constant):
        return sp.Integer(nodo.value) if isinstance(nodo.value, int) else sp.Rational(str(nodo.value))
    if isinstance(nodo, ast.Name):
        if nodo.id in simbolos:
            return simbolos[nodo.id]
        return {"pi": sp.pi, "e": sp.E}[nodo.id]
    if isinstance(nodo, ast.UnaryOp):
        valor = _a_simpy(nodo.operand, simbolos)
        return valor if isinstance(nodo.op, ast.UAdd) else -valor
    if isinstance(nodo, ast.BinOp):
        izquierda, derecha = _a_simpy(nodo.left, simbolos), _a_simpy(nodo.right, simbolos)
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
        argumentos = [_a_simpy(argumento, simbolos) for argumento in nodo.args]
        funciones = {
            "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
            "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
            "sqrt": sp.sqrt, "log": sp.log, "log10": lambda valor: sp.log(valor, 10),
            "exp": sp.exp, "abs": sp.Abs,
        }
        if nodo.func.id == "log" and len(argumentos) == 2:
            return sp.log(argumentos[0], argumentos[1])
        return funciones[nodo.func.id](*argumentos)
    raise ValueError("La expresión contiene una operación no permitida.")


def _finito(valor, nombre):
    if isinstance(valor, bool):
        raise ValueError(f"{nombre} debe ser un número real finito.")
    try:
        convertido = float(valor)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{nombre} debe ser un número real finito.") from error
    if not math.isfinite(convertido):
        raise ValueError(f"{nombre} debe ser un número real finito.")
    return convertido


def _leer_asignaciones(funcion, valores, incertidumbres):
    variables = set(funcion.variables)
    if not isinstance(valores, dict):
        raise ValueError("Los valores de las variables deben proporcionarse como un diccionario.")
    if set(valores) != variables:
        faltan = variables - set(valores)
        sobran = set(valores) - variables
        if faltan:
            raise ValueError("Falta un valor para: " + ", ".join(sorted(faltan)) + ".")
        if sobran:
            raise ValueError("Variable no válida: " + ", ".join(sorted(sobran)) + ".")
        raise ValueError("Los valores de las variables deben proporcionarse como un diccionario.")
    if not isinstance(incertidumbres, dict):
        raise ValueError("Las incertidumbres deben proporcionarse como un diccionario.")
    if set(incertidumbres) != variables:
        faltan = variables - set(incertidumbres)
        sobran = set(incertidumbres) - variables
        if faltan:
            raise ValueError("Falta una incertidumbre para: " + ", ".join(sorted(faltan)) + ".")
        if sobran:
            raise ValueError("Variable no válida en las incertidumbres: " + ", ".join(sorted(sobran)) + ".")
        raise ValueError("Las incertidumbres deben proporcionarse como un diccionario.")
    puntos, deltas = {}, {}
    for variable in funcion.variables:
        puntos[variable] = _finito(valores[variable], f"El valor de {variable}")
        deltas[variable] = _finito(incertidumbres[variable], f"La incertidumbre de {variable}")
        if deltas[variable] < 0:
            raise ValueError(f"La incertidumbre de {variable} debe ser mayor o igual que cero.")
    return puntos, deltas


def propagar_errores(expresion, valores, incertidumbres, metodo="maximo"):
    """Evalúa derivadas parciales y ambas estimaciones de propagación de primer orden."""
    if sp is None:
        raise ValueError("La propagación general necesita SymPy para calcular derivadas parciales.")
    if not isinstance(metodo, str) or metodo not in {"maximo", "estadistico"}:
        raise ValueError("Seleccione el método 'maximo' o 'estadistico'.")
    funcion = compilar_funcion_multivariable(expresion)
    puntos, deltas = _leer_asignaciones(funcion, valores, incertidumbres)
    valor_funcion = funcion.evaluar(puntos)
    simbolos = {nombre: sp.Symbol(nombre, real=True) for nombre in funcion.variables}
    try:
        simbolica = sp.simplify(_a_simpy(funcion._arbol, simbolos))
    except Exception as error:
        raise ValueError("No se pudo construir la expresión simbólica para las derivadas parciales.") from error

    sustituciones = {simbolos[nombre]: sp.Float(puntos[nombre], 17) for nombre in funcion.variables}
    contribuciones = []
    for nombre in funcion.variables:
        try:
            derivada = sp.simplify(sp.diff(simbolica, simbolos[nombre]))
            variable = simbolos[nombre]
            otros_valores = {
                simbolos[otra]: sustituciones[simbolos[otra]]
                for otra in funcion.variables if otra != nombre
            }
            expresion_univariable = simbolica.subs(otros_valores, simultaneous=True)
            punto = sp.Float(puntos[nombre], 17)
            valor_puntual = sp.N(simbolica.subs(sustituciones, simultaneous=True), 17)
            cociente = (expresion_univariable - valor_puntual) / (variable - punto)
            limites = (
                sp.limit(cociente, variable, punto, dir="-"),
                sp.limit(cociente, variable, punto, dir="+"),
            )
            if (any(limite.is_real is not True or limite.is_finite is not True for limite in limites)
                    or sp.simplify(limites[0] - limites[1]) != 0):
                raise ValueError(f"La derivada parcial respecto de {nombre} no existe en el punto indicado.")
            evaluada = sp.N(derivada.subs(sustituciones), 17)
            if evaluada.is_real is not True or evaluada.is_finite is not True:
                raise ValueError(f"La derivada parcial respecto de {nombre} no es real y finita en el punto indicado.")
            valor_derivada = float(evaluada)
            contribucion = abs(valor_derivada) * deltas[nombre]
            if not math.isfinite(contribucion):
                raise ValueError(f"La contribución de {nombre} excede el rango numérico finito.")
        except (TypeError, OverflowError, ZeroDivisionError) as error:
            raise ValueError(f"No se pudo evaluar la derivada parcial respecto de {nombre}.") from error
        contribuciones.append({
            "variable": nombre,
            "valor": puntos[nombre],
            "incertidumbre": deltas[nombre],
            "derivada": derivada,
            "derivada_evaluada": valor_derivada,
            "contribucion_maxima": contribucion,
            "contribucion_estadistica": contribucion,
        })
    try:
        error_maximo = math.fsum(fila["contribucion_maxima"] for fila in contribuciones)
        incertidumbre_estadistica = math.hypot(*(fila["contribucion_estadistica"] for fila in contribuciones))
    except OverflowError as error:
        raise ValueError("La propagación excede el rango numérico finito.") from error
    if not math.isfinite(error_maximo) or not math.isfinite(incertidumbre_estadistica):
        raise ValueError("La propagación excede el rango numérico finito.")
    estimacion = error_maximo if metodo == "maximo" else incertidumbre_estadistica
    inferior, superior = valor_funcion - estimacion, valor_funcion + estimacion
    if not math.isfinite(inferior) or not math.isfinite(superior):
        raise ValueError("El intervalo aproximado excede el rango numérico finito.")
    relativo = estimacion / abs(valor_funcion) * 100 if valor_funcion != 0 else None
    if relativo is not None and not math.isfinite(relativo):
        raise ValueError("El error relativo porcentual excede el rango numérico finito.")
    return {
        "expresion": funcion.expresion,
        "funcion_simbolica": simbolica,
        "variables": list(funcion.variables),
        "valores": puntos,
        "incertidumbres": deltas,
        "valor_funcion": valor_funcion,
        "contribuciones": contribuciones,
        "error_maximo": error_maximo,
        "incertidumbre_estadistica": incertidumbre_estadistica,
        "metodo": metodo,
        "nombre_metodo": "Error máximo" if metodo == "maximo" else "Incertidumbre estadística",
        "incertidumbre_resultado": estimacion,
        "intervalo": (inferior, superior),
        "error_relativo_porcentual": relativo,
        "interpretacion": (
            "Cota conservadora de primer orden; se suman los valores absolutos de las contribuciones."
            if metodo == "maximo" else
            "Combinación cuadrática de primer orden, suponiendo incertidumbres independientes; no es un intervalo de confianza."
        ),
    }
