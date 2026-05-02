"""
PFO2 - Sistema de Gestión de Tareas con API y Base de Datos
servidor.py: API REST con Flask + SQLite
"""

from flask import Flask, request, jsonify, render_template_string, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)

# ─── Base de datos ────────────────────────────────────────────────────────────
DB_PATH = "pfo2.db"

def get_db():
    """Abre (o crea) la conexión a SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Crea las tablas si no existen."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario    TEXT    NOT NULL UNIQUE,
                contrasena TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tareas (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                titulo     TEXT    NOT NULL,
                completada INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
        """)

# ─── HTML de bienvenida ───────────────────────────────────────────────────────
WELCOME_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gestor de Tareas — PFO2</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #e0e0e0;
    }
    .card {
      background: rgba(255,255,255,0.05);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255,255,255,0.12);
      border-radius: 20px;
      padding: 48px 56px;
      max-width: 680px;
      width: 90%;
      text-align: center;
      box-shadow: 0 24px 64px rgba(0,0,0,0.5);
    }
    .icon { font-size: 3.5rem; margin-bottom: 16px; }
    h1 { font-size: 2rem; font-weight: 700; color: #ffffff; margin-bottom: 8px; }
    .subtitle { color: #a0aec0; margin-bottom: 36px; font-size: 1rem; }
    .endpoints { text-align: left; margin-bottom: 32px; }
    .endpoints h2 { font-size: 1rem; text-transform: uppercase; letter-spacing: 2px;
                    color: #63b3ed; margin-bottom: 16px; }
    .endpoint {
      display: flex; align-items: center; gap: 12px;
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 10px;
      padding: 12px 16px;
      margin-bottom: 10px;
    }
    .method {
      font-size: 0.72rem; font-weight: 700; letter-spacing: 1px;
      padding: 3px 10px; border-radius: 6px; white-space: nowrap;
    }
    .post { background: #2d6a4f; color: #95d5b2; }
    .get  { background: #1a4e8a; color: #90cdf4; }
    .path { font-family: 'Courier New', monospace; font-size: 0.9rem; color: #e2e8f0; }
    .desc { font-size: 0.82rem; color: #718096; margin-left: auto; }
    .badge {
      display: inline-block;
      background: linear-gradient(90deg, #4776e6, #8e54e9);
      color: white; border-radius: 999px;
      padding: 6px 20px; font-size: 0.82rem; font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="icon"></div>
    <h1>Gestor de Tareas</h1>
    <p class="subtitle">PFO2 — API REST con Flask &amp; SQLite</p>

    <div class="endpoints">
      <h2>Endpoints disponibles</h2>

      <div class="endpoint">
        <span class="method post">POST</span>
        <span class="path">/registro</span>
        <span class="desc">Registrar nuevo usuario</span>
      </div>
      <div class="endpoint">
        <span class="method post">POST</span>
        <span class="path">/login</span>
        <span class="desc">Iniciar sesión</span>
      </div>
      <div class="endpoint">
        <span class="method get">GET</span>
        <span class="path">/tareas</span>
        <span class="desc">Esta página de bienvenida</span>
      </div>
    </div>

    <span class="badge">Servidor activo</span>
  </div>
</body>
</html>
"""

# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return redirect("/tareas")

@app.route("/tareas", methods=["GET"])
def bienvenida():
    """GET /tareas → muestra el HTML de bienvenida."""
    return render_template_string(WELCOME_HTML)


@app.route("/registro", methods=["POST"])
def registro():
    """POST /registro → registra un nuevo usuario con contraseña hasheada."""
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Se esperaba JSON."}), 400

    usuario = datos.get("usuario", "").strip()
    contrasena = datos.get("contraseña", "")

    if not usuario or not contrasena:
        return jsonify({"error": "Los campos 'usuario' y 'contraseña' son obligatorios."}), 400

    hash_contrasena = generate_password_hash(contrasena)

    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)",
                (usuario, hash_contrasena),
            )
        return jsonify({"mensaje": f"Usuario '{usuario}' registrado correctamente."}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": f"El usuario '{usuario}' ya existe."}), 409


@app.route("/login", methods=["POST"])
def login():
    """POST /login → verifica credenciales."""
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Se esperaba JSON."}), 400

    usuario = datos.get("usuario", "").strip()
    contrasena = datos.get("contraseña", "")

    if not usuario or not contrasena:
        return jsonify({"error": "Los campos 'usuario' y 'contraseña' son obligatorios."}), 400

    with get_db() as conn:
        fila = conn.execute(
            "SELECT contrasena FROM usuarios WHERE usuario = ?", (usuario,)
        ).fetchone()

    if fila is None or not check_password_hash(fila["contrasena"], contrasena):
        return jsonify({"error": "Credenciales incorrectas."}), 401

    return jsonify({"mensaje": f"Bienvenido, {usuario}. Inicio de sesión exitoso."}), 200


# ─── Arranque ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada.")
    print("Servidor corriendo en http://127.0.0.1:5000")
    app.run(debug=True)
