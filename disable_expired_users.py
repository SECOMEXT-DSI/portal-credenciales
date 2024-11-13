import sqlite3
from datetime import date

def disable_expired_users():
    conn = sqlite3.connect('/home/edzon_alanis/flask_app/credentials.db')
    c = conn.cursor()
    today = date.today().isoformat()
    c.execute('UPDATE credentials SET valid = 0 WHERE expiration_date < ? AND expiration_date IS NOT NULL', (today,))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    disable_expired_users()