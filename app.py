from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret123'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'mp4', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    query = request.args.get('q')
    with sqlite3.connect("edudocs.db") as con:
        if query:
            docs = con.execute("SELECT filename, description, category FROM documents WHERE filename LIKE ? OR description LIKE ? OR category LIKE ?", 
                               ('%'+query+'%', '%'+query+'%', '%'+query+'%')).fetchall()
        else:
            docs = con.execute("SELECT filename, description, category FROM documents").fetchall()
    return render_template("index.html", documents=docs, query=query)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        description = request.form['description']
        category = request.form['category']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            with sqlite3.connect("edudocs.db") as con:
                con.execute("INSERT INTO documents (filename, description, category) VALUES (?, ?, ?)",
                            (filename, description, category))
            return redirect(url_for('index'))

    return render_template("upload.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['admin'] = True
            return redirect(url_for('upload_file'))
        else:
            return 'Invalid credentials. <a href="/login">Try again</a>'
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

