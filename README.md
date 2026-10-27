# Calculadora de Álgebra Lineal

Aplicación de escritorio para explorar y resolver problemas habituales de
álgebra lineal. Cuenta con una interfaz gráfica desarrollada con
**CustomTkinter** y presenta los cálculos en forma ordenada, con explicaciones
paso a paso cuando corresponde.

## Inicio rápido

Solo requiere Python 3 instalado (desde python.org, que ya incluye Tkinter).
Después de clonar el repositorio, ejecuta:

```text
python main.py
```

La primera vez, si la computadora no tiene CustomTkinter, `main.py` lo
instala automáticamente con pip (necesita internet solo esa vez). También
puede instalarse a mano con `pip install -r requirements.txt`.

El menú principal permite seleccionar un módulo. Este se muestra en la misma
ventana y ofrece un botón para regresar al menú.

## Funcionalidades

Los módulos están numerados en el mismo orden en el menú principal. La marca
gris de cada tarjeta (P1, P2…) indica a qué parte del curso corresponde; el
mapa de la sección siguiente dice dónde está cada parte en el código.

| Módulo | Qué hace | Marca |
|---|---|---|
| 1. Sistemas de ecuaciones | Gauss y Gauss-Jordan paso a paso, clasificación, columnas pivote, variables básicas/libres y verificación por sustitución. También regla de Cramer y x = A⁻¹b. | P1 · P2 |
| 2. Vectores y combinación lineal | Suma, resta y escalar de vectores; decide si b es combinación lineal. | P3 |
| 3. Independencia lineal | Reduce Ac = 0, cuenta pivotes y da el veredicto L.I. / L.D. | P4 |
| 4. Operaciones con matrices | Opciones 1–4: suma, resta, escalar, producto. Opciones 5–8: transpuesta, determinante, inversa por Gauss-Jordan y por adjunta. Opción 9: verificador de propiedades. Copiar y pegar matrices (compatible con Excel). | P3 · P5 · P6 |
| 5. Determinantes | Determinante por eliminación triangular y por cofactores paso a paso; contraejemplo det(A + B) ≠ det(A) + det(B). | P5 |
| 6. Factorización LU y solución Ax = b | A = LU con solo reemplazos de fila, verificación L·U = A, etapas Ly = b y Ux = y. Opción de pivoteo parcial (PA = LU) y sistemas rectangulares. | P6 |
| 7. Propiedades de matrices | A(u + v) = Au + Av y A(cu) = c(Au); no conmutatividad, cancelación y producto nulo; transposición, inversa, determinantes y criterios de invertibilidad. | P3 · P5 |

Cada módulo tiene su logotipo ASCII, una guía «Cómo usar» y la opción
«0. Ver Teoremas Clave del Módulo».

## Mapa del código

Cada archivo indica su marca en el encabezado (por ejemplo `[P4]`).

**P1 · Eliminación por filas y clasificación del sistema**
- En la app: Módulo 1, método «Gauss».
- `backend/eliminacion.py` → `eliminacion_con_pasos`, `sustitucion_hacia_atras`, `solucion_general`, `resolver_sistema`
- `backend/clasificador.py` → `clasificar_sistema`
- `modulos/modulo_sistemas.py` → `resolver`, `_verificar_solucion`

**P2 · Gauss-Jordan, columnas pivote y variables básicas/libres**
- En la app: Módulo 1, método «Gauss-Jordan».
- `backend/eliminacion.py` → `eliminacion_con_pasos` (con `metodo="gauss-jordan"`)
- `backend/clasificador.py` → `columnas_pivote`
- `modulos/_comun.py` → `formatear_expresion` (solución general con parámetros t)

**P3 · Vectores, combinación lineal y operaciones con matrices**
- En la app: Módulo 2, Módulo 4 (opciones 1–4) y Módulo 7.
- `backend/vectores.py` → `suma_vectores`, `resta_vectores`, `multiplicar_escalar_vector`, `es_combinacion_lineal`
- `backend/operaciones_matriciales.py` → `suma_matrices`, `resta_matrices`, `multiplicar_escalar_matriz`, `multiplicar_matrices`, `multiplicar_matriz_vector`
- `backend/propiedades.py` → `verificar_propiedades` (A(u + v) y A(cu))
- `modulos/modulo_operaciones_vectores.py`, `modulos/modulo_propiedades.py`

**P4 · Independencia lineal y estructura modular**
- En la app: Módulo 3.
- `modulos/modulo_vectores.py` → `construir_matriz_columnas`, `construir_sistema_homogeneo`, `contar_pivotes`, `determinar_veredicto`, `analizar`
- Estructura: `main.py`, carpeta `modulos/`, `modulos/teoremas/resumen_teoremas.py` y `crear_estructura` en `modulos/_comun.py` (logotipo y opción 0)

**P5 · Determinantes e inversa**
- En la app: Módulo 4 (opciones 5–8 y 0), Módulo 5, Módulo 7 y los métodos «Cramer» y «Matriz inversa» del Módulo 1.
- `backend/matrices.py` → `determinante_cofactores_con_pasos`, `resolver_cramer`
- `modulos/modulo_determinantes.py` → `comparar_determinante_suma`
- `modulos/modulo_propiedades.py` → `calcular_teorema_producto`, `calcular_teorema_transposicion`, `calcular_teorema_inversa_determinante`, `analizar_criterios_invertibilidad`
- `backend/matrices.py` → `determinante_triangular`, `sarrus_3x3`, `invertir_gauss_jordan`, `invertir_adjunta`, `verificar_inversa`
- `backend/operaciones_matriciales.py` → `transponer_matriz`, `determinante_por_cofactores`, `matriz_menores`, `matriz_cofactores`, `matriz_adjunta`, `inversa_por_adjunta`
- `modulos/modulo_matrices.py` → `diagnostico_invertibilidad`, `_determinante`, `_inversa`

**P6 · Factorización LU y verificador completo de propiedades**
- En la app: Módulo 6 y Módulo 4 (opción 9).
- `backend/factorizacion_lu.py` → `factorizar_lu`, `resolver_por_reduccion`, `resolver_lu` (A = LU, lo que pide el programa) y `factorizar_lu_pivoteo`, `resolver_sistema_lu` (PA = LU y sistemas rectangulares)
- `backend/verificador.py` → `propiedades_transposicion`, `propiedades_inversa`, `propiedades_determinante`, `propiedades_operaciones_fila`, `propiedad_triangular`, `verificar_propiedades_matrices`
- `backend/operaciones_matriciales.py` → `son_iguales`, `identidad`
- `modulos/modulo_lu.py` → pantalla del Módulo 6
- `modulos/modulo_matrices.py` → `_verificador`

## Organización del proyecto

```text
CalculadoraAlgebra/
├── main.py         # Menú principal
├── backend/        # Algoritmos de cálculo (sin interfaz)
├── modulos/        # Una pantalla por módulo
│   └── teoremas/   # Teoremas clave de cada módulo
├── presentaciones/ # Diapositivas de clase (sesiones 9 a 12)
└── frontend/       # Interfaz anterior (ya no se usa)
```

## Implementación

- Los cálculos matriciales se realizan con listas, ciclos y funciones propias.
- `fractions.Fraction` permite trabajar con valores racionales exactos.
- CustomTkinter se utiliza para construir la interfaz gráfica.
- La aplicación no utiliza NumPy ni SciPy.
