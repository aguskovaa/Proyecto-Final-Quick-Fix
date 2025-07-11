import psycopg2
import tkinter as tk
from tkinter import filedialog
import webbrowser
import threading
import os
import time
import unidecode



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

            QHacer = input("Elegí una opción (1 o 2): ")
            MailTra = input("Ingresá el mail del trabajador: ")

            if QHacer == "1":
                cursor.execute('SELECT "CV" FROM trabajador WHERE "Mail" = %s', (MailTra,))
                CVA = cursor.fetchone()

                if CVA and CVA[0]:
                    rutaCVR = "CV_" + MailTra.replace("@", "_at_").replace(".", "_") + ".pdf"
                    with open(rutaCVR, "wb") as f:
                        f.write(CVA[0])
                    print(f"✅ CV recuperado y guardado como '{rutaCVR}'.")
                    
                    webbrowser.open(rutaCVR)

        else:
            print("❌ Datos incorrectos. Por favor, intentá nuevamente.")


elif opcion == "2":
   
    print("¿Qué querés ser?")
    print("1. Cliente")
    print("2. Trabajador")  
    print("3. Desempleado")  

    RProfesion = input("Elegí una opción (1, 2 o 3): ")
    
    if RProfesion == "1":
        cursor.execute('SELECT COUNT(*) FROM cliente')
        cantidad = cursor.fetchone()[0]

        if cantidad == 0:
            cursor.execute('ALTER SEQUENCE public.cliente_id_seq RESTART WITH 1')

        RCMail = input("Mail: ")

        cursor.execute('SELECT * FROM cliente WHERE "Mail" = %s', (RCMail,))
        existente = cursor.fetchone()

        while existente:
            print("❌ El mail ya está registrado. Ingresá otro mail:")
            RCMail = input("Mail: ")
            cursor.execute('SELECT * FROM cliente WHERE "Mail" = %s', (RCMail,))
            existente = cursor.fetchone()

        
        RCNombre = input("Nombre: ")
        RCApellido = input("Apellido: ")
        
        RCTel = input("Tel: ")
        
        cursor.execute('SELECT * FROM cliente WHERE "Tel" = %s', (RCTel,))
        existente = cursor.fetchone()

        while existente:
            print("❌ El telefono ya está registrado. Ingresá otro telefono:")
            RCTel = input("Tel: ")
            cursor.execute('SELECT * FROM cliente WHERE "Tel" = %s', (RCTel,))
            existente = cursor.fetchone()

        RCBirth = input("Fecha nacimiento (dejar espacio usando -): ")
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

        cursor.execute(
        'INSERT INTO cliente ("Nombre", "Apellido", "Tel", "Birth", "Contraseña", "Mail", "Latitud", "Longitud") VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
        (RCNombre, RCApellido, RCTel, RCBirth, RCContraseña, RCMail, RCLat, RCLng)
        
    
)
        
        print("✅ Te registraste bien. ¡Bienvenido,", RCNombre + "!")
    
    
    
    elif RProfesion == "2":

        cursor.execute('SELECT COUNT(*) FROM trabajador')
        cantidad = cursor.fetchone()[0]

        if cantidad == 0:
            cursor.execute('ALTER SEQUENCE public.trabajador_id_seq RESTART WITH 1')
            Devuelta = True
        
        else:
            Devuelta = False

            


        RTMail = input("Mail: ")

        cursor.execute('SELECT * FROM trabajador WHERE "Mail" = %s', (RTMail,))
        existente = cursor.fetchone()

        while existente:
            print("❌ El mail ya está registrado. Ingresá otro mail:")
            RTMail = input("Mail: ")
            cursor.execute('SELECT * FROM trabajador WHERE "Mail" = %s', (RTMail,))
            existente = cursor.fetchone()


        RTNombre = input("Nombre: ")
        RTApellido = input("Apellido: ")

        RTTel = input("Tel: ")
        
        cursor.execute('SELECT * FROM trabajador WHERE "Tel" = %s', (RTTel,))
        existente = cursor.fetchone()

        while existente:
            print("❌ El telefono ya está registrado. Ingresá otro telefono:")
            RTTel = input("Tel: ")
            cursor.execute('SELECT * FROM trabajador WHERE "Tel" = %s', (RTTel,))
            existente = cursor.fetchone()

        RTBirth = input("Fecha nacimiento (dejar espacio usando -): ")
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
            nombre = unidecode.unidecode(nombre)  # elimina tildes
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


        cursor.execute(
        'INSERT INTO trabajador ("Nombre", "Apellido", "Tel", "Birth", "Contraseña", "Mail", "CV") VALUES (%s, %s, %s, %s, %s, %s, %s)',
        (RTNombre, RTApellido, RTTel, RTBirth, RTContraseña, RTMail, psycopg2.Binary(RTCv))
        )
        
        id_especializacion = 0
        if Devuelta == True:
            id_especializacion = 1
        
        elif Devuelta == False:
            cursor.execute("SELECT MAX(trabajador_id) FROM trabajador")
            id_especializacion = cursor.fetchone()[0]  
        
        for esp in especializaciones_asignadasPosta:
            if esp in especializaciones_booleans:
                especializaciones_booleans[esp] = True

        cursor.execute(
        'INSERT INTO especializaciones ("especializaciones_id", "Mail", "Otro", "Fontanero / Plomero", "Electricista", "Gasista matriculado", "Albañil", "Carpintero", "Pintor", "Herrero", "Techista", "Impermeabilizador", "Cerrajero", "Instalador de aires acondicionados", "Instalador de alarmas", "Instalador de cámaras de seguridad", "Personal de limpieza ", "Limpieza de tanques de agua", "Limpieza de vidrios en altura", "Fumigador", "Lavado de alfombras / cortinas", "Jardinero", "Podador de árboles", "Mantenimiento de piletas", "Paisajista", "Técnico de electrodomésticos", "Técnico de celulares", "Técnico de computadoras / laptops", "Técnico de televisores / equipos electrónicos", "Técnico de impresoras", "Instalador de redes / WiFi") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
        (
        id_especializacion,
        RTMail,
        otrosTrabajosPosta,
        especializaciones_booleans["Fontanero_Plomero"],
        especializaciones_booleans["Electricista"],
        especializaciones_booleans["Gasista_matriculado"],
        especializaciones_booleans["Albanil"],
        especializaciones_booleans["Carpintero"],
        especializaciones_booleans["Pintor"],
        especializaciones_booleans["Herrero"],
        especializaciones_booleans["Techista"],
        especializaciones_booleans["Impermeabilizador"],
        especializaciones_booleans["Cerrajero"],
        especializaciones_booleans["Instalador_aires_acondicionados"],
        especializaciones_booleans["Instalador_alarmas"],
        especializaciones_booleans["Instalador_camaras_seguridad"],
        especializaciones_booleans["Personal_limpieza"],
        especializaciones_booleans["Limpieza_tanques_agua"],
        especializaciones_booleans["Limpieza_vidrios_altura"],
        especializaciones_booleans["Fumigador"],
        especializaciones_booleans["Lavado_alfombras_cortinas"],
        especializaciones_booleans["Jardinero"],
        especializaciones_booleans["Podador_arboles"],
        especializaciones_booleans["Mantenimiento_piletas"],
        especializaciones_booleans["Paisajista"],
        especializaciones_booleans["Tecnico_electrodomesticos"],
        especializaciones_booleans["Tecnico_celulares"],
        especializaciones_booleans["Tecnico_computadoras_laptops"],
        especializaciones_booleans["Tecnico_televisores_equipos_electronicos"],
        especializaciones_booleans["Tecnico_impresoras"],
        especializaciones_booleans["Instalador_redes_WiFi"]
    )
        )
  
        print("✅ Te registraste bien. ¡Bienvenido,", RTNombre + "!")
    
    elif RProfesion == "3":
        RDMail = input("Mail: ")
        cursor.execute('SELECT * FROM cliente WHERE "Mail" = %s', (RDMail,))
        existente = cursor.fetchone()

        while existente:
            print("❌ El mail ya está registrado. Ingresá otro mail:")
            RDMail = input("Mail: ")
            cursor.execute('SELECT * FROM desempleado WHERE "Mail" = %s', (RDMail,))
            existente = cursor.fetchone()


        RDNombre = input("Nombre: ")
        RDApellido = input("Apellido: ")
        print("¿Terminaste el secundario?")
        print("1. Si")
        print("2. No")
        RDSecundaria = input("Elegí una opción (1 o 2): ")

        if RDSecundaria == 1:
            RDSecundaria = True

        elif RDSecundaria == 2:
            RDSecundaria = False
        
        RDBirth = input("Fecha nacimiento (dejar espacio usando -): ")
        RDContraseña = input("Contraseña: ")
        print("Selecciona tu CV en formato PDF")
        ruta_archivo = seleccionar_pdf()
        if ruta_archivo:
            with open(ruta_archivo, "rb") as f:
                RDCv = f.read()


        
 

else:
    print("No es una opción")

conexion.commit()
cursor.close()
conexion.close()
