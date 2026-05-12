// static/js/main.js
// -------------------------------------------------------
// Lógica del frontend: construir formulario y llamar al backend
// -------------------------------------------------------

// Número de restricciones actuales (empieza con 2)
let numConstraints = 2;

// ── buildForm ─────────────────────────────────────────────────────────────
// Construye dinámicamente los inputs de la función objetivo
// y las restricciones según el número de variables seleccionado.
function buildForm() {
  const nVars = parseInt(document.getElementById("n-vars").value);

  buildObjectiveInputs(nVars);
  buildConstraints(nVars);
  updateObjectiveFormula();
}

// ── buildObjectiveInputs ──────────────────────────────────────────────────
function buildObjectiveInputs(nVars) {
  const container = document.getElementById("objective-inputs");
  container.innerHTML = "";

  for (let i = 1; i <= nVars; i++) {
    // Etiqueta del signo + entre términos
    if (i > 1) {
      const plus = document.createElement("span");
      plus.className = "coeff-label";
      plus.textContent = "+";
      container.appendChild(plus);
    }

    // Input del coeficiente
    const input = document.createElement("input");
    input.type = "number";
    input.id = `obj-${i}`;
    input.value = i === 1 ? 5 : 8;      // valores de ejemplo
    input.step = "any";
    input.oninput = updateObjectiveFormula;
    container.appendChild(input);

    // Etiqueta "· xN"
    const label = document.createElement("span");
    label.className = "coeff-label";
    label.textContent = `· x${i}`;
    container.appendChild(label);
  }
}

// ── buildConstraints ──────────────────────────────────────────────────────
function buildConstraints(nVars) {
  const area = document.getElementById("constraints-area");
  area.innerHTML = "";
  numConstraints = 2;   // reiniciar al cambiar variables

  for (let i = 1; i <= 2; i++) {
    area.appendChild(createConstraintRow(i, nVars));
  }
}

// ── createConstraintRow ───────────────────────────────────────────────────
// Crea una fila de restricción: [c1]·x1 + [c2]·x2 + ... ≤ [rhs]
function createConstraintRow(rowIndex, nVars) {
  const nVarsNow = nVars || parseInt(document.getElementById("n-vars").value);

  const div = document.createElement("div");
  div.className = "constraint-row";
  div.id = `constraint-${rowIndex}`;

  // Número de restricción
  const num = document.createElement("span");
  num.className = "constraint-num";
  num.textContent = `R${rowIndex}`;
  div.appendChild(num);

  // Coeficientes
  const defaultCoeffs = [
    [2, 4], [6, 3],   // ejemplos para 2 variables
    [1, 2, 1], [3, 1, 2]
  ];

  for (let j = 1; j <= nVarsNow; j++) {
    if (j > 1) {
      const plus = document.createElement("span");
      plus.className = "coeff-label";
      plus.textContent = "+";
      div.appendChild(plus);
    }

    const input = document.createElement("input");
    input.type = "number";
    input.id = `c${rowIndex}-${j}`;
    // Valor por defecto de ejemplo si existe
    const def = defaultCoeffs[rowIndex - 1];
    input.value = (def && def[j - 1] !== undefined) ? def[j - 1] : 1;
    input.step = "any";
    div.appendChild(input);

    const lbl = document.createElement("span");
    lbl.className = "coeff-label";
    lbl.textContent = `· x${j}`;
    div.appendChild(lbl);
  }

  // Signo ≤
  const sign = document.createElement("span");
  sign.className = "sign";
  sign.textContent = " ≤ ";
  div.appendChild(sign);

  // RHS (lado derecho)
  const rhs = document.createElement("input");
  rhs.type = "number";
  rhs.id = `rhs-${rowIndex}`;
  rhs.value = rowIndex === 1 ? 40 : 60;
  rhs.step = "any";
  rhs.style.width = "90px";
  div.appendChild(rhs);

  // Botón eliminar (no eliminar si solo hay 1)
  const removeBtn = document.createElement("button");
  removeBtn.className = "btn-remove";
  removeBtn.textContent = "✕";
  removeBtn.title = "Eliminar restricción";
  removeBtn.onclick = () => removeConstraint(rowIndex);
  div.appendChild(removeBtn);

  return div;
}

// ── addConstraint ─────────────────────────────────────────────────────────
function addConstraint() {
  numConstraints++;
  const nVars = parseInt(document.getElementById("n-vars").value);
  const area = document.getElementById("constraints-area");
  area.appendChild(createConstraintRow(numConstraints, nVars));
}

// ── removeConstraint ──────────────────────────────────────────────────────
function removeConstraint(id) {
  const rows = document.querySelectorAll(".constraint-row");
  if (rows.length <= 1) {
    alert("Necesitas al menos una restricción.");
    return;
  }
  const el = document.getElementById(`constraint-${id}`);
  if (el) el.remove();
}

// ── updateObjectiveFormula ────────────────────────────────────────────────
// Actualiza la visualización Z = 5·x1 + 8·x2 en tiempo real
function updateObjectiveFormula() {
  const nVars = parseInt(document.getElementById("n-vars").value);
  const parts = [];

  for (let i = 1; i <= nVars; i++) {
    const el = document.getElementById(`obj-${i}`);
    if (!el) continue;
    const val = parseFloat(el.value) || 0;
    parts.push(`${val}·x${i}`);
  }

  document.getElementById("obj-formula").textContent =
    "Z = " + (parts.join(" + ") || "0");
}

// ── solve ─────────────────────────────────────────────────────────────────
// Recopila los datos del formulario y llama al backend Flask /solve
async function solve() {
  const btn = document.querySelector(".btn-primary");
  btn.innerHTML = '<span class="spinner"></span> Resolviendo...';
  btn.disabled = true;

  try {
    const nVars = parseInt(document.getElementById("n-vars").value);

    // Recopilar función objetivo
    const objective = [];
    for (let i = 1; i <= nVars; i++) {
      const val = parseFloat(document.getElementById(`obj-${i}`).value);
      if (isNaN(val)) { throw new Error(`Coeficiente x${i} de la función objetivo inválido.`); }
      objective.push(val);
    }

    // Recopilar restricciones
    const constraints = [];
    const rows = document.querySelectorAll(".constraint-row");

    rows.forEach((row, idx) => {
      const rowId = row.id.replace("constraint-", "");
      const coeffs = [];

      for (let j = 1; j <= nVars; j++) {
        const el = document.getElementById(`c${rowId}-${j}`);
        if (!el) throw new Error(`Falta coeficiente x${j} en restricción ${idx + 1}.`);
        const v = parseFloat(el.value);
        if (isNaN(v)) throw new Error(`Coeficiente inválido en restricción ${idx + 1}.`);
        coeffs.push(v);
      }

      const rhsEl = document.getElementById(`rhs-${rowId}`);
      if (!rhsEl) throw new Error(`Falta RHS de restricción ${idx + 1}.`);
      const rhs = parseFloat(rhsEl.value);
      if (isNaN(rhs)) throw new Error(`RHS inválido en restricción ${idx + 1}.`);

      constraints.push({ coeffs, rhs });
    });

    // Llamada al backend
    const response = await fetch("/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ objective, constraints })
    });

    const result = await response.json();
    displayResults(result, nVars);

  } catch (err) {
    displayError(err.message);
  } finally {
    btn.innerHTML = "Resolver problema";
    btn.disabled = false;
  }
}

// ── displayResults ────────────────────────────────────────────────────────
function displayResults(result, nVars) {
  const section = document.getElementById("results-section");
  section.style.display = "block";
  section.scrollIntoView({ behavior: "smooth" });

  const statusEl = document.getElementById("result-status");
  const cardsEl  = document.getElementById("result-cards");
  const stepsEl  = document.getElementById("steps-list");

  // Limpiar
  cardsEl.innerHTML = "";
  stepsEl.innerHTML = "";

  if (result.error) {
    statusEl.className = "status-error";
    statusEl.textContent = "Error: " + result.error;
    return;
  }

  if (result.status === "optimal") {
    statusEl.className = "status-optimal";
    statusEl.textContent = `✓ Solución óptima encontrada en ${result.iterations} iteración(es)`;

    // Tarjeta de la función objetivo
    const objCard = makeMetricCard("Valor óptimo Z", result.objective.toFixed(2), true);
    cardsEl.appendChild(objCard);

    // Tarjeta de cada variable
    result.variables.forEach((val, i) => {
      cardsEl.appendChild(makeMetricCard(`x${i + 1}`, val.toFixed(2)));
    });

  } else {
    statusEl.className = "status-error";
    statusEl.textContent = `Estado: ${result.status}`;
  }

  // Pasos del algoritmo
  (result.steps || []).forEach(step => {
    const li = document.createElement("li");
    li.textContent = step;
    stepsEl.appendChild(li);
  });
}

// ── makeMetricCard ────────────────────────────────────────────────────────
function makeMetricCard(label, value, highlight = false) {
  const card = document.createElement("div");
  card.className = "metric-card" + (highlight ? " highlight" : "");
  card.innerHTML = `
    <div class="metric-label">${label}</div>
    <div class="metric-value">${value}</div>
  `;
  return card;
}

// ── displayError ──────────────────────────────────────────────────────────
function displayError(msg) {
  const section = document.getElementById("results-section");
  section.style.display = "block";
  const statusEl = document.getElementById("result-status");
  statusEl.className = "status-error";
  statusEl.textContent = "Error: " + msg;
  document.getElementById("result-cards").innerHTML = "";
  document.getElementById("steps-list").innerHTML = "";
}
