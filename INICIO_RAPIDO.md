# INICIO RÁPIDO - Calculadora de Álgebra Lineal

## Ejecución del Programa

```bash
cd C:\Users\LENOVO\Desktop\CalculadoraAlgebra
python main.py
```

## Ejemplo Interactivo

### Paso 1: Ingrese el número de ecuaciones y variables
```
Ingrese el número de ecuaciones (m): 2
Ingrese el número de variables (n): 2
```

### Paso 2: Ingrese los coeficientes

Para el sistema:
```
x + 2y = 5
3x + y = 8
```

Ingrese:
```
Ecuación 1:
  Coeficiente x1: 1
  Coeficiente x2: 2
  Término independiente (b): 5

Ecuación 2:
  Coeficiente x1: 3
  Coeficiente x2: 1
  Término independiente (b): 8
```

### Paso 3: Vea los resultados

El programa mostrará:
- Matriz aumentada inicial
- Pasos del proceso de eliminación
- Clasificación del sistema
- Soluciones encontradas
- Verificación automática

## Casos de Prueba Recomendados

### Caso 1: Sistema Determinado (Solución Única)
```
2 ecuaciones, 2 variables
Eq1: x + 2y = 5
Eq2: 3x + y = 8
Respuesta: x = 2.2, y = 1.4
```

### Caso 2: Sistema Indeterminado (Infinitas Soluciones)
```
2 ecuaciones, 2 variables
Eq1: x + 2y = 4
Eq2: 2x + 4y = 8
Respuesta: x = 4, y es variable libre
```

### Caso 3: Sistema Inconsistente (Sin Solución)
```
2 ecuaciones, 2 variables
Eq1: x + 2y = 4
Eq2: x + 2y = 5
Respuesta: Sin solución
```

### Caso 4: Sistema 3x3 (Más Complejo)
```
3 ecuaciones, 3 variables
Eq1: x + y + z = 6
Eq2: 2x + 3y - z = 5
Eq3: x - 2y + 4z = 10
Respuesta: x ≈ 1.67, y = 1.5, z ≈ 2.83
```

## Características Principales

✓ **Entrada Interactiva**: Solicita datos del usuario de forma clara
✓ **Visualización**: Muestra la matriz en cada paso importante
✓ **Clasificación Automática**: Identifica el tipo de sistema
✓ **Verificación**: Comprueba la solución sustituyendo en el original
✓ **Menú Iterativo**: Resuelve múltiples sistemas sin cerrar el programa

## Requisitos del Sistema

- Python 3.6 o superior
- Sistema operativo: Windows, macOS o Linux
- Terminal o línea de comandos

## Archivos Incluidos

- `main.py` - Programa principal
- `backend/matriz.py` - Operaciones con matrices
- `backend/eliminacion.py` - Algoritmo Gaussiano
- `backend/clasificador.py` - Clasificación del sistema
- `frontend/interfaz.py` - Interfaz de usuario
- `README.md` - Documentación completa
- `CAMBIOS.txt` - Detalles de la implementación

## Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'backend'"
**Solución**: Asegúrate de ejecutar el programa desde la carpeta raíz del proyecto:
```bash
cd C:\Users\LENOVO\Desktop\CalculadoraAlgebra
python main.py
```

### Error: "UnicodeEncodeError"
**Solución**: Esto ocurre en Windows. El programa está configurado para manejar esto.
Si persiste, intenta con:
```bash
python -X utf8 main.py
```

## Contacto y Soporte

Para más información, consulta el README.md
