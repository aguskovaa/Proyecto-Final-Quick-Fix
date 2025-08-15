from flask import Flask, render_template, request, redirect, url_for, session
import os
import firebase_admin
from firebase_admin import credentials, firestore

@app.route('/browser')
def ClHoLista():
    # Verificar si el usuario está logueado y es cliente (user_type == '1')
    if not session.get('is_logged_in') or session.get('user_type') != '1':
        return redirect(url_for('index'))  # Redirige al login si no cumple los requisitos
    
    # Aquí puedes agregar lógica adicional si necesitas cargar datos para la página
    # Por ejemplo, obtener lista de profesionales desde Firebase
    try:
        profesionales_ref = db.collection('trabajadores').stream()
        profesionales = [prof.to_dict() for prof in profesionales_ref]
    except Exception as e:
        print(f"Error al obtener profesionales: {str(e)}")
        profesionales = []
    
    return render_template('browser.html', profesionales=profesionales)