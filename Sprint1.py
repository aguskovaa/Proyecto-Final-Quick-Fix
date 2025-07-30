import psycopg2
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

    

conexion = psycopg2.connect(
    host="localhost",
    database="QuickFix",
    user="postgres",    
    password="Boca20052005",
    port="5432"
)

cursor = conexion.cursor()
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

        cursor.execute(
        'SELECT * FROM trabajador WHERE "Mail" = %s AND "Contraseña" = %s',
        (mail, contraseña)
         )

        usuario = cursor.fetchone()

        if usuario:
            nombre = usuario[1]
            print("✅ Inicio de sesión exitoso. ¡Bienvenido,", nombre + "!")
        else:
            print("❌ Datos incorrectos. Por favor, intentá nuevamente.")
        


    
    elif profesion == "2":
        mail = input("Ingresá tu mail: ")
        contraseña = input("Ingresá tu contraseña: ")

        cursor.execute(
        'SELECT * FROM cliente WHERE "Mail" = %s AND "Contraseña" = %s',
        (mail, contraseña)
         )

        usuario = cursor.fetchone()

        if usuario:
            nombre = usuario[1]
            print("✅ Inicio de sesión exitoso. ¡Bienvenido,", nombre + "!")
        

            print("¿Q queres hacer ahora?")
            print("1. Solicitar CV de trabajador")
            print("2. Contratar a un trabajador para un trabajo")

            QHacer = input("Elegí una opción (1 o 2): ")
            if QHacer == "1":
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
                 especializaciones = {
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
            11: "Instalador de alarmas / cámaras de seguridad",
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
            if QHacer == "2":
                print("\n🔧 Reparaciones y mantenimiento del hogar")
                for i in range(1, 12):
                    print(f"{i}. {especializaciones[i]}")
    
                print("\n🧼 Limpieza y mantenimiento")
                for i in range(12, 17):
                   print(f"{i}. {especializaciones[i]}")
    
                print("\n🌳 Jardinería y exteriores")
                for i in range(17, 21):
                    print(f"{i}. {especializaciones[i]}")

                print("\n🛠️ Servicios técnicos")
                for i in range(21, 27):
                    print(f"{i}. {especializaciones[i]}")

                print("\n27. Otro")

                Laburo = input("Que tipo de laburo necesitas hecho: ")
                Laburo = int(Laburo)
                LaburoPosta = especializaciones[Laburo]

                query = f'SELECT "mail" FROM especializaciones WHERE "{LaburoPosta}" = %s'
    
                try:
                    cursor.execute(query, (True,))
                    resultados = cursor.fetchall()

                    lista_mails = [fila[0] for fila in resultados]

                    if lista_mails:
                        print("\n📧 Trabajadores disponibles:\n")
                        for i, mail in enumerate(lista_mails, start=1):
                            print(f"{i}. {mail}")
                    else:
                        print("No se encontraron trabajadores con esa especialización.")
                
                except Exception as e:
                    print("Ocurrió un error al consultar la base de datos:", e)

                Tmail = input("A cual te gustaria contratar (ingresar el mail del trabajador)?:")
                
                cursor.execute('SELECT * FROM trabajador WHERE "Mail" = %s', (Tmail,))
                existente = cursor.fetchone()

                while existente == False:
                    print("❌ El mail no existe. Ingresá otro mail:")
                    Tmail = input("Mail: ")
                    cursor.execute('SELECT * FROM trabajador WHERE "Mail" = %s', (Tmail,))
                    existente = cursor.fetchone()

                print("Listo, contratase a " + Tmail + " para que te haga un trabajado de " + LaburoPosta)

                Costo = None
                ahora = datetime.now()

                cursor.execute(
                    'INSERT INTO "historialTC" ("Tmail", "Cmail", "Costo", "HorarioContra") VALUES (%s, %s, %s,%s)',
                    (Tmail, mail, Costo,ahora)
                    )
                


        else:
            print("❌ Datos incorrectos. Por favor, intentá nuevamente.")

    elif profesion == "3":
        mail = input("Ingresá tu mail: ")
        contraseña = input("Ingresá tu contraseña: ")

        cursor.execute(
        'SELECT * FROM desempleado WHERE "Mail" = %s AND "Contraseña" = %s',
        (mail, contraseña)
         )

        usuario = cursor.fetchone()

        if usuario:
            nombre = usuario[1]
            print("✅ Inicio de sesión exitoso. ¡Bienvenido,", nombre + "!")
        

            print("¿Q queres hacer ahora?")
            print("1. Solicitar mentoria a un trabajador")

            QHacer = input("Elegí una opción (1 o 2): ")

            especializaciones = {
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
            11: "Instalador de alarmas / cámaras de seguridad",
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
            if QHacer == "1":
                print("\n🔧 Reparaciones y mantenimiento del hogar")
                for i in range(1, 12):
                    print(f"{i}. {especializaciones[i]}")
    
                print("\n🧼 Limpieza y mantenimiento")
                for i in range(12, 17):
                   print(f"{i}. {especializaciones[i]}")
    
                print("\n🌳 Jardinería y exteriores")
                for i in range(17, 21):
                    print(f"{i}. {especializaciones[i]}")

                print("\n🛠️ Servicios técnicos")
                for i in range(21, 27):
                    print(f"{i}. {especializaciones[i]}")

                print("\n27. Otro")

                Laburo = input("Que tipo de laburo necesitas: ")
                Laburo = int(Laburo)
                LaburoPosta = especializaciones[Laburo]

                query = f'SELECT "mail" FROM especializaciones WHERE "{LaburoPosta}" = %s'
    
                try:
                    cursor.execute(query, (True,))
                    resultados = cursor.fetchall()

                    lista_mails = [fila[0] for fila in resultados]

                    if lista_mails:
                        print("\n📧 Trabajadores disponibles:\n")
                        for i, mail in enumerate(lista_mails, start=1):
                            print(f"{i}. {mail}")
                    else:
                        print("No se encontraron trabajadores con esa especialización.")
                
                except Exception as e:
                    print("Ocurrió un error al consultar la base de datos:", e)

                Tmail = input("A cual te gustaria contratar (ingresar el mail del trabajador)?:")
                
                cursor.execute('SELECT * FROM trabajador WHERE "Mail" = %s', (Tmail,))
                existente = cursor.fetchone()

                while existente == False:
                    print("❌ El mail no existe. Ingresá otro mail:")
                    Tmail = input("Mail: ")
                    cursor.execute('SELECT * FROM trabajador WHERE "Mail" = %s', (Tmail,))
                    existente = cursor.fetchone()

                print("Listo, contratase a " + Tmail + " para que te instruya en " + LaburoPosta)

                Costo = None
                ahora = datetime.now()

                cursor.execute(
                    'INSERT INTO "historialDT" ("Dmail", "Ttrabajador", "Costo", "HoraDeContra") VALUES (%s, %s, %s,%s)',
                    (mail, Tmail, Costo,ahora)
                    )
                


                     

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

        def buscar_archivo_en_c(nombre_archivo):
            for raiz, dirs, archivos in os.walk("C:\\"):
                if nombre_archivo in archivos:
                    return os.path.join(raiz, nombre_archivo)
            return None
        


        nombre_archivo = "coordenadas.txt"

        webbrowser.open_new(ruta_html)

        archivo_coords = None

        print(f"Buscando '{nombre_archivo}' en todo el disco C:\\")

        while archivo_coords is None:
            archivo_coords = buscar_archivo_en_c(nombre_archivo)
            if archivo_coords is None:
                print("Archivo no encontrado todavía. Esperando 2 segundos...")
                time.sleep(2)

        print(f"Archivo encontrado en: {archivo_coords}")

        with open(archivo_coords, "r") as f:
            contenido = f.read().strip()

        lineas = contenido.split("\n")
        lat = float(lineas[0].split("=")[1])
        lng = float(lineas[1].split("=")[1])

        print("Coordenadas recibidas:")
        print(f"Latitud: {lat}")
        print(f"Longitud: {lng}")

        os.remove(archivo_coords)
        print("Archivo eliminado.")

        RCLat = lat
        RCLng = lng

        RCLat = float(RCLat)
        RCLng = float(RCLng)
       
        def crear_cliente(nombre: str, apellido: str, telefono: int, cumpleaños: datetime, contraseña: str, mail: str, latitud: float, longitud: float):
            doc_ref = db.collection("clientes").document(mail)
            doc_ref.set({
                "nombre": nombre,
                "apellido": apellido,
                "tel": telefono,
                "birth": cumpleaños,
                "contraseña": contraseña,
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
        
        especializaciones_asignadasPosta = []
        otrosTrabajosPosta = []

        especializaciones = {
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
            11: "Instalador de alarmas / cámaras de seguridad",
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

        especializaciones_booleans = {
            "Fontanero_Plomero": False,
            "Electricista": False,
            "Gasista_matriculado": False,
            "Albanil": False,
            "Carpintero": False,
            "Pintor": False,
            "Herrero": False,
            "Techista": False, 
            "Impermeabilizador": False,
            "Cerrajero": False,
            "Instalador_aires_acondicionados": False,
            "Instalador_alarmas": False,
            "Instalador_camaras_seguridad": False,
            "Personal_limpieza": False,
            "Limpieza_tanques_agua": False,
            "Limpieza_vidrios_altura": False,
            "Fumigador": False,
            "Lavado_alfombras_cortinas": False,
            "Jardinero": False,
            "Podador_arboles": False,
            "Mantenimiento_piletas": False,
            "Paisajista": False,
            "Tecnico_electrodomesticos": False,
            "Tecnico_celulares": False,
            "Tecnico_computadoras_laptops": False,
            "Tecnico_televisores_equipos_electronicos": False,
            "Tecnico_impresoras": False,
            "Instalador_redes_WiFi": False,
        }

        


        def normalizar_nombre(nombre):
            nombre = unidecode.unidecode(nombre)  
            return nombre.lower().replace(" / ", "_").replace(" ", "_").replace("/", "_")

        def mostrar_especializaciones():
            print("\n🔧 Reparaciones y mantenimiento del hogar")
            for i in range(1, 12):
                print(f"{i}. {especializaciones[i]}")
    
            print("\n🧼 Limpieza y mantenimiento")
            for i in range(12, 17):
                print(f"{i}. {especializaciones[i]}")
    
            print("\n🌳 Jardinería y exteriores")
            for i in range(17, 21):
                print(f"{i}. {especializaciones[i]}")
    
            print("\n🛠️ Servicios técnicos")
            for i in range(21, 27):
                print(f"{i}. {especializaciones[i]}")

            print("\n27. Otro")



        def main():
            mostrar_especializaciones()
    
            entrada = input("\nElegí tu especialización/es (en caso de ser más de una, separalas con coma): ")
            seleccion = entrada.split(",")
    
            especializaciones_asignadas = []
            otros_trabajos = []

            for item in seleccion:
                try:
                    numero = int(item.strip())
                    if numero == 27:
                        otros = input("📝 Ingresá el/los otro/s trabajo/s (separados por coma en caso de ser más de uno): ")
                        otros_trabajos += [x.strip() for x in otros.split(",") if x.strip()]
                    elif numero in especializaciones:
                        especializaciones_asignadas.append(especializaciones[numero])
                    
                    else:
                        print(f"❗ Opción inválida: {numero}")
                    
                except ValueError:
                    print(f"❗ Entrada no válida: {item}")

                resultado = especializaciones_asignadas + otros_trabajos

                especializaciones_asignadasPosta[:] = especializaciones_asignadas
                otrosTrabajosPosta[:] = otros_trabajos
            
            if resultado:
                print("\n✅ Elegiste:")
                for esp in resultado:
                    print("•", esp)
            else:
                print("\n⚠️ No asignaste ninguna especialización.")
            

        if __name__ == "__main__":
            main()

        for esp in especializaciones_asignadasPosta:
            if esp in especializaciones_booleans:
                especializaciones_booleans[esp] = True

        def crear_trabajador (nombre: str, apellido: str, telefono: int, cumpleaños: datetime, contraseña: str, mail: str, cv, Fontanero_Plomero, Electricista, Gasista_matriculado, Albañil, Carpintero, Pintor, Herrero, Techista, Impermeabilizador, Cerrajero, Instalador_de_aires_acondicionados, Instalador_de_alarmas, Instalador_de_cámaras_de_seguridad, Personal_de_limpieza, Limpieza_de_tanques_de_agua, Limpieza_de_vidrios_en_altura, Fumigador, LavadoDeAlfombras_cortinas, Jardinero, Podador_de_árboles, Mantenimiento_de_piletas, Paisajista, Técnico_de_electrodomésticos, Técnico_de_celulares, TécnicoDeComputadoras_laptops, TécnicoDeTelevisores_equiposelectrónicos, Técnico_de_impresoras, InstaladorDeRedes_WiFi, Otro
            ):
            doc_ref = db.collection("trabajadores").document(mail)
            doc_ref.set({
                "nombre": nombre,
                "apellido": apellido,
                "tel": telefono,
                "birth": cumpleaños,
                "contraseña": contraseña,
                "mail": mail,
                "cv": cv,

                "Fontanero_Plomero": Fontanero_Plomero,
                "Electricista": Electricista,
                "Gasista_matriculado": Gasista_matriculado,
                "Albañil": Albañil,
                "Carpintero": Carpintero,
                "Pintor": Pintor,
                "Herrero": Herrero,
                "Techista": Techista,
                "Impermeabilizador": Impermeabilizador,
                "Cerrajero": Cerrajero,
                "Instalador_de_aires_acondicionados": Instalador_de_aires_acondicionados,
                "Instalador_de_alarmas": Instalador_de_alarmas,
                "Instalador_de_cámaras_de_seguridad": Instalador_de_cámaras_de_seguridad,
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
                nombre = RTNombre,
                apellido = RTApellido,
                telefono = RTTel,
                cumpleaños = RTBirth,
                contraseña = RTContraseña,
                mail = RTMail,
                cv = RTCv,

                Fontanero_Plomero = especializaciones_booleans["Fontanero_Plomero"],
                Electricista = especializaciones_booleans["Electricista"],
                Gasista_matriculado = especializaciones_booleans["Gasista_matriculado"],
                Albañil = especializaciones_booleans["Albanil"],
                Carpintero = especializaciones_booleans["Carpintero"],
                Pintor = especializaciones_booleans["Pintor"],
                Herrero = especializaciones_booleans["Herrero"],
                Techista = especializaciones_booleans["Techista"],
                Impermeabilizador = especializaciones_booleans["Impermeabilizador"],
                Cerrajero = especializaciones_booleans["Cerrajero"],
                Instalador_de_aires_acondicionados = especializaciones_booleans["Instalador_aires_acondicionados"],
                Instalador_de_alarmas = especializaciones_booleans["Instalador_alarmas"],
                Instalador_de_cámaras_de_seguridad = especializaciones_booleans["Instalador_camaras_seguridad"],
                Personal_de_limpieza = especializaciones_booleans["Personal_limpieza"],
                Limpieza_de_tanques_de_agua = especializaciones_booleans["Limpieza_tanques_agua"],
                Limpieza_de_vidrios_en_altura = especializaciones_booleans["Limpieza_vidrios_altura"],
                Fumigador = especializaciones_booleans["Fumigador"],
                LavadoDeAlfombras_cortinas = especializaciones_booleans["Lavado_alfombras_cortinas"],
                Jardinero = especializaciones_booleans["Jardinero"],
                Podador_de_árboles = especializaciones_booleans["Podador_arboles"],
                Mantenimiento_de_piletas = especializaciones_booleans["Mantenimiento_piletas"],
                Paisajista = especializaciones_booleans["Paisajista"],
                Técnico_de_electrodomésticos = especializaciones_booleans["Tecnico_electrodomesticos"],
                Técnico_de_celulares = especializaciones_booleans["Tecnico_celulares"],
                TécnicoDeComputadoras_laptops = especializaciones_booleans["Tecnico_computadoras_laptops"],
                TécnicoDeTelevisores_equiposelectrónicos = especializaciones_booleans["Tecnico_televisores_equipos_electronicos"],
                Técnico_de_impresoras = especializaciones_booleans["Tecnico_impresoras"],
                InstaladorDeRedes_WiFi = especializaciones_booleans["Instalador_redes_WiFi"],
                Otro = otrosTrabajosPosta
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
                "contraseña": Contraseña,
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

conexion.commit()
cursor.close()
conexion.close()
