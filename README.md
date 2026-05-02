# PFO2 — Sistema de Gestión de Tareas con API y Base de Datos

API REST construida con **Flask** y **SQLite**, con autenticación básica y contraseñas hasheadas.

---

## Estructura del proyecto

```
PFO2/
├── servidor.py   # API Flask + SQLite
└── README.md     # Este archivo
```

---

##  Requisitos previos

- Python 3.8 o superior
- pip

---

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/Lute86/PFO2.git
cd PFO2
```

### 2. (Opcional) Crear un entorno virtual

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Instalar dependencias

```bash
pip install flask werkzeug
```

### 4. Ejecutar el servidor

```bash
python servidor.py
```

El servidor arranca en **http://127.0.0.1:5000** y crea automáticamente el archivo `pfo2.db`.

---

## Endpoints

| Método | Ruta        | Descripción                         |
|--------|-------------|-------------------------------------|
| POST   | `/registro` | Registrar un nuevo usuario          |
| POST   | `/login`    | Iniciar sesión con credenciales     |
| GET    | `/tareas`   | Página HTML de bienvenida           |

---

## Cómo probar la API

### Opción A — curl (terminal)

```bash
# 1. Registrar usuario
curl -X POST http://127.0.0.1:5000/registro \
     -H "Content-Type: application/json" \
     -d '{"usuario": "ana", "contraseña": "secreta123"}'

# 2. Iniciar sesión
curl -X POST http://127.0.0.1:5000/login \
     -H "Content-Type: application/json" \
     -d '{"usuario": "ana", "contraseña": "secreta123"}'

# 3. Ver página de bienvenida
curl http://127.0.0.1:5000/tareas
```

### Opción B — Postman / Insomnia

1. Crear una request **POST** a `http://127.0.0.1:5000/registro`.
2. En el body seleccionar **raw → JSON** y enviar:
   ```json
   { "usuario": "ana", "contraseña": "secreta123" }
   ```
3. Repetir para `/login` con las mismas credenciales.
4. Hacer **GET** a `/tareas` para ver la página de bienvenida.

### Opción C — Navegador

Abrir `http://127.0.0.1:5000/tareas` directamente para ver el HTML de bienvenida.

---

## Capturas de pantalla de pruebas exitosas

### Registro exitoso (`POST /registro`)
```json
HTTP 201 Created
{
  "mensaje": "Usuario 'ana' registrado correctamente."
}
```

### Login exitoso (`POST /login`)
```json
HTTP 200 OK
{
  "mensaje": "Bienvenido, ana. Inicio de sesión exitoso."
}
```

### Login con credenciales incorrectas
```json
HTTP 401 Unauthorized
{
  "error": "Credenciales incorrectas."
}
```

### Registro de usuario duplicado
```json
HTTP 409 Conflict
{
  "error": "El usuario 'ana' ya existe."
}
```

---

## Respuestas Conceptuales

### ¿Por qué hashear contraseñas?

Guardar contraseñas en texto plano es extremadamente peligroso.  
Si la base de datos es robada o expuesta, **todas las contraseñas quedan al descubierto** al instante.

El **hashing** transforma la contraseña en una cadena irreversible:

```
"secreta123"  →  pbkdf2:sha256:600000$...(hash)...
```

- **Es unidireccional**: no se puede recuperar la contraseña original a partir del hash.  
- **Con sal (salt)**: Werkzeug añade un valor aleatorio antes de hashear, por lo que dos usuarios con la misma contraseña tendrán hashes distintos. Esto protege contra ataques de *rainbow tables*.  
- **Lento por diseño**: algoritmos como PBKDF2/bcrypt hacen que probar millones de contraseñas por fuerza bruta sea costoso en tiempo.

> **Regla de oro**: nunca almacenar ni registrar una contraseña en texto plano.

---

### Ventajas de usar SQLite en este proyecto

| Ventaja | Detalle |
|---------|---------|
| **Sin servidor** | No requiere instalar ni configurar un servicio de base de datos separado (PostgreSQL, MySQL). |
| **Archivo único** | Toda la base de datos vive en `pfo2.db`, fácil de mover, copiar o eliminar. |
| **Integrado en Python** | El módulo `sqlite3` viene en la biblioteca estándar; cero dependencias extras. |
| **Ideal para desarrollo** | Perfecto para prototipos, proyectos académicos y apps con bajo volumen de datos. |
| **Persistencia real** | Los datos sobreviven al reinicio del servidor, a diferencia de estructuras en memoria. |
| **ACID** | Garantiza transacciones atómicas, consistentes, aisladas y durables. |

Para un proyecto académico como la PFO2 SQLite es una elección correcta y suficiente.

---


##  Tecnologías utilizadas

- **Python 3** — lenguaje base  
- **Flask** — framework web liviano  
- **Werkzeug** — hashing de contraseñas (PBKDF2-SHA256)  
- **SQLite** — base de datos embebida  
