import firebase_admin
from firebase_admin import credentials, firestore

# Ruta al archivo de credenciales descargado
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

# Conectarse a Firestore
db = firestore.client()

# Agregar un documento a la colección "usuarios"
doc_ref = db.collection("usuarios").document("juan_123")
doc_ref.set({
    "nombre": "Juan",
    "edad": 30,
    "profesion": "Plomero"
})

print("Documento agregado exitosamente")
