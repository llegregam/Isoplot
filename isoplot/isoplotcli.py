'''Isoplot2 MAIN MODULE containing argument parser, cli initialization and main logger creation.'''

import datetime
import os
import logging

from isoplot.utilities import control_isoplot_plot,control_isoplot_map, get_cli_input, parseArgs
from isoplot.dataprep import IsoplotData




def initialize_cli():
    '''Initialize parser and call main function
    
    :param parser: variable to store the Argument parser object
    :type parser: class: 'argparse.ArgumentParser'
    :param args: List of strings to parse. The default is taken from sys.argv
    :type args: List of arguments
    :raises AssertionError: Error raised if format given is not png, svg, pdf, jpeg or html 
    '''
	    
    parser = parseArgs()
    args = parser.parse_args()
    
    #Check for typos and input errors
    try:
        assert args.format in ['png', 'svg', 'pdf','jpeg', 'html']
    except AssertionError:
        print("There has been a problem with the given format. Possible choices are: png, svg, pdf, jpeg, html")
        raise
        
    Main(args)       

def Main(args):   
    
    '''Main function responsible for directory creation, launching plot creation 
    and coordinating different modules. Can be put in a separate module if the need 
    ever arises (if a GUI is created for example).
    
    :param args: List of strings to parse. The default is taken from sys.argv
    :type args: list of arguments
    :param logger: main logger that will be derived in other modules
    :type logger: class: 'logging.Logger'
    :param stream_handle: logger handler that sends log to stream
    :type stream_handle: class: 'logging.Handler'
    :param formatter: formatter to give log format of logger
    :type formatter: class: 'logging.Formatter'
    :param now: current date and time in format code. Used when creating directory in which plots and log will go
    :type now: class: 'datetime.datetime'
    :param date_time: formatted string based on format code returned by datetime.datetime.now()
    :type date_time: str
    :param data_object: data container used to get data and clean data before plotting
    :type data_object: class: 'IsoplotData'
    :param metabolites: list of metabolites that user inputed for plotting
    :type metabolites: list of str
    :param conditions: list of conditions that user inputed for plotting
    :type conditions: list of str
    :param times: list of times that user inputed for plotting
    :type times: list of str
    
    :raises AssertionError: if inputed destination path does not exist raises error
    :raises AssertionError: if inputed template path does not exist raises error
    '''
    
    #Initiate logger
    logger = logging.getLogger('Isoplot')
    stream_handle = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handle.setFormatter(formatter)
    logger.addHandler(stream_handle)
    
    #Set verbosity
    if args.verbose == True:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    logger.debug("Starting main")
    
    #Prepare directory where logger, plots and data will be exported
    now = datetime.datetime.now()
    date_time = now.strftime("%d%m%Y_%H%M%S") #Récupération date et heure
    
    logger.debug("Building end folder")
    
    try:
        assert os.path.exists(args.destination)
    except AssertionError:
        logger.error("The entered destination path ({}) is not valid. Please check for typos"
                     .format(args.destination))
    
    os.chdir(args.destination) #Go to destination
    os.mkdir(args.name + " " + date_time) #Create dir
    os.chdir(args.name + " " + date_time) #Infiltrate dir
    
    logger.debug("Generating data object")
    
    #Initialize data object from path retrieved from user through argument parser
    data_object = IsoplotData(args.datafile)
    data_object.get_data()
    
    #If template is not given, we generate it and stop here
    if args.template == 0:
        logger.debug("Generating template")
        data_object.generate_template()
        logger.info("Template has been generated. Check destination folder at {}".format(args.destination))
    
    #If template is given, we check the path and then generate data object
    else:
        
        logger.debug("Getting template, merging and preparing data")
        
        try:
            assert os.path.exists(args.template)
        except AssertionError:
            logger.error("The entered path to template ({}) is not valid. Please check for typos"
                         .format(args.template))
        
        #Fetch template and merge with data
        data_object.get_template(args.template)
        data_object.merge_data()
        data_object.prepare_data()
        
        logger.debug("Getting input from cli")
        
        #Get lists of parameters for plots
        metabolites = get_cli_input(args.metabolite, "metabolite", data_object, logger)
        
        conditions = get_cli_input(args.condition, "condition", data_object, logger)
        
        times = get_cli_input(args.time, "time", data_object, logger)
        
        logger.info("metabolites: {}".format(metabolites))
        logger.info("conditions: {}".format(conditions))
        logger.info("times: {}".format(times))
        
        logger.info("Creating plots...")
        
        #Finally we call the function that coordinates the plot creation
        if args.static_heatmap or args.static_clustermap or args.interactive_heatmap:
            control_isoplot_map(args, data_object)
        
        elif metabolites[0] == 'all':
            for metabolite in data_object.dfmerge['metabolite'].unique():
                control_isoplot_plot(args, data_object, metabolite, conditions, times)
        
        else:
            for metabolite in metabolites:
                control_isoplot_plot(args, data_object, metabolite, conditions, times)
        
        logger.info('Done!')

