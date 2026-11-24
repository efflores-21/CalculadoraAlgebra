"""Derivación simbólica segura y método iterativo de Newton-Raphson."""

import ast
import math

try:
    import sympy as sp
except ImportError:
    # Sin SymPy la calculadora debe abrir igual: solo Newton-Raphson queda sin derivadas.
    sp = None

from backend.funciones import compilar_funcion

MAX_ITERACIONES = 10000
_LIMITE_PASO = 1e100


def _finito(valor, nombre):
    """Convierte una entrada en float y exige que sea real y finita."""
    if isinstance(valor, bool):
        raise ValueError(f"{nombre} debe ser un número real finito.")
    try:
        valor = float(valor)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{nombre} debe ser un número real finito.") from error
    if not math.isfinite(valor):
        raise ValueError(f"{nombre} debe ser un número real finito.")
    return valor


def _a_simpy(nodo, x):
    """Traduce solo nodos ya aceptados por la lista blanca del evaluador."""
    if isinstance(nodo, ast.Expression):
        return _a_simpy(nodo.body, x)
    if isinstance(nodo, ast.Constant):
        return sp.Integer(nodo.value) if isinstance(nodo.value, int) else sp.Float(nodo.value)
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
        funciones_simbolicas = {
            "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
            "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
            "sqrt": sp.sqrt, "log": sp.log, "log10": lambda a: sp.log(a, 10),
            "exp": sp.exp, "abs": sp.Abs,
        }
        if nodo.func.id == "log" and len(argumentos) == 2:
            return sp.log(argumentos[0]) / sp.log(argumentos[1])
        return funciones_simbolicas[nodo.func.id](*argumentos)
    raise ValueError("La expresión contiene una operación no permitida.")


def preparar_funcion(expresion):
    """Valida f(x), deriva simbólicamente y devuelve expresiones y evaluadores."""
    if sp is None:
        raise ValueError("Newton-Raphson necesita la librería SymPy para derivar f(x) y no está instalada. "
                         "Instálala con:  py -m pip install sympy  y vuelve a abrir la calculadora.")
    funcion = compilar_funcion(expresion)
    x = sp.Symbol("x", real=True)
    try:
        simbologica = _a_simpy(funcion._arbol, x)
        derivada = sp.simplify(sp.diff(simbologica, x))
    except Exception as error:
        raise ValueError("No se pudo obtener la derivada simbólica de la función.") from error

    def evaluar_derivada(valor):
        valor = _finito(valor, "x")
        try:
            resultado = derivada.subs(x, sp.Float(valor, 17)).evalf(17)
            if resultado.is_real is not True:
                raise ValueError("La derivada produjo un resultado complejo en el dominio real.")
            numero = float(resultado)
        except (TypeError, ValueError, OverflowError, ZeroDivisionError) as error:
            if isinstance(error, ValueError) and str(error).startswith("La derivada"):
                raise
            raise ValueError("La derivada no está definida en ese valor de x.") from error
        if not math.isfinite(numero):
            raise ValueError("La derivada produjo un valor no finito.")
        return numero

    return {
        "expresion": funcion.expresion,
        "expresion_simbolica": str(simbologica),
        "derivada": str(derivada),
        "funcion": funcion,
        "evaluar_derivada": evaluar_derivada,
    }


def resolver_newton_raphson(expresion, x0, tolerancia, max_iteraciones):
    """Aproxima una raíz con Newton-Raphson y registra cada paso ejecutado.

    La tolerancia se compara con el error aproximado porcentual solicitado.
    Una raíz exacta de punto flotante también se reconoce mediante residuo cero.
    """
    x0 = _finito(x0, "El valor inicial x0")
    tolerancia = _finito(tolerancia, "La tolerancia")
    if tolerancia <= 0:
        raise ValueError("La tolerancia debe ser positiva.")
    if isinstance(max_iteraciones, bool) or not isinstance(max_iteraciones, int) \
            or not 1 <= max_iteraciones <= MAX_ITERACIONES:
        raise ValueError(f"El máximo de iteraciones debe ser un entero entre 1 y {MAX_ITERACIONES}.")

    preparada = preparar_funcion(expresion)
    funcion, derivada = preparada["funcion"], preparada["evaluar_derivada"]
    tabla = []
    actual = x0
    resultado = {
        "expresion": preparada["expresion"],
        "funcion_simbolica": preparada["expresion_simbolica"],
        "derivada": preparada["derivada"], "valor_inicial": x0,
        "aproximacion": x0, "iteraciones": 0, "error_final": None,
        "residuo_final": None, "residuo_relativo_final": None,
        "residuo_relativo_porcentual_final": None,
        "convergio": False, "estado": "error",
        "motivo": "", "tabla": tabla,
    }

    try:
        valor_funcion = funcion(actual)
        resultado["residuo_final"] = abs(valor_funcion)
        if valor_funcion == 0:
            resultado.update(convergio=True, estado="convergido", residuo_relativo_final=0.0,
                             residuo_relativo_porcentual_final=0.0,
                             motivo="El valor inicial ya es una raíz exacta.")
            return resultado
        residuo_inicial = abs(valor_funcion)
        resultado.update(residuo_relativo_final=1.0, residuo_relativo_porcentual_final=100.0)

        for k in range(1, max_iteraciones + 1):
            try:
                valor_derivada = derivada(actual)
            except ValueError as error:
                tabla.append({
                    "k": k, "xi": actual, "fxi": valor_funcion, "derivada": None,
                    "xi_siguiente": None, "error_aproximado_porcentual": None,
                    "residuo": abs(valor_funcion), "motivo": str(error),
                })
                resultado.update(iteraciones=len(tabla), motivo=str(error))
                break
            fila = {"k": k, "xi": actual, "fxi": valor_funcion,
                    "derivada": valor_derivada, "xi_siguiente": None,
                    "error_aproximado_porcentual": None, "residuo": None,
                    "residuo_relativo": None, "residuo_relativo_porcentual": None}
            if valor_derivada == 0:
                fila["motivo"] = "La derivada es cero; no se puede calcular el siguiente paso."
                tabla.append(fila)
                resultado.update(iteraciones=len(tabla), motivo=fila["motivo"])
                break

            paso = valor_funcion / valor_derivada
            if not math.isfinite(paso) or abs(paso) > _LIMITE_PASO:
                fila["motivo"] = (
                    "La derivada es demasiado cercana a cero: el paso de Newton excede el rango numérico seguro."
                )
                tabla.append(fila)
                resultado.update(iteraciones=len(tabla), motivo=fila["motivo"])
                break
            siguiente = actual - paso
            if not math.isfinite(siguiente) or abs(siguiente) > _LIMITE_PASO:
                fila["motivo"] = "El siguiente valor excede el rango numérico seguro."
                tabla.append(fila)
                resultado.update(iteraciones=len(tabla), motivo=fila["motivo"])
                break
            error = None if siguiente == 0 else abs((siguiente - actual) / siguiente) * 100
            fila.update(xi_siguiente=siguiente, error_aproximado_porcentual=error)
            tabla.append(fila)
            actual = siguiente
            resultado.update(aproximacion=actual, iteraciones=k, error_final=error, residuo_final=None)
            if error is not None and not math.isfinite(error):
                fila["motivo"] = "El error porcentual excede el rango numérico finito."
                resultado["motivo"] = fila["motivo"]
                break
            valor_funcion = funcion(siguiente)
            residuo = abs(valor_funcion)
            residuo_relativo = residuo / residuo_inicial
            residuo_relativo_porcentual = residuo_relativo * 100
            fila["residuo"] = residuo
            resultado.update(residuo_final=residuo, residuo_relativo_final=residuo_relativo)
            if not math.isfinite(residuo_relativo) or not math.isfinite(residuo_relativo_porcentual):
                fila["motivo"] = "El residuo relativo excede el rango numérico finito."
                resultado["motivo"] = fila["motivo"]
                break
            fila["residuo_relativo"] = residuo_relativo
            fila["residuo_relativo_porcentual"] = residuo_relativo_porcentual
            resultado["residuo_relativo_porcentual_final"] = residuo_relativo_porcentual

            if residuo == 0:
                resultado.update(convergio=True, estado="convergido",
                                 motivo="Se obtuvo una raíz exacta en aritmética de punto flotante.")
                break
            if error is not None and error <= tolerancia:
                if residuo_relativo_porcentual <= tolerancia:
                    resultado.update(convergio=True, estado="convergido",
                                     motivo=("El error aproximado porcentual y el residuo relativo porcentual al inicial "
                                             "alcanzaron la tolerancia."))
                    break
        else:
            if tabla and tabla[-1].get("error_aproximado_porcentual") is not None \
                    and tabla[-1]["error_aproximado_porcentual"] <= tolerancia \
                    and tabla[-1].get("residuo_relativo_porcentual") is not None \
                    and tabla[-1]["residuo_relativo_porcentual"] > tolerancia:
                motivo = ("Se alcanzó el máximo: el error porcentual cumplió la tolerancia, "
                          "pero el residuo relativo porcentual al inicial sigue siendo mayor.")
            else:
                motivo = "Se alcanzó el máximo de iteraciones sin alcanzar ambos criterios de tolerancia."
            resultado.update(estado="maximo", motivo=motivo)
        if not resultado["motivo"]:
            resultado["motivo"] = "No se pudo continuar por una condición matemática inválida."
    except (ValueError, OverflowError, ZeroDivisionError) as error:
        resultado["motivo"] = str(error)
        resultado["estado"] = "error"
    return resultado


# Alias breve para mantener una API fácil de descubrir desde otros módulos.
resolver = resolver_newton_raphson
