from flask import Flask, render_template_string, request, redirect, url_for
import psycopg2

app = Flask(__name__)

# Configura tus datos de conexión a CockroachDB aquí
DB_HOST = "inventario-guffy-6375.jxf.gcp-us-east1.cockroachlabs.cloud"
DB_PORT = 26257
DB_NAME = "in_zapateria"
DB_USER = "guffy"
DB_PASSWORD = "sXKPPjk0sGiAayPxRBSi4g"
DB_SSLMODE = "verify-full"

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    sslmode=DB_SSLMODE
)
cursor = conn.cursor()

HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Inicio Tienda de Ropa</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:700,400&display=swap" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(120deg, #f8fafc 0%, #e0c3fc 100%);
            font-family: 'Montserrat', Arial, sans-serif;
            margin: 0;
        }
        .navbar {
            background: #6a82fb;
            color: #fff;
            padding: 18px 0;
            text-align: center;
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: 2px;
            box-shadow: 0 2px 8px rgba(106,130,251,0.08);
        }
        .container {
            max-width: 420px;
            margin: 80px auto;
            background: #fff;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(106,130,251,0.13);
            padding: 44px 48px 36px 48px;
            text-align: center;
        }
        h1 {
            color: #6a82fb;
            margin-bottom: 32px;
            font-size: 2.2rem;
            font-weight: 700;
        }
        .btn {
            display: block;
            width: 100%;
            margin: 22px 0;
            padding: 18px 0;
            background: linear-gradient(90deg, #6a82fb 60%, #fc5c7d 100%);
            color: #fff;
            border: none;
            border-radius: 10px;
            font-size: 1.2rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s;
            box-shadow: 0 2px 8px rgba(106,130,251,0.07);
            letter-spacing: 1px;
        }
        .btn:hover {
            background: linear-gradient(90deg, #fc5c7d 60%, #6a82fb 100%);
            transform: translateY(-2px) scale(1.03);
        }
        .shop-img {
            width: 120px;
            margin-bottom: 18px;
            filter: drop-shadow(0 2px 8px #6a82fb33);
        }
    </style>
</head>
<body>
    <div class="navbar">Tienda de Ropa</div>
    <div class="container">
        <img class="shop-img" src="https://cdn-icons-png.flaticon.com/512/892/892458.png" alt="Tienda">
        <h1>Gestión de Inventario</h1>
        <form action="{{ url_for('agregar') }}">
            <button class="btn" type="submit">Agregar Prenda</button>
        </form>
        <form action="{{ url_for('inventario') }}">
            <button class="btn" type="submit">Ver Inventario</button>
        </form>
    </div>
</body>
</html>
"""

AGREGAR_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Agregar Prenda</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:700,400&display=swap" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(120deg, #f8fafc 0%, #e0c3fc 100%);
            font-family: 'Montserrat', Arial, sans-serif;
            margin: 0;
        }
        .container {
            max-width: 420px;
            margin: 60px auto;
            background: #fff;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(106,130,251,0.13);
            padding: 44px 48px 36px 48px;
        }
        h1 {
            color: #fc5c7d;
            text-align: center;
            margin-bottom: 28px;
            font-size: 2rem;
            font-weight: 700;
        }
        form { display: flex; flex-direction: column; gap: 16px; }
        input {
            padding: 12px 16px;
            border: 1px solid #dcdde1;
            border-radius: 10px;
            font-size: 1.1rem;
            background: #f8faff;
            transition: border 0.2s;
        }
        input:focus { border: 1.5px solid #fc5c7d; outline: none;}
        button {
            background: linear-gradient(90deg, #6a82fb 60%, #fc5c7d 100%);
            color: #fff;
            border: none;
            border-radius: 10px;
            padding: 14px 0;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s;
            box-shadow: 0 2px 8px rgba(106,130,251,0.07);
            margin-top: 10px;
        }
        button:hover {
            background: linear-gradient(90deg, #fc5c7d 60%, #6a82fb 100%);
            transform: translateY(-2px) scale(1.03);
        }
        .back { margin-top: 18px; text-align: center; }
        .back a { color: #6a82fb; text-decoration: none; font-weight: 600;}
    </style>
</head>
<body>
    <div class="container">
        <h1>Agregar Prenda</h1>
        <form method="post">
            <input name="marca" placeholder="Marca o Tipo de Prenda" required>
            <input name="talla" placeholder="Talla (ej: S, M, L, 38, 40...)" required>
            <input name="color" placeholder="Color" required>
            <input name="cantidad" type="number" min="1" placeholder="Cantidad" required>
            <button type="submit">Guardar</button>
        </form>
        <div class="back"><a href="{{ url_for('home') }}">Volver al inicio</a></div>
    </div>
</body>
</html>
"""

INVENTARIO_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Inventario</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:700,400&display=swap" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(120deg, #f8fafc 0%, #e0c3fc 100%);
            font-family: 'Montserrat', Arial, sans-serif;
            margin: 0;
        }
        .container {
            max-width: 900px;
            margin: 40px auto;
            background: #fff;
            border-radius: 20px;
            box-shadow: 0 4px 24px rgba(106,130,251,0.10);
            padding: 36px 40px 24px 40px;
        }
        h1 {
            color: #6a82fb;
            text-align: center;
            margin-bottom: 24px;
            font-size: 2rem;
            font-weight: 700;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 24px;
            background: #f8faff;
            border-radius: 10px;
            overflow: hidden;
        }
        th, td {
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #eee;
            font-size: 1.1rem;
        }
        th {
            background: #e0c3fc;
            color: #6a82fb;
            font-weight: 700;
        }
        tr:last-child td { border-bottom: none; }
        form { display: inline; }
        button {
            background: #fc5c7d;
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 7px 16px;
            font-size: 1rem;
            cursor: pointer;
            font-weight: 600;
            margin: 0 2px;
        }
        button:hover { background: #6a82fb; }
        a { color: #6a82fb; text-decoration: none; font-weight: 600;}
        a:hover { text-decoration: underline; }
        .search-form { margin-bottom: 20px; text-align: center; }
        .search-input {
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid #ccc;
            font-size: 1rem;
            margin-right: 8px;
        }
        .search-btn {
            padding: 8px 16px;
            border-radius: 8px;
            border: none;
            background: #6a82fb;
            color: #fff;
            font-weight: 600;
            cursor: pointer;
        }
        .search-btn:hover { background: #fc5c7d; }
        .shop-img {
            width: 60px;
            margin-bottom: 10px;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <img class="shop-img" src="https://cdn-icons-png.flaticon.com/512/892/892458.png" alt="Tienda">
        <h1>Inventario de Prendas</h1>
        <a href="{{ url_for('home') }}">Volver al inicio</a>
        <form class="search-form" method="get" action="{{ url_for('inventario') }}">
            <input class="search-input" type="text" name="q" placeholder="Buscar por marca, color o talla" value="{{ request.args.get('q', '') }}">
            <button class="search-btn" type="submit">Buscar</button>
            {% if request.args.get('q') %}
                <a href="{{ url_for('inventario') }}">Limpiar</a>
            {% endif %}
        </form>
        <table>
            <tr>
                <th>Marca/Tipo</th>
                <th>Talla</th>
                <th>Color</th>
                <th>Cantidad</th>
                <th>Borrar</th>
                <th>Modificar</th>
                <th>Vender</th>
            </tr>
            {% for zapato in inventario %}
            <tr>
                <td>{{ zapato['marca'] }}</td>
                <td>{{ zapato['talla'] }}</td>
                <td>{{ zapato['color'] }}</td>
                <td>{{ zapato['cantidad'] }}</td>
                <td>
                    <form method="post" action="{{ url_for('borrar', id=zapato['_id']) }}">
                        <button type="submit" onclick="return confirm('¿Seguro que deseas borrar esta prenda?')">Borrar</button>
                    </form>
                </td>
                <td>
                    <form method="get" action="{{ url_for('modificar', id=zapato['_id']) }}">
                        <button type="submit">Modificar</button>
                    </form>
                </td>
                <td>
                    <form method="post" action="{{ url_for('vender', id=zapato['_id']) }}">
                        <button type="submit" {% if zapato['cantidad']|int <= 0 %}disabled{% endif %}>Vender</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

MODIFICAR_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Modificar Prenda</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:700,400&display=swap" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(120deg, #f8fafc 0%, #e0c3fc 100%);
            font-family: 'Montserrat', Arial, sans-serif;
            margin: 0;
        }
        .container {
            max-width: 420px;
            margin: 60px auto;
            background: #fff;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(106,130,251,0.13);
            padding: 44px 48px 36px 48px;
        }
        h1 {
            color: #fc5c7d;
            text-align: center;
            margin-bottom: 28px;
            font-size: 2rem;
            font-weight: 700;
        }
        form { display: flex; flex-direction: column; gap: 16px; }
        input {
            padding: 12px 16px;
            border: 1px solid #dcdde1;
            border-radius: 10px;
            font-size: 1.1rem;
            background: #f8faff;
            transition: border 0.2s;
        }
        input:focus { border: 1.5px solid #fc5c7d; outline: none;}
        button {
            background: linear-gradient(90deg, #6a82fb 60%, #fc5c7d 100%);
            color: #fff;
            border: none;
            border-radius: 10px;
            padding: 14px 0;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s;
            box-shadow: 0 2px 8px rgba(106,130,251,0.07);
            margin-top: 10px;
        }
        button:hover {
            background: linear-gradient(90deg, #fc5c7d 60%, #6a82fb 100%);
            transform: translateY(-2px) scale(1.03);
        }
        .back { margin-top: 18px; text-align: center; }
        .back a { color: #6a82fb; text-decoration: none; font-weight: 600;}
    </style>
</head>
<body>
    <div class="container">
        <h1>Modificar Prenda</h1>
        <form method="post">
            <input name="marca" placeholder="Marca o Tipo de Prenda" value="{{ zapato['marca'] }}" required>
            <input name="talla" placeholder="Talla" value="{{ zapato['talla'] }}" required>
            <input name="color" placeholder="Color" value="{{ zapato['color'] }}" required>
            <input name="cantidad" type="number" min="0" placeholder="Cantidad" value="{{ zapato['cantidad'] }}" required>
            <button type="submit">Guardar Cambios</button>
        </form>
        <div class="back"><a href="{{ url_for('inventario') }}">Volver al inventario</a></div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_HTML)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        marca = request.form['marca']
        talla = float(request.form['talla'])
        color = request.form['color']
        cantidad = int(request.form['cantidad'])
        cursor.execute(
            "INSERT INTO zapatos (marca, talla, color, cantidad) VALUES (%s, %s, %s, %s)",
            (marca, talla, color, cantidad)
        )
        conn.commit()
        return redirect(url_for('home'))
    return render_template_string(AGREGAR_HTML)

@app.route('/inventario')
def inventario():
    q = request.args.get('q', '').strip()
    if q:
        query = """
            SELECT id, marca, talla, color, cantidad FROM zapatos
            WHERE LOWER(marca) LIKE %s OR LOWER(color) LIKE %s OR CAST(talla AS TEXT) LIKE %s
        """
        like_q = f"%{q.lower()}%"
        cursor.execute(query, (like_q, like_q, like_q))
    else:
        cursor.execute("SELECT id, marca, talla, color, cantidad FROM zapatos")
    rows = cursor.fetchall()
    inventario = [
        {'_id': row[0], 'marca': row[1], 'talla': row[2], 'color': row[3], 'cantidad': row[4]}
        for row in rows
    ]
    return render_template_string(INVENTARIO_HTML, inventario=inventario)

@app.route('/borrar/<int:id>', methods=['POST'])
def borrar(id):
    cursor.execute("DELETE FROM zapatos WHERE id = %s", (id,))
    conn.commit()
    return redirect(url_for('inventario'))

@app.route('/modificar/<int:id>', methods=['GET', 'POST'])
def modificar(id):
    if request.method == 'POST':
        marca = request.form['marca']
        talla = float(request.form['talla'])
        color = request.form['color']
        cantidad = int(request.form['cantidad'])
        cursor.execute(
            "UPDATE zapatos SET marca=%s, talla=%s, color=%s, cantidad=%s WHERE id=%s",
            (marca, talla, color, cantidad, id)
        )
        conn.commit()
        return redirect(url_for('inventario'))
    cursor.execute("SELECT id, marca, talla, color, cantidad FROM zapatos WHERE id = %s", (id,))
    row = cursor.fetchone()
    zapato = {'_id': row[0], 'marca': row[1], 'talla': row[2], 'color': row[3], 'cantidad': row[4]}
    return render_template_string(MODIFICAR_HTML, zapato=zapato)

@app.route('/vender/<int:id>', methods=['POST'])
def vender(id):
    cursor.execute("SELECT cantidad FROM zapatos WHERE id = %s", (id,))
    cantidad = cursor.fetchone()[0]
    if cantidad > 0:
        cursor.execute("UPDATE zapatos SET cantidad = cantidad - 1 WHERE id = %s", (id,))
        conn.commit()
    return redirect(url_for('inventario'))

# Esto es necesario para Vercel
app = app
