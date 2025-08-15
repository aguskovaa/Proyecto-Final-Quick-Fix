from flask import Flask, render_template, request, redirect, url_for, session
import os
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Inicializar Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Mapeo de roles
ROLES_MAPPING = {
    'cliente': 'clientes',
    'trabajador': 'trabajadores',
    'desempleado': 'desempleados'
}

# Mapeo para userType (como en tu JS)
USER_TYPE_MAPPING = {
    'cliente': '1',
    'trabajador': '2',
    'desempleado': '3'
}

@app.route('/')
def index():
    return render_template('Inicio_de_Sesion.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('username', '').strip().lower()
    password = request.form.get('contra', '').strip()
    role_form = request.form.get('rol', '').strip()

    if not email or not password or not role_form:
        return render_template('Inicio_de_Sesion.html', 
                            error="Por favor, completá todos los campos.",
                            color="red")

    if role_form not in ROLES_MAPPING:
        return render_template('Inicio_de_Sesion.html',
                            error="Rol inválido seleccionado.",
                            color="red")

    try:
        firebase_collection = ROLES_MAPPING[role_form]
        users_ref = db.collection(firebase_collection)
        query = users_ref.where("mail", "==", email).where("contra", "==", password).limit(1)
        docs = query.get()

        if docs:
            usuario = docs[0].to_dict()
            nombre = usuario.get('nombre', 'Usuario')
            
            session['user_type'] = USER_TYPE_MAPPING[role_form]
            session['is_logged_in'] = True
            session['user_name'] = nombre
            
            # Redirigir a Home.html (como en tu JS)
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

@app.route('/home')
def home():
    # Verificar si el usuario está logueado
    if not session.get('is_logged_in'):
        return redirect(url_for('index'))
    
    return render_template('Home.html', 
                         user_name=session.get('user_name', 'Usuario'))

if __name__ == '__main__':
    app.run(debug=True)