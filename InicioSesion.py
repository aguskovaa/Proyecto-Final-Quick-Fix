from flask import Flask, render_template, request
import os
import firebase_admin
from firebase_admin import credentials, firestore

# Configuración CORRECTA de Flask
app = Flask(__name__)  # Elimina template_folder personalizado

# Inicializar Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Actualiza los roles para que coincidan con el HTML
ROLES_MAPPING = {
    'cliente': 'clientes',
    'trabajador': 'trabajadores',
    'desempleado': 'desempleados'
}

@app.route('/')
def index():
    return render_template('Inicio_de_Sesion.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('username', '').strip().lower()
    password = request.form.get('contra', '').strip()
    role_form = request.form.get('rol', '').strip()

    # Validación actualizada
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
            return render_template('Inicio_de_Sesion.html',
                                success=f"¡Bienvenido, {nombre}!",
                                color="green")
        else:
            return render_template('Inicio_de_Sesion.html',
                                error="Usuario o contraseña incorrectos.",
                                color="red")
    except Exception as e:
        print(f"Error: {str(e)}")
        return render_template('Inicio_de_Sesion.html',
                            error="Error en el servidor. Intente nuevamente.",
                            color="red")

if __name__ == '__main__':
    app.run(debug=True)