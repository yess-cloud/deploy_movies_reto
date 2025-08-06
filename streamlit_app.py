import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import numpy as np

import json
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="movies-project-reto")

st.header("Netflix App")

#Leer en un data frame todos los registros de Firestore
@st.cache_data
def load_all_data():
    docs = db.collection("movies").stream()
    data = [doc.to_dict() for doc in docs]
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame()

# Cargar todos los datos al inicio
data = load_all_data()

#Crear sidebar del dashboard
sidebar = st.sidebar

# Componente checkbox para mostrar todos los filmes
agree = sidebar.checkbox("Mostrar todos los filmes")
if agree:
    st.subheader("Todos los filmes")
    if not data.empty:
        st.dataframe(data)
    else:
        st.info("No hay filmes para mostrar.")

# Búsqueda por título del filme
st.subheader("Buscar filmes por título")
myname = st.text_input('Título del filme')
search_button = st.button("Buscar")

if search_button:
    if myname:
        # Filtrar el DataFrame 'data' directamente
        if not data.empty:
            filtered_data_byname = data[data['name'].str.contains(myname, case=False, na=False)]
            count_row = filtered_data_byname.shape[0]
            st.write(f"Total de filmes encontrados: {count_row}")
            if not filtered_data_byname.empty:
                st.dataframe(filtered_data_byname)
            else:
                st.info("No se encontraron filmes con ese título.")
        else:
            st.info("No hay datos para buscar.")
    else:
        st.warning("Por favor, ingresa un título para buscar.")
        
# Componente para filtrar por director
st.subheader("Filtrar por director")
if not data.empty:
    selected_director = st.selectbox("Seleccionar director:", data['director'].unique())
    btnFilterbyDirector = st.button('Filtrar por director')

    if btnFilterbyDirector:
        filtered_data_bydirector = data[data['director'] == selected_director]
        count_row = filtered_data_bydirector.shape[0]
        st.write(f"Total de filmes: {count_row}")
        st.dataframe(filtered_data_bydirector)
else:
    st.info("No hay datos para filtrar por director.")

# Componente para insertar nuevo filme
st.subheader("Insertar nuevo filme")
name = st.text_input("Nombre del filme")
company = st.text_input("Compañía")
genre = st.text_input("Género")
director = st.text_input("Director") # Añadí un campo para el director

submit = st.button("Crear nuevo filme")

if submit:
    if name and company and genre and director:
        doc_ref = db.collection("movies").document(name)
        doc_ref.set({
            "name": name,
            "company": company,
            "genre": genre,
            "director": director
        })
        st.success(f"El filme '{name}' ha sido agregado correctamente.")
        st.experimental_rerun()
    else:
        st.warning("Por favor, completa todos los campos para crear un nuevo filme.")
