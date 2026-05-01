from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "rasta-secret-key"

# دیتابیس
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- USERS ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin / reception / therapist

# ---------------- APPOINTMENTS ----------------
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    therapist_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="booked")

# ---------------- DATABASE SETUP ----------------
with app.app_context():
    db.create_all()

    # ادمین اصلی
    if not User.query.filter_by(username="admin").first():
        db.session.add(User(username="admin", password="1234", role="admin"))

    # پذیرش
    if not User.query.filter_by(username="reception").first():
        db.session.add(User(username="reception", password="1234", role="reception"))

    # نمونه درمانگرها
    therapists = ["sara", "ali", "mina"]
    for t in therapists:
        if not User.query.filter_by(username=t).first():
            db.session.add(User(username=t, password="1234", role="therapist"))

    db.session.commit()

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            session['role'] = user.role

            if user.role == "admin":
                return redirect('/admin')

            elif user.role == "reception":
                return redirect('/reception')

            elif user.role == "therapist":
                return redirect('/therapist')

        return "Login Failed"

    return render_template('login.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- ADMIN PANEL ----------------
@app.route('/admin')
def admin_dashboard():
    if session.get('role') != "admin":
        return redirect('/login')

    appointments = Appointment.query.all()
    therapists = User.query.filter_by(role="therapist").all()

    return render_template(
        'admin_dashboard.html',
        appointments=appointments,
        therapists=therapists
    )

# ---------------- RECEPTION PANEL ----------------
@app.route('/reception')
def reception_dashboard():
    if session.get('role') != "reception":
        return redirect('/login')

    appointments = Appointment.query.all()
    therapists = User.query.filter_by(role="therapist").all()

    return render_template(
        'reception_dashboard.html',
        appointments=appointments,
        therapists=therapists
    )

# ---------------- THERAPIST PANEL ----------------
@app.route('/therapist')
def therapist_dashboard():
    if session.get('role') != "therapist":
        return redirect('/login')

    therapist_id = session['user_id']

    appointments = Appointment.query.filter_by(
        therapist_id=therapist_id
    ).all()

    return render_template(
        'therapist_dashboard.html',
        appointments=appointments
    )

# ---------------- ADD APPOINTMENT ----------------
@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    if session.get('role') not in ["admin", "reception"]:
        return redirect('/login')

    new_appointment = Appointment(
        patient_name=request.form['patient_name'],
        therapist_id=request.form['therapist_id'],
        date=request.form['date'],
        time=request.form['time'],
        status="booked"
    )

    db.session.add(new_appointment)
    db.session.commit()

    if session.get('role') == "admin":
        return redirect('/admin')

    return redirect('/reception')

# ---------------- DELETE ----------------
@app.route('/delete_appointment/<int:id>')
def delete_appointment(id):
    if session.get('role') not in ["admin", "reception"]:
        return redirect('/login')

    appt = Appointment.query.get(id)

    if appt:
        db.session.delete(appt)
        db.session.commit()

    if session.get('role') == "admin":
        return redirect('/admin')

    return redirect('/reception')

# ---------------- STATUS ----------------
@app.route('/update_status/<int:id>/<string:new_status>')
def update_status(id, new_status):
    if session.get('role') not in ["admin", "reception"]:
        return redirect('/login')

    appt = Appointment.query.get(id)

    if appt:
        appt.status = new_status
        db.session.commit()

    if session.get('role') == "admin":
        return redirect('/admin')

    return redirect('/reception')

# ---------------- RUN ----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
