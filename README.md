# Solver de Programación Lineal

Implementación del algoritmo Simplex desde cero con interfaz web en Flask.

## Estructura del proyecto

```
solver_project/
├── app.py                  ← Servidor Flask (punto de entrada)
├── requirements.txt        ← Dependencias Python
├── solver/
│   ├── __init__.py
│   └── simplex.py          ← Algoritmo Simplex implementado desde cero
├── templates/
│   └── index.html          ← Interfaz web
├── static/
│   ├── css/style.css
│   └── js/main.js
└── tests/
    └── test_simplex.py     ← Pruebas automáticas
```

## Instalación y ejecución

```bash
# 1. Crear entorno virtual (buena práctica)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
python app.py

# 4. Abrir en el navegador
# http://localhost:5000
```

## Ejecutar pruebas

```bash
pip install pytest
python -m pytest tests/ -v
```

## Cómo funciona el algoritmo Simplex

1. **Forma estándar**: Se agregan variables de holgura (s1, s2, ...) para convertir ≤ en =
2. **Tabla inicial**: Se construye la tabla [A | I | b] con la fila Z negativa
3. **Columna pivote**: Se elige la variable con coeficiente más negativo en Z
4. **Fila pivote**: Se usa la prueba de razón mínima (b/a)
5. **Operación de pivote**: Eliminación gaussiana para actualizar la tabla
6. **Criterio de parada**: No hay coeficientes negativos en la fila Z

## Ejemplo de uso directo (sin interfaz)

```python
from solver import simplex

# Maximizar Z = 5x1 + 8x2
# Sujeto a: 2x1 + 4x2 <= 40
#           6x1 + 3x2 <= 60
resultado = simplex(
    c=[5, 8],
    A=[[2, 4], [6, 3]],
    b=[40, 60]
)

print(resultado["objective"])    # 88.0
print(resultado["variables"])    # [8.0, 6.0]
```
