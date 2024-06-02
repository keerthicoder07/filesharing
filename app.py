from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:Hmylon4DF2uU@ep-hidden-thunder-a5749kcq-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '0207'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filedata = db.Column(db.LargeBinary, nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    print(f"Request method: {request.method}")  
    if request.method == 'POST':
        print(f"Form data: {request.form}")  
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Username: {username}, Password: {password}")

        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        files = File.query.all()
        return render_template('dashboard.html', username=session['username'], files=files)
    else:
        return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' in session:
        if request.method == 'POST':
            file = request.files['file']
            if file:
                filename = file.filename
                filedata = file.read()
                
                new_file = File(filename=filename, filedata=filedata)
                db.session.add(new_file)
                db.session.commit()

                return redirect(url_for('dashboard'))
        return render_template('upload.html')
    else:
        return redirect(url_for('login'))

@app.route('/download/<int:file_id>')
def download(file_id):
    if 'username' in session:
        file = File.query.get(file_id)

        if file:
            print(f"File found: {file.filename}")  # Debugging statement
            return send_file(
                io.BytesIO(file.filedata),
                download_name=file.filename,
                as_attachment=True
            )
        else:
            return "File not found", 404
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/test_db')
def test_db():
    try:
        user = User.query.first()
        return "Database connection is successful!"
    except Exception as e:
        return f"Database connection failed: {e}"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
