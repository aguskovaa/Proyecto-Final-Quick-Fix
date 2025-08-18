from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuración de Firebase
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/browser')
def browser():
    # Verificar si el usuario está logueado y es cliente (tipo 1)
    if not session.get('is_logged_in'):
        flash('Debes iniciar sesión para acceder a esta página', 'warning')
        return redirect(url_for('home'))
    
    if session.get('user_type') != '1':
        flash('Esta función es solo para clientes', 'error')
        return redirect(url_for('home'))

    try:
        # Obtener profesionales disponibles de Firebase
        profesionales_ref = db.collection('trabajadores').where('disponible', '==', True).stream()
        
        profesionales = []
        for prof in profesionales_ref:
            prof_data = prof.to_dict()
            profesionales.append({
                'id': prof.id,
                'nombre': f"{prof_data.get('nombre', '')} {prof_data.get('apellido', '')}",
                'oficio': prof_data.get('oficio', 'Sin especificar'),
                'especialidad': prof_data.get('especialidad', ''),
                'valoracion': prof_data.get('valoracion', 0),
                'ubicacion': prof_data.get('ubicacion', ''),
                'foto': prof_data.get('foto_url', '/static/images/default-profile.png'),
                'tarifa': prof_data.get('tarifa', 'Consultar')
            })
            
    except Exception as e:
        print(f"Error al cargar profesionales: {str(e)}")
        flash('Error al cargar la lista de profesionales', 'error')
        profesionales = []
    
    return render_template('Browser.html', 
                         profesionales=profesionales,
                         user_name=session.get('user_name', 'Usuario'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)