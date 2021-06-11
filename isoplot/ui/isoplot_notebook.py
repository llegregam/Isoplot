import io
import datetime
import os
import subprocess
import sys

import ipywidgets as widgets
import pandas as pd

from isoplot.main.dataprep import IsoplotData
from isoplot.main.plots import StaticPlot, InteractivePlot, Map


class ValueHolder:
    x: int = None


vh = ValueHolder()


# Check if current version is outdated
def check_version(name):
    reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--outdated'])
    outdated_packages = [r.decode().split('==')[0] for r in reqs.split()]
    if name in outdated_packages:
        print("Your version of Isoplot is outdated. Please run 'pip install isoplot' to get the latest"
              "version.")


# Instanciation des widgets
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


check_version('isoplot')

metadatabtn = widgets.Button(description='Create Template')

datamerge_btn = widgets.Button(description='Submit Template')

out = widgets.Output()

out2 = widgets.Output()


def metadatabtn_eventhandler(event):
    global data_object

    with out:
        print("Loading file...")

    uploaded_filename = next(iter(uploader.value))
    content = uploader.value[uploaded_filename]['content']
    with open('myfile', 'wb') as f:
        f.write(content)

    data_object = IsoplotData(None)
    key = list(uploader.value.keys())

    if key[0][-3:] == "tsv":
        data_object.data = pd.read_csv(io.BytesIO(content), sep="\t")
    elif key[0][-3:] == "csv":
        data_object.data = pd.read_csv(io.BytesIO(content), sep=";")

    data_object.generate_template()

    with out:
        print("Done!")


def dataprep_eventhandler(event):
    with out2:
        print('Loading file...')

    mduploaded_filename = next(iter(mduploader.value))
    content = mduploader.value[mduploaded_filename]['content']
    with open('myfile', 'wb') as f: f.write(content)
    data_object.get_template(content)
    data_object.merge_data()
    data_object.prepare_data()
    vh.dfmerge = data_object.dfmerge

    with out2:
        print("Done!")


# Gestion des événements pour les boutons
metadatabtn.on_click(metadatabtn_eventhandler)
datamerge_btn.on_click(dataprep_eventhandler)


# Fonction permettant le filtrage des données à plotter et appelant les fonctions de plotting
def indiplot(stack, value, data, name, metabolites, conditions, times, fmt, display, stackplot=False):
    # Préparons le directory où seront enregistrés les html avec les plots
    now = datetime.datetime.now()
    date_time = now.strftime("%d%m%Y_%H%M%S")  # Récupération date et heure
    mydir = os.getcwd()
    os.mkdir(name + " " + date_time)  # Créons le dir
    os.chdir(name + " " + date_time)  # Rentrons dans le dir

    for metabolite in metabolites:

        plotter = StaticPlot(stack, value, data, name, metabolite, conditions, times, fmt,
                             display=display, rtrn=False)

        if value != 'mean_enrichment':
            if stackplot == True:
                plotter.stacked_areaplot()
            else:
                plotter.barplot()
        elif value == 'mean_enrichment':
            plotter.mean_enrichment_plot()

    os.chdir(mydir)  # Revenir au dir initial


# Fonction permettant le filtrage des données à plotter et appelant les fonctions de plotting
def meanplot(stack, value, data, name, metabolites, conditions, times, fmt, display):
    now = datetime.datetime.now()
    date_time = now.strftime("%d%m%Y_%H%M%S")  # Récupération date et heure
    mydir = os.getcwd()
    os.mkdir(name + " " + date_time)  # Créons le dir
    os.chdir(name + " " + date_time)  # Rentrons dans le dir

    for metabolite in metabolites:

        plotter = StaticPlot(stack, value, data, name, metabolite, conditions, times, fmt,
                             display=display, rtrn=False)

        if value != 'mean_enrichment':
            plotter.mean_barplot()
        elif value == 'mean_enrichment':
            plotter.mean_enrichment_meanplot()

    os.chdir(mydir)  # Revenir au dir initial


# Création d'une fonction pour gérer les appels aux fonctions de plotting en individuel
def indibokplot(stack, value, data, name, metabolites, conditions, times, display, stackplot=False):
    # Préparons le directory où seront enregistrés les html avec les plots
    now = datetime.datetime.now()
    date_time = now.strftime("%d%m%Y_%H%M%S")  # Récupération date et heure
    mydir = os.getcwd()
    os.mkdir(name + " " + date_time)  # Créons le dir
    os.chdir(name + " " + date_time)  # Rentrons dans le dir

    for metabolite in metabolites:

        if name == '':
            name = metabolite

        plotter = InteractivePlot(stack, value, data, name, metabolite, conditions, times,
                                  display=display, rtrn=False)

        # Le cas du mean enrichment est différent car les valeurs sont en double à la sortie d'Isocor
        if value != 'mean_enrichment':

            if stackplot == True:
                plotter.stacked_areaplot()

            elif stack == False:
                plotter.unstacked_barplot()

            elif stack == True:
                plotter.stacked_barplot()

        elif value == 'mean_enrichment':
            plotter.mean_enrichment_plot()

    os.chdir(mydir)  # Revenir au dir initial


# Création d'une fonction pour gérer les appels aux fonctions de plotting en individuel
def meanbokplot(stack, value, data, name, metabolites, conditions, times, display):
    # Préparons le directory où seront enregistrés les html avec les plots
    now = datetime.datetime.now()
    date_time = now.strftime("%d%m%Y_%H%M%S")  # Récupération date et heure
    mydir = os.getcwd()
    os.mkdir(name + " " + date_time)  # Créons le dir
    os.chdir(name + " " + date_time)  # Rentrons dans le dir

    for metabolite in metabolites:

        if name == '':
            name = metabolite

        plotter = InteractivePlot(stack, value, data, name, metabolite, conditions, times,
                                  display=display, rtrn=False)

        if value != 'mean_enrichment':  # Le cas du mean enrichment est différent car les valeurs sont en double à la sortie d'Isocor

            if stack == False:
                plotter.unstacked_meanplot()

            elif stack == True:
                plotter.stacked_meanplot()

        elif value == 'mean_enrichment':
            plotter.mean_enrichment_meanplot()

    os.chdir(mydir)  # Revenir au dir initial


# Fontion pour choisir le map à générer:
def build_map(data, name, map_select, annot, fmt, display):
    mapper = Map(data, name, annot, fmt, display=display)

    if map_select == "Static heatmap":
        mapper.build_heatmap()

    if map_select == 'Interactive heatmap':
        mapper.fmt = 'html'
        mapper.build_interactive_heatmap()

    if map_select == "Clustermap":
        mapper.build_clustermap()
