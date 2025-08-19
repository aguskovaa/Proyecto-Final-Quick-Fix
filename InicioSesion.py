from flask import Flask, render_template, redirect, url_for, session, flash, request
import os
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuración Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

ROLES_MAPPING = {
    'cliente': 'clientes',
    'trabajador': 'trabajadores',
    'desempleado': 'desempleados'
}

USER_TYPE_MAPPING = {
    'cliente': '1',
    'trabajador': '2',
    'desempleado': '3'
}

@app.route('/')
def index():
    return render_template('Inicio_de_Sesion.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('username', '').strip().lower()
        password = request.form.get('contra', '').strip()
        role_form = request.form.get('rol', '').strip()

        if not all([email, password, role_form]):
            return render_template('Inicio_de_Sesion.html', 
                                error="Por favor, completá todos los campos.",
                                color="red")

        try:
            firebase_collection = ROLES_MAPPING[role_form]
            users_ref = db.collection(firebase_collection)
            query = users_ref.where("mail", "==", email).where("contra", "==", password).limit(1)
            docs = query.get()

            if docs:
                usuario = docs[0].to_dict()
                session['is_logged_in'] = True
                session['user_name'] = usuario.get('nombre', 'Usuario')
                session['user_type'] = USER_TYPE_MAPPING[role_form]
                return redirect(url_for('home'))
            else:
                return render_template('Inicio_de_Sesion.html',
                                    error="Usuario o contraseña incorrectos.",
                                    color="red")
        except Exception as e:
            print(f"Error: {str(e)}")
            return render_template('Inicio_de_Sesion.html',
                                error="Error en el servidor. Intente nuevamente.",
                                color="red")
    return render_template('Inicio_de_Sesion.html')

@app.route('/home')
def home():
    if not session.get('is_logged_in'):
        return redirect(url_for('login'))
    return render_template('Home.html')

@app.route('/browser')
def browser():
    if not session.get('is_logged_in'):
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != '1':
        flash('Solo los clientes pueden acceder', 'error')
        return redirect(url_for('home'))
    
    profesionales = [
        {"nombre": "Juan Pérez", "especialidad": "Plomería", "rating": 4.5},
        {"nombre": "María López", "especialidad": "Electricista", "rating": 5.0}
    ]
    return render_template('Browser.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)