import argparse
import logging

from isoplot.plots import StaticPlot, InteractivePlot, Map

logger = logging.getLogger(__name__)

def parseArgs():
    
    '''Creation of Isoplot parser for usage of CLI
    
    :param parser: parser object used to parse arguments from clithrough sys.argv
    :type parser: class: arparse.ArgumentParser
        
    '''
    
    logger.debug('Initializing parser')
    parser = argparse.ArgumentParser("Isoplot2: Plotting isotopic labelling MS data")

    logger.debug('Adding positionnal arguments for general plot infos')
    parser.add_argument('datafile', help= "Path to datafile")
    parser.add_argument('destination', help= "Path to export destination")
    parser.add_argument("name", help="Name of generated file")
    parser.add_argument("format", help="Format of generated file")
    parser.add_argument('value', choices=['corrected_area', 'isotopologue_fraction', 'mean_enrichment'])
    
    parser.add_argument('-m', '--metabolite', default='all',
                        help= "Metabolite(s) to plot. For all, type in 'all' ")
    parser.add_argument('-c','--condition', default='all',
                        help= "Condition(s) to plot. For all, type in 'all' ")
    parser.add_argument('-t', '--time', default='all',
                        help= "Time(s) to plot. For all, type in 'all' ")
    parser.add_argument("-tp","--template", default=0, action="store",
                        help="Path to template")
    
    logger.debug('Adding optionnal arguments for calling the plot methods')
    parser.add_argument('-sa', '--stacked_areaplot', action="store_true", 
                        help='Create static stacked areaplot')
    parser.add_argument("-bp", "--barplot", action="store_true", 
                        help='Create static barplot(for corrected_area and isotopologue_fraction)')
    parser.add_argument('-mb', '--meaned_barplot',action="store_true", 
                        help='Create static barplot with meaned replicates(for corrected_area and isotopologue_fraction)')
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
                         help='Create interactive stacked barplot with meaned replicates (for corrected area and isotopologue_fraction)')
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
    
    '''Function to control which plot methods are called depending on the 
    arguments that were parsed'''
    
    logger.debug("Initiating plot object")
    
    static_plot = StaticPlot(args.stack, args.value, data_object.dfmerge, 
                             args.name, metabolite, conditions, times, args.format,)
    
    interactive_plot = InteractivePlot(args.stack, args.value, data_object.dfmerge, 
                                       args.name, metabolite, conditions, times)
    
    logger.debug("Selecting plot method")
    
    if args.stacked_areaplot:
        static_plot.stacked_areaplot()
    
    elif args.barplot:
        static_plot.barplot()
        
    elif args.meaned_barplot:
        static_plot.mean_barplot()
    
    elif args.static_mean_enrichment_plot:
        static_plot.mean_enrichment_plot()
        
    elif args.static_mean_enrichment_meanplot:
        static_plot.mean_enrichment_meanplot()
        
    elif args.interactive_mean_enrichment_plot:
        interactive_plot.mean_enrichment_plot()
    
    elif args.interactive_mean_enrichment_meanplot:
        interactive_plot.mean_enrichment_meanplot()

    elif args.interactive_stacked_barplot:
        interactive_plot.stacked_barplot()
        
    elif args.interactive_stacked_barplot and args.stack == False:
        interactive_plot.unstacked_barplot()
        
    elif args.interactive_stacked_meanplot:
        interactive_plot.stacked_meanplot()
        
    elif args.interactive_stacked_meanplot and args.stack == False:
        interactive_plot.unstacked_meanplot()
        
    elif args.interactive_stacked_areaplot:
        interactive_plot.stacked_areaplot()

def control_isoplot_map(args, data_object):
    '''Function to control which map methods are called depending on the 
    arguments that were parsed'''
    
    logger.debug("Initiating map object")
    
    mymap = Map(data_object.dfmerge, args.name,args.annot, args.format)
    
    logger.debug("Selecting plot method")
    
    if args.static_heatmap:
        mymap.build_heatmap()
        
    elif args.static_clustermap:
        mymap.build_clustermap()
        
    elif args.interactive_heatmap:
        mymap.interactive_heatmap()    
        

def get_local_cli_input(name, data_object, logger):
    
    '''Function to get input from user and check for errors in spelling. 
    If an error is detected input is asked once more.
    This function shall be used for local installations only 
    
    :param is_error: True while the user input is invalid
    :type is_error: boolean
    :param desire: container for the CLI user input
    :type desire: list of str
    '''
    
    is_error = True
    
    while is_error:
        try:
            #We show the list of possibilities to user
            print(data_object.dfmerge[name].unique())
            
            #Cli gives list of strings, se we must make words of them
            desire = [item for item in input("Input " + name 
                    + "(s) to plot from list above (write 'all' for all to be plotted) "
                    ).split()]
            
            #Checking input for typos
            for item in desire:
                if item == "all":
                    break
                else:
                    assert item in data_object.dfmerge[name].unique()
                    
        except AssertionError:
            logger.error(
                "One or more of the chosen " + name + "(s) were not in list. Please check and try again.")
            
        except Exception as e:
            logger.error("Unexpected error: {}".format(e))
            
        else:
            logger.info("Chosen " + name + ": {}".format(desire))
            is_error = False
     
    if item == "all":
        desire = data_object.dfmerge[name].unique() 
            
    return desire

def get_cli_input(arg, name, data_object, logger):
    
    '''Function to get input from user and check for errors in spelling.
    If an error is detected input is asked once more.
    This function is used for galaxy implementation 
    
    :param is_error: True while the user input is invalid
    :type is_error: boolean
    :param desire: container for the CLI user input
    :type desire: list of str
    '''
    
    is_error = True
    
    while is_error:
        try:
            
            #Cli gives list of strings, se we must make words of them
            desire = [item for item in arg.split(",")]
            
            #Checking input for typos
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
     
    if item == "all":
        desire = data_object.dfmerge[name].unique() 
            
    return desire

# DECORATORS

def new_dir(original_function):
    def wrapper_function(*args, **kwargs):
        from datetime import datetime
        from os import mkdir, chdir, getcwd
        now_time = datetime.now()
        date_time = now_time.strftime("%d%m%Y_%H%M%S") #Récupération date et heure
        mydir = getcwd()
        name = getattr(original_function, 'name')
        mkdir(name + " " + date_time) #Créons le dir
        chdir(name + " " + date_time) #Rentrons dans le dir
        
        result = original_function(*args, **kwargs)
        
        chdir(mydir)
        
        return result
    return wrapper_function
            
            