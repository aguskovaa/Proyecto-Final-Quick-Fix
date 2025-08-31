from flask import Flask, render_template, redirect, url_for, session, flash, request, jsonify
import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

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

# Lista de especialidades predefinidas
ESPECIALIDADES_PREDEFINIDAS = [
    'Albañil', 'Carpintero', 'Cerrajero', 'Electricista', 
    'Fontanero/Plomero', 'Fumigador', 'Gasista matriculado', 
    'Herrero', 'Instalador de Redes/WiFi', 'Instalador de aires acondicionados',
    'Instalador de alarmas/cámaras de seguridad', 'Jardinero', 
    'Lavado de Alfombras/cortinas', 'Limpieza de tanques de agua',
    'Limpieza de vidrios en altura', 'Mantenimiento de piletas',
    'Paisajista', 'Personal de limpieza', 'Pintor', 
    'Podador de árboles', 'Techista/Impermeabilizador',
    'Técnico de Computadoras/laptops', 'Técnico de Televisores/equipos electrónicos',
    'Técnico de celulares', 'Técnico de electrodomésticos', 'Técnico de impresoras'
]

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
                session['user_id'] = docs[0].id
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
    
    solicitudes_pendientes = 0
    if session.get('user_type') == '2':
        try:
            trabajador_id = session.get('user_id')
            pendientes_ref = db.collection('PendClienteTrabajador')
            query = pendientes_ref.where('profesional_id', '==', trabajador_id).where('estado', '==', 'pendiente')
            docs = query.stream()
            solicitudes_pendientes = sum(1 for _ in docs)
        except Exception as e:
            print(f"Error al contar solicitudes pendientes: {str(e)}")
            solicitudes_pendientes = 0
    
    return render_template('Home.html', solicitudes_pendientes=solicitudes_pendientes)

@app.route('/browser')
def browser():
    if not session.get('is_logged_in'):
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != '1':
        flash('Solo los clientes pueden acceder', 'error')
        return redirect(url_for('home'))
    
    try:
        trabajadores_ref = db.collection('trabajadores')
        docs = trabajadores_ref.stream()
        
        profesionales = []
        for doc in docs:
            trabajador_data = doc.to_dict()
            trabajador_data['id'] = doc.id
            
            especialidades = []
            campos_especialidad = [
                'Albañil', 'Carpintero', 'Cerrajero', 'Electricista', 
                'Fontanero_Plomero', 'Fumigador', 'Gasista_matriculado', 
                'Herrero', 'InstaladorDeRedes_WiFi', 'Instalador_de_aires_acondicionados',
                'Instalador_de_alarmas_cámaras_de_seguridad', 'Jardinero', 
                'LavadoDeAlfombras_cortinas', 'Limpieza_de_tanques_de_agua',
                'Limpieza_de_vidrios_en_altura', 'Mantenimiento_de_piletas',
                'Paisajista', 'Personal_de_limpieza', 'Pintor', 
                'Podador_de_árboles', 'Techista_Impermeabilizador',
                'TécnicoDeComputadoras_laptops', 'TécnicoDeTelevisores_equiposelectrónicos',
                'Técnico_de_celulares', 'Técnico_de_electrodomésticos', 'Técnico_de_impresoras'
            ]
            
            for especialidad in campos_especialidad:
                if trabajador_data.get(especialidad) == True:
                    nombre_bonito = especialidad.replace('_', ' ').replace('De', ' de').title()
                    especialidades.append(nombre_bonito)
            
            if not especialidades:
                especialidades = ["Servicios generales"]
            
            trabajador_data['especialidades'] = especialidades
            trabajador_data['especialidad_principal'] = especialidades[0] if especialidades else "Servicios generales"
            
            if 'nombre' not in trabajador_data:
                trabajador_data['nombre'] = 'Nombre no disponible'
            if 'apellido' not in trabajador_data:
                trabajador_data['apellido'] = ''
            if 'rating' not in trabajador_data:
                trabajador_data['rating'] = 0
            if 'reseñas' not in trabajador_data:
                trabajador_data['reseñas'] = 0
            if 'ubicacion' not in trabajador_data:
                trabajador_data['ubicacion'] = 'Ubicación no disponible'
            if 'precio' not in trabajador_data:
                trabajador_data['precio'] = 'Consultar'
            
            profesionales.append(trabajador_data)
            
    except Exception as e:
        print(f"Error al obtener trabajadores: {str(e)}")
        profesionales = []
        flash('Error al cargar los profesionales', 'error')
    
    return render_template('Browser.html', profesionales=profesionales)

@app.route('/trabajos')
def trabajos():
    if not session.get('is_logged_in'):
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != '2':
        flash('Solo los trabajadores pueden acceder a esta página', 'error')
        return redirect(url_for('home'))
    
    try:
        trabajador_id = session.get('user_id')
        pendientes_ref = db.collection('PendClienteTrabajador')
        query = pendientes_ref.where('profesional_id', '==', trabajador_id).where('estado', '==', 'pendiente')
        docs = query.stream()
        
        trabajos_pendientes = []
        for doc in docs:
            trabajo_data = doc.to_dict()
            trabajo_data['id'] = doc.id
            trabajos_pendientes.append(trabajo_data)
            
        return render_template('AceptarTrabajos.html', trabajos=trabajos_pendientes)
        
    except Exception as e:
        print(f"Error al obtener trabajos pendientes: {str(e)}")
        flash('Error al cargar los trabajos pendientes', 'error')
        return render_template('AceptarTrabajos.html', trabajos=[])

@app.route('/mis_solicitudes')
def mis_solicitudes():
    if not session.get('is_logged_in'):
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != '1':
        flash('Solo los clientes pueden acceder a esta página', 'error')
        return redirect(url_for('home'))
    
    try:
        cliente_id = session.get('user_id')
        solicitudes_ref = db.collection('PendClienteTrabajador')
        query = solicitudes_ref.where('cliente_id', '==', cliente_id)
        docs = query.stream()
        
        solicitudes = []
        for doc in docs:
            solicitud_data = doc.to_dict()
            solicitud_data['id'] = doc.id
            solicitudes.append(solicitud_data)
            
        solicitudes_pendientes = [s for s in solicitudes if s.get('estado') == 'pendiente']
        solicitudes_aceptadas = [s for s in solicitudes if s.get('estado') == 'aceptado']
        solicitudes_rechazadas = [s for s in solicitudes if s.get('estado') == 'rechazado']
        solicitudes_devueltas = [s for s in solicitudes if s.get('estado') == 'devuelto']
        
        return render_template('MisSolicitudes.html', 
                             solicitudes_pendientes=solicitudes_pendientes,
                             solicitudes_aceptadas=solicitudes_aceptadas,
                             solicitudes_rechazadas=solicitudes_rechazadas,
                             solicitudes_devueltas=solicitudes_devueltas,
                             especialidades_predefinidas=ESPECIALIDADES_PREDEFINIDAS)
        
    except Exception as e:
        print(f"Error al obtener solicitudes: {str(e)}")
        flash('Error al cargar tus solicitudes', 'error')
        return render_template('MisSolicitudes.html', 
                             solicitudes_pendientes=[],
                             solicitudes_aceptadas=[],
                             solicitudes_rechazadas=[],
                             solicitudes_devueltas=[],
                             especialidades_predefinidas=ESPECIALIDADES_PREDEFINIDAS)

@app.route('/aceptar_trabajo/<trabajo_id>', methods=['POST'])
def aceptar_trabajo(trabajo_id):
    if not session.get('is_logged_in') or session.get('user_type') != '2':
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        trabajo_ref = db.collection('PendClienteTrabajador').document(trabajo_id)
        trabajo_ref.update({
            'estado': 'aceptado',
            'fecha_actualizacion': datetime.now()
        })
        
        return jsonify({'success': True, 'message': 'Trabajo aceptado con éxito'})
        
    except Exception as e:
        print(f"Error al aceptar trabajo: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al procesar la solicitud'})

@app.route('/rechazar_trabajo/<trabajo_id>', methods=['POST'])
def rechazar_trabajo(trabajo_id):
    if not session.get('is_logged_in') or session.get('user_type') != '2':
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        trabajo_ref = db.collection('PendClienteTrabajador').document(trabajo_id)
        trabajo_ref.update({
            'estado': 'rechazado',
            'fecha_actualizacion': datetime.now()
        })
        
        return jsonify({'success': True, 'message': 'Trabajo rechazado'})
        
    except Exception as e:
        print(f"Error al rechazar trabajo: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al procesar la solicitud'})

@app.route('/devolver_trabajo/<trabajo_id>', methods=['POST'])
def devolver_trabajo(trabajo_id):
    if not session.get('is_logged_in') or session.get('user_type') != '2':
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        data = request.get_json()
        especificaciones_trabajador = data.get('especificaciones', '')
        
        if not especificaciones_trabajador:
            return jsonify({'success': False, 'message': 'Debe proporcionar especificaciones'})
        
        trabajo_ref = db.collection('PendClienteTrabajador').document(trabajo_id)
        trabajo_ref.update({
            'estado': 'devuelto',
            'especificaciones_trabajador': especificaciones_trabajador,
            'fecha_actualizacion': datetime.now()
        })
        
        return jsonify({'success': True, 'message': 'Trabajo devuelto con especificaciones'})
        
    except Exception as e:
        print(f"Error al devolver trabajo: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al procesar la solicitud'})

@app.route('/reenviar_solicitud/<solicitud_id>', methods=['POST'])
def reenviar_solicitud(solicitud_id):
    if not session.get('is_logged_in') or session.get('user_type') != '1':
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        data = request.get_json()
        
        especializacion = data.get('especializacion', '')
        fecha_trabajo = data.get('fechaTrabajo', '')
        especificaciones = data.get('especificaciones', '')
        metodo_pago = data.get('metodoPago', '')
        ubicacion = data.get('ubicacion', '')
        
        if not all([especializacion, fecha_trabajo, especificaciones, metodo_pago, ubicacion]):
            return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'})
        
        solicitud_ref = db.collection('PendClienteTrabajador').document(solicitud_id)
        solicitud = solicitud_ref.get()
        
        if not solicitud.exists:
            return jsonify({'success': False, 'message': 'Solicitud no encontrada'})
        
        solicitud_data = solicitud.to_dict()
        
        solicitud_ref.update({
            'especializacion': especializacion,
            'fecha_trabajo_propuesta': fecha_trabajo,
            'especificaciones': especificaciones,
            'metodo_pago': metodo_pago,
            'ubicacion': ubicacion,
            'estado': 'pendiente',
            'fecha_actualizacion': datetime.now(),
            'reenviada': True,
            'fecha_reenvio': datetime.now(),
            'especificaciones_originales': solicitud_data.get('especificaciones', ''),
            'especificaciones_trabajador': ''
        })
        
        return jsonify({
            'success': True, 
            'message': 'Solicitud reenviada con éxito'
        })
        
    except Exception as e:
        print(f"Error al reenviar solicitud: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al reenviar la solicitud'})

@app.route('/procesar_contratacion', methods=['POST'])
def procesar_contratacion():
    if not session.get('is_logged_in'):
        return jsonify({'success': False, 'message': 'Debes iniciar sesión primero'})
    
    if session.get('user_type') != '1':
        return jsonify({'success': False, 'message': 'Solo los clientes pueden contratar servicios'})
    
    try:
        data = request.get_json()
        
        profesional_id = data.get('profesionalId')
        especializacion = data.get('especializacion', '')
        fecha_trabajo = data.get('fechaTrabajo')
        especificaciones = data.get('especificaciones')
        metodo_pago = data.get('metodoPago')
        ubicacion = data.get('ubicacion')
        
        if not all([profesional_id, fecha_trabajo, especificaciones, metodo_pago, ubicacion]):
            return jsonify({'success': False, 'message': 'Faltan campos obligatorios'})
        
        cliente_id = session.get('user_id')
        cliente_nombre = session.get('user_name', 'Cliente')
        
        doc_ref = db.collection('trabajadores').document(profesional_id)
        profesional_doc = doc_ref.get()
        
        if not profesional_doc.exists:
            return jsonify({'success': False, 'message': 'Profesional no encontrado'})
        
        profesional_data = profesional_doc.to_dict()
        profesional_nombre = f"{profesional_data.get('nombre', '')} {profesional_data.get('apellido', '')}".strip()
        
        contratacion_data = {
            'cliente_id': cliente_id,
            'cliente_nombre': cliente_nombre,
            'profesional_id': profesional_id,
            'profesional_nombre': profesional_nombre,
            'especializacion': especializacion,
            'fecha_trabajo_propuesta': fecha_trabajo,
            'especificaciones': especificaciones,
            'metodo_pago': metodo_pago,
            'ubicacion': ubicacion,
            'estado': 'pendiente',
            'fecha_solicitud': datetime.now(),
            'fecha_actualizacion': datetime.now()
        }
        
        pendientes_ref = db.collection('PendClienteTrabajador')
        nueva_contratacion = pendientes_ref.add(contratacion_data)
        
        return jsonify({
            'success': True, 
            'message': 'Solicitud enviada con éxito. El profesional será notificado.',
            'contratacion_id': nueva_contratacion[1].id
        })
        
    except Exception as e:
        print(f"Error al procesar contratación: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al procesar la solicitud'})

@app.route('/obtener_solicitud/<solicitud_id>')
def obtener_solicitud(solicitud_id):
    try:
        solicitud_ref = db.collection('PendClienteTrabajador').document(solicitud_id)
        solicitud = solicitud_ref.get()
        
        if solicitud.exists:
            return jsonify(solicitud.to_dict())
        else:
            return jsonify({'error': 'Solicitud no encontrada'}), 404
            
    except Exception as e:
        print(f"Error al obtener solicitud: {str(e)}")
        return jsonify({'error': 'Error del servidor'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)