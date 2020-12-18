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
    ''' 
        
    #Initiate logger
    logger = logging.getLogger(__name__)
    stream_handle = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handle.setFormatter(formatter)
    logger.addHandler(stream_handle)
    
    
    parser = parseArgs()
    args = parser.parse_args()
    
    #Check for typos and input errors
    if args.format not in ['png', 'svg', 'pdf','jpeg', 'html']:
        
        raise RuntimeError("Format must be png, svg, pdf, jpeg or html")
    
    if not os.path.exists(args.destination):
        
        raise RuntimeError(
            f"The entered destination path {args.destination} is not valid. Please check for typos")
    
    #Set verbosity
    if args.verbose == True:
        logger.setLevel(logging.DEBUG)
        
    else:
        logger.setLevel(logging.INFO)
        
    Main(args, logger)       

def Main(args, logger):   
    
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
    
    :raises RuntimeError: if inputed destination path does not exist raises error
    :raises RuntimeError: if inputed template path does not exist raises error
    '''
    
    logger.debug("Starting main")
    
    #Prepare directory where logger, plots and data will be exported
    now = datetime.datetime.now()
    date_time = now.strftime("%d%m%Y_%H%M%S") #Récupération date et heure
    
    logger.debug("Building end folder")
    
    os.chdir(args.destination) #Go to destination
    os.mkdir(args.name + " " + date_time) #Create dir
    os.chdir(args.name + " " + date_time) #Infiltrate dir
    
    logger.debug("Generating data object")
    
    #Initialize data object from path retrieved from user through argument parser
    try:
        data_object = IsoplotData(args.datafile)
        data_object.get_data()
        
    except Exception as dataload_err:
        raise RuntimeError(f"Error while loading data. \n Error: {dataload_err}")
    
    #If template is not given, we generate it and stop here
    if args.template == 0:
        
        logger.debug("Generating template")
        data_object.generate_template()
        logger.info("Template has been generated. Check destination folder at {}".format(args.destination))
    
    #If template is given, we check the path and then generate data object
    else:
        
        logger.debug("Getting template, merging and preparing data")
        
        if not os.path.exists(args.template):
            raise RuntimeError(f"Error in template path {args.template}")
        
        #Fetch template and merge with data
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
        
        #Get lists of parameters for plots
        metabolites = get_cli_input(args.metabolite, "metabolite", data_object, logger)
        
        conditions = get_cli_input(args.condition, "condition", data_object, logger)
        
        times = get_cli_input(args.time, "time", data_object, logger)
        
        logger.info("--------------------")
        logger.info("metabolites: {}".format(metabolites))
        logger.info("conditions: {}".format(conditions))
        logger.info("times: {}".format(times))
        logger.info("--------------------")
        
        logger.info("Creating plots...")
        
        #Finally we call the function that coordinates the plot creation
        if args.static_heatmap or args.static_clustermap or args.interactive_heatmap:
            
            try:
                control_isoplot_map(args, data_object)
                
            except Exception as map_err:
                raise RuntimeError(f"Error while generating map.\n Error: {map_err}")

        
        else:
            for metabolite in metabolites:
                control_isoplot_plot(args, data_object, metabolite, conditions, times)
        
        logger.info('Done!')

