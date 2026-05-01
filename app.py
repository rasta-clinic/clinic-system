from flask import Flask, render_template

app = Flask(__name__)

# صفحه اصلی
@app.route('/')
def home():
    return render_template('index.html')

# صفحه ورود
@app.route('/login')
def login():
    return render_template('login.html')

# پنل مدیر
@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# پنل پذیرش
@app.route('/reception')
def reception_dashboard():
    return render_template('reception_dashboard.html')

# پنل درمانگر
@app.route('/therapist')
def therapist_dashboard():
    return render_template('therapist_dashboard.html')

# صفحه نوبت‌ها
@app.route('/appointments')
def appointments():
    return render_template('appointments.html')

# صفحه مراجعین
@app.route('/patients')
def patients():
    return render_template('patients.html')

# صفحه درمانگران
@app.route('/therapists')
def therapists():
    return render_template('therapists.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
