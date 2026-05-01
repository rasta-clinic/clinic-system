from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = "rasta-secret-key"

# ---------------- DATABASE ----------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- USERS ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)

# ---------------- APPOINTMENTS ----------------
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    therapist_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="booked")

# ---------------- INIT DB ----------------
with app.app_context():
    db.create_all()

    if not User.query.filter_by(username="admin").first():
        db.session.add(User(username="admin", password="1234", role="admin"))

    if not User.query.filter_by(username="reception").first():
        db.session.add(User(username="reception", password="1234", role="reception"))

    for t in ["sara", "ali", "mina"]:
        if not User.query.filter_by(username=t).first():
            db.session.add(User(username=t, password="1234", role="therapist"))

    db.session.commit()

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()

        if user:
            session['user_id'] = user.id
            session['role'] = user.role

            if user.role == "admin":
                return redirect('/admin')
            if user.role == "reception":
                return redirect('/reception')
            if user.role == "therapist":
                return redirect('/therapist')

        return "Login Failed"

    return render_template('login.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- ADMIN ----------------
@app.route('/admin')
def admin_dashboard():
    if session.get('role') != "admin":
        return redirect('/login')

    return render_template(
        'admin_dashboard.html',
        appointments=Appointment.query.all(),
        therapists=User.query.filter_by(role="therapist").all()
    )

# ---------------- RECEPTION ----------------
@app.route('/reception')
def reception_dashboard():
    if session.get('role') != "reception":
        return redirect('/login')

    return render_template(
        'reception_dashboard.html',
        appointments=Appointment.query.all(),
        therapists=User.query.filter_by(role="therapist").all()
    )

# ---------------- THERAPIST ----------------
@app.route('/therapist')
def therapist_dashboard():

    if session.get('role') != "therapist":
        return redirect('/login')

    therapist_id = session.get('user_id')

    today = datetime.now().date().isoformat()

    today_appointments = Appointment.query.filter_by(
        therapist_id=therapist_id,
        date=today
    ).all()

    all_appointments = Appointment.query.filter_by(
        therapist_id=therapist_id
    ).order_by(Appointment.date).all()

    total = len(all_appointments)
    done = len([a for a in all_appointments if a.status == "done"])

    return render_template(
        'therapist_dashboard.html',
        today_appointments=today_appointments,
        all_appointments=all_appointments,
        total=total,
        done=done
    )

# ---------------- ADD APPOINTMENT ----------------
@app.route('/add_appointment', methods=['POST'])
def add_appointment():

    therapist_id = request.form['therapist_id']
    date = request.form['date']
    time = request.form['time']
    patient_name = request.form['patient_name']

    existing = Appointment.query.filter_by(
        therapist_id=therapist_id,
        date=date,
        time=time
    ).first()

    if existing:
        return "This slot is already booked"

    db.session.add(Appointment(
        patient_name=patient_name,
        therapist_id=therapist_id,
        date=date,
        time=time,
        status="booked"
    ))

    db.session.commit()
    return redirect('/admin')

# ---------------- DELETE ----------------
@app.route('/delete_appointment/<int:id>')
def delete_appointment(id):

    if session.get('role') not in ["admin", "reception"]:
        return redirect('/login')

    appt = Appointment.query.get(id)
    if appt:
        db.session.delete(appt)
        db.session.commit()

    return redirect('/admin' if session.get('role') == "admin" else '/reception')

# ---------------- STATUS UPDATE ----------------
@app.route('/update_status/<int:id>/<string:new_status>')
def update_status(id, new_status):

    if session.get('role') not in ["admin", "reception"]:
        return redirect('/login')

    appt = Appointment.query.get(id)
    if appt:
        appt.status = new_status
        db.session.commit()

    return redirect('/admin' if session.get('role') == "admin" else '/reception')

# ---------------- REPORTS ----------------
@app.route('/reports')
def reports():

    if session.get('role') != "admin":
        return redirect('/login')

    report = db.session.query(
        User.username,
        func.count(Appointment.id)
    ).join(Appointment, Appointment.therapist_id == User.id)\
     .group_by(User.username).all()

    return render_template('reports.html', report=report)

# ---------------- CALENDAR ----------------
@app.route('/calendar')
def calendar():

    if session.get('role') != "therapist":
        return redirect('/login')

    return render_template(
        'calendar.html',
        appointments=Appointment.query.filter_by(
            therapist_id=session.get('user_id')
        ).order_by(Appointment.date).all()
    )

# ---------------- WEEKLY ----------------
@app.route('/weekly-calendar')
def weekly_calendar():

    if session.get('role') != "therapist":
        return redirect('/login')

    return render_template(
        'weekly_calendar.html',
        appointments=Appointment.query.filter_by(
            therapist_id=session.get('user_id')
        ).all()
    )

# ---------------- QUICK BOOK ----------------
@app.route('/quick-book')
def quick_book():

    if not session.get('user_id'):
        return redirect('/login')

    day = request.args.get('day')
    time = request.args.get('time')

    existing = Appointment.query.filter_by(
        therapist_id=session['user_id'],
        date=day,
        time=time
    ).first()

    if existing:
        return "Already booked!"

    db.session.add(Appointment(
        patient_name="Walk-in",
        date=day,
        time=time,
        therapist_id=session['user_id'],
        status="booked"
    ))

    db.session.commit()
    return redirect('/weekly-calendar')

# ---------------- RUN ----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
