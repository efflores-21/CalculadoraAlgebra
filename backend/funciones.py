"""Evaluación segura de expresiones matemáticas mediante una lista blanca AST."""

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
MAX_VARIABLES_FUNCION = 5


def _variables_en_orden(arbol):
    """Recorre la expresión en orden sintáctico, sin contar nombres de funciones."""
    encontradas = []

    class Recolector(ast.NodeVisitor):
        def visit_Name(self, nodo):
            if nodo.id not in _CONSTANTES and nodo.id not in _FUNCIONES and nodo.id not in encontradas:
                encontradas.append(nodo.id)

        def visit_Call(self, nodo):
            for argumento in nodo.args:
                self.visit(argumento)

    Recolector().visit(arbol)
    return tuple(encontradas)


def _validar(nodo, variables=frozenset({"x"})):
    """Rechaza nodos AST fuera del subconjunto aritmético admitido."""
    if isinstance(nodo, ast.Expression):
        _validar(nodo.body, variables)
    elif isinstance(nodo, ast.Constant):
        if isinstance(nodo.value, bool) or not isinstance(nodo.value, (int, float)):
            raise ValueError("Solo se permiten constantes numéricas.")
        if not math.isfinite(nodo.value):
            raise ValueError("La expresión contiene una constante no finita.")
    elif isinstance(nodo, ast.Name):
        if nodo.id not in {*variables, *_CONSTANTES}:
            raise ValueError(f"Nombre no permitido: {nodo.id}.")
    elif isinstance(nodo, ast.BinOp) and type(nodo.op) in _BINARIOS:
        _validar(nodo.left, variables)
        _validar(nodo.right, variables)
        if isinstance(nodo.op, ast.Pow) and isinstance(nodo.right, ast.Constant):
            if abs(nodo.right.value) > _MAX_POTENCIA:
                raise ValueError("El exponente constante excede el límite permitido (1000).")
    elif isinstance(nodo, ast.UnaryOp) and type(nodo.op) in _UNARIOS:
        _validar(nodo.operand, variables)
    elif isinstance(nodo, ast.Call):
        if not isinstance(nodo.func, ast.Name) or nodo.func.id not in _FUNCIONES:
            raise ValueError("La función llamada no está permitida.")
        if nodo.keywords or len(nodo.args) not in (1, 2):
            raise ValueError("Use una función autorizada con uno o dos argumentos posicionales.")
        if nodo.func.id not in {"log"} and len(nodo.args) != 1:
            raise ValueError(f"La función {nodo.func.id} acepta un solo argumento.")
        for argumento in nodo.args:
            _validar(argumento, variables)
    else:
        raise ValueError("La expresión contiene una operación o construcción no permitida.")


def _evaluar(nodo, valores):
    """Evalúa recursivamente los nodos previamente validados."""
    if isinstance(nodo, ast.Expression):
        valor = _evaluar(nodo.body, valores)
    elif isinstance(nodo, ast.Constant):
        valor = nodo.value
    elif isinstance(nodo, ast.Name):
        valor = _CONSTANTES[nodo.id] if nodo.id in _CONSTANTES else valores[nodo.id]
    elif isinstance(nodo, ast.UnaryOp):
        valor = _UNARIOS[type(nodo.op)](_evaluar(nodo.operand, valores))
    elif isinstance(nodo, ast.BinOp):
        izquierda, derecha = _evaluar(nodo.left, valores), _evaluar(nodo.right, valores)
        if isinstance(nodo.op, ast.Pow) and abs(derecha) > _MAX_POTENCIA:
            raise ValueError("El exponente excede el límite permitido (1000).")
        valor = _BINARIOS[type(nodo.op)](izquierda, derecha)
    elif isinstance(nodo, ast.Call):
        argumentos = [_evaluar(arg, valores) for arg in nodo.args]
        valor = _FUNCIONES[nodo.func.id](*argumentos)
    else:  # Defensa adicional: _validar debe excluir cualquier otro nodo.
        raise ValueError("Operación no permitida.")

    if isinstance(valor, complex) or not math.isfinite(valor):
        raise ValueError("La evaluación produjo un valor complejo o no finito.")
    return valor


class FuncionMatematica:
    """Expresión matemática validada con modo univariable compatible o multivariable."""

    def __init__(self, expresion, permitir_multivariable=False):
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
        if permitir_multivariable:
            variables = _variables_en_orden(arbol)
            if len(variables) > MAX_VARIABLES_FUNCION:
                raise ValueError(f"La función admite como máximo {MAX_VARIABLES_FUNCION} variables.")
            if any(nombre.startswith("_") or len(nombre) > 20 for nombre in variables):
                raise ValueError("Los nombres de variable deben tener entre 1 y 20 caracteres y no iniciar con '_'.")
        else:
            variables = ("x",)
        _validar(arbol, frozenset(variables))
        self.expresion = expresion.strip()
        self._arbol = arbol
        self.variables = variables

    def __call__(self, x):
        """Evalúa f(x), comunicando de forma clara errores de dominio y aritmética."""
        try:
            x = float(x)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError("x debe ser un número real finito.") from error
        if not math.isfinite(x):
            raise ValueError("x debe ser un número real finito.")
        if len(self.variables) != 1:
            raise ValueError("La función requiere valores para todas sus variables; use evaluar(valores).")
        try:
            return float(_evaluar(self._arbol, {self.variables[0]: x}))
        except ZeroDivisionError as error:
            raise ValueError("La función no está definida por división entre cero.") from error
        except (ValueError, OverflowError) as error:
            texto = str(error)
            if "límite permitido" in texto or "no finito" in texto:
                raise
            raise ValueError("La función no está definida en ese valor (dominio u overflow).") from error

    def evaluar(self, valores):
        """Evalúa una función multivariable con una asignación completa y finita."""
        if not isinstance(valores, dict):
            raise ValueError("Los valores de las variables deben proporcionarse como un diccionario.")
        faltantes = set(self.variables) - set(valores)
        sobrantes = set(valores) - set(self.variables)
        if faltantes:
            raise ValueError("Falta un valor para: " + ", ".join(sorted(faltantes)) + ".")
        if sobrantes:
            raise ValueError("Variable no válida para la función: " + ", ".join(sorted(sobrantes)) + ".")
        convertidos = {}
        for nombre in self.variables:
            valor = valores[nombre]
            if isinstance(valor, bool):
                raise ValueError(f"El valor de {nombre} debe ser un número real finito.")
            try:
                valor = float(valor)
            except (TypeError, ValueError, OverflowError) as error:
                raise ValueError(f"El valor de {nombre} debe ser un número real finito.") from error
            if not math.isfinite(valor):
                raise ValueError(f"El valor de {nombre} debe ser un número real finito.")
            convertidos[nombre] = valor
        try:
            return float(_evaluar(self._arbol, convertidos))
        except ZeroDivisionError as error:
            raise ValueError("La función no está definida por división entre cero.") from error
        except (ValueError, OverflowError) as error:
            texto = str(error)
            if "límite permitido" in texto or "no finito" in texto:
                raise
            raise ValueError("La función no está definida en esos valores (dominio u overflow).") from error


def compilar_funcion(expresion):
    """Valida una expresión y devuelve un callable f(x)."""
    return FuncionMatematica(expresion)


def compilar_funcion_multivariable(expresion):
    """Valida una expresión y detecta hasta cinco variables reales independientes."""
    return FuncionMatematica(expresion, permitir_multivariable=True)


def identificar_variables(expresion):
    """Devuelve en orden de aparición las variables usadas por una expresión válida."""
    return compilar_funcion_multivariable(expresion).variables
