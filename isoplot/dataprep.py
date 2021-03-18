import logging
import pathlib as pl

import pandas as pd
from natsort import natsorted


class IsoplotData:
    """
    Class to prepare Isoplot Data for plotting
    
    :param datapath: Path to .csv file containing Isocor output data
    :type datapath: str
    """

    def __init__(self, datapath):

        self.datapath = datapath
        self.data = None
        self.template = None
        self.dfmerge = None

        self.isoplot_logger = logging.getLogger("Isoplot.dataprep.IsoplotData")
        stream_handle = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handle.setFormatter(formatter)
        self.isoplot_logger.addHandler(stream_handle)

        self.isoplot_logger.debug('Initializing IsoplotData object')

    @staticmethod
    def read_data(path, excel_sheet=0):
        """Function to read incoming data"""

        datapath = pl.Path(path)

        if datapath.suffix == ".tsv":
            data = pd.read_csv(datapath, sep="\t", engine='python')

        elif datapath.suffix == ".csv":
            data = pd.read_csv(datapath, sep=";", engine='python')

        elif datapath.suffix == ".xlsx":
            data = pd.read_excel(datapath, engine="openpyxl", sheet_name=excel_sheet)

        else:
            raise TypeError("File extension not supported."
                            "Supported types: '.tsv', '.csv' and '.xlsx' ")

        return data

    def get_data(self):

        """Read data from tsv file and store in object data attribute."""

        self.isoplot_logger.info(f'Reading datafile {self.datapath} \n')

        self.data = IsoplotData.read_data(self.datapath)

        self.isoplot_logger.info("Data is loaded")

    def generate_template(self):
        """Generate .xlsx template that user must fill"""

        self.isoplot_logger.info("Generating template...")

        metadata = pd.DataFrame(columns=[
            "sample", "condition", "condition_order", "time", "number_rep", "normalization"])
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
                raise TypeError(
                    f"Error while merging data, dataframe not created. Data turned out to be {type(self.dfmerge)}")

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

        self.dfmerge["corrected area normalized"] = self.dfmerge["corrected_area"] / self.dfmerge["normalization"]
        self.dfmerge['metabolite'].drop_duplicates()

        self.isoplot_logger.debug("Creating IDs...")

        # Nous créons ici une colonne pour identifier chaque ligne avec condition+temps+numero de répétition
        # (possibilité de rajouter un tag metabolite plus tard si besoin)
        self.dfmerge['ID'] = self.dfmerge['condition'].apply(str) + '_T' + self.dfmerge['time'].apply(str) + '_' + \
                             self.dfmerge['number_rep'].apply(str)

        self.isoplot_logger.debug('Applying final transformations...')

        # Vaut mieux ensuite retransformer les colonnes temps et number_rep en entiers pour
        # éviter des problèmes éventuels de type
        self.dfmerge['time'].apply(int)
        self.dfmerge['number_rep'].apply(int)
        self.dfmerge.sort_values(['condition_order', 'condition'], inplace=True)
        self.dfmerge.fillna(0, inplace=True)
        self.dfmerge.to_excel(r'Data Export.xlsx', index=False)
        self.isoplot_logger.info('Data exported. Check Data Export.xlsx')
