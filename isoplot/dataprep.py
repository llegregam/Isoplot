import logging

import pandas as pd
from natsort import natsorted


class IsoplotData():
    
    """
    Class to prepare Isoplot Data for plotting

    
    :param datapath: Path to .csv file containing Isocor output data
    :type datapath: str
    :param isoplot_logger: Logger object
    :type isoplot_logger: child of logger class: 'logging.Logger'
    :param data: Isocor output data before merge
    :type data: Pandas DataFRame
    :param template: User-defined template containing conditions, times,
                    replicate numbers, etc... before merge
    :type template: Pandas DataFrame
    :param dfmerge: Dataframe containing merged data (template and isocor output). 
                    Is called by prepare_data method and used by Plot class
    :type dfmerge: Pandas DataFrame
    
    :raises UnicodeDecodeError: Is raised by get_template method when template file is 
                                not .xlsx or encoding is not utf-8
    :raises AssertionError: return error if after merge data is not of tye DataFrame
    
    """
        
    def __init__(self, datapath):
        
        self.datapath = datapath
        
        self.isoplot_logger = logging.getLogger(__name__)
        stream_handle = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handle.setFormatter(formatter)
        self.isoplot_logger.addHandler(stream_handle)
        
        self.isoplot_logger.debug('Initializing IsoplotData object')
        self.isoplot_logger.info('Reading datafile {} \n'.format(
            self.datapath))
        
    def get_data(self):
        
        """Read data from csv file and store in object data attribute."""
        
        self.isoplot_logger.info("Reading file...")
        
        try:         
            self.isoplot_logger.debug('Trying to open csv with ";" separator')
            self.data = pd.read_csv(self.datapath, sep=';')
        except:
            try:
                self.isoplot_logger.debug('Trying to open csv with "\t" separator')
                self.data = pd.read_csv(self.datapath, sep='\t')
            except Exception as err:
                self.isoplot_logger.error(
                    'There was a problem reading the csv file. Check that format is .csv with ";" or tabulated separator')
                self.isoplot_logger.error(err)
        else:
            if type(self.data) == None:
                self.isoplot_logger.error(
                    'Dataframe is empty. Please check that file is .csv with ";" or tabulated separator')
        
    def generate_template(self):
        """Generate .xlsx template that user must fill"""
        
        self.isoplot_logger.info("Generating template...")
        
        metadata = pd.DataFrame(columns=[
            "sample","condition","condition_order","time","number_rep","normalization"])
        metadata["sample"] = natsorted(self.data["sample"].unique())
        metadata["condition"] = 'votre_condition'
        metadata["condition_order"] = 1
        metadata["time"] = 1
        metadata["number_rep"] = 3
        metadata["normalization"] = 1.0
        metadata.to_excel(r'ModifyThis.xlsx', index=False)
        
        self.isoplot_logger.info('Template has been generated')

    def get_template(self, path):
        """Read user-filled template and catch any encoding errors"""
        
        self.isoplot_logger.info("Reading template...")
        
        try:
            self.isoplot_logger.debug('Trying to read excel template')
            self.template = pd.read_excel(path, engine='openpyxl')
            
        except UnicodeDecodeError as uni:
            self.isoplot_logger.error(uni)
            self.isoplot_logger.error(
                'Unable to read file. Check file encoding (must be utf-8) or file format (format must be .xlsx)')
        
        except Exception as err:
            self.isoplot_logger.error("There has been a problem...")
            self.isoplot_logger.error(err)
        
        else:
            self.isoplot_logger.info("Template succesfully loaded")
        
    def merge_data(self):
        """Merge template and data into pandas dataframe """
        
        self.isoplot_logger.info("Merging into dataframe...")
        
        try:
            self.isoplot_logger.debug('Trying to merge datas')
            self.dfmerge = self.data.merge(self.template)
            
            if not isinstance(self.dfmerge, pd.DataFrame):
                raise TypeError(f"Error while merging data, dataframe not created. Data turned out to be {type(self.dfmerge)}")
            
        except Exception as err:
            self.isoplot_logger.error(err)
            self.isoplot_logger.error(
                'Merge impossible. Check column headers or file format (format must be .xlsx)')
            raise
            
        else:
            self.isoplot_logger.info('Dataframes have been merged')
    
    def prepare_data(self):
        """Final cleaning of data and export"""
        
        self.isoplot_logger.debug('Preparing data after merge: normalizing...')
        
        self.dfmerge["corrected area normalized"] = self.dfmerge["corrected_area"]/self.dfmerge["normalization"]
        self.dfmerge['metabolite'].drop_duplicates()   
    
        self.isoplot_logger.debug("Creating IDs...")
        #Nous créons ici une colonne pour identifier chaque ligne avec condition+temps+numero de répétition (possibilité de rajouter un tag metabolite plus tard si besoin)
        self.dfmerge['ID'] = self.dfmerge['condition'].apply(str) + '_T' + self.dfmerge['time'].apply(str) + '_' + self.dfmerge['number_rep'].apply(str)
        
        
        self.isoplot_logger.debug('Applying final transformations...')
        #Vaut mieux ensuite retransformer les colonnes temps et number_rep en entiers pour éviter des problèmes éventuels de type
        self.dfmerge['time'].apply(int)
        self.dfmerge['number_rep'].apply(int)
        self.dfmerge.sort_values(['condition_order', 'condition'] , inplace=True)
        self.dfmerge.to_excel(r'Data Export.xlsx', index=False)   
        self.isoplot_logger.info('Data exported. Check Data Export.xlsx')

        
        