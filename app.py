# app.py
from flask import Flask, render_template, request, jsonify
from solver import simplex
import os


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/caso")
def caso():
    """Página del caso de estudio FincaOro S.A.S."""
    return render_template("caso.html")


@app.route("/solve", methods=["POST"])
def solve():
    """
    Recibe JSON:
    {
        "objective_type": "max" | "min",
        "objective":      [5, 8],
        "constraints": [
            { "coeffs": [2, 4], "sign": "<=", "rhs": 40 },
            { "coeffs": [6, 3], "sign": ">=", "rhs": 10 }
        ]
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos."}), 400

        obj_type    = data.get("objective_type", "max")
        c           = data.get("objective", [])
        constraints = data.get("constraints", [])

        if not c:
            return jsonify({"error": "Falta la función objetivo."}), 400
        if not constraints:
            return jsonify({"error": "Se necesita al menos una restricción."}), 400

        n_vars = len(c)
        A, b, signs = [], [], []

        for i, con in enumerate(constraints):
            coeffs = con.get("coeffs", [])
            sign   = con.get("sign", "<=")
            rhs    = con.get("rhs", 0)

            if len(coeffs) != n_vars:
                return jsonify({
                    "error": f"Restricción {i+1}: tiene {len(coeffs)} "
                             f"coeficientes pero se esperan {n_vars}."
                }), 400

            if sign not in ("<=", ">=", "="):
                return jsonify({"error": f"Signo '{sign}' no válido."}), 400

            A.append(coeffs)
            b.append(rhs)
            signs.append(sign)

        result = simplex(c, A, b, signs, obj_type)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
