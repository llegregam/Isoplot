"""Module containing Plot class. The methods correspond to different types of plots to create"""

try:
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    from natsort import natsorted
    from bokeh.plotting import figure, output_file,show
    from bokeh.models import Whisker, BasicTicker, ColorBar, LinearColorMapper, PrintfTickFormatter
    import colorcet as cc
    import bokeh as bk
    import math
except ModuleNotFoundError:
    raise ModuleNotFoundError('Some dependencies might be missing. Check installation and try again')
except Exception as err:
    print('Unexpected Error')
    print(err)
else:
    if __name__ == '__main__':
        print("Modules have been loaded")
        
        
class Plot():
    
    '''Class to create plots from Isocor output (MS data from C13 labelling experiments)
    
        :param stack: should bars be stacked or not
        :type stack: boolean
        :param value: values to be plotted (isotpologue_fraction, corrected_area or mean_enrichment)
        :type value: str
        :param data: Merged dataframe from which plots are created (comes from data_object.dfmerge)
        :type data: Pandas DataFrame
        :param name: Name of file to be created in destination directory
        :type name: str
        :param fmt: Format of output file (if interactive plots are generated,
                                           any format given will be converted to html)
        :type fmt: str
        :param metabolite: Metabolite to be plotted
        :type metabolite: str
        :param condition: Conditions to be plotted
        :type condition: str or list of str
        :param time: Times to be plotted
        :type time: Times to be plotted
        :param static_fig_name: Name of files generated for static plots (
            metabolite + fmt)
        :type static_fig_name: concatanated str
        :param filtered_data: Dataframe filtered on chosen metabolite, conditions and times
        :type filtered_data: Pandas DataFrame
        :param display: Should plots be displayed or not when created, default False
        :type display: Boolean
        :param WIDTH: Width of generated plot
        :type WIDTH: int
        :param HEIGHT: Height of generated plot
        :type HEIGHT: int

    
    '''
    
    WIDTH = 1400
    HEIGHT = 800
    
    def __init__(self, stack, value, data, name, fmt, metabolite, condition, time, display=False):
        """Initialization of Plot object"""

        self.stack = stack
        self.value = value
        self.data = data
        self.name = name
        self.fmt = fmt
        self.metabolite = metabolite
        self.condition = condition
        self.time = time     
        self.display = display
        self.static_fig_name = self.metabolite + '.' + self.fmt
        self.filtered_data = self.data[
            (self.data['metabolite'] == self.metabolite) & 
            (self.data['condition'].isin(self.condition)) & 
            (self.data['time'].isin(self.time))]
    
    def stacked_areaplot(self):
        """Creation of area stackplot (for cinetic data)"""
        
        #Commençons par la préparation de data
        stackdf = self.filtered_data
        stackpivot = stackdf.pivot(index='ID', columns='isotopologue', values=self.value)
        stackpivot = stackpivot.reindex(index=natsorted(stackpivot.index))
        pivotcol = stackpivot[0:].to_numpy()
        stackyval = pivotcol.transpose()
        stackxval = stackpivot.index.to_numpy()

        #Passons au plot
        plt.figure(figsize=[38,20])
        labels = list(stackpivot.columns)
        plt.stackplot(stackxval, 
                      stackyval, 
                      labels=labels, 
                      colors=cc.glasbey_dark[:len(
                          self.data['isotopologue'].unique())])
        plt.legend()
        plt.title("{} CID cinetics".format(self.metabolite))
        plt.xticks(rotation=45)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.tight_layout()
        plt.savefig(self.static_fig_name, bbox_inches='tight', format=self.fmt)
        if self.display == True:
            plt.show()
        plt.close()

    def barplot(self): 
        """Creation of barplots"""
        
        #Nous filtrons et préparons la table pour les donnéees
        mydata = self.filtered_data
        mydatapivot = mydata.pivot_table(index=["condition_order",'ID'], 
                                         columns='isotopologue', 
                                         values=self.value )
        
        #Ici nous mettons les données dans l'ordre choisi par le template
        mydatapivot.sort_index(level="condition_order", inplace=True) 
        mydatapivot = mydatapivot.droplevel(level = "condition_order")
        
        #Passons au plot
        sns.set_context("poster")
        ax = mydatapivot.plot.bar(stacked=self.stack, 
                                  figsize=(30,15), 
                                  title=self.metabolite, 
                                  color=cc.glasbey_dark[:len(
                                      self.data['isotopologue'].unique())])
        ax.set_xlabel('Condition, Time and Replicate')
        ax.set_ylabel(self.value)
        ax.set_xticklabels(ax.get_xticklabels(), 
                           rotation=45, 
                           horizontalalignment='right')
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.tight_layout()
        plt.savefig(self.static_fig_name, bbox_inches='tight', format=self.fmt)
        if self.display == True:
            plt.show()
        plt.close()


    def mean_barplot(self):
        """Creation of meaned barplots (on replicates)"""
         
        #Nous filtrons et préparons la table pour les donnéees
        tmpdf = self.filtered_data
        
        #Ici nous faisons les moyennes et les SD des données et nous les mettons dans un df
        df_replicate_mean = tmpdf.groupby(
            ["condition_order", "condition", "time", "isotopologue"])[self.value].mean()
        df_replicate_std = tmpdf.groupby(
            ["condition_order", "condition", "time", "isotopologue"])[self.value].std()
        df_full = pd.concat([df_replicate_mean, df_replicate_std],  axis=1)
        df_full.columns = ("mean", "std")
        
        #Nous formattons le df pour pouvoir plotter
        df_ready = df_full.unstack()
        df_ready.sort_index(level="condition_order", inplace=True)
        df_ready = df_ready.droplevel(level = "condition_order")
    
        #Passons au plot
        sns.set_context("poster")
        colors = cc.glasbey_dark[:len(df_ready.columns)]
        this_ax = df_ready["mean"].plot.bar(stacked=self.stack, 
                                            yerr=df_ready['std'], 
                                            figsize=(30,15), 
                                            title=self.metabolite, 
                                            color=colors)
        this_ax.set_xlabel('Condition, Time and Replicate')
        this_ax.set_ylabel(self.value)
        this_ax.set_xticklabels(this_ax.get_xticklabels(), 
                                rotation=45, 
                                horizontalalignment='right')
        this_ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.static_fig_name, bbox_inches='tight', format=self.fmt)
        if self.display == True:
            plt.show()
        plt.close()

    def static_mean_enrichment_plot(self):
        """Generate static mean_enrichment plots"""
         
        #Nous filtrons les données en fonction des paramètres du dashboard
        tmpdf = self.filtered_data
        
        #Nous préparons une liste et un df dans lesquels on va ajouter les mean_enrichment 
        mean_enrichment_df = pd.DataFrame(columns=tmpdf.columns.tolist())
        list_of_tmpdfs = []
        
        #Nous retirons les duplicats pour chaque ID individuel
        for ID in tmpdf["ID"].drop_duplicates():
            tmpdf2 = tmpdf[tmpdf["ID"] == ID].drop_duplicates(subset=['mean_enrichment'])
            list_of_tmpdfs.append(tmpdf2)
            
        #Nous mettons l'ordre de conditions en fonction du template, et nous préparons les datas pour plotter
        mean_enrichment_df = pd.concat(list_of_tmpdfs, ignore_index=True)
        mean_enrichment_df = mean_enrichment_df[["ID", "condition_order", "mean_enrichment"]]
        mean_enrichment_df.sort_values(by="condition_order", inplace=True)
        mean_enrichment_df.drop(labels="condition_order", axis = 1, inplace=True)
        mean_enrichment_df.set_index("ID", inplace=True)
        
        #Nous plottons les data avec la fonction de pandas
        sns.set_context("poster")
        ax = mean_enrichment_df.plot.bar(figsize=(30,15),
                                        title=self.metabolite, 
                                        color=cc.glasbey_dark[3])
        ax.set_xlabel('Condition, Time and Replicate')
        ax.set_ylabel("mean_enrichment")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.tight_layout()
        plt.savefig(self.static_fig_name, bbox_inches='tight', format=self.fmt)
        if self.display == True:
            plt.show()
        plt.close()

    def static_mean_enrichment_meanplot(self):
        """Generate static mean_enrichment plots with meaned replicates"""
        
        #Nous filtrons les données en fonction des paramètres du dashboard
        tmpdf = self.filtered_data

        #Nous préparons une liste et un df dans lesquels on va ajouter les mean_enrichment 
        mean_enrichment_df = pd.DataFrame(columns=tmpdf.columns.tolist())
        list_of_tmpdfs = []
        
        #Nous retirons les duplicats pour chaque ID individuel
        for ID in tmpdf["ID"].drop_duplicates():
            tmpdf2 = tmpdf[tmpdf["ID"] == ID].drop_duplicates(subset=['mean_enrichment'])
            list_of_tmpdfs.append(tmpdf2)
        mean_enrichment_df = pd.concat(list_of_tmpdfs, ignore_index=True)

        #Ici nous faisons les moyennes et les SD des données et nous les mettons dans un df
        df_replicate_mean = mean_enrichment_df.groupby(
            ["condition_order", "condition", "time", "isotopologue"])['mean_enrichment'].mean()
        df_replicate_std = mean_enrichment_df.groupby(
            ["condition_order", "condition", "time", "isotopologue"])['mean_enrichment'].std()
        df_full = pd.concat([df_replicate_mean, df_replicate_std],  axis=1)
        df_full.columns = ("mean", "std")
        
        #Nous formattons le df pour pouvoir plotter
        df_ready = df_full.unstack()
        df_ready.sort_index(level="condition_order", inplace=True)
        df_ready = df_ready.droplevel(level = "condition_order")

        #Passons au plot
        sns.set_context("poster")
        this_ax = df_ready["mean"].plot.bar(yerr=df_ready['std'], 
                                            figsize=(30,15), 
                                            title=self.metabolite, 
                                            color=cc.glasbey_dark[3])
        this_ax.set_xlabel('Condition, Time and Replicate')
        this_ax.set_ylabel('mean_enrichment')
        this_ax.set_xticklabels(this_ax.get_xticklabels(), 
                                rotation=45, 
                                horizontalalignment='right')
        this_ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.static_fig_name, bbox_inches='tight', format=self.fmt)
        if self.display == True:
            plt.show()
        plt.close()

    def interactive_mean_enrichment_plot(self):
        """Generate interactive mean_enrichment plots"""
        
        output_file(filename = self.metabolite + ".html", title = self.metabolite + ".html")

        #Nous filtrons les données en fonction des paramètres du dashboard
        tmpdf = self.filtered_data
        
        #Nous préparons une liste et un df dans lesquels on va ajouter les mean_enrichment 
        mean_enrichment_df = pd.DataFrame(columns=tmpdf.columns.tolist())
        list_of_tmpdfs = []
        
        #Nous retirons les duplicats pour chaque ID individuel
        for ID in tmpdf["ID"].drop_duplicates():
            tmpdf2 = tmpdf[tmpdf["ID"] == ID].drop_duplicates(subset=['mean_enrichment'])
            list_of_tmpdfs.append(tmpdf2)
            
        #Nous mettons l'ordre de conditions en fonction du template, et nous préparons les datas pour plotter
        mean_enrichment_df = pd.concat(list_of_tmpdfs, ignore_index=True)
        mean_enrichment_df = mean_enrichment_df[["ID", "condition_order", "mean_enrichment"]]
        mean_enrichment_df.sort_values(by="condition_order", inplace=True)
        mean_enrichment_df.drop(labels="condition_order", axis = 1, inplace=True)
        mean_enrichment_df.set_index("ID", inplace=True)

        my_x_range = mean_enrichment_df.index.tolist()
        source = bk.models.ColumnDataSource(mean_enrichment_df)

        TOOLTIPS = [
        ("", "@ID"),
        ("value", "@mean_enrichment"),
        ]

        myplot = figure(plot_width=self.WIDTH,
                       plot_height=self.HEIGHT,
                       title=self.name,
                       y_axis_label="mean_enrichment",
                       tools="save, wheel_zoom, reset, hover",
                       tooltips = TOOLTIPS,
                       x_range=my_x_range)

        myplot.vbar(width=0.9,
                   bottom=0,
                   top="mean_enrichment",
                   color=cc.glasbey_dark[3],
                   x="ID",
                   source=source)

        myplot.xaxis.major_label_orientation = math.pi/4
        show(myplot)

    def interactive_mean_enrichment_meanplot(self):
        """Generate interactive mean_enrichment plots with meaned replicates"""
        
        output_file(filename = self.metabolite +".html", title = self.metabolite + ".html")

        #Nous filtrons les données en fonction des paramètres du dashboard
        tmpdf = self.filtered_data

        df_replicate_mean = tmpdf.groupby(
            ["condition_order", "condition", "time", "isotopologue"])[self.value].mean()
        df_replicate_std = tmpdf.groupby(
            ["condition_order", "condition", "time", "isotopologue"])[self.value].std()
        mean_df = df_replicate_mean.to_frame()
        std_df = df_replicate_std.to_frame()

        #Ici nous mettons les moyennes dans un df et nous trions dans l'ordre demandé dans le template
        mean_df_unstack = mean_df.unstack()
        mean_df_unstack.sort_index(level="condition_order", inplace=True)
        mean_df_unstack = mean_df_unstack.droplevel(level = 0)
        mean_df_unstack.columns = mean_df_unstack.columns.droplevel(level = 0)
        mean_df_unstack.columns = mean_df_unstack.columns.astype(str)
        mean_df_unstack.index = ['{}_{}'.format(i, j) for i, j in mean_df_unstack.index] #Nous recréons la colonne ID

        #Les colonnes contenants toutes les mêmes valeurs, nous pouvons juste prendre la première
        mean_series = mean_df_unstack.iloc[:, 0].copy()

        #Ici nous mettons les SD dans un df et nous trions dans l'ordre demandé dans le template
        std_df_unstack = std_df.unstack()
        std_df_unstack.sort_index(level="condition_order", inplace=True)
        std_df_unstack = std_df_unstack.droplevel(level = 0)
        std_df_unstack.columns = std_df_unstack.columns.droplevel(level = 0)
        std_df_unstack.columns = std_df_unstack.columns.astype(str)
        std_df_unstack.index = ['{}_{}'.format(i, j) for i, j in std_df_unstack.index]

        #Les colonnes contenants toutes les mêmes valeurs, nous pouvons juste prendre la première
        std_series = std_df_unstack.iloc[:, 0].copy()

        #Nous préparons les hauts et bas pour placer les barres d'erreur
        upper_series = mean_series.add(std_series, fill_value=0)
        upper_list = upper_series.to_list()

        lower_series = mean_series.sub(std_series, axis='index', fill_value=0)
        lower_list = lower_series.to_list()

        #Nous préparons les datas pour plotter
        my_x_range = mean_series.index.tolist()
        values = mean_series.to_list()
        my_dict = dict(ID=my_x_range, tops=values)
        source = bk.models.ColumnDataSource(my_dict)

        #Nous préparons le dictionnaire qui va faire le ColumnDataSource pour les barres d'erreur
        whisker_dico = dict(base = my_x_range, upper = upper_list, lower = lower_list)

        #Passons au plot
        TOOLTIPS = [
        ("", "@ID"),
        ("value", "@tops"),
        ]

        myplot = figure(plot_width=self.WIDTH,
                       plot_height=self.HEIGHT,
                       title=self.name,
                       y_axis_label="mean_enrichment",
                       tools="save, wheel_zoom, reset, hover",
                       tooltips = TOOLTIPS,
                       x_range=my_x_range)

        myplot.vbar(width=0.9,
                   bottom=0,
                   top='tops',
                   color=cc.glasbey_dark[3],
                   x='ID',
                   source = source)

        mywhisker = bk.models.Whisker(source = bk.models.ColumnDataSource(whisker_dico), 
                                      base = "base", 
                                      upper = "upper", 
                                      lower = "lower", 
                                      level="overlay")

        #Nous ajoutons les barres d'erreurs
        myplot.add_layout(mywhisker)

        myplot.xaxis.major_label_orientation = math.pi/4
        show(myplot)

    def interactive_stacked_barplot(self):
        """Generate interactive stacked barplots"""
        
        output_file(filename = self.metabolite +".html", title = self.metabolite)

        #Nous filtrons les datas à plotter
        mydata = self.filtered_data
        mydatapivot = mydata.pivot_table(index=["condition_order",'ID'],
                                         columns='isotopologue', 
                                         values=self.value )
        mydatapivot.sort_index(level="condition_order", inplace=True)
        mydatapivot = mydatapivot.droplevel(level = "condition_order")
        mydatapivot.columns = mydatapivot.columns.astype(str)

        #préparons les différentes couches des barres à stacker
        stackers = mydatapivot.columns.tolist()
        
        #Récupérons les noms à mettre en x
        my_x_range = mydatapivot.index.tolist()
        
        #Nous faisons ici des listes avec les données pour chaque couche (une couche=un isotopologue)
        listoflists =[mydatapivot[val].tolist() for val in stackers]

        #Nous mettons ça dans un dictionnaire pour le ColumnDataSource
        myplotdic = dict(zip(stackers, listoflists))
        myplotdic.update({'ID' : my_x_range})

        #Préparation des tooltips
        TOOLTIPS = [
            ("", "@ID"),
            ("isotopologue", "$name"),
            ("fraction", "@$name"),
            ]

        #Initialization de la figure
        myplot = figure(
            x_range = my_x_range,
            plot_width=self.WIDTH,
            plot_height=self.HEIGHT,
            title=self.name,
            y_axis_label=self.value,
            tools="save,wheel_zoom,reset,hover", 
            tooltips=TOOLTIPS
        )

        #Passons au plot
        myplot.vbar_stack(stackers, 
        x='ID', 
        source=myplotdic,
        width=0.9,
        color=cc.glasbey_dark[:len(stackers)]
        )

        myplot.xaxis.major_label_orientation = math.pi/4

        show(myplot)


    def interactive_unstacked_barplot(self):
        """Generate interactive unstacked barplots"""
        
        output_file(filename = self.metabolite +".html", title = self.metabolite)

        #Nous filtrons les datas à plotter
        mydata = self.filtered_data
        mydatapivot = mydata.pivot_table(index=["condition_order",'ID'], 
                                         columns='isotopologue', 
                                         values=self.value )
        mydatapivot.sort_index(level="condition_order", inplace=True)
        mydatapivot = mydatapivot.droplevel(level = "condition_order")
        
        #Nous récupérons les colonnes pour faire les couches à stacker 
        stackers = mydatapivot.columns.astype(str).tolist()
        
        #Nous faisons des tuples avec index et couche à plotter
        factors= [(i, stack) for i in mydatapivot.index for stack in stackers]
        
        #Nous récupérons les valeurs de chaque couche
        tops = [row[int(stack)+1] 
                for row in mydatapivot.itertuples() 
                for stack in stackers]
        
        #Nous mettons tout ça dans un ColumnDataSource
        source = bk.models.ColumnDataSource(data=dict(x=factors, tops=tops))

        #Préparation des tooltips
        TOOLTIPS = [
            ("(Nom, Isotopologue)", "@x"),
            ("Value", "@tops")
            ]

        #Initialisation de la figure
        plot = figure(
        x_range= bk.models.FactorRange(*factors), #Voir docu sur Bokeh.org pour ça
        plot_width=self.WIDTH, 
        plot_height=self.HEIGHT, 
        tools="save,wheel_zoom,reset,hover,pan", 
        tooltips=TOOLTIPS)

        #Passons au plot
        plot.vbar(x='x', 
                  top='tops', 
                  width=0.9, 
                  source=source, 
                  fill_color = bk.transform.factor_cmap('x', 
                                                        palette=cc.glasbey_dark, 
                                                        factors=stackers, 
                                                        start=1, end=2),
                  line_color="white")

        plot.y_range.start = 0
        plot.x_range.range_padding = 0.1
        show(plot)

    def interactive_stacked_meanplot(self):
        """Generate interactive stacked barplots with meaned replicates"""
        
        output_file(filename = self.metabolite +".html", title = self.metabolite)

        #Nous filtrons les datas à plotter et préparons les moyennes et SD
        tmpdf = self.filtered_data
        df_replicate_mean = tmpdf.groupby(
            ["condition_order", "condition", "time", "isotopologue"])[self.value].mean()
        df_replicate_std = tmpdf.groupby(
            ["condition_order", "condition", "time", "isotopologue"])[self.value].std()
        mean_df = df_replicate_mean.to_frame()
        std_df = df_replicate_std.to_frame()

        #Ici nous mettons les moyennes et SD dans des df
        mean_df_unstack = mean_df.unstack()
        mean_df_unstack.sort_index(level="condition_order", inplace=True)
        mean_df_unstack = mean_df_unstack.droplevel(level = 0)
        mean_df_unstack.columns = mean_df_unstack.columns.droplevel(level = 0)
        mean_df_unstack.columns = mean_df_unstack.columns.astype(str)
        mean_df_unstack.index = ['{}_{}'.format(i, j) for i, j in mean_df_unstack.index]

        std_df_unstack = std_df.unstack()
        std_df_unstack.sort_index(level="condition_order", inplace=True)
        std_df_unstack = std_df_unstack.droplevel(level = 0)
        std_df_unstack.columns = std_df_unstack.columns.droplevel(level = 0)
        std_df_unstack.columns = std_df_unstack.columns.astype(str)
        std_df_unstack.index = ['{}_{}'.format(i, j) for i, j in std_df_unstack.index]

        upper_df = mean_df_unstack.add(std_df_unstack, fill_value=0)
        upper_df.columns = upper_df.columns.astype(str)
        lower_df = mean_df_unstack.sub(std_df_unstack, axis='index', fill_value=0)
        lower_df.columns = lower_df.columns.astype(str)

        stackers = mean_df_unstack.columns.tolist()
        my_x_range = mean_df_unstack.index.tolist()

        #Nous initialisons les listes qui serviront à récupérer les positions des hauts et bas des barres d'erreur
        mean_listoflists, upper_listoflists, lower_listoflists = [], [], []

        mean_listoflists = [mean_df_unstack[val].tolist() for val in stackers]

        meanplotdic = dict(zip(stackers, mean_listoflists))
        meanplotdic.update({'ID' : my_x_range})

        #Préparation des tooltips
        TOOLTIPS = [
            ("", "@ID"),
            ("isotopologue", "$name"),
            ("fraction", "@$name"),
            ]

        #Initialization de la figure
        myplot = figure(
            x_range = my_x_range,
            plot_width=self.WIDTH,
            plot_height=self.HEIGHT,
            title=self.name,
            y_axis_label=self.value,
            tools="save,wheel_zoom,reset,hover,pan", 
            tooltips=TOOLTIPS
        )

        colors = cc.glasbey_dark[:len(stackers)]

        #Passons au plot
        myplot.vbar_stack(stackers, 
        x='ID', 
        source=meanplotdic,
        width=0.9,
        color=colors
        )   


        #Nous préparons les données pour positionner les barres d'erreur
        dico_upper_list = []
        dico_lower_list = []

        for element in upper_df[stackers[0]]:
            dico_upper_list.append(0)
            dico_lower_list.append(0)

        dico_upper_array = np.array(dico_upper_list)
        dico_lower_array = np.array(dico_lower_list)

        #Nous faisons la suite couche par couche
        for val in stackers:
            
            base = my_x_range

            #Nous devons incrementer à chaque loop la valeur pour la barre d'erreur du dessous pour qvoir la bonne hauteur de placement
            upper_listoflists = list(upper_df[val])
            lower_listoflists = list(lower_df[val])
            upper_array = np.array(upper_listoflists)
            lower_array = np.array(lower_listoflists)
            dico_upper_array = np.add(dico_upper_array, upper_array)
            dico_lower_array = np.add(dico_lower_array, lower_array)
            dico_lower_list = dico_lower_array.tolist()
            dico_upper_list = dico_upper_array.tolist()
            whisker_dico = dict(base = base, upper = dico_upper_list, lower = dico_lower_list)
            source = bk.models.ColumnDataSource(data=whisker_dico)
            mywhisker = Whisker(source = source, base = "base", upper = "upper", lower = "lower", level="overlay")

            #Nous ajoutons les barres d'erreurs (couche par couche)
            myplot.add_layout(mywhisker)    

        myplot.xaxis.major_label_orientation = math.pi/4
        show(myplot)

    def interactive_unstacked_meanplot(self):
        """Generate interactive unstacked barplots with meaned replicates"""
        
        output_file(filename = self.metabolite +".html", title = self.metabolite)

        #Préparation des datas à plotter
        tmpdf = self.filtered_data
        df_replicate_mean = tmpdf.groupby(
            ["condition_order", "condition", "time", "isotopologue"])[self.value].mean()
        df_replicate_std = tmpdf.groupby(
            ["condition_order", "condition", "time", "isotopologue"])[self.value].std()
        mean_df = df_replicate_mean.to_frame()
        std_df = df_replicate_std.to_frame()

        mean_df_unstack = mean_df.unstack()
        mean_df_unstack.sort_index(level="condition_order", inplace=True)
        mean_df_unstack = mean_df_unstack.droplevel(level = 0)
        mean_df_unstack.columns = mean_df_unstack.columns.droplevel(level = 0)
        mean_df_unstack.columns = mean_df_unstack.columns.astype(str)
        mean_df_unstack.index = ['{}_{}'.format(i, j) for i, j in mean_df_unstack.index]

        std_df_unstack = std_df.unstack()
        std_df_unstack.sort_index(level="condition_order", inplace=True)
        std_df_unstack = std_df_unstack.droplevel(level = 0)
        std_df_unstack.columns = std_df_unstack.columns.droplevel(level = 0)
        std_df_unstack.columns = std_df_unstack.columns.astype(str)
        std_df_unstack.index = ['{}_{}'.format(i, j) for i, j in std_df_unstack.index]
        stackers = mean_df_unstack.columns.tolist()

        upper_df = mean_df_unstack.add(std_df_unstack, fill_value=0)
        lower_df = mean_df_unstack.sub(std_df_unstack, axis='index', fill_value=0)

        #Même principe que pour les non stackés non moyennés sauf que nous préparons les barres d'erreur aussi
        factors= [(i, stack) for i in mean_df_unstack.index for stack in stackers]
        
        tops=[row[int(stack) + 1] 
              for row in mean_df_unstack.itertuples() 
              for stack in stackers]
        
        upper_list=[row[int(stack) + 1]
                    for row in upper_df.itertuples()
                    for stack in stackers]
        
        lower_list=[row[int(stack) + 1]
                    for row in lower_df.itertuples()
                    for stack in stackers]

        base = factors
        source = bk.models.ColumnDataSource(data=dict(x=factors, tops=tops))
        
        #Nous faisons un ColumnDataSource pour les incertitudes
        source_error = bk.models.ColumnDataSource(
            data=dict(base = base, upper = upper_list, lower = lower_list))

        #Préparation des tooltips
        TOOLTIPS = [
            ("(Nom, Isotopologue)", "@x"),
            ("Fraction", "@tops")
            ]

        #Initialisation de la figure
        plot = figure(
        x_range= bk.models.FactorRange(*factors), 
        plot_width=self.WIDTH, 
        plot_height=self.HEIGHT, 
        tools="save,wheel_zoom,reset,hover,pan", 
        tooltips=TOOLTIPS)

        #Passons au plot
        plot.vbar(x='x', 
                  top='tops', 
                  width=0.9, 
                  source=source, 
                  fill_color = bk.transform.factor_cmap(
                      'x', palette=cc.glasbey_dark, 
                      factors=stackers, start=1, end=2),
                  line_color="white")

        plot.add_layout(bk.models.Whisker(
            source = source_error, 
            base = "base", upper = "upper", 
            lower = "lower", level="overlay"))
        plot.y_range.start = 0
        plot.x_range.range_padding = 0.1
        show(plot)

    def interactive_stacked_areaplot(self):
        """Generate interactive stacked areaplots"""
        
        output_file(filename = self.metabolite + ".html", title = self.metabolite)
        
        #Commençons par la préparation de data
        stackdf = self.filtered_data
        stackpivot = stackdf.pivot(index='ID', columns='isotopologue', values=self.value)
        stackpivot.columns = stackpivot.columns.astype(str)
        mysource = bk.models.ColumnDataSource(data=stackpivot)
        mystackers = stackpivot.columns.tolist()
        colors = cc.glasbey_dark[:len(mystackers)]

        TOOLTIPS = [
            ("", "<strong>@ID</strong>"),
            ("isotopologue", "$name"),
            ("ID", "@$name"),
            ]

        plot = figure(
        width=1000,
        height = 600,
        tools="save,wheel_zoom,reset,hover,pan",
        tooltips=TOOLTIPS,
        x_range = stackpivot.index.values
        )

        plot.xaxis.major_label_orientation = math.pi/4
        plot.varea_stack(mystackers, x = "ID", color=colors, source=mysource)
        show(plot)
        
    
class Map():
    
    '''
    Class to create maps from Isocor output (MS data from C13 labelling experiments)
    
    
    :param heatmapdf(dataframe): Modified dfmerge dataframe used for creating heatmaps
    :type heatmapdf: Pandas DataFrame
    :param dc_heatmap: Heatmapdf but described (check pandas.DataFrame.describe method for details)
    :type dc_heatmap: Pandas DataFrame
    :param heatmap_center: Value to center colormap used in heatmaps and clustermaps
    :type heatmap_center: float
    :param clustermapdf: Modified dfmerge dataframe used for creating clustermaps
    :type clustermapdf: Pandas DataFrame
    
    '''

    def __init__(self, data, name, annot, fmt, display=False):
        
        self.data = data
        self.name = name
        self.annot = annot
        self.fmt = fmt
        self.display = display
        
        #Il faut préparer les données pour les maps:
        self.heatmapdf = self.data[
            ['metabolite', 'mean_enrichment', 
             'condition', 'time', 'number_rep']]
        self.heatmapdf = self.heatmapdf[self.heatmapdf['mean_enrichment'] != 0]
        self.heatmapdf.drop_duplicates(inplace=True)
        self.heatmapdf.dropna(inplace=True)
        self.heatmapdf.set_index('metabolite', inplace=True)
        self.heatmapdf['Condition_Time'] = self.heatmapdf['condition'].apply(str) + '_T' + self.heatmapdf['time'].apply(str)
        self.heatmapdf = self.heatmapdf.groupby(
            ['metabolite','Condition_Time'])['mean_enrichment'].mean()
        self.heatmapdf = self.heatmapdf.unstack(0)
        self.dc_heatmap = self.heatmapdf.describe(include='all')
        self.heatmap_center = self.dc_heatmap.iloc[5,0].mean()
        self.clustermapdf = self.heatmapdf.fillna(value=0)
        
    def build_heatmap(self):
        '''
        Create a heatmap of mean_enrichment data across 
        all conditions & times & metabolites
        '''
        
        fig, ax = plt.subplots(figsize = (30,30)) 
        sns.set(font_scale=1)
        sns.heatmap(self.heatmapdf,vmin=0.02, 
                    robust=True, center=self.heatmap_center, 
                    annot=self.annot, fmt="f", linecolor='black', 
                    linewidths=.2, cmap = 'Blues', ax=ax)
        plt.yticks(rotation = 0, fontsize=20)
        plt.xticks(rotation = 45, fontsize=20)
        bottom, top = ax.get_ylim()
        plt.savefig(self.name + '.' + self.fmt, bbox_inches='tight', format=self.fmt)
        if self.display == True:
            plt.show()
        plt.close()
         
    def build_clustermap(self):
        '''
        Create a clustermap of mean_enrichment data across 
        all conditions & times & metabolites
        '''
        
        sns.set(font_scale=1)
        cg = sns.clustermap(self.clustermapdf, 
                            cmap="Blues", fmt="f", 
                            linewidths=.2, standard_scale=1, 
                            figsize = (30,30), linecolor='black', 
                            annot=self.annot)
        plt.setp(cg.ax_heatmap.yaxis.get_majorticklabels(), rotation=0, fontsize=20)
        plt.setp(cg.ax_heatmap.xaxis.get_majorticklabels(), rotation=45, fontsize=20)
        plt.savefig(self.name + '.' + self.fmt, bbox_inches='tight', format=self.fmt)
        if self.display == True:
            plt.show()
        plt.close()
            
    def build_interactive_heatmap(self):
        '''
        Create an interactive heatmap of mean_enrichment data across 
        all conditions & times & metabolites
        '''
        
        output_file(filename = self.name + ".html", title = self.name + ".html")
        
        condition_time = list(self.heatmapdf.index.astype(str))
        metabolites = list(self.heatmapdf.columns)
        
        #Nous réordonnons les données
        df = pd.DataFrame(self.heatmapdf.stack(), columns=["values"]).reset_index()
        
        #Nous préparons les couleurs
        colors = cc.kbc[len(df)]
        mapper = LinearColorMapper(palette= cc.kbc[:len(df)])
        
        TOOLTIPS = "hover,save,pan,box_zoom,reset,wheel_zoom"
        
        #initialisation de la figure
        p = figure(title=self.name,
               x_range=condition_time, y_range=list(reversed(metabolites)),
               x_axis_location="below", plot_width=1200, plot_height=1200,
               tools=TOOLTIPS, toolbar_location='above',
               tooltips=[('datapoint', '@metabolite @Condition_Time'), ('value', "@values")])
        
        p.grid.grid_line_color = None
        p.axis.axis_line_color = None
        p.axis.major_tick_line_color = None
        p.axis.major_label_text_font_size = "15px"
        p.axis.major_label_standoff = 0
        p.xaxis.major_label_orientation = math.pi / 3
        
        #Passons au plot
        p.rect(x="Condition_Time", 
               y="metabolite", 
               width=1, height=1,
               source=df,
               fill_color={'field': "values", 'transform': mapper},
               line_color=None)
        
        #Nous préparons la barre de couleur pour la légende
        color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="7px",
                         ticker=BasicTicker(desired_num_ticks=len(colors)),
                         formatter=PrintfTickFormatter(),
                         label_standoff=6, border_line_color=None, location=(0, 0))
        
        #Ajoutons la barre de couleur de la légende
        p.add_layout(color_bar, 'right')
        
        show(p)
    
