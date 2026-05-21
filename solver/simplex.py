# solver/simplex.py  —  Metodo de DOS FASES (Two-Phase Simplex)
#
# Mas robusto que Big-M para restricciones >= y =
#
# FASE 1: Minimizar sum(artificiales) para encontrar solucion factible.
#         Si el minimo es 0 -> factible. Si > 0 -> infeasible.
# FASE 2: Con la base factible de Fase 1, optimizar la funcion objetivo real.

def simplex(c, A, b, signs, objective_type="max"):

    steps = []
    c     = [float(x) for x in c]
    A     = [[float(x) for x in row] for row in A]
    b     = [float(x) for x in b]
    signs = list(signs)

    n_vars        = len(c)
    n_constraints = len(b)
    is_min        = (objective_type == "min")

    # Asegurar b >= 0
    for i in range(n_constraints):
        if b[i] < 0:
            A[i]     = [-x for x in A[i]]
            b[i]     = -b[i]
            signs[i] = ">=" if signs[i] == "<=" else "<="

    steps.append(f"Tipo: {'Minimizar' if is_min else 'Maximizar'} Z = {_fmt_obj(c)}")

    # Contar variables auxiliares
    n_slack      = sum(1 for s in signs if s == "<=")
    n_excess     = sum(1 for s in signs if s == ">=")
    n_artificial = sum(1 for s in signs if s in (">=", "="))
    total_aux    = n_slack + n_excess + n_artificial
    total_cols   = n_vars + total_aux + 1

    steps.append(f"Variables auxiliares: holgura={n_slack}, exceso={n_excess}, artificiales={n_artificial}")

    # Construir tabla (misma estructura para las dos fases)
    tableau         = []
    basis           = []
    artificial_cols = []
    col = n_vars

    for i in range(n_constraints):
        row  = [float(x) for x in A[i]]
        row += [0.0] * total_aux

        if signs[i] == "<=":
            row[col] = 1.0
            basis.append(col)
            col += 1

        elif signs[i] == ">=":
            row[col]     = -1.0   # exceso
            row[col + 1] =  1.0   # artificial
            basis.append(col + 1)
            artificial_cols.append(col + 1)
            col += 2

        elif signs[i] == "=":
            row[col] = 1.0        # artificial
            basis.append(col)
            artificial_cols.append(col)
            col += 1

        row.append(b[i])
        tableau.append(row)

    has_artificials = len(artificial_cols) > 0
    total_iters = 0

    # ══════════════════════════════════════════════════════════════
    # FASE 1: minimizar suma de artificiales (solo si hay artificiales)
    # ══════════════════════════════════════════════════════════════
    if has_artificials:
        steps.append("FASE 1: encontrar solucion factible inicial.")

        # Funcion objetivo de fase 1: minimizar sum(artificiales)
        # En forma maximizar: maximizar -sum(artificiales)
        # z1[j] = -1 si j es artificial, 0 en otro caso
        z1 = [0.0] * total_cols
        for ac in artificial_cols:
            z1[ac] = -1.0   # queremos maximizar (-artificial) = minimizar artificial

        # Ajuste inicial: las artificiales estan en la base con coef -1 en Z1
        # Hacemos eliminacion para que queden en 0
        for i, bv in enumerate(basis):
            if bv in artificial_cols:
                f = z1[bv]
                if abs(f) > 1e-12:
                    z1 = [z1[j] - f * tableau[i][j] for j in range(total_cols)]

        tableau.append(z1)

        basis, tableau, iters, status = _iterate(tableau, basis, n_constraints, total_cols)
        total_iters += iters

        phase1_val = -round(tableau[-1][-1], 6)   # valor suma artificiales

        if phase1_val > 1e-6:
            steps.append(f"FASE 1: suma artificiales = {phase1_val:.6f} > 0 -> INFEASIBLE.")
            return {"status":"infeasible","objective":None,
                    "variables":[],"steps":steps,"iterations":total_iters}

        steps.append(f"FASE 1 completada en {iters} iteraciones: solucion factible encontrada.")

        # Sacar artificiales de la base si quedaron con valor 0
        for idx, bv in enumerate(basis):
            if bv in artificial_cols:
                # Intentar pivotear para sacarla
                pivoted = False
                for j in range(n_vars + n_slack + n_excess):
                    if j not in artificial_cols and abs(tableau[idx][j]) > 1e-9:
                        # Hacer pivote para sacar artificial
                        pe = tableau[idx][j]
                        tableau[idx] = [x / pe for x in tableau[idx]]
                        for r in range(len(tableau)):
                            if r != idx:
                                f = tableau[r][j]
                                if abs(f) > 1e-12:
                                    tableau[r] = [tableau[r][k] - f * tableau[idx][k] for k in range(total_cols)]
                        basis[idx] = j
                        pivoted = True
                        break

        # Eliminar fila Z de fase 1 y columnas artificiales de la tabla
        tableau.pop()   # quitar fila Z1

        # Construir tabla reducida sin columnas artificiales
        art_set = set(artificial_cols)
        keep    = [j for j in range(total_cols) if j not in art_set]
        tableau = [[row[j] for j in keep] for row in tableau]

        # Actualizar indices de basis
        remap = {old: new for new, old in enumerate(keep)}
        basis = [remap[bv] for bv in basis if bv in remap]

        # Actualizar dimensiones
        n_rem        = len(keep)   # total_cols sin artificiales
        total_cols_f2 = n_rem
        n_vars_f2     = n_vars

    else:
        total_cols_f2 = total_cols
        steps.append("No hay variables artificiales: saltando Fase 1.")

    # ══════════════════════════════════════════════════════════════
    # FASE 2: optimizar funcion objetivo real
    # ══════════════════════════════════════════════════════════════
    steps.append("FASE 2: optimizando funcion objetivo.")

    # Construir fila Z para fase 2
    c_work = [-ci for ci in c] if is_min else c[:]

    if has_artificials:
        tc = total_cols_f2
        # keep contiene los indices que sobrevivieron
        c_full = [-ci for ci in c_work] + [0.0] * (total_aux - n_artificial) + [0.0]
        z2 = [c_full[keep[j]] for j in range(tc - 1)] + [0.0]
    else:
        tc = total_cols_f2
        z2 = [-ci for ci in c_work] + [0.0] * total_aux + [0.0]

    tableau.append(z2)

    # Ajuste inicial Z2: eliminar variables basicas de Z2
    for i, bv in enumerate(basis):
        coef = tableau[-1][bv]
        if abs(coef) > 1e-12:
            tableau[-1] = [
                tableau[-1][j] - coef * tableau[i][j]
                for j in range(tc)
            ]

    tableau, basis, iters, _ = _iterate_ret(tableau, basis, n_constraints, tc)
    total_iters += iters
    steps.append(f"FASE 2 completada en {iters} iteraciones.")

    # Leer solucion
    solution = [0.0] * n_vars
    for i, bv in enumerate(basis):
        if bv < n_vars:
            solution[bv] = round(tableau[i][-1], 6)

    z_val     = round(tableau[-1][-1], 6)
    objective = round(-z_val if is_min else z_val, 6)

    steps.append(f"Solucion optima: Z = {objective}")
    for i, v in enumerate(solution):
        steps.append(f"  x{i+1} = {v}")

    return {
        "status":     "optimal",
        "objective":  objective,
        "variables":  solution,
        "steps":      steps,
        "iterations": total_iters,
    }


# ── Motor de iteraciones ──────────────────────────────────────────

def _iterate(tableau, basis, n_constraints, total_cols):
    MAX_ITER = 300
    for it in range(1, MAX_ITER + 1):
        z = tableau[-1]
        pivot_col = None
        min_val   = -1e-9
        for j in range(total_cols - 1):
            if z[j] < min_val:
                min_val   = z[j]
                pivot_col = j
        if pivot_col is None:
            return basis, tableau, it, "optimal"

        pivot_row = None
        min_ratio = float("inf")
        for i in range(n_constraints):
            elem = tableau[i][pivot_col]
            if elem > 1e-9:
                ratio = tableau[i][-1] / elem
                if ratio < min_ratio - 1e-12:
                    min_ratio = ratio
                    pivot_row = i
        if pivot_row is None:
            return basis, tableau, it, "unbounded"

        basis[pivot_row] = pivot_col
        pe = tableau[pivot_row][pivot_col]
        tableau[pivot_row] = [x / pe for x in tableau[pivot_row]]
        for i in range(len(tableau)):
            if i != pivot_row:
                f = tableau[i][pivot_col]
                if abs(f) > 1e-12:
                    tableau[i] = [tableau[i][j] - f * tableau[pivot_row][j] for j in range(total_cols)]

    return basis, tableau, MAX_ITER, "optimal"


def _iterate_ret(tableau, basis, n_constraints, total_cols):
    MAX_ITER = 300
    for it in range(1, MAX_ITER + 1):
        z = tableau[-1]
        pivot_col = None
        min_val   = -1e-9
        for j in range(total_cols - 1):
            if z[j] < min_val:
                min_val   = z[j]
                pivot_col = j
        if pivot_col is None:
            return tableau, basis, it, "optimal"

        pivot_row = None
        min_ratio = float("inf")
        for i in range(n_constraints):
            elem = tableau[i][pivot_col]
            if elem > 1e-9:
                ratio = tableau[i][-1] / elem
                if ratio < min_ratio - 1e-12:
                    min_ratio = ratio
                    pivot_row = i
        if pivot_row is None:
            return tableau, basis, it, "unbounded"

        basis[pivot_row] = pivot_col
        pe = tableau[pivot_row][pivot_col]
        tableau[pivot_row] = [x / pe for x in tableau[pivot_row]]
        for i in range(len(tableau)):
            if i != pivot_row:
                f = tableau[i][pivot_col]
                if abs(f) > 1e-12:
                    tableau[i] = [tableau[i][j] - f * tableau[pivot_row][j] for j in range(total_cols)]

    return tableau, basis, MAX_ITER, "optimal"


# ── Auxiliares ────────────────────────────────────────────────────

def _vname(idx, n_vars, n_slack, n_excess):
    if idx < n_vars: return f"x{idx+1}"
    i = idx - n_vars
    if i < n_slack:  return f"s{i+1}"
    i -= n_slack
    if i < n_excess: return f"e{i+1}"
    return f"a{i-n_excess+1}"

def _fmt_obj(c):
    parts = [f"{ci}*x{i+1}" for i, ci in enumerate(c) if ci != 0]
    return " + ".join(parts) or "0"
