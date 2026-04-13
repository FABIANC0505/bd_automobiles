from contextlib import contextmanager
from flask import Flask, jsonify, render_template, flash, request, redirect, url_for
import pymysql
import pymysql.cursors
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'secretkey'

CORS(app, origins=["http://localhost:51192/", "http://192.168.11.236"])

# ─── Configuración de base de datos ────────────────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '050523Fe.',
    'database': 'bd_automobiles',
    'cursorclass': pymysql.cursors.DictCursor,
    'ssl_disabled': True,
}

@contextmanager
def get_db():
    """Context manager que abre la conexión, la entrega y la cierra siempre."""
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        yield conn, cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ─── API REST ──────────────────────────────────────────────────────────────────

@app.route('/api/clientes', methods=['GET', 'POST'])
def api_clientes():
    """
    GET  → lista todos los clientes (JSON)
    POST → crea un cliente nuevo (JSON body)
    """
    if request.method == 'GET':
        try:
            with get_db() as (conn, cur):
                cur.execute("SELECT * FROM clientes")
                clientes = cur.fetchall()
            return jsonify(clientes), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # POST
    if not request.is_json:
        return jsonify({'error': 'Content-Type debe ser application/json'}), 415

    data = request.get_json()
    nif      = data.get('nif')
    nombre   = data.get('nombre')
    direccion = data.get('direccion')
    telefono = data.get('telefono')

    if not all([nif, nombre, direccion, telefono]):
        return jsonify({'error': 'Faltan parámetros'}), 400

    try:
        with get_db() as (conn, cur):
            cur.execute(
                "INSERT INTO clientes (nif, nombre, direccion, telefono) VALUES (%s, %s, %s, %s)",
                (nif, nombre, direccion, telefono)
            )
            nuevo_id = cur.lastrowid
        return jsonify({'mensaje': 'Cliente agregado correctamente', 'id': nuevo_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/datos/clientes', methods=['GET'])
def consultar_todos_los_clientes():
    """Endpoint adicional que devuelve todos los clientes en JSON."""
    try:
        with get_db() as (conn, cur):
            cur.execute("SELECT * FROM clientes")
            lista_clientes = cur.fetchall()
        return jsonify(lista_clientes), 200
    except Exception as e:
        return jsonify({'mensaje': 'Error al obtener los clientes', 'error': str(e)}), 500


# ─── Vistas Web ────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    try:
        with get_db() as (conn, cur):
            cur.execute("SELECT * FROM clientes")
            data = cur.fetchall()
        return render_template('index.html', clientes=data)
    except Exception as e:
        flash(f'Error al obtener datos: {e}', 'danger')
        return render_template('index.html', clientes=[])


@app.route('/add', methods=['GET', 'POST'])
def add_clientes():
    if request.method == 'POST':
        nif       = request.form['nif']
        nombre    = request.form['nombre']
        direccion = request.form['direccion']
        telefono  = request.form['telefono']

        try:
            with get_db() as (conn, cur):
                cur.execute(
                    "INSERT INTO clientes (nif, nombre, direccion, telefono) VALUES (%s, %s, %s, %s)",
                    (nif, nombre, direccion, telefono)
                )
            flash('Cliente agregado correctamente', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error al agregar cliente: {e}', 'danger')
            return redirect(url_for('index'))

    return render_template('ingresar.html')


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_clientes(id):
    if request.method == 'POST':
        nif       = request.form['nif']
        nombre    = request.form['nombre']
        direccion = request.form['direccion']
        telefono  = request.form['telefono']

        try:
            with get_db() as (conn, cur):
                cur.execute(
                    "UPDATE clientes SET nif=%s, nombre=%s, direccion=%s, telefono=%s WHERE id=%s",
                    (nif, nombre, direccion, telefono, id)
                )
            flash('Cliente actualizado correctamente', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error al actualizar cliente: {e}', 'danger')
            return redirect(url_for('index'))

    try:
        with get_db() as (conn, cur):
            cur.execute("SELECT * FROM clientes WHERE id=%s", (id,))
            cliente = cur.fetchone()
        return render_template('editar.html', cliente=cliente)
    except Exception as e:
        flash(f'Error al obtener cliente: {e}', 'danger')
        return redirect(url_for('index'))


@app.route('/delete/<id>', methods=['POST'])
def delete_clientes(id):
    try:
        with get_db() as (conn, cur):
            cur.execute("DELETE FROM clientes WHERE id=%s", (id,))
        flash('Cliente eliminado correctamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar cliente: {e}', 'danger')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)