# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 12:10:01 2022

@author: Émile
"""
from st_aggrid import AgGrid
#streamlit-aggrid==0.2.3.post2
import streamlit as st
import pandas as pd
#import numpy as np
import datetime


st.image("https://regio-business.nl/media/3495018/NOVO-Logo.jpg")
st.write("""
         ***
         
         # Planning Generator
         
         Deze tool is gemaakt voor het genereren van een planning voor de productieafdeling van NOVO Packaging & Warehousing. Probeer zo veel mogelijk het originele databestand te gebruiken. Verander dus zo min mogelijk kolom- en rijnamen, met uitzondering van het toevoegen van extra personeel en taken.
         
         ***
         """)
st.text("")
st.text("")

uploaded_file = st.file_uploader("Selecteer hier het databestand")
if uploaded_file is not None:
    dataframe = pd.read_excel(uploaded_file)
    #AgGrid(dataframe)
    grid_return = AgGrid(dataframe, editable=True)
    new_df = grid_return['data']
    #st.write(dataframe)
    
    st.text("")  
    option = st.selectbox(
         'Hoe moet de planning eruit zien?',
         ('Iedereen doet waar hij het beste in is', 'Iedereen staat zo veel mogelijk op een machine waar hij nog over moet leren', 'Op de belangrijke taken staan goede mensen, op de rest staan beginners'))
    st.text("")
    options = st.multiselect(
         'Wie zijn er afwezig?',dataframe['Werknemers'])
         #['Ad-Hendrik', 'Rudy', 'Tamara', 'Hans'])
        
    
    st.text("")
    
    
    
    if st.checkbox('Planning genereren'):
         st.write('We zijn er mee bezig, nog een paar weken geduld alstublieft.')
         #HIER KOMT DE PLANNING
          
    #De planning krijgt hier een gepaste naam, waarna de planning te downloaden is via een button
    bestandsnaam = "".join(['planning ',str(datetime.datetime.now())[:16], '.csv'])
    st.download_button(
         label="Download planning als CSV",
         data=uploaded_file,
         file_name=bestandsnaam,
         mime='text/csv', )

#leegte om de disclaimer onderaan de pagina te krijgen
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
st.text("")

#De disclaimer
st.write("""
         ###### Disclaimer
         Deze tool is gemaakt door Rachelle Hermans en Emile Baljeu. Zij zijn, evenals Fontys Hogescholen, niet aansprakelijk voor mogelijke complicaties tijdens en/of na het gebruik van deze site. Ook hebben zij geen rechten voor het gebruiken van het logo op deze site, dus klaag ze alstublieft niet aan. Groetjes!""")
         
         
         
#OM TE RUNNEN:
#open terminal van ML via anaconda navigator
#typ: cd C:\Users\Émile\Desktop\School\TW3\Stage\python
#typ: streamlit run streamlit_stage.py

#hulplinkjes
#deploy de app https://www.youtube.com/watch?v=kXvmqg8hc70
#uitbreiden https://www.youtube.com/watch?v=JwSS70SZdyM
#streamlit documentatie https://docs.streamlit.io/library/get-started
#editable grid?????? https://github.com/PablocFonseca/streamlit-aggrid