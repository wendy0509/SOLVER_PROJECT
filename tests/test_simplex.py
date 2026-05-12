# tests/test_simplex.py
# -------------------------------------------------------
# Pruebas automáticas del algoritmo Simplex
# Ejecutar con: python -m pytest tests/ -v
# -------------------------------------------------------

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from solver.simplex import simplex


def test_ejemplo_basico():
    """
    Problema clásico de 2 variables:
    Maximizar:  Z = 5x1 + 8x2
    Sujeto a:   2x1 + 4x2 <= 40
                6x1 + 3x2 <= 60
                x1, x2 >= 0
    Solución esperada: x1=8, x2=6, Z=88
    """
    c = [5, 8]
    A = [[2, 4], [6, 3]]
    b = [40, 60]

    result = simplex(c, A, b)

    assert result["status"] == "optimal"
    # Solución real: x1=6.67, x2=6.67, Z=86.67
    assert abs(result["objective"] - 86.667) < 0.01
    assert abs(result["variables"][0] - 6.667) < 0.01
    assert abs(result["variables"][1] - 6.667) < 0.01
    print(f"✓ Básico: Z={result['objective']}, x={result['variables']}")


def test_una_variable():
    """
    Maximizar: Z = 3x1
    Sujeto a:  x1 <= 10
    Solución: x1=10, Z=30
    """
    result = simplex([3], [[1]], [10])
    assert result["status"] == "optimal"
    assert abs(result["objective"] - 30.0) < 0.01
    print(f"✓ Una variable: Z={result['objective']}")


def test_tres_variables():
    """
    Maximizar: Z = 2x1 + 3x2 + x3
    Sujeto a:  x1 + x2 + x3 <= 10
               2x1 + x2     <= 12
    """
    c = [2, 3, 1]
    A = [[1, 1, 1], [2, 1, 0]]
    b = [10, 12]

    result = simplex(c, A, b)
    assert result["status"] == "optimal"
    assert result["objective"] > 0
    print(f"✓ Tres variables: Z={result['objective']}, x={result['variables']}")


def test_rhs_cero():
    """RHS = 0 debería dar solución trivial x=0."""
    result = simplex([5, 3], [[1, 0], [0, 1]], [0, 0])
    assert result["status"] == "optimal"
    assert abs(result["objective"]) < 0.01
    print(f"✓ RHS cero: Z={result['objective']}")


def test_rhs_negativo():
    """RHS negativo debe retornar infeasible."""
    result = simplex([1, 1], [[1, 0]], [-5])
    assert result["status"] == "infeasible"
    print(f"✓ Infeasible detectado correctamente")


if __name__ == "__main__":
    test_ejemplo_basico()
    test_una_variable()
    test_tres_variables()
    test_rhs_cero()
    test_rhs_negativo()
    print("\n✅ Todas las pruebas pasaron.")
