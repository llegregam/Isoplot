"""Module containing the plotting classes."""

import math

import colorcet as cc
import matplotlib.pyplot as plt
from bokeh.io import output_file, show, save
from bokeh.models import FactorRange, BasicTicker, ColorBar, LinearColorMapper, PrintfTickFormatter, ColumnDataSource
from bokeh.transform import factor_cmap
from bokeh.plotting import figure
import seaborn as sns
import pandas as pd


class StaticPlot:
    """
    Class to generate the different Static Plots using pandas built-in plotting modules
    """

    def __init__(self, data, mean_data, metabolite, conditions, times, value, stack=True, display=True):
        """
        During initialization, data is filtered on the desired metabolite, conditions, times and value to plot. We also
        input the desired format, and booleans to define if bars in barplots should be unstacked and if plots should be
        directly displayed.

        :param data: Dataframe containing the clean data passed on by DataHandler object
        :param metabolite: Metabolite to plot
        :param conditions: List of conditions to plot
        :param times: List of time points to plot
        :param value: Which value should be plotted (mean enrichment, isotopologue fraction or corrected areas)
        :param stack: While true bars are stacked
        :param display: While true plots are displayed
        """

        self.data = data.loc[(metabolite, conditions, times)].droplevel(0)
        self.mean_data = mean_data.loc[(metabolite, conditions, times)].droplevel(0)
        if value == "mean_enrichment":
            self.data = self.data[self.data.index.get_level_values("isotopologue") == 0]
            self.mean_data = self.mean_data[self.mean_data.index.get_level_values("isotopologue") == 0]
        self.metabolite = metabolite
        self.conditions = conditions
        self.times = times
        self.value = value
        self.stack = stack
        self.display = display
        self.WIDTH = 30
        self.HEIGHT = 15

    def barplot(self, mean=False):
        """
        Build stacked or unstacked barplot

        :param mean: should meaned data and SDs be plotted
        :return: figure containing plot
        """

        fig, ax = plt.subplots()
        if not mean:
            df = self.data.pivot_table(index=["ID", "condition_order"],
                                       columns="isotopologue",
                                       values=self.value).sort_index(
                level="condition_order").droplevel(level="condition_order")
            ax = df.plot.bar(stacked=self.stack, figsize=(self.WIDTH, self.HEIGHT), title=self.metabolite,
                             color=cc.glasbey_dark[:len(self.data.index.get_level_values("isotopologue").unique())]
                             )
            ax.set_xlabel('Condition, Time and Replicate')
        else:
            df = self.mean_data.pivot_table(index=["ID", "condition_order"],
                                            columns="isotopologue",
                                            values=self.value + "_mean").sort_index(
                level="condition_order").droplevel(level="condition_order")
            sd_df = self.mean_data.pivot_table(index=["ID", "condition_order"],
                                               columns="isotopologue",
                                               values=self.value + "_std").sort_index(
                level="condition_order").droplevel(level="condition_order")

            ax = df.plot.bar(stacked=self.stack, figsize=(self.WIDTH, self.HEIGHT), title=self.metabolite,
                             color=cc.glasbey_dark[:len(self.data.index.get_level_values("isotopologue").unique())],
                             yerr=sd_df
                             )
        ax.set_ylabel(self.value)
        ax.set_xticklabels(ax.get_xticklabels(),
                           rotation=45,
                           horizontalalignment='right')
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        fig.tight_layout()
        if self.display:
            fig.show()
        else:
            return fig

    def stacked_areaplot(self):

        fig, ax = plt.subplots()
        df = self.data.pivot_table(index=["ID", "condition_order"],
                                   columns="isotopologue",
                                   values=self.value).sort_index(
            level="condition_order").droplevel(level="condition_order")
        ax = df.plot.area(stacked=self.stack)
        ax.set_ylabel(self.value)
        ax.set_xticklabels(ax.get_xticklabels(),
                           rotation=45,
                           horizontalalignment='right')
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        fig.tight_layout()
        if self.display:
            fig.show()
        else:
            return fig


class InteractivePlot(StaticPlot):
    """
    Class to generate the different Interactive Plots using the bokeh package
    """

    def __init__(self, data, mean_data, metabolite, conditions, times, value, stack=True, display=True):
        super().__init__(data, mean_data, metabolite, conditions, times, value, stack, display)
        self.filename = self.metabolite + "_" + self.value + ".html"
        output_file(self.filename)
        self.WIDTH = 1080
        self.HEIGHT = 640
        self.plot_tools = "save, wheel_zoom, reset, hover, pan"

    def __repr__(self):
        return f"Interactive plot object for data analysis and exploration. \nDataset:\n{self.data}"

    @staticmethod
    def _split_ids(ids):
        """
        Function to split IDs and get back lists of conditions, times and replicates in order

        :param ids: IDs generated by IsoplotData Object
        :type ids: list
        :return: lists containing conditions, times and replicates
        :rtype: lists
        """

        count = ids[0].count('_')
        if count == 2:
            conditions, times, replicates = [], [], []
            for i in ids:
                c, t, r = i.split("_")
                conditions.append(c)
                times.append(t)
                replicates.append(r)
            return conditions, times, replicates
        if count == 1:
            conditions, times = [], []
            for i in ids:
                c, t = i.split("_")
                conditions.append(c)
                times.append(t)
            return conditions, times
        else:
            raise ValueError('Number of underscores is different from 2 or 3')

    def _compute_whisker_points(self, df, df_sds, labels):
        """
        Compute the bottom, top and base values for placing whiskers on a stacked bar plot

        :param df: DataFrame containing
        :param df_sds:
        :return:
        """

        if self.stack:
            df = df.cumsum(axis=1)
        upper_df = df + df_sds
        lower_df = df - df_sds
        whisker_points = {}
        for col in df.columns:
            if len(labels) > len(df.index):
                base = [base for base in labels if base[1] == col]
            else:
                base = labels
            whisker_points.update(
                {col: {
                    "upper": upper_df[col].to_list(),
                    "lower": lower_df[col].to_list(),
                    "base": base
                }}
            )
        return whisker_points

    def _pivot_data(self, mean):
        """
        Pivot the data to get the isotopologues as columns.

        :param mean: should means be computed (error bars)
        :return: pivoted dataframes
        """

        if mean:
            df = self.mean_data.pivot_table(index=["condition_order", "ID"],
                                            columns="isotopologue",
                                            values=self.value + "_mean").sort_index(
                level="condition_order").droplevel(level="condition_order")
            df_sds = self.mean_data.pivot_table(index=["condition_order", "ID"],
                                                columns="isotopologue",
                                                values=self.value + "_sd").sort_index(
                level="condition_order").droplevel(level="condition_order")
            return df, df_sds
        else:
            df = self.data.pivot_table(index=["condition_order", "ID"],
                                       columns="isotopologue",
                                       values=self.value).sort_index(
                level="condition_order").droplevel(level="condition_order")
            return df

    def _build_stacked_barplot(self, mean):
        """
        Build barplot with bars stacked on top of each other (each bar corresponds to one isotopologue)

        :param mean: should means be computed (error bars)
        :return: figure containing the interactive barplot
        """

        try:
            df, df_sds = self._pivot_data(mean)
            df.columns, df_sds.columns = df.columns.astype(str), df_sds.columns.astype(str)
        except ValueError:
            df = self._pivot_data(mean)
            df.columns = df.columns.astype(str)
        except Exception:
            raise RuntimeError("Error while pivoting the data")
        stackers = df.columns.to_list()
        x_range = df.index.to_list()
        data = {y: df[y].to_numpy() for y in stackers}
        if mean:
            conditions, times = InteractivePlot._split_ids(x_range)
            data.update({
                "x_labels": x_range,
                "conditions": conditions,
                "times": times,
            })
            tooltips = [
                ("Condition", "@conditions"),
                ("Time", "@times"),
                ("Isotopologue", "$name"),
                ("Value", "@$name")
            ]
        else:
            conditions, times, replicates = InteractivePlot._split_ids(x_range)
            data.update({
                "x_labels": x_range,
                "conditions": conditions,
                "times": times,
                "replicates": replicates
            })
            tooltips = [
                ("Condition", "@conditions"),
                ("Time", "@times"),
                ("Replicate", "@replicates"),
                ("Isotopologue", "$name"),
                ("Value", "@$name")
            ]
        plot = figure(x_range=x_range, width=self.WIDTH, height=self.HEIGHT, title=self.metabolite,
                      tools=self.plot_tools, y_axis_label=self.value, tooltips=tooltips)
        plot.vbar_stack(stackers, x="x_labels", source=data, legend_label=stackers,
                        color=cc.glasbey_dark[:len(stackers)], width=0.9)
        plot.xaxis.major_label_orientation = math.pi / 4
        plot.legend.location = "top_left"
        plot.legend.orientation = "horizontal"
        plot.outline_line_color = "black"
        if mean:
            from bokeh.models import Whisker
            whisker_points = self._compute_whisker_points(df, df_sds, x_range)
            for key in whisker_points.keys():
                cds = ColumnDataSource(data=whisker_points[key])
                plot.add_layout(
                    Whisker(source=cds, base="base", upper="upper", lower="lower", level="overlay")
                )
        return plot

    def _build_unstacked_barplot(self, mean):
        """
        Build grouped bar chart
        :param mean: Should means be computed
        :return: grouped bar chart
        """

        try:
            df, df_sds = self._pivot_data(mean)
            df.columns, df_sds.columns = df.columns.astype(str), df_sds.columns.astype(str)
        except ValueError:
            df = self._pivot_data(mean)
            df.columns = df.columns.astype(str)
        except Exception:
            raise RuntimeError("Error while pivoting the data")

        x_range = df.index.to_list()
        stackers = df.columns.to_list()
        # We prepare the labels for tooltips on the plot
        x = [(idx, stack) for idx in x_range for stack in stackers]
        labels = [i[0] for i in x]
        isotops = [i[1] for i in x]
        # We get the list of all the top values of the bars in our plot
        tops = [item for sublist in [row[1].to_list() for row in df.iterrows()] for item in sublist]
        if not mean:
            conditions, times, replicates = InteractivePlot._split_ids(labels)
            source = ColumnDataSource(dict(x=x, tops=tops, conditions=conditions,
                                           times=times, replicates=replicates,
                                           isotops=isotops))
            tooltips = [
                ("Condition", "@conditions"),
                ("Time", "@times"),
                ("Replicate", "@replicates"),
                ("Value", "@tops")
            ]
        else:
            conditions, times = InteractivePlot._split_ids(labels)
            source = ColumnDataSource(dict(x=x, tops=tops, conditions=conditions,
                                           times=times, isotops=isotops)
                                      )
            tooltips = [
                ("Condition", "@conditions"),
                ("Time", "@times"),
                ("Value", "@tops")
            ]
        plot = figure(
            x_range=FactorRange(*x),
            plot_width=self.WIDTH,
            plot_height=self.HEIGHT,
            tools=self.plot_tools,
            tooltips=tooltips
        )
        plot.vbar(x='x',
                  top='tops',
                  width=0.9,
                  source=source,
                  fill_color=factor_cmap('x',
                                         palette=cc.glasbey_dark,
                                         factors=stackers,
                                         start=1, end=2),
                  line_color="white")
        if mean:
            from bokeh.models import Whisker
            whisker_points = self._compute_whisker_points(df, df_sds, x)
            for key in whisker_points.keys():
                cds = ColumnDataSource(data=whisker_points[key])
                plot.add_layout(
                    Whisker(source=cds, base="base", upper="upper", lower="lower", level="overlay")
                )
        plot.xaxis.major_label_orientation = math.pi / 4
        plot.y_range.start = 0
        plot.x_range.range_padding = 0.1
        return plot

    def stacked_areaplot(self, mean=False):

        # TODO: fix tooltips not showing

        df = self._pivot_data(mean)
        data_points = {str(col): df[col].to_list() for col in df.columns}
        stackers = list(data_points.keys())
        data_points.update({"x": df.index.to_list()})
        source = ColumnDataSource(data_points)
        tooltips = [
            ("X", "@x"),
            ("Value", "@$name")
        ]
        plot = figure(x_range=data_points["x"], width=self.WIDTH, height=self.HEIGHT, y_axis_label=self.value,
                      tooltips=tooltips, tools=self.plot_tools)
        plot.varea_stack(stackers, x="x", source=source, color=cc.glasbey_dark[:len(stackers)])
        plot.xaxis.major_label_orientation = math.pi / 4
        plot.y_range.start = 0
        plot.x_range.range_padding = 0.1
        show(plot)

    def barplot(self, mean=False):

        if self.stack:
            plot = self._build_stacked_barplot(mean)
        else:
            plot = self._build_unstacked_barplot(mean)
        show(plot)


class Map:
    """
    Class to create maps from Isocor output (MS data from C13 labelling experiments)

    :param annot: Should annotations be apparent on map or not
    :type annot: Bool
    """

    def __init__(self, data, name, annot, fmt, display=False):

        self.data = data
        self.name = name
        self.annot = annot
        self.fmt = fmt
        self.display = display

        # Il faut préparer les données pour les maps:
        self.heatmapdf = self.data[self.data['mean_enrichment'] != 0].copy()
        self.heatmapdf.drop_duplicates(inplace=True)
        self.heatmapdf.dropna(inplace=True)
        self.heatmapdf.reset_index(inplace=True)
        self.heatmapdf.set_index("metabolite", inplace=True)
        self.heatmapdf['Condition_Time'] = self.heatmapdf['condition'].apply(str) + '_T' + self.heatmapdf['time'].apply(
            str)
        self.heatmapdf = self.heatmapdf.groupby(
            ['metabolite', 'Condition_Time'])['mean_enrichment'].mean()
        self.heatmapdf = self.heatmapdf.unstack(0)
        self.dc_heatmap = self.heatmapdf.describe(include='all')
        self.heatmap_center = self.dc_heatmap.iloc[5, 0].mean()
        self.clustermapdf = self.heatmapdf.fillna(value=0)

    def build_heatmap(self):
        """
        Create a heatmap of mean_enrichment data across
        all conditions & times & metabolites
        """

        fig, ax = plt.subplots(figsize=(30, 30))
        sns.set(font_scale=1)
        sns.heatmap(self.heatmapdf, vmin=0.02,
                    robust=True, center=self.heatmap_center,
                    annot=self.annot, fmt="f", linecolor='black',
                    linewidths=.2, cmap='Blues', ax=ax)
        plt.yticks(rotation=0, fontsize=20)
        plt.xticks(rotation=45, fontsize=20)
        if self.display:
            plt.show()
        return fig

    def build_clustermap(self):
        """
        Create a clustermap of mean_enrichment data across
        all conditions & times & metabolites
        """

        sns.set(font_scale=1)
        cg = sns.clustermap(self.clustermapdf,
                            cmap="Blues", fmt="f",
                            linewidths=.2, standard_scale=1,
                            figsize=(30, 30), linecolor='black',
                            annot=self.annot)
        plt.setp(cg.ax_heatmap.yaxis.get_majorticklabels(), rotation=0, fontsize=20)
        plt.setp(cg.ax_heatmap.xaxis.get_majorticklabels(), rotation=45, fontsize=20)
        plt.savefig(self.name + '_' + 'clustermap' + '.' + self.fmt, bbox_inches='tight', format=self.fmt)
        if self.display:
            plt.show()

    def build_interactive_heatmap(self):
        """
        Create an interactive heatmap of mean_enrichment data across
        all conditions & times & metabolites
        """

        output_file(filename=self.name + '_' + 'heatmap' + ".html", title=self.name + ".html")
        condition_time = list(self.heatmapdf.index.astype(str))
        metabolites = list(self.heatmapdf.columns)
        # Nous réordonnons les données
        df = pd.DataFrame(self.heatmapdf.stack(), columns=["values"]).reset_index()
        # Nous préparons les couleurs
        colors = cc.kbc[len(df)]
        mapper = LinearColorMapper(palette=cc.kbc[:len(df)])
        tooltips = "hover,save"
        # initialisation de la figure
        myplot = figure(title=self.name,
                        x_range=list(reversed(metabolites)), y_range=condition_time,
                        x_axis_location="below", plot_width=1080, plot_height=640,
                        tools=tooltips, toolbar_location='above',
                        tooltips=[('datapoint', '@metabolite @Condition_Time'), ('value', "@values")])
        myplot.grid.grid_line_color = None
        myplot.axis.axis_line_color = None
        myplot.axis.major_tick_line_color = None
        myplot.axis.major_label_text_font_size = "15px"
        myplot.axis.major_label_standoff = 0
        myplot.xaxis.major_label_orientation = math.pi / 3
        # Passons au plot
        myplot.rect(x="metabolite",
                    y="Condition_Time",
                    width=1, height=1,
                    source=df,
                    fill_color={'field': "values", 'transform': mapper},
                    line_color=None)
        # Nous préparons la barre de couleur pour la légende
        color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="7px",
                             ticker=BasicTicker(desired_num_ticks=len(colors)),
                             formatter=PrintfTickFormatter(),
                             label_standoff=6, border_line_color=None, location=(0, 0))
        # Ajoutons la barre de couleur de la légende
        myplot.add_layout(color_bar, 'right')
        if self.display:
            show(myplot)
        else:
            save(myplot)
