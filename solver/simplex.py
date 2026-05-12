# solver/simplex.py
# -------------------------------------------------------
# Algoritmo Simplex — soporta:
#   - Maximizar y Minimizar
#   - Restricciones <=, >= e =
# -------------------------------------------------------
#
# ESTRATEGIA según tipo de restricción:
#
#  <=  →  agregar variable de HOLGURA  (+s)
#  >=  →  restar variable de EXCESO (-e) + agregar ARTIFICIAL (+a)
#  =   →  solo agregar ARTIFICIAL (+a)
#
# Las variables artificiales se penalizan con Big-M en la función
# objetivo → método Big-M.
#
# MINIMIZAR: se convierte a maximizar negando los coeficientes.
#   Min Z = cx  ↔  Max Z' = -cx   (al final Z = -Z')


def simplex(c, A, b, signs, objective_type="max"):
    """
    Resuelve un problema de Programación Lineal.

    Parámetros:
        c              : coeficientes de la función objetivo
        A              : matriz de coeficientes de restricciones
        b              : lados derechos (se ajustan si son negativos)
        signs          : lista de signos: '<=', '>=' o '='
        objective_type : 'max' o 'min'
    """

    steps = []
    c = [float(x) for x in c]
    A = [[float(x) for x in row] for row in A]
    b = [float(x) for x in b]
    signs = list(signs)

    n_vars        = len(c)
    n_constraints = len(b)
    is_min        = (objective_type == "min")

    # ── Paso 0: asegurar b >= 0 ───────────────────────────────────────────
    for i in range(n_constraints):
        if b[i] < 0:
            A[i] = [-x for x in A[i]]
            b[i] = -b[i]
            if signs[i] == "<=":
                signs[i] = ">="
            elif signs[i] == ">=":
                signs[i] = "<="

    # ── Paso 1: minimizar → maximizar ────────────────────────────────────
    c_work = [-ci for ci in c] if is_min else c[:]

    steps.append(f"Tipo: {'Minimizar' if is_min else 'Maximizar'} "
                 f"Z = {_format_objective(c)}")
    if is_min:
        steps.append("Conversión: Minimizar Z  →  Maximizar Z' = -Z")

    # ── Paso 2: contar variables auxiliares ──────────────────────────────
    BIG_M = 1e6

    n_slack = signs.count("<=")
    n_excess = signs.count(">=")
    n_artificial = signs.count(">=") + signs.count("=")

    total_aux  = n_slack + n_excess + n_artificial
    total_cols = n_vars + total_aux + 1

    steps.append(f"Variables auxiliares → holgura: {n_slack}, "
                 f"exceso: {n_excess}, artificiales: {n_artificial}")

    # ── Paso 3: construir tabla ───────────────────────────────────────────
    tableau          = []
    basis            = []
    artificial_cols  = []
    aux_col          = n_vars   # cursor

    for i in range(n_constraints):
        row  = A[i][:]
        row += [0.0] * total_aux

        if signs[i] == "<=":
            row[aux_col] = 1.0
            basis.append(aux_col)
            aux_col += 1

        elif signs[i] == ">=":
            row[aux_col]     = -1.0   # exceso
            row[aux_col + 1] =  1.0   # artificial
            basis.append(aux_col + 1)
            artificial_cols.append(aux_col + 1)
            aux_col += 2

        elif signs[i] == "=":
            row[aux_col] = 1.0        # artificial
            basis.append(aux_col)
            artificial_cols.append(aux_col)
            aux_col += 1

        row.append(b[i])
        tableau.append(row)

    # Fila Z
    z_row = [-ci for ci in c_work] + [0.0] * total_aux + [0.0]
    for ac in artificial_cols:
        z_row[ac] = -BIG_M
    tableau.append(z_row)

    # Ajuste inicial por artificiales en la base
    for i, bv in enumerate(basis):
        if bv in artificial_cols:
            f = tableau[-1][bv]
            tableau[-1] = [
                tableau[-1][j] - f * tableau[i][j]
                for j in range(total_cols)
            ]

    steps.append("Tabla inicial construida. Iniciando iteraciones Simplex...")

    # ── Paso 4: iteraciones ───────────────────────────────────────────────
    MAX_ITER = 200
    iteration = 0

    for iteration in range(1, MAX_ITER + 1):

        z = tableau[-1]

        # Columna pivote: más negativo
        pivot_col = None
        min_val   = -1e-9
        for j in range(total_cols - 1):
            if z[j] < min_val:
                min_val   = z[j]
                pivot_col = j

        if pivot_col is None:
            steps.append(f"Iteración {iteration}: Sin coeficientes negativos "
                         "→ solución óptima.")
            break

        var_name = _var_name(pivot_col, n_vars, n_slack, n_excess)
        steps.append(f"Iter {iteration}: Entra {var_name} "
                     f"(coef. Z = {min_val:.4f})")

        # Fila pivote: razón mínima
        pivot_row = None
        min_ratio = float("inf")
        for i in range(n_constraints):
            if tableau[i][pivot_col] > 1e-9:
                ratio = tableau[i][-1] / tableau[i][pivot_col]
                if ratio < min_ratio:
                    min_ratio = ratio
                    pivot_row = i

        if pivot_row is None:
            steps.append("Problema no acotado (unbounded).")
            return {"status": "unbounded", "objective": None,
                    "variables": [], "steps": steps, "iterations": iteration}

        leaving = _var_name(basis[pivot_row], n_vars, n_slack, n_excess)
        steps.append(f"  Sale {leaving} (razón = {min_ratio:.4f})")

        basis[pivot_row] = pivot_col

        # Pivoteo
        pe = tableau[pivot_row][pivot_col]
        tableau[pivot_row] = [x / pe for x in tableau[pivot_row]]

        for i in range(len(tableau)):
            if i != pivot_row:
                f = tableau[i][pivot_col]
                tableau[i] = [
                    tableau[i][j] - f * tableau[pivot_row][j]
                    for j in range(total_cols)
                ]

    else:
        steps.append(f"Límite de {MAX_ITER} iteraciones alcanzado.")

    # ── Paso 5: verificar artificiales ───────────────────────────────────
    for bv in basis:
        if bv in artificial_cols:
            val = 0.0
            for i, b2 in enumerate(basis):
                if b2 == bv:
                    val = tableau[i][-1]
            if abs(val) > 1e-6:
                steps.append("Infeasible: artificial quedó en la base con "
                             "valor > 0.")
                return {"status": "infeasible", "objective": None,
                        "variables": [], "steps": steps,
                        "iterations": iteration}

    # ── Paso 6: solución ──────────────────────────────────────────────────
    solution = [0.0] * n_vars
    for i, var_idx in enumerate(basis):
        if var_idx < n_vars:
            solution[var_idx] = round(tableau[i][-1], 6)

    z_val     = round(tableau[-1][-1], 6)
    objective = round(-z_val if is_min else z_val, 6)

    steps.append(f"Solución óptima: Z = {objective}")
    for i, val in enumerate(solution):
        steps.append(f"  x{i+1} = {val}")

    return {
        "status":     "optimal",
        "objective":  objective,
        "variables":  solution,
        "steps":      steps,
        "iterations": iteration,
    }


# ── Auxiliares ────────────────────────────────────────────────────────────

def _var_name(idx, n_vars, n_slack, n_excess):
    if idx < n_vars:
        return f"x{idx + 1}"
    i2 = idx - n_vars
    if i2 < n_slack:
        return f"s{i2 + 1}"
    i2 -= n_slack
    if i2 < n_excess:
        return f"e{i2 + 1}"
    return f"a{i2 - n_excess + 1}"


def _format_objective(c):
    parts = [f"{ci}·x{i+1}" for i, ci in enumerate(c) if ci != 0]
    return " + ".join(parts) if parts else "0"