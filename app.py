from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():

    conn = sqlite3.connect("clinic.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient TEXT,
        therapist TEXT,
        time TEXT,
        price TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():

    conn = sqlite3.connect("clinic.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM appointments")
    appointments = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        appointments=appointments
    )

@app.route("/add", methods=["POST"])
def add():

    patient = request.form["patient"]
    therapist = request.form["therapist"]
    time = request.form["time"]
    price = request.form["price"]

    conn = sqlite3.connect("clinic.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO appointments
    (patient, therapist, time, price)
    VALUES (?, ?, ?, ?)
    """, (patient, therapist, time, price))

    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
