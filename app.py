
from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('clinic.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient TEXT,
        therapist TEXT,
        time TEXT,
        status TEXT,
        payment TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def dashboard():
    conn = sqlite3.connect('clinic.db')
    c = conn.cursor()
    c.execute("SELECT * FROM appointments")
    appointments = c.fetchall()
    conn.close()

    total = 0
    for a in appointments:
        try:
            total += int(a[5])
        except:
            pass

    return render_template('dashboard.html', appointments=appointments, total=total)

@app.route('/add', methods=['POST'])
def add():
    patient = request.form['patient']
    therapist = request.form['therapist']
    time = request.form['time']
    status = request.form['status']
    payment = request.form['payment']

    conn = sqlite3.connect('clinic.db')
    c = conn.cursor()

    c.execute(
        "INSERT INTO appointments (patient, therapist, time, status, payment) VALUES (?, ?, ?, ?, ?)",
        (patient, therapist, time, status, payment)
    )

    conn.commit()
    conn.close()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
