import io
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

    def __init__(self, datapath, verbose=False):

        self.datapath = datapath
        self.verbose = verbose
        self.data = None
        self.template = None
        self.dfmerge = None

        self.isoplot_logger = logging.getLogger("Isoplot.dataprep.IsoplotData")
        self.isoplot_logger.setLevel(logging.DEBUG)
        stream_handle = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handle.setFormatter(formatter)
        if self.verbose:
            stream_handle.setLevel(logging.DEBUG)
        else:
            stream_handle.setLevel(logging.INFO)
        self.isoplot_logger.addHandler(stream_handle)

        self.isoplot_logger.debug('Initializing IsoplotData object')

    @staticmethod
    def load_isocor_data(path):
        """Function to read incoming data"""

        datapath = pl.Path(path)
        self.isoplot_logger.debug(f"Path to data: {datapath}")
        if not datapath.is_file():
            raise ValueError("No data file selected")
        try:
            with open(str(datapath), 'r', encoding='utf-8') as dp:
                data = pd.read_csv(dp, sep='\t')
                if len(data.columns) == 1:
                    del data
                    with open(str(datapath), 'r', encoding='utf-8') as dp:
                        data = pd.read_csv(dp, sep=";")
        except Exception as err:
            raise ValueError(f"Error during the lecture of the file {path}. Please make sure file is tsv or csv. "
                             f"Traceback: {err}")
        to_check = ['sample', 'metabolite', 'isotopologue', 'area', 'corrected_area', 'isotopologue_fraction',
                    'mean_enrichment']
        for i in to_check:
            if i not in data.columns:
                raise ValueError(f"Column {i} not found in data file {path}")
        return data

    @staticmethod
    def load_template(input, excel_sheet=0):
        """Function to read incoming template data"""

        # Since the template can be in excel format, when input comes from upload button in the notebook it is a
        # bytes file. So we check and handle this here
        if isinstance(input, bytes):
            toread = io.BytesIO()
            toread.write(input)
            toread.seek(0)
            try:
                data = pd.read_excel(input, engine='openpyxl', sheet_name=excel_sheet)
            except ValueError:
                data = pd.read_csv(input, sep=";")
                if len(data.columns) == 1:
                    del data
                    data = pd.read_csv(input, sep="\t")
                return data
            except Exception as ex:
                raise ValueError(f"There was a problem while processing the input template. Traceback: {ex}")
            else:
                return data
        else:
            datapath = pl.Path(input).resolve()
            self.isoplot_logger.debug(f"Path to template: {datapath}")
            if not datapath.is_file():
                raise ValueError("No data file selected")
            try:
                data = pd.read_excel(datapath, engine='openpyxl', sheet_name=excel_sheet)
            except Exception:
                try:
                    with open(str(datapath), 'r', encoding='utf-8') as dp:
                        data = pd.read_csv(dp, sep=";")
                        if len(data.columns) == 1:
                            del data
                            data = pd.read_csv(dp, sep="\t")
                except Exception as err:
                    raise ValueError(
                        f"Error during the lecture of the template file {input}. "
                        f"Please check file content and format. Traceback: {err}")
            to_check = ['sample', 'condition', 'condition_order', 'time', 'number_rep', 'normalization']
            for i in to_check:
                if i not in data.columns:
                    raise ValueError(f"Column {i} not found in template file {input}")
            return data

    def get_data(self):
        """Read data from tsv file and store in object data attribute."""

        self.isoplot_logger.info(f'Reading datafile {self.datapath} \n')
        try:
            self.data = IsoplotData.load_isocor_data(self.datapath)
        except Exception:
            self.isoplot_logger.exception("Error while reading isocor data")
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
            self.isoplot_logger.debug('Trying to read template')
            self.template = IsoplotData.load_template(path)
        except Exception:
            self.isoplot_logger.exception("Error while loading data")
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

    def prepare_data(self, export=True):
        """Final cleaning of data and export"""

        self.isoplot_logger.debug('Preparing data after merge: normalizing...')

        self.dfmerge["corrected area normalized"] = self.dfmerge["corrected_area"] / self.dfmerge["normalization"]
        self.dfmerge['metabolite'].drop_duplicates()

        self.isoplot_logger.debug("Creating IDs...")

        # Nous créons ici une colonne pour identifier chaque ligne avec condition+temps+numero de répétition
        # (possibilité de rajouter un tag metabolite plus tard si besoin)
        self.dfmerge.condition = self.dfmerge.condition.str.replace("_", "-")
        self.dfmerge['ID'] = self.dfmerge['condition'].apply(str) + '_T' + self.dfmerge['time'].apply(str) + '_' + \
                             self.dfmerge['number_rep'].apply(str)

        self.isoplot_logger.debug('Applying final transformations...')

        # Vaut mieux ensuite retransformer les colonnes temps et number_rep en entiers pour
        # éviter des problèmes éventuels de type
        self.dfmerge['time'].apply(int)
        self.dfmerge['number_rep'].apply(int)
        self.dfmerge.sort_values(['condition_order', 'condition'], inplace=True)
        self.dfmerge.fillna(0, inplace=True)
        if export:
            self.dfmerge.to_csv(r"./Data_Export", sep=';', index=False)
            self.isoplot_logger.info('Data exported. Check Data_Export.csv')
        else:
            output = io.StringIO()
            self.dfmerge.to_csv(output, sep=';', index=False)
            output.seek(0)
            print(output.read())
