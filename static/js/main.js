// static/js/main.js

let numConstraints = 2;
let objType = "max";

function setObjType(type) {
  objType = type;
  document.querySelectorAll('.toggle-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.value === type);
  });
  const badge = document.getElementById('obj-badge');
  if (badge) badge.textContent = type === 'max' ? 'Maximizar Z' : 'Minimizar Z';
  updateObjectiveFormula();
}

function buildForm() {
  const nVars = parseInt(document.getElementById("n-vars").value);
  buildObjectiveInputs(nVars);
  buildConstraints(nVars);
  updateObjectiveFormula();
}

function buildObjectiveInputs(nVars) {
  const container = document.getElementById("objective-inputs");
  container.innerHTML = "";
  for (let i = 1; i <= nVars; i++) {
    if (i > 1) {
      const plus = document.createElement("span");
      plus.className = "coeff-label";
      plus.textContent = "+";
      container.appendChild(plus);
    }
    const input = document.createElement("input");
    input.type = "number";
    input.id = `obj-${i}`;
    input.value = i === 1 ? 5 : 8;
    input.step = "any";
    input.oninput = updateObjectiveFormula;
    container.appendChild(input);
    const label = document.createElement("span");
    label.className = "coeff-label";
    label.textContent = `· x${i}`;
    container.appendChild(label);
  }
}

function buildConstraints(nVars) {
  const area = document.getElementById("constraints-area");
  area.innerHTML = "";
  numConstraints = 2;
  for (let i = 1; i <= 2; i++) {
    area.appendChild(createConstraintRow(i, nVars));
  }
}

function createConstraintRow(rowIndex, nVars) {
  const nVarsNow = nVars || parseInt(document.getElementById("n-vars").value);
  const div = document.createElement("div");
  div.className = "constraint-row";
  div.id = `constraint-${rowIndex}`;

  const num = document.createElement("span");
  num.className = "constraint-num";
  num.textContent = `R${rowIndex}`;
  div.appendChild(num);

  const defaultCoeffs = [[2, 4], [6, 3], [1, 2, 1], [3, 1, 2]];

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
    const def = defaultCoeffs[rowIndex - 1];
    input.value = (def && def[j - 1] !== undefined) ? def[j - 1] : 1;
    input.step = "any";
    div.appendChild(input);
    const lbl = document.createElement("span");
    lbl.className = "coeff-label";
    lbl.textContent = `· x${j}`;
    div.appendChild(lbl);
  }

  // ── Select de signo (<=, >=, =) ──────────────────────────────
  const signSel = document.createElement("select");
  signSel.className = "sign-select";
  signSel.id = `sign-${rowIndex}`;
  [["<=", "≤"], [">=", "≥"], ["=", "="]].forEach(([val, label]) => {
    const opt = document.createElement("option");
    opt.value = val;
    opt.textContent = label;
    if (val === "<=") opt.selected = true;
    signSel.appendChild(opt);
  });
  div.appendChild(signSel);

  const rhs = document.createElement("input");
  rhs.type = "number";
  rhs.id = `rhs-${rowIndex}`;
  rhs.value = rowIndex === 1 ? 40 : 60;
  rhs.step = "any";
  rhs.style.width = "90px";
  div.appendChild(rhs);

  const removeBtn = document.createElement("button");
  removeBtn.className = "btn-remove";
  removeBtn.textContent = "✕";
  removeBtn.title = "Eliminar restricción";
  removeBtn.onclick = () => removeConstraint(rowIndex);
  div.appendChild(removeBtn);

  return div;
}

function addConstraint() {
  numConstraints++;
  const nVars = parseInt(document.getElementById("n-vars").value);
  const area = document.getElementById("constraints-area");
  area.appendChild(createConstraintRow(numConstraints, nVars));
}

function removeConstraint(id) {
  const rows = document.querySelectorAll(".constraint-row");
  if (rows.length <= 1) { alert("Necesitas al menos una restricción."); return; }
  const el = document.getElementById(`constraint-${id}`);
  if (el) el.remove();
}

function updateObjectiveFormula() {
  const nVars = parseInt(document.getElementById("n-vars").value);
  const parts = [];
  for (let i = 1; i <= nVars; i++) {
    const el = document.getElementById(`obj-${i}`);
    if (!el) continue;
    const val = parseFloat(el.value) || 0;
    parts.push(`${val}·x${i}`);
  }
  const verb = objType === 'min' ? 'Min' : 'Max';
  document.getElementById("obj-formula").textContent =
    `${verb} Z = ` + (parts.join(" + ") || "0");
}

async function solve() {
  const btn = document.getElementById('solve-btn');
  btn.innerHTML = '<span class="spinner"></span> Resolviendo...';
  btn.disabled = true;

  try {
    const nVars = parseInt(document.getElementById("n-vars").value);
    const objective = [];
    for (let i = 1; i <= nVars; i++) {
      const val = parseFloat(document.getElementById(`obj-${i}`).value);
      if (isNaN(val)) throw new Error(`Coeficiente x${i} inválido.`);
      objective.push(val);
    }

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
      const rhsEl  = document.getElementById(`rhs-${rowId}`);
      const signEl = document.getElementById(`sign-${rowId}`);
      if (!rhsEl)  throw new Error(`Falta RHS en restricción ${idx + 1}.`);
      const rhs  = parseFloat(rhsEl.value);
      const sign = signEl ? signEl.value : "<=";
      if (isNaN(rhs)) throw new Error(`RHS inválido en restricción ${idx + 1}.`);
      constraints.push({ coeffs, sign, rhs });
    });

    const response = await fetch("/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ objective_type: objType, objective, constraints })
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

function displayResults(result, nVars) {
  const section = document.getElementById("results-section");
  section.style.display = "block";
  section.scrollIntoView({ behavior: "smooth" });

  const statusEl = document.getElementById("result-status");
  const cardsEl  = document.getElementById("result-cards");
  const stepsEl  = document.getElementById("steps-list");

  cardsEl.innerHTML = "";
  stepsEl.innerHTML = "";

  if (result.error) {
    statusEl.className = "status-error";
    statusEl.textContent = "Error: " + result.error;
    return;
  }

  if (result.status === "optimal") {
    statusEl.className = "status-optimal";
    statusEl.textContent =
      `✓ Solución óptima encontrada en ${result.iterations} iteración(es)`;
    cardsEl.appendChild(makeMetricCard("Valor óptimo Z", result.objective.toFixed(2), true));
    result.variables.forEach((val, i) => {
      cardsEl.appendChild(makeMetricCard(`x${i + 1}`, val.toFixed(4)));
    });
  } else {
    statusEl.className = "status-error";
    statusEl.textContent = `Estado: ${result.status}`;
  }

  (result.steps || []).forEach(step => {
    const li = document.createElement("li");
    li.textContent = step;
    stepsEl.appendChild(li);
  });
}

function makeMetricCard(label, value, highlight = false) {
  const card = document.createElement("div");
  card.className = "metric-card" + (highlight ? " highlight" : "");
  card.innerHTML = `
    <div class="metric-label">${label}</div>
    <div class="metric-value">${value}</div>`;
  return card;
}

function displayError(msg) {
  const section = document.getElementById("results-section");
  section.style.display = "block";
  const statusEl = document.getElementById("result-status");
  statusEl.className = "status-error";
  statusEl.textContent = "Error: " + msg;
  document.getElementById("result-cards").innerHTML = "";
  document.getElementById("steps-list").innerHTML = "";
}
