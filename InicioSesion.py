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

@app.route('/chat_home')
def chat_home():
    if not session.get('is_logged_in'):
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    
    try:
        user_id = session.get('user_id')
        user_name = session.get('user_name')
        user_type = session.get('user_type')
        
        # Convertir user_type numérico a string para el chat
        user_type_str = {
            '1': 'cliente',
            '2': 'trabajador', 
            '3': 'desempleado'
        }.get(user_type, 'usuario')
        
        # Obtener conversaciones REALES de la base de datos
        conversaciones = obtener_conversaciones_reales(user_id)
        total_no_leidos = sum(conv.get('no_leidos', 0) for conv in conversaciones)
        
        # Guardar en sesión para el badge del botón
        session['total_mensajes_no_leidos'] = total_no_leidos
        
        # Verificar si se solicita una conversación específica
        conversacion_activa = request.args.get('conversacion')
        es_ajax = request.args.get('ajax')
        
        if conversacion_activa:
            # Cargar datos de la conversación activa
            return cargar_conversacion_activa(conversacion_activa, user_id, user_name, 
                                            user_type, conversaciones, user_type_str, es_ajax)
        
        # Si es AJAX sin conversación, retornar solo el panel de chat vacío
        if es_ajax:
            return render_template('chat_panel_empty.html')
        
        # Vista normal - lista de chats
        return render_template('chat_home.html', 
                             conversaciones=conversaciones,
                             user_name=user_name,
                             user_type=user_type_str,
                             total_no_leidos=total_no_leidos,
                             conversacion_activa=None)
        
    except Exception as e:
        print(f"Error en chat_home: {str(e)}")
        flash('Error al cargar los chats', 'error')
        return render_template('chat_home.html', 
                             conversaciones=[], 
                             error=str(e))

def obtener_conversaciones_reales(user_id):
    """Obtener conversaciones reales de la base de datos"""
    try:
        conversaciones = []
        
        # Buscar conversaciones donde el usuario sea participante
        conversaciones_ref = db.collection('conversaciones')
        query = conversaciones_ref.where('participantes', 'array_contains', user_id)
        docs = query.stream()
        
        for doc in docs:
            conv_data = doc.to_dict()
            conv_data['id'] = doc.id
            
            # Contar mensajes no leídos
            no_leidos = contar_mensajes_no_leidos_reales(doc.id, user_id)
            conv_data['no_leidos'] = no_leidos
            
            # Obtener info del otro usuario
            otros_participantes = [p for p in conv_data.get('participantes', []) if p != user_id]
            if otros_participantes:
                otro_usuario_id = otros_participantes[0]
                conv_data['otro_usuario_id'] = otro_usuario_id
                
                # Buscar en todas las colecciones de usuarios
                otro_usuario_info = obtener_info_usuario(otro_usuario_id)
                conv_data['otro_usuario_nombre'] = otro_usuario_info.get('nombre', 'Usuario')
                conv_data['otro_usuario_tipo'] = otro_usuario_info.get('tipo', 'usuario')
            else:
                conv_data['otro_usuario_nombre'] = 'Usuario'
                conv_data['otro_usuario_tipo'] = 'usuario'
            
            conversaciones.append(conv_data)
        
        # Ordenar por último mensaje (más reciente primero)
        conversaciones.sort(key=lambda x: x.get('ultimo_timestamp', datetime.min), reverse=True)
        
        return conversaciones
        
    except Exception as e:
        print(f"Error obteniendo conversaciones reales: {str(e)}")
        return []

def contar_mensajes_no_leidos_reales(conversacion_id, usuario_id):
    """Contar mensajes no leídos reales"""
    try:
        mensajes_ref = db.collection('mensajes')
        query = mensajes_ref.where('conversacion_id', '==', conversacion_id)
        docs = query.stream()
        
        no_leidos = 0
        for doc in docs:
            mensaje_data = doc.to_dict()
            if (mensaje_data.get('emisor_id') != usuario_id and 
                not mensaje_data.get('leido', False)):
                no_leidos += 1
        
        return no_leidos
    except Exception as e:
        print(f"Error contando mensajes no leídos: {str(e)}")
        return 0

def obtener_info_usuario(usuario_id):
    """Obtener información de un usuario desde cualquier colección"""
    try:
        # Buscar en todas las colecciones posibles
        colecciones = ['clientes', 'trabajadores', 'desempleados']
        
        for coleccion in colecciones:
            usuario_ref = db.collection(coleccion).document(usuario_id)
            usuario_doc = usuario_ref.get()
            if usuario_doc.exists:
                usuario_data = usuario_doc.to_dict()
                return {
                    'nombre': usuario_data.get('nombre', 'Usuario'),
                    'tipo': coleccion[:-1]  # Remover la 's' final (clientes -> cliente)
                }
        
        return {'nombre': 'Usuario', 'tipo': 'usuario'}
    except Exception as e:
        print(f"Error obteniendo info usuario: {str(e)}")
        return {'nombre': 'Usuario', 'tipo': 'usuario'}

@app.route('/muro_publicaciones')
def muro_publicaciones():
    if not session.get('is_logged_in'):
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    
    try:
        user_type = session.get('user_type')
        
        # Obtener solo las publicaciones DISPONIBLES (no las que están en proceso)
        muro_ref = db.collection('MuroPublicaciones')
        query = muro_ref.where('estado', '==', 'disponible')  # SOLO LAS DISPONIBLES
        docs = query.stream()
        
        publicaciones = []
        for doc in docs:
            pub_data = doc.to_dict()
            pub_data['id'] = doc.id
            pub_data['fecha_publicacion_str'] = pub_data.get('fecha_publicacion').strftime('%d/%m/%Y %H:%M') if pub_data.get('fecha_publicacion') else 'Fecha no disponible'
            publicaciones.append(pub_data)
        
        # Ordenar por fecha más reciente
        publicaciones.sort(key=lambda x: x.get('fecha_publicacion', datetime.min), reverse=True)
        
        return render_template('muro.html', 
                             publicaciones=publicaciones,
                             user_type=user_type,
                             user_id=session.get('user_id'))
        
    except Exception as e:
        print(f"Error al cargar el muro: {str(e)}")
        flash('Error al cargar el muro de publicaciones', 'error')
        return render_template('muro.html', publicaciones=[], user_type=session.get('user_type'))

@app.route('/publicar_trabajo', methods=['POST'])
def publicar_trabajo():
    if not session.get('is_logged_in') or session.get('user_type') != '1':
        return jsonify({'success': False, 'message': 'Solo los clientes pueden publicar trabajos'})
    
    try:
        data = request.get_json()
        
        titulo = data.get('titulo')
        descripcion = data.get('descripcion')
        categoria = data.get('categoria')
        ubicacion = data.get('ubicacion')
        presupuesto = data.get('presupuesto')
        fecha_limite = data.get('fecha_limite')
        
        if not all([titulo, descripcion, categoria, ubicacion]):
            return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'})
        
        # Crear publicación
        publicacion_data = {
            'cliente_id': session.get('user_id'),
            'cliente_nombre': session.get('user_name', 'Cliente'),
            'titulo': titulo,
            'descripcion': descripcion,
            'categoria': categoria,
            'ubicacion': ubicacion,
            'presupuesto': presupuesto,
            'fecha_limite': fecha_limite,
            'fecha_publicacion': datetime.now(),
            'estado': 'disponible',
            'tipo': 'publicacion_muro'
        }
        
        muro_ref = db.collection('MuroPublicaciones')
        nueva_publicacion = muro_ref.add(publicacion_data)
        
        return jsonify({
            'success': True, 
            'message': 'Trabajo publicado exitosamente en el muro',
            'publicacion_id': nueva_publicacion[1].id
        })
        
    except Exception as e:
        print(f"Error al publicar trabajo: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al publicar el trabajo'})

@app.route('/aceptar_trabajo_muro/<publicacion_id>', methods=['POST'])
def aceptar_trabajo_muro(publicacion_id):
    if not session.get('is_logged_in') or session.get('user_type') != '2':
        return jsonify({'success': False, 'message': 'Solo los trabajadores pueden aceptar trabajos'})
    
    try:
        # Obtener datos de la publicación
        pub_ref = db.collection('MuroPublicaciones').document(publicacion_id)
        publicacion = pub_ref.get()
        
        if not publicacion.exists:
            return jsonify({'success': False, 'message': 'Publicación no encontrada'})
        
        publicacion_data = publicacion.to_dict()
        
        # Crear solicitud de trabajo directamente ACEPTADA
        trabajo_data = {
            'cliente_id': publicacion_data.get('cliente_id'),
            'cliente_nombre': publicacion_data.get('cliente_nombre'),
            'profesional_id': session.get('user_id'),
            'profesional_nombre': session.get('user_name', 'Trabajador'),
            'titulo': publicacion_data.get('titulo'),
            'especializacion': publicacion_data.get('categoria'),
            'descripcion': publicacion_data.get('descripcion'),
            'categoria': publicacion_data.get('categoria'),
            'ubicacion': publicacion_data.get('ubicacion'),
            'presupuesto': publicacion_data.get('presupuesto'),
            'fecha_trabajo_propuesta': publicacion_data.get('fecha_limite'),
            'especificaciones': publicacion_data.get('descripcion'),
            'metodo_pago': 'efectivo',  # Valor por defecto para trabajos del muro
            'estado': 'aceptado',  # ✅ DIRECTAMENTE ACEPTADO
            'fecha_solicitud': datetime.now(),
            'fecha_actualizacion': datetime.now(),
            'origen': 'muro',
            'aceptado_directamente': True  # Marcar que fue aceptado directamente del muro
        }
        
        # Guardar en PendClienteTrabajador
        pendientes_ref = db.collection('PendClienteTrabajador')
        nuevo_trabajo = pendientes_ref.add(trabajo_data)
        
        # Marcar publicación como "aceptado" (desaparecerá del muro)
        pub_ref.update({
            'estado': 'aceptado',
            'trabajador_asignado_id': session.get('user_id'),
            'trabajador_asignado_nombre': session.get('user_name', 'Trabajador'),
            'fecha_asignacion': datetime.now(),
            'trabajo_id': nuevo_trabajo[1].id  # Guardar referencia al trabajo creado
        })
        
        return jsonify({
            'success': True, 
            'message': 'Trabajo aceptado exitosamente. Ya aparece en tus trabajos pendientes.',
            'trabajo_id': nuevo_trabajo[1].id
        })
        
    except Exception as e:
        print(f"Error al aceptar trabajo del muro: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al aceptar el trabajo'})
    
# Función auxiliar para obtener usuarios
def obtener_usuarios_para_chat(usuario_actual_id, usuario_actual_tipo):
    """Obtener usuarios disponibles para chatear"""
    try:
        # Por ahora retornar lista vacía
        return []
    except Exception as e:
        print(f"Error obteniendo usuarios: {str(e)}")
        return []

# Ruta simple para probar
@app.route('/api/crear_conversacion', methods=['POST'])
def crear_conversacion():
    if not session.get('is_logged_in'):
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        data = request.get_json()
        otro_usuario_id = data.get('otro_usuario_id')
        
        # Por ahora, solo simular una respuesta
        conversacion_id = f"chat_{session.get('user_id')}_{otro_usuario_id}"
        
        return jsonify({
            'success': True, 
            'conversacion_id': conversacion_id, 
            'existe': False
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al crear conversación'})


# ✅ AGREGAR ESTA FUNCIÓN NUEVA:
def cargar_conversacion_activa(conversacion_id, user_id, user_name, user_type, 
                              conversaciones, user_type_str, es_ajax):
    """Cargar datos de una conversación específica"""
    try:
        # Verificar que el usuario tiene acceso a esta conversación
        conversacion_ref = db.collection('conversaciones').document(conversacion_id)
        conversacion_doc = conversacion_ref.get()
        
        if not conversacion_doc.exists:
            if es_ajax:
                return "<div class='error-message'>Conversación no encontrada</div>"
            flash('Conversación no encontrada', 'error')
            return redirect(url_for('chat_home'))
        
        conversacion_data = conversacion_doc.to_dict()
        
        if user_id not in conversacion_data.get('participantes', []):
            if es_ajax:
                return "<div class='error-message'>No tienes acceso a esta conversación</div>"
            flash('No tienes acceso a esta conversación', 'error')
            return redirect(url_for('chat_home'))
        
        # Obtener info del otro usuario
        otros_participantes = [p for p in conversacion_data['participantes'] if p != user_id]
        otro_usuario_id = otros_participantes[0] if otros_participantes else None
        otro_usuario_nombre = "Usuario"
        otro_usuario_tipo = "usuario"
        otro_usuario_email = None
        
        if otro_usuario_id:
            otro_usuario_info = obtener_info_usuario_completa(otro_usuario_id)
            otro_usuario_nombre = otro_usuario_info.get('nombre', 'Usuario')
            otro_usuario_tipo = otro_usuario_info.get('tipo', 'usuario')
            otro_usuario_email = otro_usuario_info.get('email')
        
        # Obtener mensajes de la conversación
        mensajes = obtener_mensajes_conversacion(conversacion_id)
        
        # Si es AJAX, retornar solo el panel del chat
        if es_ajax:
            return render_template('chat_panel.html',
                                 conversacion_activa=conversacion_id,
                                 otro_usuario_nombre=otro_usuario_nombre,
                                 otro_usuario_tipo=otro_usuario_tipo,
                                 otro_usuario_email=otro_usuario_email,
                                 mensajes=mensajes,
                                 user_id=user_id,
                                 user_name=user_name,
                                 user_type=user_type)
        
        # Vista completa
        return render_template('chat_home.html',
                             conversaciones=conversaciones,
                             user_name=user_name,
                             user_type=user_type_str,
                             conversacion_activa=conversacion_id,
                             otro_usuario_nombre=otro_usuario_nombre,
                             otro_usuario_tipo=otro_usuario_tipo,
                             otro_usuario_email=otro_usuario_email,
                             mensajes=mensajes,
                             user_id=user_id)
        
    except Exception as e:
        print(f"Error cargando conversación activa: {str(e)}")
        if es_ajax:
            return f"<div class='error-message'>Error: {str(e)}</div>"
        flash('Error al cargar la conversación', 'error')
        return redirect(url_for('chat_home'))
    

# ✅ AGREGAR ESTA FUNCIÓN NUEVA:
def obtener_mensajes_conversacion(conversacion_id):
    """Obtener mensajes de una conversación"""
    try:
        mensajes = []
        mensajes_ref = db.collection('mensajes')
        query = mensajes_ref.where('conversacion_id', '==', conversacion_id)
        docs = query.stream()
        
        for doc in docs:
            msg_data = doc.to_dict()
            msg_data['id'] = doc.id
            
            # Formatear timestamp
            if 'timestamp' in msg_data:
                if hasattr(msg_data['timestamp'], 'strftime'):
                    msg_data['timestamp_str'] = msg_data['timestamp'].strftime('%H:%M')
                else:
                    try:
                        dt = datetime.fromisoformat(msg_data['timestamp'].replace('Z', '+00:00'))
                        msg_data['timestamp_str'] = dt.strftime('%H:%M')
                    except:
                        msg_data['timestamp_str'] = '--:--'
            else:
                msg_data['timestamp_str'] = '--:--'
            
            mensajes.append(msg_data)
        
        # Ordenar mensajes por timestamp
        mensajes.sort(key=lambda x: x.get('timestamp', datetime.min))
        
        return mensajes
        
    except Exception as e:
        print(f"No se pudieron cargar los mensajes: {str(e)}")
        return []
# ✅ AGREGAR ESTA FUNCIÓN NUEVA:
def obtener_info_usuario_completa(usuario_id):
    """Obtener información completa de un usuario"""
    try:
        colecciones = ['clientes', 'trabajadores', 'desempleados']
        
        for coleccion in colecciones:
            usuario_ref = db.collection(coleccion).document(usuario_id)
            usuario_doc = usuario_ref.get()
            if usuario_doc.exists:
                usuario_data = usuario_doc.to_dict()
                return {
                    'nombre': usuario_data.get('nombre', 'Usuario'),
                    'tipo': coleccion[:-1],  # Remover la 's' final
                    'email': usuario_data.get('mail')
                }
        
        return {'nombre': 'Usuario', 'tipo': 'usuario', 'email': None}
    except Exception as e:
        print(f"Error obteniendo info usuario completa: {str(e)}")
        return {'nombre': 'Usuario', 'tipo': 'usuario', 'email': None}
# Ruta para una conversación específica
# ⚠️ REEMPLAZAR ESTA FUNCIÓN COMPLETA:
@app.route('/chat/<conversacion_id>')
def chat_conversacion(conversacion_id):
    # Redirigir a la nueva versión unificada
    return redirect(url_for('chat_home', conversacion=conversacion_id))

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
            
            # Contar SOLICITUDES DE CLIENTES pendientes
            pendientes_ref = db.collection('PendClienteTrabajador')
            query_clientes = pendientes_ref.where('profesional_id', '==', trabajador_id).where('estado', '==', 'pendiente')
            docs_clientes = query_clientes.stream()
            count_clientes = sum(1 for _ in docs_clientes)
            
            # Contar SOLICITUDES DE MENTORÍA pendientes
            mentorias_ref = db.collection('Mentorias')
            query_mentorias = mentorias_ref.where('mentor_id', '==', trabajador_id).where('estado', '==', 'pendiente')
            docs_mentorias = query_mentorias.stream()
            count_mentorias = sum(1 for _ in docs_mentorias)
            
            # Sumar ambos tipos
            solicitudes_pendientes = count_clientes + count_mentorias
            
            # (Opcional) Guardar los conteos separados si los necesitas después)
            session['solicitudes_clientes'] = count_clientes
            session['solicitudes_mentorias'] = count_mentorias
            
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

@app.route('/actualizar_progreso/<mentoria_id>', methods=['POST'])
def actualizar_progreso(mentoria_id):
    if not session.get('is_logged_in') or session.get('user_type') != '3':
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        data = request.get_json()
        progreso = data.get('progreso')
        
        if progreso is None or not (0 <= progreso <= 100):
            return jsonify({'success': False, 'message': 'Progreso inválido'})
        
        mentoria_ref = db.collection('Mentorias').document(mentoria_id)
        mentoria_ref.update({
            'progreso': progreso,
            'fecha_actualizacion': datetime.now()
        })
        
        return jsonify({'success': True, 'message': 'Progreso actualizado correctamente'})
        
    except Exception as e:
        print(f"Error al actualizar progreso: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al actualizar el progreso'})

@app.route('/finalizar_mentoria/<mentoria_id>', methods=['POST'])
def finalizar_mentoria(mentoria_id):
    if not session.get('is_logged_in') or session.get('user_type') != '2':
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        mentoria_ref = db.collection('Mentorias').document(mentoria_id)
        mentoria_ref.update({
            'estado': 'completada',
            'fecha_actualizacion': datetime.now(),
            'completado_por': 'mentor',
            'fecha_completacion': datetime.now()
        })
        
        return jsonify({'success': True, 'message': 'Mentoría marcada como completada'})
        
    except Exception as e:
        print(f"Error al finalizar mentoría: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al procesar la solicitud'})

@app.route('/calificar_mentor/<mentoria_id>', methods=['POST'])
def calificar_mentor(mentoria_id):
    if not session.get('is_logged_in') or session.get('user_type') != '3':
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        data = request.get_json()
        calificacion = data.get('calificacion')
        mentor_id = data.get('mentorId')
        
        if not calificacion or not (1 <= calificacion <= 5):
            return jsonify({'success': False, 'message': 'Calificación inválida'})
        
        # Actualizar la mentoría con la calificación
        mentoria_ref = db.collection('Mentorias').document(mentoria_id)
        mentoria_ref.update({
            'calificacion': calificacion,
            'fecha_calificacion': datetime.now()
        })
        
        # Aquí podrías también actualizar el rating del mentor en su perfil
        # trabajador_ref = db.collection('trabajadores').document(mentor_id)
        # ... lógica para actualizar rating del mentor ...
        
        return jsonify({'success': True, 'message': 'Calificación enviada correctamente'})
        
    except Exception as e:
        print(f"Error al calificar mentor: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al enviar la calificación'})

@app.route('/capacitaciones')
def capacitaciones():
    if not session.get('is_logged_in'):
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != '3':  # 3 = desempleado
        flash('Solo los desempleados pueden acceder a capacitaciones', 'error')
        return redirect(url_for('home'))
    
    try:
        desempleado_id = session.get('user_id')
        
        # Obtener MENTORÍAS ACEPTADAS (activas)
        mentorias_ref = db.collection('Mentorias')
        query_activas = mentorias_ref.where('desempleado_id', '==', desempleado_id).where('estado', '==', 'aceptado')
        docs_activas = query_activas.stream()
        
        mentorias_activas = []
        for doc in docs_activas:
            mentoria_data = doc.to_dict()
            mentoria_data['id'] = doc.id
            mentoria_data['tipo'] = 'activa'
            mentorias_activas.append(mentoria_data)
        
        # Obtener MENTORÍAS COMPLETADAS (ya sea por mentor o por aprendiz)
        query_completadas = mentorias_ref.where('desempleado_id', '==', desempleado_id).where('estado', '==', 'completada')
        docs_completadas = query_completadas.stream()
        
        mentorias_completadas = []
        for doc in docs_completadas:
            mentoria_data = doc.to_dict()
            mentoria_data['id'] = doc.id
            mentoria_data['tipo'] = 'completada'
            
            # Agregar información sobre quién completó la mentoría
            if 'completado_por' in mentoria_data:
                mentoria_data['completado_por'] = mentoria_data['completado_por']
            else:
                mentoria_data['completado_por'] = 'sistema'
                
            mentorias_completadas.append(mentoria_data)
        
        return render_template('Capacitaciones.html', 
                             mentorias_activas=mentorias_activas,
                             mentorias_completadas=mentorias_completadas)
        
    except Exception as e:
        print(f"Error al obtener capacitaciones: {str(e)}")
        flash('Error al cargar las capacitaciones', 'error')
        return render_template('Capacitaciones.html', 
                             mentorias_activas=[],
                             mentorias_completadas=[])



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
        
        # SOLICITUDES DE TRABAJO PENDIENTES (clientes)
        pendientes_ref = db.collection('PendClienteTrabajador')
        query_trabajos = pendientes_ref.where('profesional_id', '==', trabajador_id).where('estado', '==', 'pendiente')
        docs_trabajos = query_trabajos.stream()
        
        trabajos_pendientes = []
        for doc in docs_trabajos:
            trabajo_data = doc.to_dict()
            trabajo_data['id'] = doc.id
            trabajo_data['tipo'] = 'contratacion'
            trabajos_pendientes.append(trabajo_data)
        
        # SOLICITUDES DE MENTORÍA PENDIENTES (desempleados)
        mentorias_ref = db.collection('Mentorias')
        query_mentorias = mentorias_ref.where('mentor_id', '==', trabajador_id).where('estado', '==', 'pendiente')
        docs_mentorias = query_mentorias.stream()
        
        mentorias_pendientes = []
        for doc in docs_mentorias:
            mentoria_data = doc.to_dict()
            mentoria_data['id'] = doc.id
            mentoria_data['tipo'] = 'mentoria'
            mentorias_pendientes.append(mentoria_data)
        
        # Combinar ambas listas
        todas_las_solicitudes = trabajos_pendientes + mentorias_pendientes
            
        return render_template('AceptarTrabajos.html', 
                             trabajos=todas_las_solicitudes,
                             trabajos_contrataciones=trabajos_pendientes,
                             trabajos_mentorias=mentorias_pendientes)
        
    except Exception as e:
        print(f"Error al obtener trabajos pendientes: {str(e)}")
        flash('Error al cargar los trabajos pendientes', 'error')
        return render_template('AceptarTrabajos.html', 
                             trabajos=[],
                             trabajos_contrataciones=[],
                             trabajos_mentorias=[])

@app.route('/mis_solicitudes')
def mis_solicitudes():
    try:
        # SOLICITUDES PENDIENTES (excluyendo las del muro que fueron aceptadas directamente)
        solicitudes_pendientes = []
        docs_pendientes = db.collection('PendClienteTrabajador').where('estado', '==', 'pendiente').stream()
        
        for doc in docs_pendientes:
            data = doc.to_dict()
            data['documento_id'] = doc.id
            # Solo incluir si no es una aceptación directa del muro
            if not data.get('aceptado_directamente'):
                solicitudes_pendientes.append(data)

        # SOLICITUDES ACEPTADAS (incluyendo las del muro)
        solicitudes_aceptadas = []
        docs_aceptados = db.collection('PendClienteTrabajador').where('estado', '==', 'aceptado').stream()
        
        for doc in docs_aceptados:
            data = doc.to_dict()
            data['documento_id'] = doc.id
            # Incluir tanto trabajos normales como del muro
            solicitudes_aceptadas.append(data)

        # ... (el resto del código de la función se mantiene igual)
        # SOLICITUDES DEVUELTAS
        solicitudes_devueltas = []
        docs_devueltos = db.collection('PendClienteTrabajador').where('estado', '==', 'devuelto').stream()
        
        for doc in docs_devueltos:
            data = doc.to_dict()
            data['documento_id'] = doc.id
            solicitudes_devueltas.append(data)

        # SOLICITUDES RECHAZADAS
        solicitudes_rechazadas = []
        docs_rechazados = db.collection('PendClienteTrabajador').where('estado', '==', 'rechazado').stream()
        
        for doc in docs_rechazados:
            data = doc.to_dict()
            data['documento_id'] = doc.id
            solicitudes_rechazadas.append(data)

        # SOLICITUDES FINALIZADAS (de TrabajosFinalizados)
        solicitudes_finalizadas = []
        docs_finalizados = db.collection('TrabajosFinalizados').stream()
        
        for doc in docs_finalizados:
            data = doc.to_dict()
            data['documento_id'] = doc.id
            solicitudes_finalizadas.append(data)

        # SOLICITUDES CANCELADAS (de TrabajosCancelados)
        solicitudes_canceladas = []
        docs_cancelados = db.collection('TrabajosCancelados').stream()
        
        for doc in docs_cancelados:
            data = doc.to_dict()
            data['documento_id'] = doc.id
            solicitudes_canceladas.append(data)

        # Obtener especialidades predefinidas
        especialidades_predefinidas = [
            "Fontanero Pionero", 
            "Electricista", 
            "Carpintero", 
            "Pintor", 
            "Albañil",
            "Técnico en climatización",
            "Jardinero",
            "Técnico en electrodomésticos"
        ]

        return render_template('MisSolicitudes.html',
                             solicitudes_pendientes=solicitudes_pendientes,
                             solicitudes_aceptadas=solicitudes_aceptadas,
                             solicitudes_devueltas=solicitudes_devueltas,
                             solicitudes_rechazadas=solicitudes_rechazadas,
                             solicitudes_finalizadas=solicitudes_finalizadas,
                             solicitudes_canceladas=solicitudes_canceladas,
                             especialidades_predefinidas=especialidades_predefinidas)

    except Exception as e:
        print(f"Error al obtener solicitudes: {e}")
        return render_template('MisSolicitudes.html',
                             solicitudes_pendientes=[],
                             solicitudes_aceptadas=[],
                             solicitudes_devueltas=[],
                             solicitudes_rechazadas=[],
                             solicitudes_finalizadas=[],
                             solicitudes_canceladas=[],
                             especialidades_predefinidas=[])

        
   

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

@app.route('/api/enviar_mensaje', methods=['POST'])
def enviar_mensaje():
    if not session.get('is_logged_in'):
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        data = request.get_json()
        conversacion_id = data.get('conversacion_id')
        contenido = data.get('contenido')
        
        if not all([conversacion_id, contenido]):
            return jsonify({'success': False, 'message': 'Faltan datos'})
        
        user_id = session.get('user_id')
        user_name = session.get('user_name')
        
        # Crear mensaje
        mensaje_data = {
            'conversacion_id': conversacion_id,
            'emisor_id': user_id,
            'emisor_nombre': user_name,
            'contenido': contenido.strip(),
            'timestamp': datetime.now(),
            'leido': False,
            'tipo': 'texto'
        }
        
        # Guardar en Firebase
        mensajes_ref = db.collection('mensajes')
        nuevo_mensaje = mensajes_ref.add(mensaje_data)
        
        # Actualizar conversación
        conversacion_ref = db.collection('conversaciones').document(conversacion_id)
        conversacion_ref.update({
            'ultimo_mensaje': contenido[:50] + '...' if len(contenido) > 50 else contenido,
            'ultimo_timestamp': datetime.now(),
            'ultimo_emisor': user_name
        })
        
        # Obtener timestamp formateado
        now = datetime.now()
        timestamp_str = now.strftime('%H:%M')
        
        return jsonify({
            'success': True, 
            'mensaje_id': nuevo_mensaje[1].id,
            'timestamp': timestamp_str
        })
        
    except Exception as e:
        print(f"Error enviando mensaje: {str(e)}")
        return jsonify({'success': False, 'message': 'Error del servidor'})

@app.route('/api/marcar_leidos', methods=['POST'])
def marcar_mensajes_leidos():
    if not session.get('is_logged_in'):
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        data = request.get_json()
        conversacion_id = data.get('conversacion_id')
        user_id = session.get('user_id')
        
        # Marcar mensajes como leídos
        mensajes_ref = db.collection('mensajes')
        query = mensajes_ref.where('conversacion_id', '==', conversacion_id)\
                          .where('leido', '==', False)\
                          .where('emisor_id', '!=', user_id)
        docs = query.stream()
        
        batch = db.batch()
        mensajes_actualizados = 0
        
        for doc in docs:
            mensaje_ref = mensajes_ref.document(doc.id)
            batch.update(mensaje_ref, {'leido': True})
            mensajes_actualizados += 1
        
        if mensajes_actualizados > 0:
            batch.commit()
        
        return jsonify({
            'success': True, 
            'mensajes_actualizados': mensajes_actualizados
        })
        
    except Exception as e:
        print(f"Error marcando mensajes como leídos: {str(e)}")
        return jsonify({'success': False, 'message': 'Error del servidor'})

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
        # Obtener la solicitud
        doc_ref = db.collection('PendClienteTrabajador').document(solicitud_id)
        doc = doc_ref.get()
        
        if doc.exists:
            solicitud_data = doc.to_dict()
            solicitud_data['documento_id'] = doc.id  # ← Agregar ID del documento
            
            # Obtener las especialidades del trabajador
            trabajador_id = solicitud_data.get('profesional_id')
            especialidades_trabajador = []
            
            if trabajador_id:
                # Buscar el trabajador en la colección de trabajadores
                trabajador_ref = db.collection('trabajadores').document(trabajador_id)
                trabajador_doc = trabajador_ref.get()
                
                if trabajador_doc.exists:
                    trabajador_data = trabajador_doc.to_dict()
                    
                    # ✅ CORREGIDO: Obtener especialidades como lo haces en /browser
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
                            especialidades_trabajador.append(nombre_bonito)
                    
                    if not especialidades_trabajador:
                        especialidades_trabajador = ["Servicios generales"]
            
            # ✅ CORREGIDO: Usar el nombre correcto de la propiedad
            solicitud_data['especialidades_trabajador'] = especialidades_trabajador
            
            return jsonify(solicitud_data)
        else:
            return jsonify({'error': 'Solicitud no encontrada'}), 404
            
    except Exception as e:
        print(f"Error en obtener_solicitud: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/trabajos_pendientes')
def trabajos_pendientes():
    if not session.get('is_logged_in'):
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != '2':
        flash('Solo los trabajadores pueden acceder a esta página', 'error')
        return redirect(url_for('home'))
    
    try:
        trabajador_id = session.get('user_id')
        
        # Obtener TRABAJOS ACEPTADOS (incluyendo los del muro)
        trabajos_ref = db.collection('PendClienteTrabajador')
        query_trabajos = trabajos_ref.where('profesional_id', '==', trabajador_id).where('estado', '==', 'aceptado')
        docs_trabajos = query_trabajos.stream()
        
        trabajos_aceptados = []
        for doc in docs_trabajos:
            trabajo_data = doc.to_dict()
            trabajo_data['id'] = doc.id
            
            # Verificar si existe un registro en TrabajosFinalizados
            finalizado_ref = db.collection('TrabajosFinalizados').document(doc.id)
            finalizado_doc = finalizado_ref.get()
            
            if not finalizado_doc.exists:
                trabajo_data['tipo'] = 'contratacion'
                # Marcar si es del muro para mostrarlo diferente
                if trabajo_data.get('origen') == 'muro':
                    trabajo_data['es_muro'] = True
                trabajos_aceptados.append(trabajo_data)
        
        # ... (el resto del código de la función se mantiene igual)
        # Obtener MENTORÍAS ACEPTADAS
        mentorias_ref = db.collection('Mentorias')
        query_mentorias = mentorias_ref.where('mentor_id', '==', trabajador_id).where('estado', '==', 'aceptado')
        docs_mentorias = query_mentorias.stream()
        
        mentorias_activas = []
        for doc in docs_mentorias:
            mentoria_data = doc.to_dict()
            mentoria_data['id'] = doc.id
            mentoria_data['tipo'] = 'mentoria'
            mentorias_activas.append(mentoria_data)
        
        # Combinar ambas listas
        todos_los_trabajos = trabajos_aceptados + mentorias_activas
        
        # Obtener TRABAJOS COMPLETADOS (historial)
        trabajos_finalizados_ref = db.collection('TrabajosFinalizados')
        query_completados = trabajos_finalizados_ref.where('profesional_id', '==', trabajador_id)
        docs_completados = query_completados.stream()
        
        trabajos_completados = []
        for doc in docs_completados:
            trabajo_data = doc.to_dict()
            trabajo_data['id'] = doc.id
            trabajo_data['tipo'] = 'completado'
            trabajos_completados.append(trabajo_data)

        # Obtener MENTORÍAS COMPLETADAS
        query_mentorias_completadas = mentorias_ref.where('mentor_id', '==', trabajador_id).where('estado', '==', 'completada')
        docs_mentorias_completadas = query_mentorias_completadas.stream()
        
        mentorias_completadas = []
        for doc in docs_mentorias_completadas:
            mentoria_data = doc.to_dict()
            mentoria_data['id'] = doc.id
            mentoria_data['tipo'] = 'mentoria-completada'
            mentorias_completadas.append(mentoria_data)

        return render_template('TrabajosPendientes.html', 
                             trabajos=todos_los_trabajos,
                             trabajos_contrataciones=trabajos_aceptados,
                             trabajos_mentorias=mentorias_activas,
                             trabajos_completados=trabajos_completados,
                             mentorias_completadas=mentorias_completadas)
        
    except Exception as e:
        print(f"Error al obtener trabajos pendientes: {str(e)}")
        flash('Error al cargar los trabajos pendientes', 'error')
        return render_template('TrabajosPendientes.html', 
                             trabajos=[],
                             trabajos_contrataciones=[],
                             trabajos_mentorias=[],
                             trabajos_completados=[],
                             mentorias_completadas=[])

@app.route('/historial_trabajos')
def historial_trabajos():
    if not session.get('is_logged_in'):
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != '2':
        flash('Solo los trabajadores pueden acceder a esta página', 'error')
        return redirect(url_for('home'))
    
    try:
        trabajador_id = session.get('user_id')
        
        # Obtener TRABAJOS FINALIZADOS de clientes
        trabajos_finalizados_ref = db.collection('TrabajosFinalizados')
        query_trabajos = trabajos_finalizados_ref.where('profesional_id', '==', trabajador_id)
        docs_trabajos = query_trabajos.stream()
        
        trabajos_completados = []
        for doc in docs_trabajos:
            trabajo_data = doc.to_dict()
            trabajo_data['id'] = doc.id
            trabajo_data['tipo'] = 'contratacion'
            trabajos_completados.append(trabajo_data)
        
        # Obtener MENTORÍAS COMPLETADAS
        mentorias_ref = db.collection('Mentorias')
        query_mentorias = mentorias_ref.where('mentor_id', '==', trabajador_id).where('estado', '==', 'completada')
        docs_mentorias = query_mentorias.stream()
        
        mentorias_completadas = []
        for doc in docs_mentorias:
            mentoria_data = doc.to_dict()
            mentoria_data['id'] = doc.id
            mentoria_data['tipo'] = 'mentoria'
            mentorias_completadas.append(mentoria_data)
        
        return render_template('HistorialTrabajos.html', 
                             trabajos_completados=trabajos_completados,
                             mentorias_completadas=mentorias_completadas)
        
    except Exception as e:
        print(f"Error al obtener historial de trabajos: {str(e)}")
        flash('Error al cargar el historial de trabajos', 'error')
        return render_template('HistorialTrabajos.html', 
                             trabajos_completados=[],
                             mentorias_completadas=[])

@app.route('/oportunidades')
def oportunidades():
    if not session.get('is_logged_in'):
        flash('Debes iniciar sesión primero', 'warning')
        return redirect(url_for('login'))
    
    if session.get('user_type') != '3':  # 3 = desempleado
        flash('Solo los desempleados pueden acceder a oportunidades', 'error')
        return redirect(url_for('home'))
    
    try:
        # Obtener trabajadores que son mentores
        trabajadores_ref = db.collection('trabajadores')
        query = trabajadores_ref.where('AyudarAOtros', '==', True)
        docs = query.stream()
        
        mentores = []
        for doc in docs:
            trabajador_data = doc.to_dict()
            trabajador_data['id'] = doc.id
            
            # Procesar especialidades (igual que en browser)
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
            
            # Datos por defecto
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
            if 'experiencia' not in trabajador_data:
                trabajador_data['experiencia'] = 'Experiencia no especificada'
            
            mentores.append(trabajador_data)
            
    except Exception as e:
        print(f"Error al obtener mentores: {str(e)}")
        mentores = []
        flash('Error al cargar las oportunidades de mentoría', 'error')
    
    return render_template('Oportunidades.html', mentores=mentores)

@app.route('/solicitar_mentoria', methods=['POST'])
def solicitar_mentoria():
    if not session.get('is_logged_in') or session.get('user_type') != '3':
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        data = request.get_json()
        
        mentor_id = data.get('mentorId')
        objetivo = data.get('objetivo')
        disponibilidad = data.get('disponibilidad')
        area_interes = data.get('areaInteres')
        
        if not all([mentor_id, objetivo, disponibilidad, area_interes]):
            return jsonify({'success': False, 'message': 'Faltan campos obligatorios'})
        
        desempleado_id = session.get('user_id')
        desempleado_nombre = session.get('user_name', 'Desempleado')
        
        # Obtener datos del mentor
        mentor_ref = db.collection('trabajadores').document(mentor_id)
        mentor_doc = mentor_ref.get()
        
        if not mentor_doc.exists:
            return jsonify({'success': False, 'message': 'Mentor no encontrado'})
        
        mentor_data = mentor_doc.to_dict()
        mentor_nombre = f"{mentor_data.get('nombre', '')} {mentor_data.get('apellido', '')}".strip()
        
        # Crear solicitud de mentoría
        mentoria_data = {
            'desempleado_id': desempleado_id,
            'desempleado_nombre': desempleado_nombre,
            'mentor_id': mentor_id,
            'mentor_nombre': mentor_nombre,
            'area_interes': area_interes,
            'objetivo': objetivo,
            'disponibilidad': disponibilidad,
            'estado': 'pendiente',
            'fecha_solicitud': datetime.now(),
            'fecha_actualizacion': datetime.now(),
            'tipo': 'mentoria'
        }
        
        # Guardar en colección de Mentorias
        mentorias_ref = db.collection('Mentorias')
        nueva_mentoria = mentorias_ref.add(mentoria_data)
        
        return jsonify({
            'success': True, 
            'message': 'Solicitud de mentoría enviada con éxito',
            'mentoria_id': nueva_mentoria[1].id
        })
        
    except Exception as e:
        print(f"Error al procesar solicitud de mentoría: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al procesar la solicitud'})

@app.route('/finalizar_trabajo/<trabajo_id>', methods=['POST'])
def finalizar_trabajo(trabajo_id):
    if not session.get('is_logged_in') or session.get('user_type') != '2':
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        # Obtener datos del trabajo
        trabajo_ref = db.collection('PendClienteTrabajador').document(trabajo_id)
        trabajo = trabajo_ref.get()
        
        if not trabajo.exists:
            return jsonify({'success': False, 'message': 'Trabajo no encontrado'})
        
        trabajo_data = trabajo.to_dict()
        
        # Crear registro en TrabajosFinalizados
        finalizado_data = {
            'trabajo_id': trabajo_id,
            'cliente_id': trabajo_data.get('cliente_id'),
            'cliente_nombre': trabajo_data.get('cliente_nombre'),
            'profesional_id': session.get('user_id'),
            'profesional_nombre': trabajo_data.get('profesional_nombre'),
            'especializacion': trabajo_data.get('especializacion'),
            'fecha_trabajo_propuesta': trabajo_data.get('fecha_trabajo_propuesta'),
            'fecha_finalizacion': datetime.now(),
            'especificaciones': trabajo_data.get('especificaciones'),
            'metodo_pago': trabajo_data.get('metodo_pago'),
            'ubicacion': trabajo_data.get('ubicacion'),
            'estado': 'finalizado'
        }
        
        db.collection('TrabajosFinalizados').document(trabajo_id).set(finalizado_data)
        
        # Actualizar estado en PendClienteTrabajador
        trabajo_ref.update({
            'estado': 'finalizado',
            'fecha_finalizacion': datetime.now()
        })
        
        return jsonify({'success': True, 'message': 'Trabajo marcado como finalizado'})
        
    except Exception as e:
        print(f"Error al finalizar trabajo: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al procesar la solicitud'})

@app.route('/cancelar_trabajo/<trabajo_id>', methods=['POST'])
def cancelar_trabajo(trabajo_id):
    if not session.get('is_logged_in') or session.get('user_type') != '2':
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        data = request.get_json()
        motivo_cancelacion = data.get('motivo', '')
        
        # Obtener datos del trabajo
        trabajo_ref = db.collection('PendClienteTrabajador').document(trabajo_id)
        trabajo = trabajo_ref.get()
        
        if not trabajo.exists:
            return jsonify({'success': False, 'message': 'Trabajo no encontrado'})
        
        trabajo_data = trabajo.to_dict()
        
        # Crear registro en TrabajosCancelados
        cancelado_data = {
            'trabajo_id': trabajo_id,
            'cliente_id': trabajo_data.get('cliente_id'),
            'cliente_nombre': trabajo_data.get('cliente_nombre'),
            'profesional_id': session.get('user_id'),
            'profesional_nombre': trabajo_data.get('profesional_nombre'),
            'especializacion': trabajo_data.get('especializacion'),
            'fecha_trabajo_propuesta': trabajo_data.get('fecha_trabajo_propuesta'),
            'fecha_cancelacion': datetime.now(),
            'especificaciones': trabajo_data.get('especificaciones'),
            'metodo_pago': trabajo_data.get('metodo_pago'),
            'ubicacion': trabajo_data.get('ubicacion'),
            'motivo_cancelacion': motivo_cancelacion,
            'cancelado_por': 'trabajador',
            'estado': 'cancelado'
        }
        
        db.collection('TrabajosCancelados').document(trabajo_id).set(cancelado_data)
        
        # Actualizar estado en PendClienteTrabajador
        trabajo_ref.update({
            'estado': 'cancelado',
            'motivo_cancelacion': motivo_cancelacion,
            'fecha_cancelacion': datetime.now(),
            'cancelado_por': 'trabajador'
        })
        
        return jsonify({'success': True, 'message': 'Trabajo cancelado correctamente'})
        
    except Exception as e:
        print(f"Error al cancelar trabajo: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al procesar la solicitud'})

@app.route('/aceptar_mentoria/<mentoria_id>', methods=['POST'])
def aceptar_mentoria(mentoria_id):
    if not session.get('is_logged_in') or session.get('user_type') != '2':
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        mentoria_ref = db.collection('Mentorias').document(mentoria_id)
        mentoria_ref.update({
            'estado': 'aceptado',
            'fecha_actualizacion': datetime.now()
        })
        
        return jsonify({'success': True, 'message': 'Mentoría aceptada con éxito'})
        
    except Exception as e:
        print(f"Error al aceptar mentoría: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al procesar la solicitud'})

@app.route('/rechazar_mentoria/<mentoria_id>', methods=['POST'])
def rechazar_mentoria(mentoria_id):
    if not session.get('is_logged_in') or session.get('user_type') != '2':
        return jsonify({'success': False, 'message': 'No autorizado'})
    
    try:
        mentoria_ref = db.collection('Mentorias').document(mentoria_id)
        mentoria_ref.update({
            'estado': 'rechazado',
            'fecha_actualizacion': datetime.now()
        })
        
        return jsonify({'success': True, 'message': 'Mentoría rechazada'})
        
    except Exception as e:
        print(f"Error al rechazar mentoría: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al procesar la solicitud'})

print ""

if __name__ == '__main__':
    app.run()