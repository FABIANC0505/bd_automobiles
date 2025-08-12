from flask import Flask, render_template, flash, request, redirect, url_for
import pymysql 

app = Flask (__name__)
app.secret_key= 'secretkey'

#hacemos la coneccion con la base de datos
def connect_to_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='bd_automobiles',
        cursorclass=pymysql.cursors.DictCursor,
        ssl_disabled=True  
          
    )

# Ruta para eliminar clientes
@app.route('/delete/<id>', methods=['POST'])
def delete_clientes(id):
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM clientes WHERE id=%s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Cliente eliminado correctamente')
    except Exception as e:
        flash(f"Error al eliminar cliente: {e}")
    return redirect(url_for('index'))

# Ruta para la página principal: muestra todos los registros

@app.route('/') 
def index(): 
    try: 
        conn = connect_to_db() 
        cur = conn.cursor() 
        cur.execute("SELECT * FROM clientes") 
        data = cur.fetchall() 
        cur.close() 
        conn.close() 
        return render_template('index.html', clientes=data) 
    except Exception as e: 
        flash(f"Error al obtener datos: {e}") 
        return render_template('index.html', clientes=[])
        
# Ruta para agregar un nuevo cliente

@app.route('/add', methods=['GET', 'POST']) 
def add_clientes(): 

    if request.method == 'POST':
         nif = request.form['nif'] 
         nombre = request.form['nombre'] 
         direccion = request.form['direccion'] 
         telefono = request.form['telefono']



         try: 
        
            conn = connect_to_db() 
            cur = conn.cursor() 
            cur.execute("INSERT INTO clientes (nif, nombre, direccion, telefono) " 
            "VALUES (%s, %s, %s, %s)", (nif, nombre, direccion, telefono))
            conn.commit() 
            cur.close() 
            conn.close() 
            flash('cliente agregado correctamente') 
            return redirect(url_for('index')) 
         except Exception as e: 
            flash(f"Error al agregar cliente: {e}") 
            return redirect(url_for('index')) 
    return render_template('ingresar.html')

@app.route('/edit/<id>', methods=['GET', 'POST']) 
def edit_clientes(id): 
    if request.method == 'POST': 
        nif = request.form['nif'] 
        nombre = request.form['nombre'] 
        direccion = request.form['direccion'] 
        telefono = request.form['telefono'] 
 
        try: 
            conn = connect_to_db() 
            cur = conn.cursor() 
            cur.execute(""" 
                UPDATE clientes 
                SET nif=%s, nombre=%s, direccion=%s, telefono=%s 
                WHERE id=%s 
            """, (nif, nombre, direccion, telefono, id)) 
            conn.commit() 
            cur.close() 
            conn.close() 
            flash('Cliente actualizado correctamente') 
            return redirect(url_for('index')) 
        except Exception as e: 
            flash(f"Error al actualizar clientes: {e}") 
            return redirect(url_for('index')) 
    
    # Si es GET: cargar los datos y mostrarlos en el formulario
    try: 
        conn = connect_to_db() 
        cur = conn.cursor() 
        cur.execute("SELECT * FROM clientes WHERE id=%s", (id,)) 
        cliente = cur.fetchone() 
        cur.close() 
        conn.close() 
        return render_template('editar.html', cliente=cliente)
    except Exception as e: 
        flash(f"Error al obtener cliente: {e}") 
        return redirect(url_for('index'))




                    
if __name__ == '__main__': 
    app.run(debug=True)