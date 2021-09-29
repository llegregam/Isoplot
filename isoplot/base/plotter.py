"""Module containing the plotting classes."""

import math

import colorcet as cc
import matplotlib.pyplot as plt
from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.transform import factor_cmap
from bokeh.plotting import figure


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
        self.cds = ColumnDataSource(self.data)
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

    @staticmethod
    def _compute_whisker_points(df, df_sds):
        """
        Compute the bottom, top and base values for placing whiskers on a stacked bar plot

        :param df: DataFrame containing
        :param df_sds:
        :return:
        """

        heights = df.cumsum(axis=1)
        upper_df = heights + df_sds
        lower_df = heights - df_sds
        base = df.index.to_list()
        whisker_points = {}
        for col in heights.columns:
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
            whisker_points = InteractivePlot._compute_whisker_points(df, df_sds)
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
        contition_time_replicate = [i[0] for i in x]
        isotops = [i[1] for i in x]
        conditions, times, replicates = InteractivePlot._split_ids(contition_time_replicate)
        # We get the list of all the top values of the bars in our plot
        tops = [item for sublist in [row[1].to_list() for row in df.iterrows()] for item in sublist]
        source = ColumnDataSource(dict(x=x, tops=tops, conditions=conditions,
                                       times=times, replicates=replicates,
                                       isotops=isotops))
        tooltips = [
            ("Condition", "@conditions"),
            ("Time", "@times"),
            ("Replicate", "@replicates"),
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
        plot.xaxis.major_label_orientation = math.pi / 4
        plot.y_range.start = 0
        plot.x_range.range_padding = 0.1
        return plot

    def barplot(self, mean=False):

        if self.stack:
            plot = self._build_stacked_barplot(mean)
        else:
            plot = self._build_unstacked_barplot(mean)
        show(plot)
