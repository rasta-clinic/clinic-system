from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "rasta-secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------- مدل کاربر --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# -------------------- ساخت ادمین اولیه --------------------
@app.before_first_request
def create_admin():
    db.create_all()

    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", password="1234")
        db.session.add(admin)
        db.session.commit()

# -------------------- صفحات ساده --------------------
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

    return render_template('admin_dashboard.html')

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

# -------------------- اجرا --------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
