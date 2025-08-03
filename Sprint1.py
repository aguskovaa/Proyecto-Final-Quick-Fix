import tkinter as tk
from tkinter import filedialog
import webbrowser
import threading
import os
import time
import unidecode
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import http.server
import socketserver
import pytz



cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()



ruta_html = "C:\\Users\\HOME\\Documents\\QuickFix\\maps.html"

root = tk.Tk()
root.withdraw()  # Oculta la ventana principal

# Función para seleccionar un archivo PDF
def seleccionar_pdf():
    return filedialog.askopenfilename(
        title="Seleccionar tu CV en formato PDF",
        filetypes=[("Archivos PDF", "*.pdf")]
    )

    


Devuelta = None

print("¿Qué querés hacer?")
print("1. Ingresar")
print("2. Registrarte")

opcion = input("Elegí una opción (1 o 2): ")

if opcion == "1":

    print("¿Cual es tu profesion?")
    print("1. Trabajador")
    print("2. Cliente")
    print("3. Desempleado")

    profesion = input("Elegí una opción (1, 2 o 3): ")
    
    if profesion == "1":

        mail = input("Ingresá tu mail: ")
        contraseña = input("Ingresá tu contraseña: ")

        trabajadores_ref = db.collection("trabajadores")
        query = (
            trabajadores_ref
            .where("mail", "==", mail)
            .where("contra", "==", contraseña)
            .limit(1)
            .stream()
        )
        
        usuario = None
        for doc in query:
            usuario = doc.to_dict()
            break  

        if usuario:
            nombre = usuario.get("nombre", "usuario")  
            print("✅ Inicio de sesión exitoso. ¡Bienvenido,", nombre + "!")
        else:
            print("❌ Datos incorrectos. Por favor, intentá nuevamente.")  


    
    elif profesion == "2":
        mail = input("Ingresá tu mail: ")
        contraseña = input("Ingresá tu contraseña: ")
        
        clientes_ref = db.collection("clientes")
        query = (
            clientes_ref
            .where("mail", "==", mail)
            .where("contra", "==", contraseña)
            .limit(1)
            .stream()
        )
        
        usuario = None
        for doc in query:
            usuario = doc.to_dict()
            break  
       

        if usuario:
            nombre = usuario.get("nombre", "usuario")  
            print("✅ Inicio de sesión exitoso. ¡Bienvenido,", nombre + "!")

            Cmail = mail

            print("¿Q queres hacer ahora?")
            print("1. Solicitar CV de trabajador")
            print("2. Contratar a un trabajador para un trabajo")

            QHacer = input("Elegí una opción (1 o 2): ")
            if QHacer == "1": #modifcar para firestore
                MailTra = input("Ingresá el mail del trabajador: ")

                cursor.execute('SELECT "CV" FROM trabajador WHERE "Mail" = %s', (MailTra,))
                CVA = cursor.fetchone()

                if CVA and CVA[0]:
                    rutaCVR = "CV_" + MailTra.replace("@", "_at_").replace(".", "_") + ".pdf"
                    with open(rutaCVR, "wb") as f:
                        f.write(CVA[0])
                    print(f"✅ CV recuperado y guardado como '{rutaCVR}'.")
                    
                    webbrowser.open(rutaCVR)
            
            
            elif QHacer == "2":
                 especializaciones_legibles = {
            1: "Fontanero / Plomero",
            2: "Electricista",
            3: "Gasista matriculado",
            4: "Albañil",
            5: "Carpintero",
            6: "Pintor",
            7: "Herrero",
            8: "Techista / Impermeabilizador",
            9: "Cerrajero",
            10: "Instalador de aires acondicionados",
            11: "Instalador de alarmas/cámaras de seguridad",
            12: "Personal de limpieza",
            13: "Limpieza de tanques de agua",
            14: "Limpieza de vidrios en altura",
            15: "Lavado de alfombras / cortinas",
            16: "Fumigador",
            17: "Jardinero",
            18: "Podador de árboles",
            19: "Mantenimiento de piletas",
            20: "Paisajista",
            21: "Técnico de electrodomésticos",
            22: "Técnico de celulares",
            23: "Técnico de computadoras / laptops",
            24: "Técnico de televisores / equipos electrónicos",
            25: "Técnico de impresoras",
            26: "Instalador de redes / WiFi",
            27: "Otro"
            }
                 
            especializaciones_firestore = {
                1: "Fontanero_Plomero",
                2: "Electricista",
                3: "Gasista_matriculado",
                4: "Albanil",
                5: "Carpintero",
                6: "Pintor",
                7: "Herrero",
                8: "Techista_Impermeabilizador",
                9: "Cerrajero",
                10: "Instalador_de_aires_acondicionados",
                11: "Instalador_de_alarmas_camáras_de_seguridad",
                12: "Personal_de_limpieza",
                13: "Limpieza_de_tanques_de_agua",
                14: "Limpieza_de_vidrios_en_altura",
                15: "LavadoDeAlfombras_cortinas",
                16: "Fumigador",
                17: "Jardinero",
                18: "Podador_de_árboles",
                19: "Mantenimiento_de_piletas",
                20: "Paisajista",
                21: "Técnico_de_electrodomésticos",
                22: "Técnico_celulares",
                23: "TécnicoDeComputadoras_laptops",
                24: "TécnicoDeTelevisores_equiposelectrónicos",
                25: "Técnico_de_impresoras",
                26: "InstaladorDeRedes_WiFi",
                27: "Otro"
}
            if QHacer == "2":
                print("\n🔧 Reparaciones y mantenimiento del hogar")
                for i in range(1, 12):
                    print(f"{i}. {especializaciones_legibles[i]}")
    
                print("\n🧼 Limpieza y mantenimiento")
                for i in range(12, 17):
                   print(f"{i}. {especializaciones_legibles[i]}")
    
                print("\n🌳 Jardinería y exteriores")
                for i in range(17, 21):
                    print(f"{i}. {especializaciones_legibles[i]}")

                print("\n🛠️ Servicios técnicos")
                for i in range(21, 27):
                    print(f"{i}. {especializaciones_legibles[i]}")

                print("\n27. Otro")

                try:
                    Laburo = int(input("\n¿Qué tipo de laburo necesitás hecho (ingresá el número)? "))
                    LaburoPosta_legible = especializaciones_legibles[Laburo]
                    LaburoPosta_firestore = especializaciones_firestore[Laburo]

                    campo_especializacion = LaburoPosta_firestore
                    
                    trabajadores_ref = db.collection("trabajadores").where(campo_especializacion, "==", True)
                    resultados = trabajadores_ref.stream()

                    lista_mails = []

                    for doc in resultados:
                        data = doc.to_dict()
                        if "mail" in data:
                            if data.get("AyudarAOtros") == True:
                                lista_mails.append(data["mail"])

                    if lista_mails:
                        print("\n📧 Trabajadores disponibles:\n")
                        for i, mail in enumerate(lista_mails, start=1):
                            print(f"{i}. {mail}")
                    else:
                        print("No se encontraron trabajadores con esa especialización.")

                except Exception as e:
                    print("Ocurrió un error:", e)

                Tmail = input("A cual te gustaria contratar (ingresar el mail del trabajador)?:")
                
                trabajador_docs = list(db.collection("trabajadores").where("mail", "==", Tmail).stream())

                while not trabajador_docs:
                    print("❌ El mail no existe. Ingresá otro mail:")
                    Tmail = input("Mail: ")
                    trabajador_docs = list(db.collection("trabajadores").where("mail", "==", Tmail).stream())

                print("✅ Contrataste a " + Tmail + " para que te haga un trabajo de " + LaburoPosta_legible)

                Costo = None  
                argentina = pytz.timezone("America/Argentina/Buenos_Aires")
                ahora = datetime.now(argentina)
                Finalizado = False

                try:
                    db.collection("historialTC").document(Tmail + " - " + Cmail).set({
                        "Tmail": Tmail,
                        "Cmail": Cmail,
                        "Costo": Costo,
                        "Trabajo": LaburoPosta_legible,
                        "HorarioContratacion": ahora,
                        "Finalizado": Finalizado
                    })
                    print("📝 Contratación registrada en el historial.")
                except Exception as e:
                    print("❌ Error al guardar en Firestore:", e)
                


        else:
            print("❌ Datos incorrectos. Por favor, intentá nuevamente.")

    elif profesion == "3":
        mail = input("Ingresá tu mail: ")
        contraseña = input("Ingresá tu contraseña: ")

        desempleados_ref = db.collection("desempleados")
        query = (
            desempleados_ref
            .where("mail", "==", mail)
            .where("contra", "==", contraseña)
            .limit(1)
            .stream()
        )
        
        usuario = None
        for doc in query:
            usuario = doc.to_dict()
            break  

        if usuario:
            nombre = usuario.get("nombre", "usuario")  
            print("✅ Inicio de sesión exitoso. ¡Bienvenido,", nombre + "!")
        
            DMail = mail

            print("¿Q queres hacer ahora?")
            print("1. Solicitar mentoria a un trabajador")

            QHacer = input("Elegí una opción (1 o 2): ")

            argentina = pytz.timezone("America/Argentina/Buenos_Aires")
            ahora = datetime.now(argentina)
            
            especializaciones_legibles = {
            1: "Fontanero / Plomero",
            2: "Electricista",
            3: "Gasista matriculado",
            4: "Albañil",
            5: "Carpintero",
            6: "Pintor",
            7: "Herrero",
            8: "Techista / Impermeabilizador",
            9: "Cerrajero",
            10: "Instalador de aires acondicionados",
            11: "Instalador de alarmas/cámaras de seguridad",
            12: "Personal de limpieza",
            13: "Limpieza de tanques de agua",
            14: "Limpieza de vidrios en altura",
            15: "Lavado de alfombras / cortinas",
            16: "Fumigador",
            17: "Jardinero",
            18: "Podador de árboles",
            19: "Mantenimiento de piletas",
            20: "Paisajista",
            21: "Técnico de electrodomésticos",
            22: "Técnico de celulares",
            23: "Técnico de computadoras / laptops",
            24: "Técnico de televisores / equipos electrónicos",
            25: "Técnico de impresoras",
            26: "Instalador de redes / WiFi",
            27: "Otro"
            }
                 
            especializaciones_firestore = {
                1: "Fontanero_Plomero",
                2: "Electricista",
                3: "Gasista_matriculado",
                4: "Albanil",
                5: "Carpintero",
                6: "Pintor",
                7: "Herrero",
                8: "Techista_Impermeabilizador",
                9: "Cerrajero",
                10: "Instalador_de_aires_acondicionados",
                11: "Instalador_de_alarmas_camáras_de_seguridad",
                12: "Personal_de_limpieza",
                13: "Limpieza_de_tanques_de_agua",
                14: "Limpieza_de_vidrios_en_altura",
                15: "LavadoDeAlfombras_cortinas",
                16: "Fumigador",
                17: "Jardinero",
                18: "Podador_de_árboles",
                19: "Mantenimiento_de_piletas",
                20: "Paisajista",
                21: "Técnico_de_electrodomésticos",
                22: "Técnico_celulares",
                23: "TécnicoDeComputadoras_laptops",
                24: "TécnicoDeTelevisores_equiposelectrónicos",
                25: "Técnico_de_impresoras",
                26: "InstaladorDeRedes_WiFi",
                27: "Otro"
            }
            
            if QHacer == "1":
                print("\n🔧 Reparaciones y mantenimiento del hogar")
                for i in range(1, 12):
                    print(f"{i}. {especializaciones_legibles[i]}")
    
                print("\n🧼 Limpieza y mantenimiento")
                for i in range(12, 17):
                   print(f"{i}. {especializaciones_legibles[i]}")
    
                print("\n🌳 Jardinería y exteriores")
                for i in range(17, 21):
                    print(f"{i}. {especializaciones_legibles[i]}")

                print("\n🛠️ Servicios técnicos")
                for i in range(21, 27):
                    print(f"{i}. {especializaciones_legibles[i]}")

                print("\n27. Otro")

                

                try:
                    Laburo = int(input("\n¿Qué tipo de laburo queres tener (ingresá el número)? "))
                    LaburoPosta_legible = especializaciones_legibles[Laburo]
                    LaburoPosta_firestore = especializaciones_firestore[Laburo]

                    campo_especializacion = LaburoPosta_firestore
                    
                    trabajadores_ref = db.collection("trabajadores").where(campo_especializacion, "==", True)
                    resultados = trabajadores_ref.stream()

                    lista_mails = []

                    for doc in resultados:
                        data = doc.to_dict()
                        if "mail" in data:
                            lista_mails.append(data["mail"])

                    if lista_mails:
                        print("\n📧 Trabajadores disponibles:\n")
                        for i, mail in enumerate(lista_mails, start=1):
                            print(f"{i}. {mail}")
                    else:
                        print("No se encontraron trabajadores con esa especialización dispuestos a enseñar.")

                except Exception as e:
                    print("Ocurrió un error:", e)

                Tmail = input("A cual te gustaria contratar (ingresar el mail del trabajador)?:")
                
                trabajador_docs = list(db.collection("trabajadores").where("mail", "==", Tmail).stream())

                while not trabajador_docs:
                    print("❌ El mail no existe. Ingresá otro mail:")
                    Tmail = input("Mail: ")
                    trabajador_docs = list(db.collection("trabajadores").where("mail", "==", Tmail).stream())

                print("✅ Contrataste a " + Tmail + " para que te enseñe a como ser un " + LaburoPosta_legible)


                Costo = None

                try:
                    db.collection("historialTD").document(Tmail + " - " + DMail).set({
                        "Tmail": Tmail,
                        "Dmail": DMail,
                        "Costo": Costo,
                        "Trabajo": LaburoPosta_legible,
                        "HorarioContratacion": ahora,
                    })
                    print("📝 Contratación registrada en el historial.")
                except Exception as e:
                    print("❌ Error al guardar en Firestore:", e)
                


                     

elif opcion == "2":

   
    print("¿Qué querés ser?")
    print("1. Cliente")
    print("2. Trabajador")  
    print("3. Desempleado")  

    RProfesion = input("Elegí una opción (1, 2 o 3): ")
    
    if RProfesion == "1":
        

        RCMail = input("Mail: ")

        existenteMailCliente = False

        def obtener_datos_cliente(cliente_id):
            global existenteMailCliente  
            doc_ref = db.collection("clientes").document(cliente_id)
            doc = doc_ref.get()
            if doc.exists:
                existenteMailCliente = True
            else:
                existenteMailCliente = False

        obtener_datos_cliente(RCMail)  

        while existenteMailCliente == True:
            print("❌ El mail ya está registrado. Ingresá otro mail:")
            RCMail = input("Mail: ")
            obtener_datos_cliente(RCMail)  

        
        

        
        RCNombre = input("Nombre: ")
        RCApellido = input("Apellido: ")
        
        RCTel = input("Tel: ")

        
        
        existenteTelCliente = False

        def obtener_datos_cliente_por_tel(telefono_busqueda):
            global existenteTelCliente  
            clientes_ref = db.collection("clientes")
            query = clientes_ref.where("tel", "==", telefono_busqueda).limit(1).stream()

            for doc in query:
                existenteTelCliente = True
                return
            existenteTelCliente = False

        obtener_datos_cliente_por_tel(RCTel)  

        while existenteTelCliente == True:
            print("❌ El teléfono ya está registrado. Ingresá otro teléfono:")
            RCTel = input("Tel: ")
            obtener_datos_cliente_por_tel(RCTel)  

        RCTel = int(RCTel)

        RCBirth = datetime.strptime(input("Nacimiento (YYYY-MM-DD): "), "%Y-%m-%d")

        RCContraseña = input("Contraseña: ")

        PORT = 8000
        NOMBRE_ARCHIVO = "coordenadas.txt"

        DIRECTORIO = os.path.dirname(os.path.abspath(__file__))

        class Handler(http.server.SimpleHTTPRequestHandler):
        
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=DIRECTORIO, **kwargs)

        def levantar_servidor():
            with socketserver.TCPServer(("", PORT), Handler) as httpd:
                print(f"Servidor corriendo en http://localhost:{PORT}")
                httpd.serve_forever()

        def buscar_archivo_en_c(nombre_archivo):
            for raiz, dirs, archivos in os.walk("C:\\"):
                if nombre_archivo in archivos:
                    return os.path.join(raiz, nombre_archivo)
            return None


        threading.Thread(target=levantar_servidor, daemon=True).start()

        webbrowser.open_new(f"http://localhost:{PORT}/maps.html")

        print(f"Buscando '{NOMBRE_ARCHIVO}' en todo el disco C:\\")
        archivo_coords = None

        while archivo_coords is None:
            archivo_coords = buscar_archivo_en_c(NOMBRE_ARCHIVO)
            if archivo_coords is None:
                print("Archivo no encontrado todavía. Esperando 2 segundos...")
                time.sleep(2)

        print(f"✅ Archivo encontrado en: {archivo_coords}")

        with open(archivo_coords, "r") as f:
            contenido = f.read().strip()

        try:
            lineas = contenido.split("\n")
            lat = float(lineas[0].split("=")[1])
            lng = float(lineas[1].split("=")[1])
        except Exception as e:
            print("❌ Error al leer el archivo:", e)
            lat = None
            lng = None

        os.remove(archivo_coords)
        print("🗑️ Archivo eliminado.")

        if lat is not None and lng is not None:
            print("📍 Coordenadas recibidas:")
            print(f"Latitud: {lat}")
            print(f"Longitud: {lng}")
            RCLat = float(lat)
            RCLng = float(lng)
        else:
            print("❌ No se pudieron obtener coordenadas válidas.")
       
        def crear_cliente(nombre: str, apellido: str, telefono: int, cumpleaños: datetime, contraseña: str, mail: str, latitud: float, longitud: float):
            doc_ref = db.collection("clientes").document(mail)
            doc_ref.set({
                "nombre": nombre,
                "apellido": apellido,
                "tel": telefono,
                "birth": cumpleaños,
                "contra": contraseña,
                "mail": mail,
                "latitud": latitud,
                "longitud": longitud
            })


        
        crear_cliente(
                nombre = RCNombre,
                apellido = RCApellido,
                telefono = RCTel,
                cumpleaños = RCBirth,
                contraseña = RCContraseña,
                mail = RCMail,
                latitud = RCLat,
                longitud = RCLng
            )   
    

        
        print("✅ Te registraste bien. ¡Bienvenido,", RCNombre + "!")

    
    
    
    elif RProfesion == "2":
        RTMail = input("Mail: ")

        existenteMailTrabajador = False

        def obtener_datos_trabajador(trabajador_id):
            global existenteMailTrabajador  
            doc_ref = db.collection("trabajadores").document(trabajador_id)
            doc = doc_ref.get()
            if doc.exists:
                existenteMailTrabajador = True
            else:
                existenteMailTrabajador = False

        obtener_datos_trabajador(RTMail)  

        while existenteMailTrabajador == True:
            print("❌ El mail ya está registrado. Ingresá otro mail:")
            RTMail = input("Mail: ")
            obtener_datos_trabajador(RTMail)  



        RTNombre = input("Nombre: ")
        RTApellido = input("Apellido: ")

        RTTel = input("Tel: ")
        
        existenteTelTrabajador = False

        def obtener_datos_trabajador_por_tel(telefono_busqueda):
            global existenteTelTrabajador  
            trabajadores_ref = db.collection("trabajadores")
            query = trabajadores_ref.where("tel", "==", telefono_busqueda).limit(1).stream()

            for doc in query:
                existenteTelTrabajador = True
                return
            existenteTelTrabajador = False

        obtener_datos_trabajador_por_tel(RTTel)  

        while existenteTelTrabajador == True:
            print("❌ El teléfono ya está registrado. Ingresá otro teléfono:")
            RTTel = input("Tel: ")
            obtener_datos_trabajador_por_tel(RTTel)  
        
        RTTel = int(RTTel)

        
        RTBirth = datetime.strptime(input("Nacimiento (YYYY-MM-DD): "), "%Y-%m-%d")


        RTContraseña = input("Contraseña: ")
        
        print("Selecciona tu CV en formato PDF")
        ruta_archivo = seleccionar_pdf()

        if ruta_archivo:
            with open(ruta_archivo, "rb") as f:
                RTCv = f.read()
        
        especializaciones = {
            1: "Fontanero/Plomero",
            2: "Electricista",
            3: "Gasista matriculado",
            4: "Albañil",
            5: "Carpintero",
            6: "Pintor",
            7: "Herrero",
            8: "Techista/Impermeabilizador",
            9: "Cerrajero",
            10: "Instalador de aires acondicionados",
            11: "Instalador de alarmas/cámaras de seguridad",
            12: "Personal de limpieza",
            13: "Limpieza de tanques de agua",
            14: "Limpieza de vidrios en altura",
            15: "Lavado de alfombras/cortinas",
            16: "Fumigador",
            17: "Jardinero",
            18: "Podador de árboles",
            19: "Mantenimiento de piletas",
            20: "Paisajista",
            21: "Técnico de electrodomésticos",
            22: "Técnico de celulares",
            23: "Técnico de computadoras/laptops",
            24: "Técnico de televisores/equipos electrónicos",
            25: "Técnico de impresoras",
            26: "Instalador de redes/WiFi",
            27: "Otro"
        }

        def normalizar_especializacion(nombre):
            nombre = nombre.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ü", "u")
            nombre = nombre.replace("/", "_").replace("-", "").replace(".", "")
            nombre = nombre.replace(" ", "_")
            return nombre


        especializaciones_booleans = {
        normalizar_especializacion(nombre): False
        for nombre in especializaciones.values()
        if nombre != "Otro"
        }

        otrosTrabajosPosta = []

        def mostrar_especializaciones():
            print("\nEspecializaciones disponibles:")
            for key in especializaciones:
                print(f"{key}. {especializaciones[key]}")

        def main():
            global otrosTrabajosPosta  
            mostrar_especializaciones()
            entrada = input("\nElegí tu especialización/es (en caso de ser más de una, separalas con coma): ")
            seleccion = entrada.split(",")

            for item in seleccion:
                try:
                    index = int(item.strip())
                    if index == 27:
                        otro = input("Especificá cuál es tu otra especialización: ")
                        otrosTrabajosPosta = [trabajo.strip() for trabajo in otro.split(",") if trabajo.strip() != ""]
                    elif 1 <= index <= 26:
                        nombre = especializaciones[index]
                        clave_normalizada = normalizar_especializacion(nombre)
                        especializaciones_booleans[clave_normalizada] = True
                    else:
                        print(f"Opción inválida: {index}")
                
                except ValueError:
                    print(f"Opción inválida: {item.strip()}")

            print("\n✅ Especializaciones asignadas:")
            for clave, valor in especializaciones_booleans.items():
                estado = "✅" if valor else "❌"
                print(f"{estado} {clave}")

            if otrosTrabajosPosta:
                print("\n🔧 Otros trabajos especificados:")
                for otro in otrosTrabajosPosta:
                    print(f"- {otro}")

        if __name__ == "__main__":
            main()
        
        print("¿Estas dispuesto a enseñarles a otros tus conocimientos en esta area?")
        print("1. Si")
        print("2. No")
        RTCaridad = int(input("Elegí una opción (1 o 2): "))

        if RTCaridad == 1:
            RTCaridad = True

        elif RTCaridad == 2:
            RTCaridad = False


        def crear_trabajador(
            nombre: str, apellido: str, telefono: int, cumpleaños, contraseña: str, mail: str, cv, RTCaridad: bool,
            Fontanero_Plomero, Electricista, Gasista_matriculado, Albañil, Carpintero, Pintor,
            Herrero, Techista_Impermeabilizador, Cerrajero, Instalador_de_aires_acondicionados,
            Instalador_de_alarmas_cámaras_de_seguridad, Personal_de_limpieza,
            Limpieza_de_tanques_de_agua, Limpieza_de_vidrios_en_altura, Fumigador,
            LavadoDeAlfombras_cortinas, Jardinero, Podador_de_árboles, Mantenimiento_de_piletas,
            Paisajista, Técnico_de_electrodomésticos, Técnico_de_celulares,
            TécnicoDeComputadoras_laptops, TécnicoDeTelevisores_equiposelectrónicos,
            Técnico_de_impresoras, InstaladorDeRedes_WiFi, Otro: list
        ):
            doc_ref = db.collection("trabajadores").document(mail)
            doc_ref.set({
                "nombre": nombre,
                "apellido": apellido,
                "tel": telefono,
                "birth": cumpleaños,
                "contra": contraseña,
                "mail": mail,
                "cv": cv,
                "AyudarAOtros": RTCaridad,
                "Fontanero_Plomero": Fontanero_Plomero,
                "Electricista": Electricista,
                "Gasista_matriculado": Gasista_matriculado,
                "Albañil": Albañil,
                "Carpintero": Carpintero,
                "Pintor": Pintor,
                "Herrero": Herrero,
                "Techista_Impermeabilizador": Techista_Impermeabilizador,
                "Cerrajero": Cerrajero,
                "Instalador_de_aires_acondicionados": Instalador_de_aires_acondicionados,
                "Instalador_de_alarmas_cámaras_de_seguridad": Instalador_de_alarmas_cámaras_de_seguridad,
                "Personal_de_limpieza": Personal_de_limpieza,
                "Limpieza_de_tanques_de_agua": Limpieza_de_tanques_de_agua,
                "Limpieza_de_vidrios_en_altura": Limpieza_de_vidrios_en_altura,
                "Fumigador": Fumigador,
                "LavadoDeAlfombras_cortinas": LavadoDeAlfombras_cortinas,
                "Jardinero": Jardinero,
                "Podador_de_árboles": Podador_de_árboles,
                "Mantenimiento_de_piletas": Mantenimiento_de_piletas,
                "Paisajista": Paisajista,
                "Técnico_de_electrodomésticos": Técnico_de_electrodomésticos,
                "Técnico_de_celulares": Técnico_de_celulares,
                "TécnicoDeComputadoras_laptops": TécnicoDeComputadoras_laptops,
                "TécnicoDeTelevisores_equiposelectrónicos": TécnicoDeTelevisores_equiposelectrónicos,
                "Técnico_de_impresoras": Técnico_de_impresoras,
                "InstaladorDeRedes_WiFi": InstaladorDeRedes_WiFi,
                "Otro": Otro
            })


        crear_trabajador(
            nombre=RTNombre,
            apellido=RTApellido,
            telefono=RTTel,
            cumpleaños=RTBirth,
            contraseña=RTContraseña,
            mail=RTMail,
            cv=RTCv,
            RTCaridad = RTCaridad,
            Fontanero_Plomero=especializaciones_booleans["fontanero_plomero"],
            Electricista=especializaciones_booleans["electricista"],
            Gasista_matriculado=especializaciones_booleans["gasista_matriculado"],
            Albañil=especializaciones_booleans["albañil"],
            Carpintero=especializaciones_booleans["carpintero"],
            Pintor=especializaciones_booleans["pintor"],
            Herrero=especializaciones_booleans["herrero"],
            Techista_Impermeabilizador=especializaciones_booleans["techista_impermeabilizador"],
            Cerrajero=especializaciones_booleans["cerrajero"],
            Instalador_de_aires_acondicionados=especializaciones_booleans["instalador_de_aires_acondicionados"],
            Instalador_de_alarmas_cámaras_de_seguridad=especializaciones_booleans["instalador_de_alarmas_camaras_de_seguridad"], # Revisa esta clave, podría ser "instalador_de_alarmas_camaras_de_seguridad"
            Personal_de_limpieza=especializaciones_booleans["personal_de_limpieza"],
            Limpieza_de_tanques_de_agua=especializaciones_booleans["limpieza_de_tanques_de_agua"],
            Limpieza_de_vidrios_en_altura=especializaciones_booleans["limpieza_de_vidrios_en_altura"],
            Fumigador=especializaciones_booleans["fumigador"],
            LavadoDeAlfombras_cortinas=especializaciones_booleans["lavado_de_alfombras_cortinas"],
            Jardinero=especializaciones_booleans["jardinero"],
            Podador_de_árboles=especializaciones_booleans["podador_de_arboles"],
            Mantenimiento_de_piletas=especializaciones_booleans["mantenimiento_de_piletas"],
            Paisajista=especializaciones_booleans["paisajista"],
            Técnico_de_electrodomésticos=especializaciones_booleans["tecnico_de_electrodomesticos"],
            Técnico_de_celulares=especializaciones_booleans["tecnico_de_celulares"],
            TécnicoDeComputadoras_laptops=especializaciones_booleans["tecnico_de_computadoras_laptops"],
            TécnicoDeTelevisores_equiposelectrónicos=especializaciones_booleans["tecnico_de_televisores_equipos_electronicos"],
            Técnico_de_impresoras=especializaciones_booleans["tecnico_de_impresoras"],
            InstaladorDeRedes_WiFi=especializaciones_booleans["instalador_de_redes_wifi"],
            Otro=otrosTrabajosPosta
        )

          
        print("✅ Te registraste bien. ¡Bienvenido,", RTNombre + "!")
    
    elif RProfesion == "3":
        RDMail = input("Mail: ")

        existenteMailDesempleado = False

        def obtener_datos_cliente(desempleado_id):
            global existenteMailDesempleado  
            doc_ref = db.collection("desempleados").document(desempleado_id)
            doc = doc_ref.get()
            if doc.exists:
                existenteMailDesempleado = True
            else:
                existenteMailDesempleado = False

        obtener_datos_cliente(RDMail)  

        while existenteMailDesempleado == True:
            print("❌ El mail ya está registrado. Ingresá otro mail:")
            RDMail = input("Mail: ")
            obtener_datos_cliente(RDMail)  


        RDNombre = input("Nombre: ")
        RDApellido = input("Apellido: ")
        print("¿Terminaste el secundario?")
        print("1. Si")
        print("2. No")
        RDSecundaria = int(input("Elegí una opción (1 o 2): "))

        if RDSecundaria == 1:
            RDSecundaria = True

        elif RDSecundaria == 2:
            RDSecundaria = False
        

        

        RDBirth = datetime.strptime(input("Nacimiento (YYYY-MM-DD): "), "%Y-%m-%d")
        
        RDContraseña = input("Contraseña: ")
        print("Selecciona tu CV en formato PDF")
        ruta_archivo = seleccionar_pdf()
        if ruta_archivo:
            with open(ruta_archivo, "rb") as f:
                RDCv = f.read()
        
       

        def crear_desempleado(mail, Nombre, Apellido, Secundaria, Fecha_de_nacimiento, Contraseña, cv):
            doc_ref = db.collection("desempleados").document(mail)
            doc_ref.set({
                "mail": mail,
                "nombre": Nombre,
                "apellido": Apellido,
                "birth": Fecha_de_nacimiento,
                "contra": Contraseña,
                "CV": cv,
                "Secundaria": Secundaria
            })


        
        crear_desempleado(
                mail = RDMail,
                Nombre =  RDNombre,
                Apellido =  RDApellido,
                Fecha_de_nacimiento =  RDBirth,
                Contraseña = RDContraseña,
                cv = RDCv,
                Secundaria = RDSecundaria
            )  


else:
    print("No es una opción")

