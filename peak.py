import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from flask_httpauth import HTTPBasicAuth
import sqlite3
import pytz

app = Flask(__name__)
auth = HTTPBasicAuth()

# Configuración de Telegram
TOKEN_TELEGRAM = '7464790504:AAH4wfKlAAseOwE8bZ0rsJFDyAl0dZgMCqU'
CHAT_ID = ['1021374007']

# Variables globales para rastrear el estado
last_status = "Online"
last_alert_time = datetime.min

# Reemplaza con tu usuario y contraseña deseados
USER_DATA = {
    "admin": "password"
}

@auth.verify_password
def verify(username, password):
    if username in USER_DATA and USER_DATA[username] == password:
        return username

def init_db():
    conn = sqlite3.connect('credentials.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS credentials (id TEXT PRIMARY KEY, name TEXT, valid BOOLEAN, expiration_date DATE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS monitor_history (timestamp TEXT, status TEXT)''')
    conn.commit()
    conn.close()

def send_telegram_message(token, chat_ids, text):
    for chat_id in chat_ids:
        url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}"
        requests.get(url).json()

@app.route('/verify/<id>', methods=['GET'])
def verify_credential(id):
    from datetime import date

    conn = sqlite3.connect('credentials.db')
    c = conn.cursor()
    c.execute('SELECT name, valid, expiration_date FROM credentials WHERE id = ?', (id,))
    result = c.fetchone()
    conn.close()

    if result is None:
        return render_template('verification.html', status="invalid", name=None)
    else:
        name, valid, expiration_date = result
        if expiration_date is not None and expiration_date < date.today().isoformat():
            valid = 0
        status = "ACTIVO" if valid else "INACTIVO"
        status_class = "active" if valid else "inactive"
        return render_template('verification.html', status=status, name=name, status_class=status_class)

@app.route('/')
@auth.login_required
def admin():
    conn = sqlite3.connect('credentials.db')
    c = conn.cursor()
    c.execute('SELECT id, name, valid, expiration_date FROM credentials')
    users = c.fetchall()
    conn.close()

    return render_template('admin.html', users=users)

@app.route('/add_user', methods=['POST'])
@auth.login_required
def add_user():
    id = request.form['id']
    name = request.form['name']
    valid = request.form.get('valid') == 'on'
    expiration_date = request.form['expiration_date']

    conn = sqlite3.connect('credentials.db')
    c = conn.cursor()
    c.execute('INSERT INTO credentials (id, name, valid, expiration_date) VALUES (?, ?, ?, ?)', (id, name, valid, expiration_date))
    conn.commit()
    conn.close()

    return jsonify({'status': 'user added'})

@app.route('/update_status', methods=['POST'])
@auth.login_required
def update_status():
    data = request.get_json()
    id = data.get('id')
    new_status = data.get('valid')

    conn = sqlite3.connect('credentials.db')
    c = conn.cursor()
    c.execute('UPDATE credentials SET valid = ? WHERE id = ?', (new_status, id))
    conn.commit()
    conn.close()

    return jsonify({'status': 'updated'})

@app.route('/update_expiration', methods=['POST'])
@auth.login_required
def update_expiration():
    data = request.get_json()
    id = data.get('id')
    expiration_date = data.get('expiration_date')

    conn = sqlite3.connect('credentials.db')
    c = conn.cursor()
    c.execute('UPDATE credentials SET expiration_date = ? WHERE id = ?', (expiration_date, id))
    conn.commit()
    conn.close()

    return jsonify({'status': 'expiration date updated'})

@app.route('/delete_user', methods=['POST'])
@auth.login_required
def delete_user():
    data = request.get_json()
    id = data.get('id')

    conn = sqlite3.connect('credentials.db')
    c = conn.cursor()
    c.execute('DELETE FROM credentials WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({'status': 'user deleted'})

# Endpoints para monitoreo
@app.route('/monitor')
def monitor():
    return render_template('monitor.html')

@app.route('/check_status', methods=['GET'])
def check_status():
    global last_status, last_alert_time

    try:
        response = requests.get('https://www.secomext.com.mx/acsis_login.html', timeout=5)
        if response.status_code == 200:
            status = 'Online'
        else:
            status = 'Offline'
    except requests.exceptions.RequestException:
        status = 'Offline'
    
    # Convertir a UTC-6 (America/Mexico_City)
    local_tz = pytz.timezone('America/Mexico_City')
    timestamp = datetime.now(local_tz).strftime('%Y-%m-%d %H:%M:%S')

    # Insertar en la base de datos
    conn = sqlite3.connect('credentials.db')
    c = conn.cursor()
    c.execute('INSERT INTO monitor_history (timestamp, status) VALUES (?, ?)', (timestamp, status))
    conn.commit()
    conn.close()

    # Enviar notificaciones de Telegram
    current_time = datetime.now(local_tz)
    if status == 'Offline' and last_status == 'Online':
        send_telegram_message(TOKEN_TELEGRAM, CHAT_ID, "Alerta: El EVS y Portal Web está caído.")
        last_alert_time = current_time
    elif status == 'Offline' and (current_time - last_alert_time) >= timedelta(minutes=15):
        send_telegram_message(TOKEN_TELEGRAM, CHAT_ID, "El EVS y Portal Web continúa caído.")
        last_alert_time = current_time
    elif status == 'Online' and last_status == 'Offline':
        send_telegram_message(TOKEN_TELEGRAM, CHAT_ID, "El EVS y Portal Web operan con normalidad.")
    
    last_status = status

    return jsonify({
        'status': status,
        'timestamp': timestamp
    })

@app.route('/get_history', methods=['GET'])
def get_history():
    conn = sqlite3.connect('credentials.db')
    c = conn.cursor()
    c.execute('SELECT timestamp, status FROM monitor_history ORDER BY timestamp DESC LIMIT 200')
    history = c.fetchall()
    conn.close()

    history_data = [{'timestamp': row[0], 'status': row[1]} for row in reversed(history)]
    return jsonify(history_data)

@app.route('/test')
def test():
    return jsonify({'message': 'success'})

if __name__ == '__main__':
    init_db()
    app.run()