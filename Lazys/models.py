from tkinter import ttk, filedialog
from tkinter import *
import os
import pathlib
import sqlite3
import laspy as lp
import numpy as np
from db import *
import db
from sqlalchemy import Column, Integer, String, Boolean
import pandas as pd
import openpyxl



class FicheroLazLas:

    def __init__(self, root):
        self.ventana = root
        self.ventana.title("Lazys App")
        self.ventana.resizable(1,1)
        self.ventana.wm_iconbitmap("recursos/perezoso.ico")

        # Frame principal
        frame = LabelFrame(self.ventana, text="Lectura de ficheros LAZ/LAS")
        frame.grid(row=0, column=0, columnspan=4, pady=20)

        #Frame tabla
        frameTabla = LabelFrame(self.ventana)
        frameTabla.grid(row=4, column=0, columnspan=4, pady=20)


        # Label Seleccion de ficheros
        self.etiqueta_select_ficheros = Label(frame, text="Seleccionar ficheros LAZ/LAS")
        self.etiqueta_select_ficheros.grid(row=1, column=0)
        # Boton de busqueda de ficheros
        self.busqueda_ficheros = ttk.Button(frame, text="Lectura carpeta...", command=self.input_info_db)
        self.busqueda_ficheros.grid(row=1, column=1, columnspan=2, sticky=W + E)

        # Label Nombre Proyecto
        self.etiqueta_nom_proyecto =Label(frame, text = "Nombra la exportación")
        self.etiqueta_nom_proyecto.grid(row=2, column=0)
        # Entry Nombre Proyecto
        self.nom_proyecto = Entry(frame)
        self.nom_proyecto.focus()
        self.nom_proyecto.grid(row=2, column=1, columnspan=3, sticky= W +E)

        # Boton de Exportar Fichero DB
        self.boton_exportar_lectura = ttk.Button(frame, text = "Exportar...", command= self.eleccion_exportar)
        self.boton_exportar_lectura.grid(row = 3, column=0, columnspan=1, sticky= W + E)

        # Tipo de ficheros a exportar
        self.boton_eleccion_exportar = ttk.Combobox(frame,state="readonly", values=["Excel","CSV" ,"JSON"])
        self.boton_eleccion_exportar.grid(row=3, column=1, columnspan=2, sticky=W + E)


        # Label de Validacion
        self.mensaje = Label(text="",fg="red")
        self.mensaje.grid(row=1, column=1, columnspan=2, sticky=W + E)

        # Tabla de variables LiDAR
        # Estilo personalizado para la tabla creado por nosotros
        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 10))
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 12, 'bold'))
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

        # Estructura de la tabla
        self.tabla = ttk.Treeview(frameTabla,
                                  height=20,
                                  columns=[f"{n}" for n in range(0, 6)],
                                  style="mystyle.Treeview")

        self.tabla.grid(row=5, column=0, columnspan=3)
        self.tabla.heading("#0", text="Nombre Fichero", anchor=CENTER)
        self.tabla.heading("#1", text="Nº Retornos", anchor=CENTER)
        self.tabla.heading("#2", text="Ptos.Suelo R1", anchor=CENTER)
        self.tabla.heading("#3", text="Ptos.Suelo R2", anchor=CENTER)
        self.tabla.heading("#4", text="Ptos.Suelo R3", anchor=CENTER)
        self.tabla.heading("#5", text="Altitud MIN", anchor=CENTER)
        self.tabla.heading("#6", text="Altitud MAX", anchor=CENTER)

        # Boton de Añadir 1 registro completo
        self.boton_aniadir = ttk.Button(frameTabla, text="AÑADIR REGISTRO", command= self.aniadir_info)
        self.boton_aniadir.grid(row=6, sticky=W + E)

        # Boton de Eliminar 1 registro completo
        self.boton_eliminar = ttk.Button(frameTabla, text="ELIMINAR REGISTRO", command=self.del_registro)
        self.boton_eliminar.grid(row=6, column=1, sticky= W + E)

        # Boton de Eliminar Registros de la BBDD
        self.boton_eliminarBBDD = ttk.Button(frameTabla, text="LIMPIAR BBDD", command=self.restart_db)
        self.boton_eliminarBBDD.grid(row=6, column=2, sticky=W + E)

        self.get_datosFicheros()


    # Encontrar y selecionar los ficheros en carpetas
    def directorio_carpeta(self):
        # Obtener la carpeta donde estan los ficheros
        carpeta = filedialog.askdirectory()
        if carpeta != "":
            os.chdir(carpeta)
            return os.getcwd()

    def crear_rutas_ficheros(self):
        lista_rutas_ficheros = []
        carpeta = pathlib.Path(self.directorio_carpeta())
        laslaz = ['*.las', '*.laz']
        for extension in laslaz:
            for f in carpeta.glob(extension):
                lista_rutas_ficheros.append(f)
        return lista_rutas_ficheros


    # Lectura de los archivos LAZ/LAS, varaibles a mostrar
    # Las funciones leeran 1 unico fichero
    def readlazlas_nombrefichero(self, rutafichero):
        nombre = os.path.basename(rutafichero)
        return nombre

    def readlazlas_retornos(self, rutafichero):
        with lp.open(rutafichero) as fh:
            retornos = fh.header.point_count
            return retornos

    def readlazlas_ptosSuelo(self, rutafichero):
        with lp.open(rutafichero) as fh:
            las = fh.read()
            ground_pts = las.classification == 2
            bins, counts = np.unique(las.return_number[ground_pts], return_counts=True)
            for r, c in zip(bins, counts):
                if r == 1:
                    ptossueloR1 = int(c)
                elif r == 2:
                    ptossueloR2 = int(c)
                elif r == 3:
                    ptossueloR3 = int(c)

            return ptossueloR1, ptossueloR2, ptossueloR3

    def readlazlas_altitud(self, rutafichero):

        point_cloud = lp.read(rutafichero)
        pointsZ = np.vstack((point_cloud.z)).transpose()

        altitudMax = np.max(pointsZ)
        altitudMin = np.min(pointsZ)

        return altitudMax, altitudMin

    # El metodo que extraera de golpe todas las variables de 1 fichero LAZ/LAS
    def lectura_variables_fichero(self, fichero):
        namefich = self.readlazlas_nombrefichero(fichero)
        retornos = self.readlazlas_retornos(fichero)
        sueloR1, sueloR2, sueloR3 = self.readlazlas_ptosSuelo(fichero)
        altMax, altMin = self.readlazlas_altitud(fichero)

        return namefich, retornos, sueloR1, sueloR2, sueloR3, altMax, altMin

    # Este metodo tarda algo en ejecutarse, mueve muchos datos de golpe
    def lectura_masiva_ficheros(self):
        lista_lecturas_ficheros = []
        for ruta in self.crear_rutas_ficheros():
            namefich, retornos, sueloR1, sueloR2, sueloR3, altMax, altMin = self.lectura_variables_fichero(ruta)
            lista_lecturas_ficheros.append([namefich, retornos, sueloR1, sueloR2, sueloR3, altMax, altMin])
        return lista_lecturas_ficheros


    # Metodos de introduccion de los datos generados
    def input_info_db(self, listainfo = [[]]):
        listainfo = self.lectura_masiva_ficheros()
        for fichero in listainfo:
            datoslaslaz = DatosLAZLAS( nombreFichero = fichero[0],
                                       numRetornos =fichero[1],
                                       ptoSuelo_R1 = fichero[2],
                                       ptoSuelo_R2 =fichero[3],
                                       ptoSuelo_R3=fichero[4],
                                       altMax = fichero[5],
                                       altMin =fichero[6])
            db.session.add(datoslaslaz)
            db.session.commit()
            db.session.close()
        self.get_datosFicheros()

        self.mensaje["text"] = "Información registrada"
        return

    def db_consulta(self):
        resultado = db.session.query(DatosLAZLAS).all()
        db.session.close()
        return resultado


    def get_datosFicheros(self):
        registros_tabla = self.tabla.get_children()
        for i in registros_tabla:
            self.tabla.delete(i)

        registros = self.db_consulta()
        for i in registros:
            self.tabla.insert("", 0, text=i.nombreFichero, values=(i.numRetornos,
                                                                   i.ptoSuelo_R1,
                                                                   i.ptoSuelo_R2,
                                                                   i.ptoSuelo_R3,
                                                                   i.altMax,
                                                                   i.altMin))


    # Añadir 1 registro seleccionado por el usuario
    def aniadir_info(self):
        ficheroAniadir = filedialog.askopenfilename(initialdir="/", title= "Selecione archivo",
                                                    filetypes=(("LAZ files", ".laz"), ("LAS files", ".las")))

        # Leer las variables de ese fichero
        lista_lecturas_ficheros = []
        namefich, retornos, sueloR1, sueloR2, sueloR3, altMax, altMin = self.lectura_variables_fichero(ficheroAniadir)
        lista_lecturas_ficheros.append([namefich, retornos, sueloR1, sueloR2, sueloR3, altMax, altMin])

        # Añadimos a BBDD
        for fichero in lista_lecturas_ficheros:
            datoslaslaz = DatosLAZLAS( nombreFichero = fichero[0],
                                       numRetornos =fichero[1],
                                       ptoSuelo_R1 = fichero[2],
                                       ptoSuelo_R2 =fichero[3],
                                       ptoSuelo_R3=fichero[4],
                                       altMax = fichero[5],
                                       altMin =fichero[6])
            db.session.add(datoslaslaz)
            db.session.commit()
            db.session.close()

        # Mostramos los cambios en la aplicacion
        self.get_datosFicheros()

        self.mensaje["text"] = "Fichero AÑADIDO correctamente"


    # Eliminar un registro
    def del_registro(self):
        nombrefichero = self.tabla.item(self.tabla.selection())['text']
        print(nombrefichero)
        db.session.query(DatosLAZLAS).filter_by(nombreFichero = nombrefichero).delete()
        db.session.commit()
        db.session.close()
        self.get_datosFicheros()
        self.mensaje['text'] = "Registro ELIMINADO correctamente"


    # Limpiar y borrar toda la BBDD
    def restart_db(self):
        registros = self.db_consulta()
        for i in registros:
            print(i)
            db.session.query(DatosLAZLAS).filter_by(nombreFichero = i.nombreFichero).delete()
            db.session.commit()
            db.session.close()

        self.mensaje['text'] = "Todos los registros han sido borrados de la BBDD"
        self.get_datosFicheros()


    # Funciones de exportacion de los datos de la BBDD a otros gestores de informacion
    def df_datoslazys(self):
        df_datos = pd.read_sql_table(table_name="datos_Lazys", con= engine)
        return df_datos

    def export_to_xlsx(self):
        df_datos = self.df_datoslazys()

        if self.validacion_nombreExport() == False:
            self.mensaje['text'] = "Debe introducir un nombre al fichero para poder exportarlo"

        elif self.validacion_nombreExport() == True:
            nombreProyecto = self.nom_proyecto.get()

            with pd.ExcelWriter(f"{nombreProyecto}.xlsx") as excel_lazlas:
                df_datos.to_excel(excel_lazlas,
                                  index = False, header = True, sheet_name='Variables LiDAR', encoding="utf-8")
                excel_lazlas.save()

            self.mensaje['text'] = "Archivo Excel exportado correctamente"

    def export_to_csv(self):
        df_datos = self.df_datoslazys()

        if self.validacion_nombreExport() == False:
            self.mensaje['text'] = "Debe introducir un nombre al fichero para poder exportarlo"

        elif self.validacion_nombreExport() == True:

            nombreProyecto = self.nom_proyecto.get()
            df_datos.to_csv(f"{nombreProyecto}.csv", index= False, sep= ';', encoding='utf-8')
            self.mensaje['text'] = "Archivo CSV exportado correctamente"

    def export_to_json(self):
        df_datos = self.df_datoslazys()

        if self.validacion_nombreExport() == False:
            self.mensaje['text'] = "Debe introducir un nombre al fichero para poder exportarlo"

        elif self.validacion_nombreExport() == True:

            nombreProyecto = self.nom_proyecto.get()
            df_datos.to_json(f"{nombreProyecto}.json")
            self.mensaje['text'] = "Archivo JSON exportado correctamente"

    def eleccion_exportar(self):
        eleccion_ususario = self.boton_eleccion_exportar.get()

        if eleccion_ususario == "Excel":
            self.export_to_xlsx()
        elif eleccion_ususario == "CSV":
            self.export_to_csv()
        elif eleccion_ususario == "JSON":
            self.export_to_json()

        elif self.validacion_tipoExport()== False:
            self.mensaje['text'] = "Debes elegir el TIPO DE EXPORTACIÓN"

        else:
            self.mensaje['text'] = "ERROR DE EXPORTACIÓN"

    def validacion_nombreExport(self):
        nombre_exportacion_ususario = self.nom_proyecto.get()
        return len(nombre_exportacion_ususario) != 0

    def validacion_tipoExport(self):
        tipo_exportacion_usuario = self.boton_eleccion_exportar.get()
        return len(tipo_exportacion_usuario) != 0


'''
Creamos una clase llamada DatosLAZLAS
Esta clase va a ser nuestro modelo de datos de los datos leidos (el cual nos servirá 
luego para la base de datos)
Esta clase va a almacenar toda la información referente a cada unos de los ficheros que leamos
'''
class DatosLAZLAS(db.Base):
    __tablename__ = "datos_Lazys"
    id = Column(Integer, primary_key=True)
    nombreFichero = Column(String(200), nullable=False) # Nombre de cada fichero leido
    numRetornos = Column(Integer, nullable=False) # Numero de Retornos totales que hay en el fichero
    ptoSuelo_R1 = Column(Integer, nullable = False) # Puntos clasificados como suelo en el 1º retorno
    ptoSuelo_R2 = Column(Integer, nullable=False) # Puntos clasificados como suelo en el 2º retorno
    ptoSuelo_R3= Column(Integer, nullable=False) # Puntos clasificados como suelo en el 3º retorno
    altMax = Column(Integer, nullable = False) # La altitud maxima que tiene los puntos
    altMin = Column(Integer, nullable = False) # La altitud minima que tiene los puntos

    def __init__(self, nombreFichero, numRetornos, ptoSuelo_R1, ptoSuelo_R2, ptoSuelo_R3, altMax, altMin ):
        self.nombreFichero = nombreFichero
        self.numRetornos = numRetornos
        self.ptoSuelo_R1 = ptoSuelo_R1
        self.ptoSuelo_R2 = ptoSuelo_R2
        self.ptoSuelo_R3 = ptoSuelo_R3
        self.altMax = altMax
        self.altMin = altMin

    def __getitem__(self, item):
        return item[0]


    def __str__(self):
        return """El fichero {} contiene las siguiente caracteristicas: 
            \nNumero de retornos : {} retornos
            \nPuntos clasificados como suelo en los retornos:
            \n\t1º: {}
            \n\t2º: {}
            \n\t3º: {}
            \nAltitud Maxima: {} metros
            \nAltitud Minima: {} metros""".format(self.nombreFichero,
                                                  self.numRetornos,
                                                  self.ptoSuelo_R1,
                                                  self.ptoSuelo_R2,
                                                  self.ptoSuelo_R3,
                                                  self.altMax,
                                                  self.altMin)