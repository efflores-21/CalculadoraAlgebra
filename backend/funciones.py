"""Evaluación segura de expresiones de una variable mediante una lista blanca AST."""

import ast
import math
import operator


_BINARIOS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}
_UNARIOS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCIONES = {
    nombre: getattr(math, nombre)
    for nombre in ("sin", "cos", "tan", "asin", "acos", "atan", "sqrt", "log", "log10", "exp")
}
_FUNCIONES["abs"] = abs
_CONSTANTES = {"pi": math.pi, "e": math.e}
_MAX_NODOS = 100
_MAX_POTENCIA = 1000


def _validar(nodo):
    """Rechaza nodos AST fuera del subconjunto aritmético admitido."""
    if isinstance(nodo, ast.Expression):
        _validar(nodo.body)
    elif isinstance(nodo, ast.Constant):
        if isinstance(nodo.value, bool) or not isinstance(nodo.value, (int, float)):
            raise ValueError("Solo se permiten constantes numéricas.")
        if not math.isfinite(nodo.value):
            raise ValueError("La expresión contiene una constante no finita.")
    elif isinstance(nodo, ast.Name):
        if nodo.id not in {"x", *_CONSTANTES}:
            raise ValueError(f"Nombre no permitido: {nodo.id}.")
    elif isinstance(nodo, ast.BinOp) and type(nodo.op) in _BINARIOS:
        _validar(nodo.left)
        _validar(nodo.right)
        if isinstance(nodo.op, ast.Pow) and isinstance(nodo.right, ast.Constant):
            if abs(nodo.right.value) > _MAX_POTENCIA:
                raise ValueError("El exponente constante excede el límite permitido (1000).")
    elif isinstance(nodo, ast.UnaryOp) and type(nodo.op) in _UNARIOS:
        _validar(nodo.operand)
    elif isinstance(nodo, ast.Call):
        if not isinstance(nodo.func, ast.Name) or nodo.func.id not in _FUNCIONES:
            raise ValueError("La función llamada no está permitida.")
        if nodo.keywords or len(nodo.args) not in (1, 2):
            raise ValueError("Use una función autorizada con uno o dos argumentos posicionales.")
        if nodo.func.id not in {"log"} and len(nodo.args) != 1:
            raise ValueError(f"La función {nodo.func.id} acepta un solo argumento.")
        for argumento in nodo.args:
            _validar(argumento)
    else:
        raise ValueError("La expresión contiene una operación o construcción no permitida.")


def _evaluar(nodo, x):
    """Evalúa recursivamente los nodos previamente validados."""
    if isinstance(nodo, ast.Expression):
        valor = _evaluar(nodo.body, x)
    elif isinstance(nodo, ast.Constant):
        valor = nodo.value
    elif isinstance(nodo, ast.Name):
        valor = x if nodo.id == "x" else _CONSTANTES[nodo.id]
    elif isinstance(nodo, ast.UnaryOp):
        valor = _UNARIOS[type(nodo.op)](_evaluar(nodo.operand, x))
    elif isinstance(nodo, ast.BinOp):
        izquierda, derecha = _evaluar(nodo.left, x), _evaluar(nodo.right, x)
        if isinstance(nodo.op, ast.Pow) and abs(derecha) > _MAX_POTENCIA:
            raise ValueError("El exponente excede el límite permitido (1000).")
        valor = _BINARIOS[type(nodo.op)](izquierda, derecha)
    elif isinstance(nodo, ast.Call):
        argumentos = [_evaluar(arg, x) for arg in nodo.args]
        valor = _FUNCIONES[nodo.func.id](*argumentos)
    else:  # Defensa adicional: _validar debe excluir cualquier otro nodo.
        raise ValueError("Operación no permitida.")

    if isinstance(valor, complex) or not math.isfinite(valor):
        raise ValueError("La evaluación produjo un valor complejo o no finito.")
    return valor


class FuncionMatematica:
    """Expresión matemática validada que puede evaluarse para distintos valores de x."""

    def __init__(self, expresion):
        """Analiza y valida una expresión sin ejecutarla como código Python."""
        if not isinstance(expresion, str) or not expresion.strip():
            raise ValueError("Ingrese una expresión matemática.")
        if len(expresion) > 500:
            raise ValueError("La expresión es demasiado larga (máximo 500 caracteres).")
        try:
            arbol = ast.parse(expresion, mode="eval")
        except (SyntaxError, ValueError) as error:
            raise ValueError("La expresión tiene una sintaxis inválida.") from error
        if sum(1 for _ in ast.walk(arbol)) > _MAX_NODOS:
            raise ValueError("La expresión supera el límite de complejidad permitido.")
        _validar(arbol)
        self.expresion = expresion.strip()
        self._arbol = arbol

    def __call__(self, x):
        """Evalúa f(x), comunicando de forma clara errores de dominio y aritmética."""
        try:
            x = float(x)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError("x debe ser un número real finito.") from error
        if not math.isfinite(x):
            raise ValueError("x debe ser un número real finito.")
        try:
            return float(_evaluar(self._arbol, x))
        except ZeroDivisionError as error:
            raise ValueError("La función no está definida por división entre cero.") from error
        except (ValueError, OverflowError) as error:
            texto = str(error)
            if "límite permitido" in texto or "no finito" in texto:
                raise
            raise ValueError("La función no está definida en ese valor (dominio u overflow).") from error


def compilar_funcion(expresion):
    """Valida una expresión y devuelve un callable f(x)."""
    return FuncionMatematica(expresion)
