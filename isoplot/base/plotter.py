"""Module containing the plotting classes."""

import matplotlib.pyplot as plt
import numpy as np
import colorcet as cc


class StaticPlot:
    """
    Class to generate the different Static Plots using pandas built-in plotting modules
    """

    def __init__(self, data, metabolite, conditions, times, value, fmt, stack=True, display=True):
        """
        During initialization, data is filtered on the desired metabolite, conditions, times and value to plot. We also
        input the desired format, and booleans to define if bars in barplots should be unstacked and if plots should be
        directly displayed.

        :param data: Dataframe containing the clean data passed on by DataHandler object
        :param metabolite: Metabolite to plot
        :param conditions: List of conditions to plot
        :param times: List of time points to plot
        :param value: Which value should be plotted (mean enrichment, isotopologue fraction or corrected areas)
        :param fmt: Format in which plots should be saved
        :param stack: While true bars are stacked
        :param display: While true plots are displayed
        """

        self.data = data.loc[(metabolite, conditions, times)].droplevel(0)
        if value == "mean_enrichment":
            self.data = self.data[self.data.index.get_level_values("isotopologue") == 0]
        self.metabolite = metabolite
        self.conditions = conditions
        self.times = times
        self.value = value
        self.fmt = fmt
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
            df = self.data.pivot_table(index=["ID", "condition_order"],
                                       columns="isotopologue",
                                       values=self.value + "_mean").sort_index(
                level="condition_order").droplevel(level="condition_order")
            sd_df = self.data.pivot_table(index=["ID", "condition_order"],
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

    def stacked_areaplot(self, mean=False):

        fig, ax = plt.subplots()
        if not mean:
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
            return fig
        else:
            pass
