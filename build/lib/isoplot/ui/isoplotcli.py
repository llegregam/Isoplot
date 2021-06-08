"""Module containing the CLI class that will be used during the cli process to get arguments from user and
generate the desired plots"""

import os
import argparse
from isoplot.main.plots import StaticPlot, InteractivePlot, Map


class IsoplotCli:

    def __init__(self):

        self.parser = argparse.ArgumentParser("Isoplot2: Plotting isotopic labelling MS data")

        self.home = None
        self.run_home = None
        self.static_plot = None
        self.int_plot = None
        self.map = None
        self.args = None

        self.metabolites = []
        self.conditions = []
        self.times = []

    def dir_init(self, plot_type):
        """Initialize directory for plot"""
        wd = self.run_home / plot_type
        if os.path.exists(wd):
            os.chdir(wd)
        else:
            wd.mkdir()
            os.chdir(wd)

    def go_home(self):
        """Exit after work is done"""
        os.chdir(self.home)

    def parse_Args(self):
        """
        Parse arguments from user

        :return: Argument Parser object
        :rtype: class: argparse.ArgumentParser
        """

        self.parser.add_argument('input_path', help="Path to datafile")
        self.parser.add_argument("run_name", help="Name of the current run")
        self.parser.add_argument("format", help="Format of generated file")

        values = ['corrected_area', 'isotopologue_fraction', 'mean_enrichment']
        self.parser.add_argument('--value', choices=values, default='isotopologue_fraction',
                                 action="store", required=True, nargs='*',
                                 help="Select values to plot. This option can be given multiple times")

        self.parser.add_argument('-m', '--metabolite', default='all',
                                 help="Metabolite(s) to plot. For all, type in 'all' ")
        self.parser.add_argument('-c', '--condition', default='all',
                                 help="Condition(s) to plot. For all, type in 'all' ")
        self.parser.add_argument('-t', '--time', default='all',
                                 help="Time(s) to plot. For all, type in 'all' ")
        self.parser.add_argument("-gt", "--generate_template", action="store_true",
                                 help="Generate the template using datafile metadata")
        self.parser.add_argument("-tp", "--template_path", type=str,
                                 help="Path to template file")

        self.parser.add_argument('-sa', '--stacked_areaplot', action="store_true",
                                 help='Create static stacked areaplot')
        self.parser.add_argument("-bp", "--barplot", action="store_true",
                                 help='Create static barplot')
        self.parser.add_argument('-mb', '--meaned_barplot', action="store_true",
                                 help='Create static barplot with meaned replicates')

        self.parser.add_argument('-IB', '--interactive_barplot', action="store_true",
                                 help='Create interactive stacked barplot')
        self.parser.add_argument('-IM', '--interactive_stacked_meanplot', action="store_true",
                                 help='Create interactive stacked barplot with meaned replicates')
        self.parser.add_argument('-IS', '--interactive_areaplot', action="store_true",
                                 help='Create interactive stacked areaplot')

        self.parser.add_argument('-hm', '--static_heatmap', action="store_true",
                                 help='Create a static heatmap using mean enrichment data')
        self.parser.add_argument('-cm', '--static_clustermap', action="store_true",
                                 help='Create a static heatmap with clustering using mean enrichment data')
        self.parser.add_argument('-HM', '--interactive_heatmap', action="store_true",
                                 help='Create interactive heatmap using mean enrichment data')

        self.parser.add_argument('-s', '--stack', action="store_false",
                                 help='Add option if barplots should be unstacked')
        self.parser.add_argument('-v', '--verbose', action="store_true",
                                 help='Turns logger to debug mode')
        self.parser.add_argument('-a', '--annot', action='store_true',
                                 help='Add option if annotations should be added on maps')

        self.parser.add_argument('-g', '--galaxy', action='store_true',
                                 help='Option for galaxy integration. Not useful for local usage')

    @staticmethod
    def get_cli_input(arg, param, data_object):
        """
        Function to get input from user and check for errors in spelling.
        If an error is detected input is asked once more.
        This function is used for galaxy implementation

        :param arg: list from which strings must be parsed
        :param param: name of what we are looking for
        :type param: str
        :param data_object: IsoplotData object containing final clean dataframe
        :type data_object: class: 'isoplot.dataprep.IsoplotData'

        :return: Desired string after parsing
        :rtype: list

        """

        if arg == "all":
            desire = data_object.dfmerge[param].unique()
        else:
            is_error = True

            while is_error:
                try:
                    # Cli gives list of strings, se we must make words of them
                    desire = [item for item in arg.split(",")]
                    # Checking input for typos
                    for item in desire:
                        if item == "all":
                            break
                        else:
                            if item not in data_object.dfmerge[param].unique():
                                raise KeyError(f"One or more of the chosen {param}(s) were not in list. "
                                               f"Please check and try again. Error: {item}")
                except Exception as e:
                    raise RuntimeError(f"There was a problem while reading input. Error: {e}")

                else:
                    is_error = False
        return desire

    def plot_figs(self, metabolite_list, data_object):
        """Function to control which plot methods are called depending on the
            arguments that were parsed"""

        for metabolite in metabolite_list:
            for value in self.args.value:
                self.static_plot = StaticPlot(self.args.stack, value, data_object.dfmerge,
                                              self.args.run_name, metabolite, self.conditions, self.times,
                                              self.args.format, display=False)

                self.int_plot = InteractivePlot(self.args.stack, value, data_object.dfmerge,
                                                self.args.run_name, metabolite, self.conditions, self.times,
                                                display=False)

                # STATIC PLOTS
                if self.args.stacked_areaplot:
                    self.dir_init("Static_Areaplots")
                    self.static_plot.stacked_areaplot()

                if self.args.barplot and not (value == "mean_enrichment"):
                    self.dir_init("Static_barplots")
                    self.static_plot.barplot()

                if self.args.meaned_barplot and not (value == "mean_enrichment"):
                    self.dir_init("Static_barplots_SD")
                    self.static_plot.mean_barplot()

                if self.args.barplot and (value == "mean_enrichment"):
                    self.dir_init("Static_barplots")
                    self.static_plot.mean_enrichment_plot()

                if self.args.meaned_barplot and (value == "mean_enrichment"):
                    self.dir_init("Static_barplots_SD")
                    self.static_plot.mean_enrichment_meanplot()

                # INTERACTIVE PLOTS
                if self.args.interactive_barplot and not (value == "mean_enrichment"):
                    self.dir_init("Interactive_barplots")
                    self.int_plot.stacked_barplot()

                if self.args.interactive_barplot and not self.args.stack:
                    self.dir_init("Interactive_barplots")
                    self.int_plot.unstacked_barplot()

                if self.args.interactive_meanplot and not (value == "mean_enrichment"):
                    self.dir_init("Interactive_barplots_SD")
                    self.int_plot.stacked_meanplot()

                if self.args.interactive_meanplot and not self.args.stack:
                    self.dir_init("Interactive_barplots_SD")
                    self.int_plot.unstacked_meanplot()

                if self.args.interactive_barplot and (value == "mean_enrichment"):
                    self.dir_init("Interactive_barplots")
                    self.int_plot.mean_enrichment_plot()

                if self.args.interactive_meanplot and (value == "mean_enrichment"):
                    self.dir_init("Interactive_barplots_SD")
                    self.int_plot.mean_enrichment_meanplot()

                if self.args.interactive_areaplot:
                    self.dir_init("Interactive_stackplots")
                    self.int_plot.stacked_areaplot()

        # MAPS
        self.map = Map(data_object.dfmerge, self.args.run_name, self.args.annot, self.args.format)

        if self.args.static_heatmap:
            self.dir_init("Maps")
            self.map.build_heatmap()

        if self.args.static_clustermap:
            self.dir_init("Maps")
            self.map.build_clustermap()

        if self.args.interactive_heatmap:
            self.dir_init("Maps")
            self.map.build_interactive_heatmap()

        if rtrn:
            IsoplotCli.zip_export(figures, self.args.run_name)
        if not self.args.galaxy:
            self.go_home()

    def initialize_cli(self):
        """Launch argument parsing and perform checks"""

        self.parse_Args()
        self.args = self.parser.parse_args()

        # Check for typos and input errors
        valid_formats = ['png', 'svg', 'pdf', 'jpeg', 'html']
        forbidden_characters = ["*", ".", '"', "/", "\\", "[", "]", ":", ";", "|", ","]

        if not os.path.exists(self.args.input_path):
            raise RuntimeError(f"Input path does not lead to valid file. "
                               f"Please check path: {self.args.input_path}")

        if self.args.format not in valid_formats:
            raise RuntimeError("Format must be png, svg, pdf, jpeg or html")

        for char in forbidden_characters:
            if char in self.args.run_name:
                raise RuntimeError(f"Invalid character in run name. "
                                   f"Forbidden characters are: {forbidden_characters}")

        if self.args.template_path and not os.path.exists(self.args.template_path):
            raise RuntimeError(f"Template path does not lead to valid file. "
                               f"Please check path: {self.args.template_path}")
