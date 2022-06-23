from PIL import Image
import streamlit as st
from typing import List, Dict
import sqlite3
from streamlit.proto.DataFrame_pb2 import MultiIndex
import json
from fpdf import FPDF
from datetime import datetime,time
import base64

    ## Zarpa Pagina Web:
        # Para correr localmente:
        #   Requisitos:
        #   >= Python 3.8
        #       pip install streamlit
        #   probablemente:
        #       pip install fpdf
     # -> Para iniciar la página:
     #      streamlit run proto.py


########################################
    # mySQL init, funciones:

datab = sqlite3.connect('base.db')
c = datab.cursor()
def create_table():
  c.execute('CREATE TABLE IF NOT EXISTS mascotas_table (nombre TEXT,info TEXT,fecha TEXT, UNIQUE (nombre))')  
def add_data(nombre,info,fecha):
    c.execute('INSERT OR IGNORE INTO mascotas_table(nombre,info,fecha) VALUES (?,?,?)', (nombre,info,fecha))
    datab.commit()
def rem_data(nombre):
    c.execute(f'DELETE FROM mascotas_table WHERE nombre = {nombre}')
    datab.commit()
def view_all_notes():
    c.execute('SELECT * FROM mascotas_table')
    data = c.fetchall()
    return data
def get_data_nombre(nombre):
    c.execute(f'SELECT *  FROM mascotas_table WHERE nombre = "{nombre}"')   
    data = c.fetchall()
    return data 

########################################
custom_html ="""
<div style="background-color:#464e5f;padding:10px;border-radius:5px;margin:10px;">
<h3 style="color:white;text-align:center;">{}</h3>
<img src="http://www.esda.es/files/images/u576/logo53685.jpg" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;">
<h4> &nbsp;&nbsp;&nbsp;&nbsp;Descripción: {}</h4>
<h6> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;En Zarpa desde: {} </h6>
</div>
"""

create_table()
if 'mascotas' not in st.session_state:
    st.session_state['mascotas'] = {}
    st.session_state['idx'] = 0


def create_mascota(nombre: str, edad: int, raza: str, foto: str, descripcion="Hermoso animal listo para amar y jugar"):
    st.session_state.mascotas[str(nombre)] = {
        "edad": edad,
        "raza": raza,
        "descripcion": descripcion,
        "foto": foto,
    }
    now = datetime.now()
    hora = now.strftime("%H:%M:%S")
    add_data(nombre,descripcion,hora)
    return None

def print_mascota(nombre : str):
    st.markdown(f'## Datos de {nombre}')
    st.image(st.session_state.mascotas[nombre]['foto'])
    st.markdown("Descripción: "+ st.session_state.mascotas[nombre]['descripcion'])
    st.text('Edad: ' + str(st.session_state.mascotas[nombre]['edad']))
    return None

def nav_mascotas():
    id_nombre = [i for i in st.session_state.mascotas]
    name : str
    idx = st.session_state.idx

    button_izq, img, button_der = st.columns([0.75,4,0.5])
    if button_izq.button("<",help="anterior") and idx > 0: idx=idx-1 
    if button_der.button(">",help="siguiente") and idx < len(id_nombre)-1: idx=idx+1
    st.session_state.idx=idx

    with img:
        name = id_nombre[idx]
        st.text(f'idx: {idx}')
        print_mascota(name)

def generar_pdf(nombre, cedula, edad, mascota, direccion, adicional,fecha):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size = 14)
    pdf.set_title("Formulario Zarpa")
    now = datetime.now()
    hora = now.strftime("%H:%M:%S")
    pdf.set_author("Jean Pierre Vargas, Juan David Jimenez, David Penilla")
    pdf.image('./images/zarpa.jpg')
    pdf.cell(50,8,txt="Zarpa Fundacion\n")
    pdf.multi_cell(0,10,"\n\n        FORMULARIO DE ADOPCION\n\n")
    pdf.dashed_line(5,60,200,60,1,0)
    texto = f'''Yo, {nombre}, identificado con la cédula de ciudadanía {cedula},
    quiero adoptar a la mascota {mascota}. Tengo {edad} años de edad y resido en {direccion}.\n\n
    Adicional: {adicional}.\n\n
             Nombre Completo     |          Fecha   \n
            {nombre}              {fecha}\n\n\nFirma: '''
    pdf.multi_cell(0,6,texto,align='C')
    pdf.rect(115,140,60,12)
    pdf.text(125,170,f"Hora Local: {hora}")
    pdf.image(st.session_state.mascotas[mascota]['foto'],20,155,75,100)
    y_coord = pdf.get_y() 
    pdf.text(25,y_coord,txt=f'Mascota: {mascota}')
    
    pdf.output('formulario.pdf','F')

st.set_page_config(page_title='Zarpa',page_icon='🐶')

icono, titulo = st.beta_columns([0.5,4])
icono.image('./images/logo.jpg',output_format='JPG')
titulo.title(' Zarpa Fundación Animal')
titulo.markdown('####  Adopta, no compres.')

nombres = ["paco","socito","carlitos","firulais", 
"fiscalin pillin barbosa","esmadsito",
"biki","nicolas wilson stivenson","jampi","mafecabal"]

tipos = ["Chandoberman","Criollito","Bull Terrier",
"Salchicha","Pit Bull","Animal salvaje neonazi",
"gato","gato","gato","gato"]

edades = [3,1,4,1,5,9,2,6,5,3]

def montar_mascotas():
    for i in range(len(nombres)):
        if i < 6:
            create_mascota(nombres[i],edades[i],tipos[i],f"./images/dog{i+1}.jpg")
        else:
            create_mascota(nombres[i],edades[i],tipos[i],f"./images/cat{i-5}.jpg")
    
    with open("data.json","w") as outfile:
        data = json.dumps(st.session_state.mascotas)
        outfile.write(data)
    return None

montar_mascotas()
#create_mascota("paco",3,"chandoberman","./images/dog1.jpg")
#create_mascota("carlitos",1,"perrito","./images/dog2.jpg")


audio_fondo = open('./sonidos/firebird_lullaby.mp3','rb')
audio_bytes = audio_fondo.read()

st.sidebar.title('Navegación')
st.sidebar.audio(audio_bytes,format="audio/mp3")

if st.sidebar.button("Cargar Datos"):
    with open("data.json","r") as infile:
        data = infile.read()
        data = json.loads(data)

    st.sidebar.json(data)
    st.session_state.mascotas = data

if st.sidebar.button("Guardar datos"):
    with open("data.json","w") as outfile:
        data = json.dumps(st.session_state.mascotas)
        outfile.write(data)
    st.sidebar.markdown(" Datos guardados.")


opcion_menu : str = st.sidebar.radio(label='Menu Principal',
                      options = ['Inicio','Buscar','Adoptar'])

if opcion_menu == "Inicio":
    st.subheader("¿Por qué adoptar una mascota? ")
    st.markdown("$\qquad$ 1.Salvarás la vida de una Mascota")
    st.markdown("$\qquad$ 2.Le Harás la Vida más Feliz a la Mascota ")
    st.markdown("$\qquad$ 3.Se Mantiene en Funcionamiento el Refugio ")
    st.markdown("$\qquad$ 4.Evita la Promoción de las Tiendas de Ventas de Mascotas")
    st.header("\nConoce las mascotas en nuestra fundación ")
    nav_mascotas()
    st.markdown("$\qquad$ Recuerda, puedes ser __TU__ el que salva una **__VIDA__**")
    st.info( "Autores: David Penilla, Juan David Jimenez, Jean Pierre Vargas")



elif opcion_menu == "Buscar":
    st.subheader("    Encuentra la mascota que te gustó")
    search_ = st.text_input("Ingresar para buscar una mascota")
        
    if st.button("Buscar"):  
        info_result = get_data_nombre(search_)

        for i in info_result:
            a_name = i[0]
            a_descrip = i[1]
            a_fecha = i[2]              
            st.markdown(custom_html.format(a_name,a_descrip,a_fecha),unsafe_allow_html=True)

elif opcion_menu == "Adoptar":
    st.header("Formulario de Adopción Zarpa")
    with st.beta_expander("¿Cómo adoptar una mascota?"):
        st.markdown(r'''Para adoptar una mascota, debes llenar el siguiente formulario con tus datos,
una vez estes list@ para adoptar la mascota de tu gusto. 
Luego proceder a descargarlo llenado.''')
    nombre = st.text_input(label = 'Ingrese su nombre completo')
    cedula = st.text_input('Ingrese su cédula')
    nombress = tuple(nombres)
    mascota = st.selectbox(label = 'Me gustaria adoptar a:',options = nombress)
    edad = st.number_input('Ingrese su edad, recuerde: tiene que ser mayor que 18', step=1,min_value=18)
    direccion = st.text_input('Resido en:')
    adicional = st.text_input("¿Algo más que nos quieras decir? Por ejemplo, ¿A qué se dedica?")
    fecha = st.date_input("La fecha de hoy es: ", datetime(2021,7,6))
    video = st.file_uploader("Sube el video de tu motivación por la mascota.",type=["mp4","webm"], help=f"En este video, describe porqué quieres a {mascota}.")

    if st.checkbox("Mis datos están correctos.", value=False,help="¿Estás seguro?"):
        if st.button("Generar Formulario",help="Procede una vez seguro de tus datos."): 
            generar_pdf(nombre,cedula,edad,mascota,direccion,adicional,fecha)
            st.success("PDF Generado! Has iniciado una solicitud de adopción.")
            with open("formulario.pdf","rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = F'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
                st.markdown(pdf_display, unsafe_allow_html= True)

