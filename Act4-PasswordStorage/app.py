from flask import Flask, request, redirect, url_for, render_template, session, flash, g
import sqlite3
import env
import os

app = Flask(__name__)
ph = env.passHasher()


# * FUNCIONES DE AYUDA
def generate_salt():
  return os.urandom(16)

def hash_password(password, salt):
  pepper = env.pepperStr()
  password_peppered = password.encode() + pepper
  return ph.hash(password=password_peppered, salt=salt)



# * RUSTAS DE LA APLICACION
@app.route('/')
def index():
  return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    db = get_db()
    username = request.form['username']
    password = request.form['password']
    salt = generate_salt()
    password_hash = hash_password(password, salt)

    # print("\n\n//////////////////////////////////////////////////////////////////")
    # print(f'Valores de la Actuales del registro (Nombre): {password}')
    # print(f'Valores de la Actuales del registro (PassHash): {password_hash}')
    # print(f'Valores de la Actuales del registro (Salt): {salt}')
    # print("//////////////////////////////////////////////////////////////////\n\n")

    db.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", (username, password_hash, salt))
    db.commit()
    return redirect(url_for('login'))
  
  # SE RENDERIZA LA VISTA
  return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    db = get_db()
    username = request.form['username']
    password = request.form['password']
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    if user:
      currentPasswordHashed = hash_password(password, user[3]) 
      
      # print("\n\n//////////////////////////////////////////////////////////////////")
      # print(f'PassGenerado en el momento: {currentPasswordHashed}')
      # print(f'Pass de la BD: {user[2]}')
      # print("\n------------------------------------------------------------------\n")
      # print(f'Valores de la db (id): {user[0]}')
      # print(f'Valores de la db (Nombre): {user[1]}')
      # print(f'Valores de la db (PassHash): {user[2]}')
      # print(f'Valores de la db (Salt): {user[3]}')
      # print("//////////////////////////////////////////////////////////////////\n\n")

      # if ph.verify(user[2], currentPasswordHashed):
      if user[2] == currentPasswordHashed:
        session['user_id'] = user[0]
        # print("Es aqi")
        return redirect(url_for('dashboard'))
      else:
        # print("Es aki")
        flash('Incorrect username or password')
    else:
      # print("Es aca")
      flash('This user dont exists')

  # SE RENDERIZA LA VISTA
  return render_template('login.html')


@app.route('/dashboard')
def dashboard():
  if 'user_id' in session:
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()

    # SE RENDERIZA LA VISTA
    return render_template('dashboard.html', username=user[1])
  return redirect(url_for('login'))



# * CREACION DE LA BASE DE DATOS
def get_db():
  if 'db' not in g:
      g.db = sqlite3.connect('password.db')
      g.db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT, salt TEXT)')
      g.db.commit()
  return g.db


@app.teardown_appcontext
def close_db(error):
  db = g.pop('db', None)
  if db is not None:
    db.close()



# * MAIN
if __name__ == '__main__':
  app.secret_key = os.urandom(16)
  app.run(debug=True)