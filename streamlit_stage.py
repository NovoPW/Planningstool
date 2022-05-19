# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 12:10:01 2022

@author: Émile
"""
import datetime
import numpy as np
import pandas as pd
import streamlit as st

#from sys import exit
from io import BytesIO
from st_aggrid import AgGrid
from itertools import product
from collections import defaultdict
from mip import Model, xsum, minimize, maximize, BINARY, CBC, OptimizationStatus, INTEGER

# =============================================================================
# TODO:
# de vooraf ingevulde aanwezigheid (bij bijv. data aanpassen) meenemen als default value bij selectere bijv. afwezigen
# de capaciteit moet aangepast kunnen worden voor alle machines die aanstaan!!!!!!!!!!!!!!!!!!!!!!!
# het conceptueel model van rachelle moet nog toegevoegd worden
# logo van krant afhalen en verplaatsen naar github?
# machines op bepaalde dagen standaard op aanwezig?
# Hoofdletters in de dataset toevoegen
# =============================================================================


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
    dataframe = pd.read_excel(uploaded_file, sheet_name='Werknemers')
    dataframe2 = pd.read_excel(uploaded_file, sheet_name='Taken')
    
    if st.checkbox('Ruwe data bewerken'):
        grid_return = AgGrid(dataframe, editable=True)
        new_df = grid_return['data']

    else:
        new_df = dataframe
    
    
    st.text("")  
    
    
    
    st.write("""
             ***
             ### Werknemers informatie
             ***
             """)
    
    dagen = ['maandag', 'dinsdag', 'woensdag', 'donderdag','vrijdag', 'zaterdag', 'zondag']
    vandaag_i = datetime.datetime.today().weekday()
    dagen2 = dagen[vandaag_i:7]+dagen[0:vandaag_i]
    dag = st.selectbox(
         'Voor wanneer is de planning?',dagen2)
    
    vandaag = dagen[vandaag_i]
    
    vrije_mensen = []
    for i in range(len(new_df["vrije dagen"])):
        if str(new_df["vrije dagen"][i]) != 'nan':
            vrije_dagen = new_df["vrije dagen"][i].lower().split()
            if dag in vrije_dagen:
                vrije_mensen.append(new_df["Werknemers"][i])
    
    if st.checkbox("TESTKNOP EMILE AFWEZIGEN OVERNEMEN OM TE CHECKEN"):
        vrije_mensen = list(new_df["Werknemers"][new_df["Aanwezig"]==0])
    afwezigen = st.multiselect(
         'Wie zijn er afwezig?',new_df['Werknemers'],vrije_mensen)
    #afwezigen verwerken:
    for i in range(len(new_df["Werknemers"])):
        if new_df["Werknemers"][i] in afwezigen:
            new_df["Aanwezig"][i] = 0
        else:
            new_df["Aanwezig"][i] = 1
    
    
    st.text("")
    
    if st.checkbox("Wil je zelf het aantal uitzendkrachten opgeven?"):
        uitzendkrachten = st.number_input("Hoeveel uitzendkrachten zijn er?",min_value=0, value = 1, step = 1)
        for i in range(int(uitzendkrachten)):
            uitzendkracht_skills = ["".join(["Uitzendkracht ",str(i)]),1,0,1,0,0] + list(np.ones(len(new_df.columns)-6)*3)
            df_uitzendkracht_skills = pd.DataFrame(uitzendkracht_skills).transpose()
            df_uitzendkracht_skills.columns = new_df.columns
            new_df = pd.concat([new_df, df_uitzendkracht_skills], ignore_index = True)
    else:
        uitzendkrachten = 0
    st.text("")
    
    grid_return = AgGrid(new_df, editable=False)
    
    for i in range(10):
        st.text("")
    
    
    st.write("""
             ***
             ### Taken informatie
             ***
             """)
    
    st.text("")
             
    
    if st.checkbox('Ruwe taken-data bewerken'):
        #grid_return = AgGrid(dataframe, editable=True)
        #new_df = grid_return['data']

        grid_return2 = AgGrid(dataframe2, editable=True)
        new_df2 = grid_return2['data']
    else:
        #new_df = dataframe
        new_df2 = dataframe2
    
    vooraf_aanwezig = list(new_df2["Taken"][new_df2["Aan"]==1])
    aanwezige_taken = st.multiselect(
         'Welke taken moeten er gedaan worden?',new_df2['Taken'],vooraf_aanwezig)
    #aanwezige taken verwerken:
    for i in range(len(new_df2["Taken"])):
        if new_df2["Taken"][i] in aanwezige_taken:
            new_df2["Aan"][i] = 1
        else:
            new_df2["Aan"][i] = 0
    
    
    st.write("Hoeveel mensen zijn er nodig op elke taak?")

    grid_return4 = AgGrid(new_df2[['Taken','Aantal']][new_df2['Aan']==1], editable=True, fit_columns_on_grid_load=True)
    temp = grid_return4['data']
    for i in new_df2['Taken'][new_df2['Aan']==1]:
        new_df2.loc[new_df2['Taken']==i,'Aantal'] = int(temp['Aantal'][temp['Taken']==i])
    
    for i in range(10):
        st.text("")
    st.write("""
             ***
             ### Planning maken en opslaan
             ***
             """)        
    
    st.text("")
    doelfunctie_keuzebox = st.selectbox(
         'Hoe moet de planning eruit zien?',
         ('Iedereen doet waar hij het beste in is', 'Iedereen staat zo veel mogelijk op een machine waar hij nog over moet leren', 'Op de belangrijke taken staan goede mensen, op de rest staan beginners'))
    st.text("")
    st.text("")
    
    if st.checkbox('Planning genereren'):
        if len(new_df[new_df['Aanwezig'] == 1]) != sum(new_df2[new_df2['Aan']==1]['Aantal']):
            aantal_werknemers = len(new_df[new_df['Aanwezig'] == 1])
            aantal_benodigd_voor_taken = sum(new_df2[new_df2['Aan']==1]['Aantal'])
            
            grid_return62 = AgGrid(new_df, editable=False, key=(999))
            grid_return54 = AgGrid(new_df2, editable=False, key = (1000))
            
            
            
            st.error(f'WARNING: Het aantal werknemers is niet gelijk aan het benodigde aantal werknemers voor alle taken. Er zijn {aantal_werknemers} werknemers aanwezig en er zijn {aantal_benodigd_voor_taken} werknemers nodig om alle taken af te kunnen ronden')
        else:
            #st.write('We zijn er mee bezig, nog een paar weken geduld alstublieft.')
            data_werknemers = new_df
            data_machines = new_df2
            
            
# =============================================================================
# =============================================================================
# =============================================================================
# # #             HIER KOMT HET WISKUNDIG MODEL
# =============================================================================
# =============================================================================
# =============================================================================
            
# =============================================================================
#             ''' Data prepareren'''
# =============================================================================

            # check: zijn er genoeg mensen om op de machines te zetten?
            #if len(data_werknemers[data_werknemers['Aanwezig'] == 1]) != sum(data_machines[data_machines['Aan']==1]['Aantal']):
            #    exit('WARNING: Het aantal werknemers is niet gelijk aan het benodigde aantal werknemers voor alle taken.')

            # dataframes aanpassen aan de aanwezige werkenemers
            data_aanwezig = data_werknemers.loc[data_werknemers['Aanwezig'] == 1,:]
            data_taken = data_machines.loc[data_machines['Aan']==1,:]

            # wanneer er bij werknemers geen specifieke taak is gegeven, maken we hier taak -1 van
            data_aanwezig.loc[data_aanwezig['Taak'].isna(),'Taak'] = -1

            # de overige ('rest') benodigde competenties verwerken
            for i in data_taken.index:
                # hoeveel mensen er per niveau er al minimaal moeten zijn
                ingepland = data_taken.Aantal_min_niveau_2[i]+data_taken.Aantal_min_niveau_1[i]+data_taken.Aantal_min_niveau_3[i]
                # kijken of er sprake is van een minimaal niveau van de rest/overige
                if data_taken.Aantal[i] > ingepland:
                    # als er iets staat als: 1v1, 2v2 en DE REST NIVEAU 2,dan plannen we hier de 'rest' op niveau 2.
                    # bepaal eerst het restant werknemers, hier genaamd 'overig'
                    niet_ingedeeld = data_taken.Aantal[i] - ingepland
                    data_taken.loc[i,"".join(("Aantal_min_niveau_", str(int(data_taken.Rest_min_niveau[i]))))] += niet_ingedeeld


            # dataframe met alleen competenties
            df_comp = data_aanwezig.loc[:,data_taken.Taken]


            # =============================================================================


# =============================================================================
#             '''Wiskundig model (1): sets en parameters opstellen'''
# =============================================================================

            # Set van taken, levels en werknemers maken
            levels = range(1,4)
            taken = data_taken.index
            werknemers = data_aanwezig.index

            # parameter aanmaken die zegt of een werknemer een bepaald level op een taak bezit
            vorm_skill = list(product(levels, werknemers, taken))
            skill = np.zeros(len(vorm_skill))

            for taak in taken:
                naam_taak = data_taken.Taken[taak]
                for werknemer in werknemers:
                    for level in levels:
                        
                        if df_comp.loc[werknemer,naam_taak] <= level:
                            ind = vorm_skill.index((level,werknemer,taak))
                            skill[ind] = 1


                            
            # aantal mensen die per level per taak nodig zijn (minimaal niveau)             
            vorm_teamsize = list(product(levels, taken))
            teamsize = np.zeros(len(vorm_teamsize))
            for taak in taken:
                for level in levels:
                    kolomnaam = "".join(("Aantal_min_niveau_", str(level)))
                    aantal = data_taken.loc[taak,kolomnaam]
                    ind = vorm_teamsize.index((level,taak))
                    teamsize[ind] = aantal
                    
                    
            # parameter die aangeeft of 2 mensen samen kunnen werken
            vorm_taal = list(product(werknemers, werknemers))
            taal = np.ones(len(vorm_taal))
            for werknemer1 in werknemers[:-1]:
                for werknemer2 in werknemers[1:]:
                    if ((data_aanwezig.Nederlands[werknemer1] + data_aanwezig.Nederlands[werknemer2] == 2) 
                        or (data_aanwezig.Pools[werknemer1] + data_aanwezig.Pools[werknemer2] == 2)):
                        ind = vorm_taal.index((werknemer1,werknemer2))
                        taal[ind] = 0
           
                        
                
            # =============================================================================
                
                        
# =============================================================================
#             '''Wiskundig model (2): model met beslisvariabele, constraints en doelfunctie opstellen'''
# =============================================================================

                        
            # model opstellen
            model = Model(solver_name=CBC) 
            
            # beslisvariabele opstellen
            X = [model.add_var(name="x({},{},{})".format(l,w,t), var_type=BINARY) 
                 for [l, w, t] in product(levels, werknemers, taken)] 
            
            T = [model.add_var(name="t({},{},{})".format(i,j,t), var_type=BINARY) 
                 for [i, j, t] in product(werknemers, werknemers, taken)] 
            vorm_T = list(product(werknemers, werknemers, taken))
            
            
            if doelfunctie_keuzebox == 'Iedereen doet waar hij het beste in is':
                # DOELFUNCTIE 1 opstellen (in dit geval zo min mogelijk kosten) #########################################################
                model.objective = maximize(xsum(X[vorm_skill.index((1,w,t))] for w in werknemers for t in taken))
                
            if doelfunctie_keuzebox == 'Iedereen staat zo veel mogelijk op een machine waar hij nog over moet leren':
                # DOELFUNCTIE 2 opstellen (in dit geval zo veel mogelijk bij de minimum eisen) ##########################################
                U = [model.add_var(name="u({},{})".format(l,t), var_type=INTEGER) 
                     for [l, t] in product(levels, taken)] 
                
                model.objective = minimize(xsum(U[vorm_teamsize.index((l,t))]  for l in levels for t in taken))
                
                for level in levels:
                    for taak in taken:
                        model += xsum(X[vorm_skill.index((level,w,taak))] 
                                      for w in werknemers) - teamsize[vorm_teamsize.index((level,taak))] <= U[vorm_teamsize.index((level,taak))]
                        model += -(xsum(X[vorm_skill.index((level,w,taak))] 
                                      for w in werknemers) - teamsize[vorm_teamsize.index((level,taak))]) <= U[vorm_teamsize.index((level,taak))]
                
                # 2e doelfunctie tot hier #############################################################################################
            
            if doelfunctie_keuzebox == 'Op de belangrijke taken staan goede mensen, op de rest staan beginners':
                # DOELFUNCTIE 3 combi van 1 en 2
                 
                 U = [model.add_var(name="u({},{})".format(l,t), var_type=INTEGER) 
                      for [l, t] in product(levels, taken)] 
                 
                 model.objective = minimize(xsum(U[vorm_teamsize.index((l,t))]  for l in levels for t in taken)
                                            + 2*xsum(X[vorm_skill.index((3,w,t))] for w in werknemers for t in taken)
                                            + 2*xsum(X[vorm_skill.index((2,w,t))] for w in werknemers for t in taken))
                 
                 for level in levels:
                     for taak in taken:
                         model += xsum(X[vorm_skill.index((level,w,taak))] 
                                       for w in werknemers) - teamsize[vorm_teamsize.index((level,taak))] <= U[vorm_teamsize.index((level,taak))]
                         model += -(xsum(X[vorm_skill.index((level,w,taak))] 
                                       for w in werknemers) - teamsize[vorm_teamsize.index((level,taak))]) <= U[vorm_teamsize.index((level,taak))]
                
            
            
            ### CONSTRAINT 1: iedere persoon krijgt maar 1 taak toegewezen
            for werknemer in werknemers:
                model += (xsum(X[vorm_skill.index((l,werknemer,t))] for l in levels for t in taken) == 1)
                
            ### CONSTRAINT 2: een persoon wordt alleen toegedeeld aan een bepaald level van een taak als hij/zij deze ook bezit
            for level in levels:
                for werknemer in werknemers:
                    for taak in taken:
                        model += (X[vorm_skill.index((level,werknemer,taak))] <= skill[vorm_skill.index((level,werknemer,taak))])
            
            ### CONSTRAINT 3: op iedere taak worden evenveel mensen ingepland als dat er nodig zijn
            for taak in taken:
                aantal_taak = 0
                for level in levels:
                    aantal_level = teamsize[vorm_teamsize.index((level,taak))]
                    aantal_taak += aantal_level
                model += (xsum(X[vorm_skill.index((l,w,taak))] for l in levels for w in werknemers) == aantal_taak)
                
            ### CONSTRAINT 4: taak wordt alleen uitgevoerd op minimum level
            for taak in taken:
                aantal_min_level1 = data_taken.loc[taak,'Aantal_min_niveau_1']
                model += (xsum(X[vorm_skill.index((1,w,taak))] for w in werknemers) >= aantal_min_level1)
                aantal_max_level3 = data_taken.loc[taak,'Aantal_min_niveau_3']
                model += (xsum(X[vorm_skill.index((3,w,taak))] for w in werknemers) <= aantal_max_level3)
            
                        
            ### CONSTRAINT 5: mensen spreken dezelfde taal waar nodig
            # eerst zorgen dat variabele T goed is gefenieerd; dus 1 als mensen samenwerken
            for i in werknemers:
                ind = werknemers.tolist().index(i)
                for j in werknemers[ind+1:]:
                    for taak in taken:
                        # x >= z;  y>= z;  x+y-1 <= z   ----> T = 1 als mensen samenwerken (x en y beide 1 zijn)
                        model += (xsum(X[vorm_skill.index((l,i,taak))] for l in levels ) >= T[vorm_T.index((i,j,taak))])
                        model += (xsum(X[vorm_skill.index((l,j,taak))] for l in levels ) >= T[vorm_T.index((i,j,taak))])
                        model += (xsum(X[vorm_skill.index((l,i,taak))] + X[vorm_skill.index((l,j,taak))] 
                                       for l in levels ) -1 <= T[vorm_T.index((i,j,taak))])
            
            
            for taak in taken[data_taken.Samenwerken==1]:
                model += (xsum(T[vorm_T.index((i,j,taak))] * taal[vorm_taal.index((i,j))] 
                                   for i in werknemers for j in werknemers) == 0)
                            


 
            # =============================================================================


# =============================================================================
#             '''Wiskundig model (3): Oplossing eruit halen'''
# =============================================================================

            # lege oplossing
            solution = pd.DataFrame(columns = ['x','level','werknemer','taak','waarde'])

            ################################# MAX_SECONDS ALS VRAAG OPGEVEN ########################################
            count = 0
            status = model.optimize(max_seconds=300)
            if status == OptimizationStatus.OPTIMAL:
                print('optimal solution cost {} found'.format(model.objective_value))
            elif status == OptimizationStatus.FEASIBLE:
                print('sol.cost {} found, best possible: {} '.format(model.objective_value, model.objective_bound))
            elif status == OptimizationStatus.INFEASIBLE:
                print('Infeasible')
            elif status == OptimizationStatus.NO_SOLUTION_FOUND:
                print('no feasible solution found, lower bound is: {} '.format(model.objective_bound))
            if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
                print('solution:')
                for v in model.vars:
                    if v.name[0] == 'x':
                        solution.loc[count,'x'] = v.name
                        [v1,v2,v3] = v.name.split('(')[1].split(')')[0].split(',')
                        solution.loc[count,'level'] = v1
                        solution.loc[count,'werknemer'] = v2
                        solution.loc[count,'taak'] = v3
                        solution.loc[count,'waarde'] = v.x
                        count += 1
                        if abs(v.x) > 1e-6: # only printing non-zeros
                            print('{} : {} '.format(v.name, v.x))

            print('model has {} vars, {} constraints and {} nzs'.format(model.num_cols, model.num_rows, model.num_nz))

            # dataframe aanpassen naar wat we terug willen geven

            solution_def = solution.loc[solution['waarde']==1,['werknemer','taak','level']]
            for mens in solution_def.index:
                naam_ind = int(solution_def.werknemer[mens])
                naam = data_aanwezig.Werknemers[naam_ind]
                solution_def.loc[mens,'werknemer'] = naam
                
                taak_ind = int(solution_def.taak[mens])
                taak = data_taken.Taken[taak_ind]
                solution_def.loc[mens,'taak'] = taak


              

            # ==============================================================================

# =============================================================================
#             ''' Oplossing in dictionary + terug naar dataframe'''
# =============================================================================

            # lege dictionary maken, met de taken als keys
            oplossing = defaultdict(list)
            for taak in data_taken.Taken:
                oplossing[taak]=[]

            # Werknemers toevoegen aan de values van de keys (taken)
            for i in solution_def.index:
                taak = solution_def.taak[i]
                werknemer = solution_def.werknemer[i]
                oplossing[taak].append(werknemer)

            # terug naar een dataframe
            df = pd.DataFrame.from_dict(oplossing, orient = 'index')
            df.fillna('', inplace=True)
            # array van werknemers die afwezig zijn
            afwezig = data_werknemers[data_werknemers['Aanwezig'] == 0].Werknemers
            st.dataframe(df)
            #grid_return = AgGrid(df, editable=False)
  
  

# =============================================================================
# =============================================================================
# =============================================================================
# # # HIER EINDIGD HET WISKUNDIG MODEL    
# =============================================================================
# =============================================================================
# =============================================================================
            #De planning krijgt hier een gepaste naam, waarna de planning te downloaden is via een button
            bestandsnaam = "".join(['planning ',str(datetime.datetime.now())[:16], '.xlsx'])
        
            def to_excel(df):
                output = BytesIO()
                writer = pd.ExcelWriter(output, engine='xlsxwriter')
                df.to_excel(writer, index=True, sheet_name='Planning')
                afwezig.to_excel(writer, sheet_name='Planning', index = False, startcol=len(df.columns)+3)
                workbook = writer.book
                worksheet = writer.sheets['Planning']
                #format1 = writer.book.add_format({'left': 1}) 
                # Adjust columns' width
                for column in df:
                    maximum_colums = df[column].str.len().max()
                    writer.sheets['Planning'].set_column(column + 1, column + 1, maximum_colums + 1)
            
                # define workbook and worksheet
                workbook  = writer.book
                worksheet = writer.sheets['Planning']
                    
                # adjust index column
                maximum_index = df.index.str.len().max()
                writer.sheets['Planning'].set_column(0, 0, maximum_index + 1)
            
                # adjust afwezigheid column
                maximum_index = afwezig.str.len().max()
                writer.sheets['Planning'].set_column(0, len(df.columns)+3, maximum_index + 1)
                
                # define format
                merge_format = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': '#59B6AD'})
            
                format2 = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': '#FF6103'})
                # format header aanpassen
                m = chr(ord('a')+len(df.columns)).capitalize()
                range_header = "".join(['B1:',m,'1'])
                worksheet.merge_range(range_header, 'Werknemers', merge_format)
                worksheet.write(0,0, 'Taken', merge_format)
                worksheet.write(0,len(df.columns)+1, 'Comments', merge_format)
                worksheet.write(0,len(df.columns)+3, 'Afwezigen', format2)
                
                writer.save()
                processed_data = output.getvalue()
            
                return processed_data
            df_xlsx = to_excel(df)
            st.download_button(label='📥 Download planning als Excel bestand',
                                            data=df_xlsx ,
                                            file_name= bestandsnaam)
          

    
#leegte om de disclaimer onderaan de pagina te krijgen

for i in range(20):
    st.text("")


#De disclaimer
st.write("""
         ###### Disclaimer
         Deze tool is gemaakt door Rachelle Hermans en Emile Baljeu. Zij zijn, evenals Fontys Hogescholen, niet aansprakelijk voor mogelijke complicaties tijdens en/of na het gebruik van deze site. Ook hebben zij geen rechten voor het gebruiken van het logo op deze site, dus klaag ze alstublieft niet aan. Groetjes!""")
         
         
         
#OM TE RUNNEN:
    #(eventueel conda avtivate ML)
#open terminal van ML via anaconda navigator
#typ: cd C:\Users\Émile\Desktop\School\TW3\Stage\python
#typ: streamlit run streamlit_stage.py

#hulplinkjes
#deploy de app https://www.youtube.com/watch?v=kXvmqg8hc70
#uitbreiden https://www.youtube.com/watch?v=JwSS70SZdyM
#streamlit documentatie https://docs.streamlit.io/library/get-started
#editable grid?????? https://github.com/PablocFonseca/streamlit-aggrid
