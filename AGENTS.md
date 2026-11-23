# Instrucciones del proyecto CalculadoraAlgebra

## Propósito

CalculadoraAlgebra es una calculadora educativa de álgebra lineal. Su prioridad es ayudar a que la persona entienda qué se hace en cada paso, por qué el paso es matemáticamente válido, cómo se realizan los cálculos y cómo interpretar y comprobar el resultado. Las explicaciones deben permitir reconstruir el razonamiento; evita añadir texto genérico que no corresponda a los cálculos mostrados.

## Alcance y cuidado del repositorio

- Trabaja únicamente dentro del alcance que el usuario autorice en la solicitud actual. Estas instrucciones describen cómo trabajar; por sí solas no autorizan ni inician cambios de código o nuevas funcionalidades.
- Antes de cualquier trabajo en el proyecto, inspecciona el estado real de Git con `git status`, `git status -sb`, `git diff --stat` y `git diff --check`. Después inspecciona los diffs pertinentes antes de editar.
- Protege siempre el trabajo ajeno o previo, incluido el trabajo de Cramer. Nunca descartes, restaures, sobrescribas ni limpies cambios existentes, estén rastreados o no. Si no puedes determinar qué contienen o si exceden el alcance, detente antes de tocar esos archivos y comunica el hallazgo.
- No hagas `git add`, `git commit` ni `git push` sin autorización expresa. No uses `git add .` indiscriminadamente.
- Verifica en el código actual los nombres, firmas y comportamientos antes de depender de notas anteriores o modificar una ruta. El historial y este documento son contexto, no evidencia del estado actual del árbol de trabajo.
- No amplíes el alcance por encontrar defectos en otras partes; documenta el hallazgo y espera autorización para corregirlo.

## Reglas matemáticas y técnicas

- **Nunca uses NumPy ni SciPy**, ni los agregues como dependencias. Implementa con Python estándar y los algoritmos propios ya existentes en el proyecto.
- Conserva la exactitud de `fractions.Fraction` en cálculos racionales. No conviertas valores exactos a `float` durante el cálculo; limita el redondeo a la presentación cuando ya exista ese comportamiento y sea apropiado.
- No cambies algoritmos matemáticos que ya funcionan sin una razón comprobada y pruebas que cubran el cambio.
- Mantén separadas las responsabilidades: `backend/` contiene algoritmos y lógica matemática; `modulos/` contiene presentación e interacción; `tests/` contiene pruebas. `main.py` es el punto de entrada. Reutiliza las utilidades existentes cuando corresponda y evita duplicar cálculos entre backend y presentación.
- Muestra las sustituciones numéricas y los cálculos intermedios que ayuden a seguir el procedimiento. Explica el fundamento de cada operación relevante y qué representa el resultado parcial.
- Interpreta el resultado en el contexto del problema. Verifica la solución en el problema original cuando sea matemáticamente pertinente, explicando qué confirma la comprobación.
- Conserva el tratamiento correcto de casos límite y degenerados. Por ejemplo, un determinante principal nulo impide aplicar Cramer para obtener una solución única, pero por sí solo no distingue entre sistema incompatible y sistema con infinitas soluciones.

## Forma de trabajo y verificación

1. Explica en español el objetivo de cada fase antes de cambios importantes; mantén las actualizaciones claras y breves.
2. Inspecciona el código, las pruebas y los cambios existentes dentro del alcance solicitado antes de editar.
3. Cuando se autorice un cambio, añade pruebas dirigidas a su comportamiento y a la coherencia entre los cálculos y la explicación.
4. Después de cambios relevantes, ejecuta las pruebas dirigidas y la suite completa: `python -m unittest discover -s tests -v`.
5. Ejecuta también `python -m compileall -q backend modulos` y `git diff --check` al verificar cambios.
6. Informa qué cambió, qué comandos de verificación se ejecutaron y sus resultados. No afirmes que una comprobación pasó si no se ejecutó en el estado actual.

## Contexto de progreso — no asumir el estado actual

Las notas recibidas indican que en etapas anteriores se trabajó en explicaciones pedagógicas para factorización LU, eliminación de Gauss y Gauss-Jordan, y que se preparó trabajo de Cramer junto con pruebas. Son antecedentes, no garantía de que esos cambios estén actualmente en Git ni de que el árbol esté limpio. Inspecciona primero el estado real y protege todo trabajo pendiente, en especial Cramer.

El contexto recibido identifica como posible siguiente fase una mejora pedagógica del método de matriz inversa para resolver `Ax = b`: explicar la invertibilidad, la matriz aumentada `[A | I]`, las operaciones de Gauss-Jordan, la lectura de `[I | A⁻¹]`, el cálculo exacto de `A⁻¹b`, la verificación de `Ax = b` y el caso singular. **Es una tarea futura, no una orden para comenzarla automáticamente.** Empiézala solo cuando el usuario la solicite o la autorice explícitamente en el contexto vigente. Verifica los nombres y comportamientos actuales antes de usar los nombres de funciones o archivos mencionados en notas anteriores.

La meta a largo plazo es mejorar progresivamente las explicaciones de todas las funcionalidades (incluidas operaciones de matrices y vectores, combinación e independencia lineal, determinantes, inversas y propiedades de matrices), siempre dentro del alcance autorizado en cada tarea.
