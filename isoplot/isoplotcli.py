"""Isoplot2 cli module containing argument parser, cli initialization and main logger creation."""

import datetime
import os
import logging
import argparse

from isoplot.plots import StaticPlot, InteractivePlot, Map
from isoplot.dataprep import IsoplotData


def initialize_cli():
    """Initialize parser and call main function"""

    parser = parse_args()
    args = parser.parse_args()

    # Check for typos and input errors
    if args.format not in ['png', 'svg', 'pdf', 'jpeg', 'html']:
        raise RuntimeError("Format must be png, svg, pdf, jpeg or html")

    if not os.path.exists(args.destination):
        raise RuntimeError(
            f"The entered destination path {args.destination} is not valid. Please check for typos")

    main(args)


def parse_args():
    """
    :return: Argument Parser object
    :rtype: class: argparse.ArgumentParser
    """

    parser = argparse.ArgumentParser("Isoplot2: Plotting isotopic labelling MS data")

    parser.add_argument('datafile', help="Path to datafile")
    parser.add_argument('destination', help="Path to export destination")
    parser.add_argument("name", help="Name of generated file")
    parser.add_argument("format", help="Format of generated file")
    parser.add_argument('value', choices=['corrected_area', 'isotopologue_fraction', 'mean_enrichment'])

    parser.add_argument('-m', '--metabolite', default='all',
                        help="Metabolite(s) to plot. For all, type in 'all' ")
    parser.add_argument('-c', '--condition', default='all',
                        help="Condition(s) to plot. For all, type in 'all' ")
    parser.add_argument('-t', '--time', default='all',
                        help="Time(s) to plot. For all, type in 'all' ")
    parser.add_argument("-tp", "--template", default=0, action="store",
                        help="Path to template")

    parser.add_argument('-sa', '--stacked_areaplot', action="store_true",
                        help='Create static stacked areaplot')
    parser.add_argument("-bp", "--barplot", action="store_true",
                        help='Create static barplot(for corrected_area and isotopologue_fraction)')
    parser.add_argument('-mb', '--meaned_barplot', action="store_true",
                        help='Create static barplot with meaned replicates(for corrected_area and '
                             'isotopologue_fraction)')
    parser.add_argument('-smp', '--static_mean_enrichment_plot', action="store_true",
                        help='Create static barplot with mean enrichment data')
    parser.add_argument('-smm', '--static_mean_enrichment_meanplot', action="store_true",
                        help='Create static barplot with mean enrichment data and meaned replicates')

    parser.add_argument('-IMP', '--interactive_mean_enrichment_plot', action="store_true",
                        help='Create interactive barplot with mean enrichment data')
    parser.add_argument('-IMM', '--interactive_mean_enrichment_meanplot', action="store_true",
                        help='Create interactive barplot with mean enrichment data and meaned replicates')
    parser.add_argument('-ISB', '--interactive_stacked_barplot', action="store_true",
                        help='Create interactive stacked barplot (for corrected area and isotopologue_fraction)')
    parser.add_argument('-ISM', '--interactive_stacked_meanplot', action="store_true",
                        help='Create interactive stacked barplot with meaned replicates (for corrected area and '
                             'isotopologue_fraction)')
    parser.add_argument('-ISA', '--interactive_stacked_areaplot', action="store_true",
                        help='Create interactive stacked areaplot')

    parser.add_argument('-hm', '--static_heatmap', action="store_true",
                        help='Create a static heatmap using mean enrichment data')
    parser.add_argument('-cm', '--static_clustermap', action="store_true",
                        help='Create a static heatmap with clustering using mean enrichment data')
    parser.add_argument('-HM', '--interactive_heatmap', action="store_true",
                        help='Create interactive heatmap using mean enrichment data')

    parser.add_argument('-s', '--stack', action="store_false",
                        help='Add option if barplots should be unstacked')
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='Turns logger to debug mode')
    parser.add_argument('-a', '--annot', action='store_true',
                        help='Add option if annotations should be added on maps')

    return parser


def control_isoplot_plot(args, data_object, metabolite, conditions, times):
    """Function to control which plot methods are called depending on the
    arguments that were parsed"""

    StatPlot = StaticPlot(args.stack, args.value, data_object.dfmerge,
                          args.name, metabolite, conditions, times, args.format, display=False)

    IntPlot = InteractivePlot(args.stack, args.value, data_object.dfmerge,
                              args.name, metabolite, conditions, times, display=False)

    if args.stacked_areaplot:
        StatPlot.stacked_areaplot()

    elif args.barplot:
        StatPlot.barplot()

    elif args.meaned_barplot:
        StatPlot.mean_barplot()

    elif args.static_mean_enrichment_plot:
        StatPlot.mean_enrichment_plot()

    elif args.static_mean_enrichment_meanplot:
        StatPlot.mean_enrichment_meanplot()

    elif args.interactive_mean_enrichment_plot:
        IntPlot.mean_enrichment_plot()

    elif args.interactive_mean_enrichment_meanplot:
        IntPlot.mean_enrichment_meanplot()

    elif args.interactive_stacked_barplot:
        IntPlot.stacked_barplot()

    elif args.interactive_stacked_barplot and not args.stack:
        IntPlot.unstacked_barplot()

    elif args.interactive_stacked_meanplot:
        IntPlot.stacked_meanplot()

    elif args.interactive_stacked_meanplot and not args.stack:
        IntPlot.unstacked_meanplot()

    elif args.interactive_stacked_areaplot:
        IntPlot.stacked_areaplot()

def control_isoplot_map(args, data_object):
    """Function to control which map methods are called depending on the
    arguments that were parsed"""

    mymap = Map(data_object.dfmerge, args.name, args.annot, args.format)

    if args.static_heatmap:
        mymap.build_heatmap()

    elif args.static_clustermap:
        mymap.build_clustermap()

    elif args.interactive_heatmap:
        mymap.interactive_heatmap()

def get_cli_input(arg, name, data_object, logger):
    """
    Function to get input from user and check for errors in spelling.
    If an error is detected input is asked once more.
    This function is used for galaxy implementation

    :param arg: list from which strings must be parsed
    :param name: name of what we are looking for
    :type name: str
    :param data_object: IsoplotData object containing final clean dataframe
    :type data_object: class: 'isoplot.dataprep.IsoplotData'
    :param logger: Logger object
    :type logger: class: 'logging.Logger'
    :return: Desired string after parsing
    :rtype: list

    """

    if arg == "all":
        desire = data_object.dfmerge[name].unique()
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
                        assert item in data_object.dfmerge[name].unique()

            except AssertionError:
                logger.error(
                    "One or more of the chosen " + name +
                    "(s) were not in list. Please check and try again. Error: {}".format(item))

            except Exception as e:
                logger.error("Unexpected error: {}".format(e))

            else:
                logger.info("Chosen " + name + ": {}".format(desire))
                is_error = False

    return desire

def main(args):
    """
    Main function responsible for directory creation, launching plot creation
    and coordinating different modules. Can be put in a separate module if the need
    ever arises (if a GUI is created for example).

    :param args: List of strings to parse. The default is taken from sys.argv

    :raises RuntimeError: if inputed destination path does not exist raises error
    :raises RuntimeError: if inputed template path does not exist raises error
     """

    logger = logging.getLogger("Isoplot.isoplotcli")
    handle = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handle.setFormatter(formatter)
    logger.addHandler(handle)
    logger.setLevel(logging.INFO)
    handle.setLevel(logging.INFO)

    logger.debug("Starting main")

    # Prepare directory where logger, plots and data will be exported
    now = datetime.datetime.now()
    date_time = now.strftime("%d%m%Y_%H%M%S")  # Récupération date et heure

    logger.debug("Building end folder")

    os.chdir(args.destination)  # Go to destination
    os.mkdir(args.name + " " + date_time)  # Create dir
    os.chdir(args.name + " " + date_time)  # Infiltrate dir

    logger.debug("Generating data object")

    # Initialize data object from path retrieved from user through argument parser
    try:
        data_object = IsoplotData(args.datafile)
        data_object.get_data()

    except Exception as dataload_err:
        raise RuntimeError(f"Error while loading data. \n Error: {dataload_err}")

    # If template is not given, we generate it and stop here
    if args.template == 0:

        logger.debug("Generating template")
        data_object.generate_template()
        logger.info("Template has been generated. Check destination folder at {}".format(args.destination))

    # If template is given, we check the path and then generate data object
    else:

        logger.debug("Getting template, merging and preparing data")

        if not os.path.exists(args.template):
            raise RuntimeError(f"Error in template path {args.template}")

        # Fetch template and merge with data
        try:
            data_object.get_template(args.template)

        except Exception as temp_err:
            raise RuntimeError(f"Error while getting template file.\n Error: {temp_err}")

        try:
            data_object.merge_data()

        except Exception as merge_err:
            raise RuntimeError(f"Error while merging data. \n Error: {merge_err}")

        try:
            data_object.prepare_data()

        except Exception as prep_err:
            raise RuntimeError(f"Error during final preparation of data.\n Error: {prep_err}")

        logger.debug("Getting input from cli")

        # Get lists of parameters for plots
        metabolites = get_cli_input(args.metabolite, "metabolite", data_object, logger)

        conditions = get_cli_input(args.condition, "condition", data_object, logger)

        times = get_cli_input(args.time, "time", data_object, logger)

        logger.info("--------------------")
        logger.info("metabolites: {}".format(metabolites))
        logger.info("conditions: {}".format(conditions))
        logger.info("times: {}".format(times))
        logger.info("--------------------")

        logger.info("Creating plots...")

        # Finally we call the function that coordinates the plot creation
        if args.static_heatmap or args.static_clustermap or args.interactive_heatmap:

            try:
                control_isoplot_map(args, data_object)

            except Exception as map_err:
                raise RuntimeError(f"Error while generating map.\n Error: {map_err}")

        else:
            for metabolite in metabolites:
                control_isoplot_plot(args, data_object, metabolite, conditions, times)

        logger.info('Done!')
