import io
import datetime
import os

import ipywidgets as widgets

from isoplot.dataprep import IsoplotData
from isoplot.plots import Plot, Map


class ValueHolder():
    x: int = None
vh = ValueHolder()


#Instanciation des widgets
def make_uploader():
    global uploader
    uploader = widgets.FileUpload(
        accept='',  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
        multiple=False  # True to accept multiple files upload else False
    )
    
    return uploader
    
def make_mduploader():
    global mduploader
    mduploader = widgets.FileUpload(
        accept='',  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
        multiple=False  # True to accept multiple files upload else False
    )

    return mduploader

metadatabtn = widgets.Button(description='Create Template')

datamerge_btn = widgets.Button(description='Submit Template')

out = widgets.Output()

out2 = widgets.Output()

debug_view = widgets.Output(layout={'border': '1px solid black'})
    
@debug_view.capture(clear_output=True)
def metadatabtn_eventhandler(event):
    global data_object
    
    with out:
        print("Loading file...")
    
    uploaded_filename = next(iter(uploader.value))
    content = uploader.value[uploaded_filename]['content']
    with open('myfile', 'wb') as f: f.write(content)
        
    data_object = IsoplotData(io.BytesIO(content))
    data_object.get_data()
    data_object.generate_template()
    
    with out:
        print("Done!")
        
@debug_view.capture(clear_output=True)
def dataprep_eventhandler(event):
    
    with out2:
        print('Loading file...')
    
    mduploaded_filename = next(iter(mduploader.value))
    content = mduploader.value[mduploaded_filename]['content']
    with open('myfile', 'wb') as f: f.write(content)
    
    data_object.get_template(io.BytesIO(content))
    data_object.merge_data()
    data_object.prepare_data()
    vh.dfmerge = data_object.dfmerge
    
    with out2:
        print("Done!")
    
#Gestion des événements pour les boutons    
metadatabtn.on_click(metadatabtn_eventhandler)
datamerge_btn.on_click(dataprep_eventhandler)

#Fonction permettant le filtrage des données à plotter et appelant les fonctions de plotting
@debug_view.capture(clear_output=True)
def indiplot (stack, value, data, name, fmt, metabolites, conditions, times, stackplot=False):
    
    #Préparons le directory où seront enregistrés les html avec les plots
    now = datetime.datetime.now()
    date_time = now.strftime("%d%m%Y_%H%M%S") #Récupération date et heure
    mydir = os.getcwd()
    os.mkdir(name + " " + date_time) #Créons le dir
    os.chdir(name + " " + date_time) #Rentrons dans le dir
    
    for metabolite in metabolites:
        
        plotter = Plot(stack, value, data, name, fmt, metabolite, conditions, times)
        plotter.display = True
        
        if value != 'mean_enrichment':
            if stackplot == True:
                plotter.stacked_areaplot()
            else:
                plotter.barplot()
        elif value == 'mean_enrichment':
            plotter.plot_static_mean_enrichment_plot()

    os.chdir(mydir) #Revenir au dir initial
    
#Fonction permettant le filtrage des données à plotter et appelant les fonctions de plotting
def meanplot(stack, value, data, name, fmt, metabolites, conditions, times, stackplot=False):
    now = datetime.datetime.now()
    date_time = now.strftime("%d%m%Y_%H%M%S") #Récupération date et heure
    mydir = os.getcwd()
    os.mkdir(name + " " + date_time) #Créons le dir
    os.chdir(name + " " + date_time) #Rentrons dans le dir
   
    for metabolite in metabolites:
        
        plotter = Plot(stack, value, data, name, fmt, metabolite, conditions, times)
        plotter.display = True
        
        if value != 'mean_enrichment':
            plotter.mean_barplot()
        elif value == 'mean_enrichment':
            plotter.static_mean_enrichment_meanplot()

    os.chdir(mydir) #Revenir au dir initial  
    
#Création d'une fonction pour gérer les appels aux fonctions de plotting en individuel
def indibokplot(stack, value, data, name, fmt, metabolites, conditions, times, stackplot=False):
    
    #Préparons le directory où seront enregistrés les html avec les plots
    now = datetime.datetime.now()
    date_time = now.strftime("%d%m%Y_%H%M%S") #Récupération date et heure
    mydir = os.getcwd()
    os.mkdir(name + " " + date_time) #Créons le dir
    os.chdir(name + " " + date_time) #Rentrons dans le dir

    for metabolite in metabolites:
        
        if name == '':
            name = metabolite
        
        plotter = Plot(stack, value, data, name, fmt, metabolite, conditions, times)
        plotter.display = True
        
        if value != 'mean_enrichment': #Le cas du mean enrichment est différent car les valeurs sont en double à la sortie d'Isocor   
            
            if stackplot == True:
                plotter.interactive_stacked_areaplot()
            
            elif stack == False:
                plotter.interactive_unstacked_barplot()
                
            elif stack == True:
                plotter.interactive_stacked_barplot()
        
        elif value == 'mean_enrichment':
            plotter.interactive_mean_enrichment_plot()
            
    os.chdir(mydir) #Revenir au dir initial
    
#Création d'une fonction pour gérer les appels aux fonctions de plotting en individuel
def meanbokplot(stack, value, data, name, fmt, metabolites, conditions, times, stackplot=False):
    
    #Préparons le directory où seront enregistrés les html avec les plots
    now = datetime.datetime.now()
    date_time = now.strftime("%d%m%Y_%H%M%S") #Récupération date et heure
    mydir = os.getcwd()
    os.mkdir(name + " " + date_time) #Créons le dir
    os.chdir(name + " " + date_time) #Rentrons dans le dir

    for metabolite in metabolites:
        
        if name == '':
            name = metabolite
        
        plotter = Plot(stack, value, data, name, fmt, metabolite, conditions, times)
        plotter.display = True
        
        if value != 'mean_enrichment': #Le cas du mean enrichment est différent car les valeurs sont en double à la sortie d'Isocor   
            
            if stack == False:
                plotter.interactive_unstacked_meanplot()
                
            elif stack == True:
                plotter.interactive_stacked_meanplot()
        
        elif value == 'mean_enrichment':
            plotter.interactive_mean_enrichment_meanplot()
            
    os.chdir(mydir) #Revenir au dir initial
    
#Fontion pour choisir le map à générer:
def build_map(data, name, map_select, annot, fmt):
    
    mapper = Map(data, name, annot, fmt)
    mapper.display == True
    
    if map_select == "Static heatmap":
        mapper.build_heatmap()
        
    elif map_select == 'Interactive heatmap':
        mapper.fmt = 'html'
        mapper.build_interactive_heatmap()
        
    else:
        mapper.build_clustermap()