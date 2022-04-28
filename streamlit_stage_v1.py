# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 12:10:01 2022

@author: Émile
"""
import streamlit as st
import pandas as pd
#import numpy as np
import datetime

#OM TE RUNNEN:
#open terminal van ML via anaconda navigator
#typ: cd C:\Users\Émile\Desktop\School\TW3\Stage\python
#typ: streamlit run streamlit_stage.py
st.image("https://regio-business.nl/media/3495018/NOVO-Logo.jpg")
st.title('Planning Generator')
st.text("")
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    dataframe = pd.read_excel(uploaded_file)
    #st.write(dataframe)
    bestandsnaam = "".join(['planning ',str(datetime.datetime.now())[:16], '.csv'])
    st.download_button(
         label="Download planning als CSV",
         data=uploaded_file,
         file_name=bestandsnaam,
         mime='text/csv', )    
st.text("")  
option = st.selectbox(
     'Hoe moet de planning eruit zien?',
     ('Iedereen doet waar hij het beste in is', 'Iedereen staat zo veel mogelijk op een machine waar hij nog over moet leren', 'Op de belangrijke taken staan goede mensen, op de rest staan beginners'))
st.text("")
options = st.multiselect(
     'Wie zijn er afwezig?',
     ['Ad-Hendrik', 'Rudy', 'Tamara', 'Hans'])

st.text("")



if st.checkbox('Planning genereren'):
     st.write('We zijn er mee bezig, nog een paar weken geduld alstublieft.')
     if st.checkbox('Wil je dit moment vereeuwigen?'):
          st.write('Oke dan! ga je gang :)')
          picture = st.camera_input("Take a picture")
          if picture:
              st.image(picture)

              btn = st.download_button(
                             label="Download de foto",
                             data=picture,
                             file_name="Stage_is_leuk.png",
                             mime="image/png")
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
#deploy de app https://www.youtube.com/watch?v=kXvmqg8hc70

st.write("Deze tool is gemaakt door Rachelle Hermans en Emile Baljeu. Zij zijn, evenals Fontys Hogescholen, niet aansprakelijk voor mogelijke complicaties tijdens en/of na het gebruik van deze site. Ook hebben zij geen rechten voor het gebruiken van het logo op deze site, dus klaag ze alstublieft niet aan. Groetjes!")
st.image("https://raw.githubusercontent.com/emile-stage/Stage/main/Stage_is_leuk.png")
