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

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(120),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

# ---------------- APPOINTMENTS ----------------

class Appointment(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    patient_name = db.Column(
        db.String(100),
        nullable=False
    )

    patient_phone = db.Column(db.String(20))

    therapist_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    date = db.Column(
        db.String(20),
        nullable=False
    )

    time = db.Column(
        db.String(20),
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="رزرو اولیه"
    )

    # رزرو اولیه / قطعی / انجام شد / کنسل شد

    session_fee = db.Column(
        db.Integer,
        default=0
    )

    paid_amount = db.Column(
        db.Integer,
        default=0
    )

    payment_status = db.Column(
        db.String(30),
        default="پرداخت نشده"
    )

    tracking_code = db.Column(
        db.String(50)
    )

    payment_method = db.Column(
        db.String(50)
    )

    payment_date = db.Column(
        db.String(30)
    )

    payment_time = db.Column(
        db.String(30)
    )

    notes = db.Column(db.Text)

# ---------------- INIT DB ----------------

with app.app_context():

    db.create_all()

    # مدیر

    if not User.query.filter_by(
        username="admin"
    ).first():

        db.session.add(
            User(
                username="admin",
                password="1234",
                role="admin"
            )
        )

    # پذیرش

    if not User.query.filter_by(
        username="reception"
    ).first():

        db.session.add(
            User(
                username="reception",
                password="1234",
                role="reception"
            )
        )

    # درمانگرها

    therapists = [
        "sara",
        "ali",
        "mina"
    ]

    for t in therapists:

        if not User.query.filter_by(
            username=t
        ).first():

            db.session.add(
                User(
                    username=t,
                    password="1234",
                    role="therapist"
                )
            )

    db.session.commit()

# ---------------- LOGIN ----------------

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])

def login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            session['user_id'] = user.id
            session['role'] = user.role

            if user.role == "admin":
                return redirect('/admin')

            elif user.role == "reception":
                return redirect('/reception')

            elif user.role == "therapist":
                return redirect('/therapist')

        return "ورود ناموفق"

    return render_template('login.html')

# ---------------- LOGOUT ----------------

@app.route('/logout')

def logout():

    session.clear()

    return redirect('/login')

# ---------------- ADMIN DASHBOARD ----------------

@app.route('/admin')

def admin_dashboard():

    if session.get('role') != "admin":
        return redirect('/login')

    appointments = Appointment.query.order_by(
        Appointment.date
    ).all()

    therapists = User.query.filter_by(
        role="therapist"
    ).all()

    return render_template(
        'admin_dashboard.html',
        appointments=appointments,
        therapists=therapists
    )

# ---------------- RECEPTION DASHBOARD ----------------

@app.route('/reception')

def reception_dashboard():

    if session.get('role') != "reception":
        return redirect('/login')

    appointments = Appointment.query.order_by(
        Appointment.date
    ).all()

    therapists = User.query.filter_by(
        role="therapist"
    ).all()

    return render_template(
        'reception_dashboard.html',
        appointments=appointments,
        therapists=therapists
    )

# ---------------- THERAPIST DASHBOARD ----------------
@app.route('/therapist')
def therapist_dashboard():

    if session.get('role') != "therapist":
        return redirect('/login')

    therapist_id = session['user_id']

    all_appointments = Appointment.query.filter_by(
        therapist_id=therapist_id
    ).order_by(Appointment.date).all()

    today_date = datetime.now()

    today = today_date.strftime("%Y-%m-%d")
    tomorrow = (today_date.replace(day=today_date.day + 1)).strftime("%Y-%m-%d")

    next_week_dates = []
    for i in range(2, 8):
        next_day = today_date.replace(day=today_date.day + i)
        next_week_dates.append(next_day.strftime("%Y-%m-%d"))

    today_appointments = Appointment.query.filter_by(
        therapist_id=therapist_id,
        date=today
    ).all()

    tomorrow_appointments = Appointment.query.filter_by(
        therapist_id=therapist_id,
        date=tomorrow
    ).all()

    next_week_appointments = Appointment.query.filter(
        Appointment.therapist_id == therapist_id,
        Appointment.date.in_(next_week_dates)
    ).all()

    total = len(all_appointments)

    done = Appointment.query.filter_by(
        therapist_id=therapist_id,
        status="انجام شد"
    ).count()

    return render_template(
        'therapist_dashboard.html',
        all_appointments=all_appointments,
        today_appointments=today_appointments,
        tomorrow_appointments=tomorrow_appointments,
        next_week_appointments=next_week_appointments,
        total=total,
        done=done
    )

# ---------------- ADD APPOINTMENT ----------------

@app.route('/add_appointment', methods=['POST'])

def add_appointment():

    patient_name = request.form['patient_name']

    therapist_id = request.form['therapist_id']

    date = request.form['date']

    time = request.form['time']

    payment_amount = request.form.get(
        'payment_amount',
        0
    )

    payment_status = request.form.get(
        'payment_status',
        'پرداخت نشده'
    )

    payment_method = request.form.get(
        'payment_method',
        ''
    )

    tracking_code = request.form.get(
        'tracking_code',
        ''
    )

    payment_date = datetime.now().strftime(
        "%Y-%m-%d"
    )

    payment_time = datetime.now().strftime(
        "%H:%M"
    )

    existing = Appointment.query.filter_by(
        therapist_id=therapist_id,
        date=date,
        time=time
    ).first()

    if existing:
        return "این زمان قبلاً رزرو شده است"

    new_appointment = Appointment(

        patient_name=patient_name,

        therapist_id=therapist_id,

        date=date,

        time=time,

        status="رزرو اولیه",

        paid_amount=payment_amount,

        payment_status=payment_status,

        payment_method=payment_method,

        tracking_code=tracking_code,

        payment_date=payment_date,

        payment_time=payment_time

    )

    db.session.add(new_appointment)

    db.session.commit()

    if session.get('role') == "admin":
        return redirect('/admin')

    return redirect('/reception')

# ---------------- DELETE APPOINTMENT ----------------

@app.route('/delete_appointment/<int:id>')

def delete_appointment(id):

    if session.get('role') not in [
        "admin",
        "reception"
    ]:
        return redirect('/login')

    appointment = Appointment.query.get(id)

    if appointment:

        db.session.delete(appointment)

        db.session.commit()

    if session.get('role') == "admin":
        return redirect('/admin')

    return redirect('/reception')

# ---------------- UPDATE STATUS ----------------

@app.route('/update_status/<int:id>/<string:new_status>')

def update_status(id, new_status):

    if session.get('role') not in [
        "admin",
        "reception"
    ]:
        return redirect('/login')

    appointment = Appointment.query.get(id)

    if appointment:

        appointment.status = new_status

        db.session.commit()

    if session.get('role') == "admin":
        return redirect('/admin')

    return redirect('/reception')

# ---------------- REPORTS ----------------

@app.route('/reports')

def reports():

    if session.get('role') != "admin":
        return redirect('/login')

    report = db.session.query(
        User.username,
        func.count(Appointment.id)
    ).join(
        Appointment,
        Appointment.therapist_id == User.id
    ).group_by(
        User.username
    ).all()

    return render_template(
        'reports.html',
        report=report
    )

# ---------------- MONTHLY CALENDAR ----------------

@app.route('/calendar')

def calendar():

    if session.get('role') != "therapist":
        return redirect('/login')

    therapist_id = session['user_id']

    appointments = Appointment.query.filter_by(
        therapist_id=therapist_id
    ).order_by(
        Appointment.date
    ).all()

    return render_template(
        'calendar.html',
        appointments=appointments
    )

# ---------------- WEEKLY CALENDAR ----------------

@app.route('/weekly-calendar')

def weekly_calendar():

    if session.get('role') != "therapist":
        return redirect('/login')

    therapist_id = session['user_id']

    appointments = Appointment.query.filter_by(
        therapist_id=therapist_id
    ).order_by(
        Appointment.date
    ).all()

    return render_template(
        'weekly_calendar.html',
        appointments=appointments
    )

# ---------------- QUICK BOOK ----------------

@app.route('/quick-book')

def quick_book():

    if session.get('role') != "therapist":
        return redirect('/login')

    therapist_id = session['user_id']

    day = request.args.get('day')

    time = request.args.get('time')

    existing = Appointment.query.filter_by(
        therapist_id=therapist_id,
        date=day,
        time=time
    ).first()

    if existing:
        return "این زمان قبلاً رزرو شده"

    new_appointment = Appointment(

        patient_name="مراجع حضوری",

        therapist_id=therapist_id,

        date=day,

        time=time,

        status="رزرو اولیه"

    )

    db.session.add(new_appointment)

    db.session.commit()

    return redirect('/weekly-calendar')
def to_persian(value):
    digits = "0123456789"
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    return str(value).translate(str.maketrans(digits, persian_digits))

app.jinja_env.filters['to_persian'] = to_persian
# ---------------- RUN ----------------

if __name__ == '__main__':

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host='0.0.0.0',
        port=port
    )
