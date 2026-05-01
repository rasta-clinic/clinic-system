from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "rasta-secret"

# دیتابیس
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------- مدل کاربر --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# -------------------- مدل نوبت --------------------
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100))
    therapist_name = db.Column(db.String(100))
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    status = db.Column(db.String(20), default="booked")

# -------------------- ساخت دیتابیس و ادمین --------------------
with app.app_context():
    db.create_all()

    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", password="1234")
        db.session.add(admin)
        db.session.commit()

# -------------------- صفحات --------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            return redirect('/admin')

        return "Login Failed"

    return render_template('login.html')

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    appointments = Appointment.query.all()

    return render_template('admin_dashboard.html', appointments=appointments)

# ثبت نوبت
@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    if 'user_id' not in session:
        return redirect('/login')

    new_appointment = Appointment(
        patient_name=request.form['patient_name'],
        therapist_name=request.form['therapist_name'],
        date=request.form['date'],
        time=request.form['time']
    )

    db.session.add(new_appointment)
    db.session.commit()

    return redirect('/admin')

@app.route('/reception')
def reception_dashboard():
    return render_template('reception_dashboard.html')

@app.route('/therapist')
def therapist_dashboard():
    return render_template('therapist_dashboard.html')

@app.route('/appointments')
def appointments():
    return render_template('appointments.html')

@app.route('/patients')
def patients():
    return render_template('patients.html')

@app.route('/therapists')
def therapists():
    return render_template('therapists.html')
@app.route('/update_status/<int:id>/<string:new_status>')
def update_status(id, new_status):
    if 'user_id' not in session:
        return redirect('/login')

    appt = Appointment.query.get(id)

    if appt:
        appt.status = new_status
        db.session.commit()

    return redirect('/admin')
# -------------------- اجرا روی Render --------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
