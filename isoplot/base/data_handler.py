"""Main data handling module for the isoplot software"""

import logging
from pathlib import Path

import pandas as pd
import numpy as np
from natsort import natsorted

import isoplot.logger

mod_logger = logging.getLogger('Isoplot_logger.base.data_handler')


class DataHandler:
    """
    Data handling class to prepare Isocor Data for plotting

    :param verbose: should debug info be logged or not
    :type verbose: boolean
    """

    def __init__(self, verbose):

        self.logger = logging.getLogger('Isoplot_logger.base.data_handler.DataHandler')
        if verbose:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        handle = logging.StreamHandler()
        handle.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        handle.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(handle)

        self.data = None
        self.template = None
        self.final_data = None

    def import_isocor_data(self, data_path):
        """
        Import isotopic data set that has been corrected for natural abundances by Isocor.
        Data set should be in .tsv format

        :param data_path: path to dataset
        """
        self.logger.info("Reading Input data...")
        try:
            path = Path(data_path)
        except TypeError:
            raise TypeError("The input path must be a chain of characters")
        else:
            if not path.is_file():
                raise ValueError(f"Data file not found in: \n '{data_path}' ")
        try:
            with open(path, 'r', encoding='utf-8') as file:
                self.data = pd.read_csv(file, sep='\t')
        except Exception as err:
            raise ValueError(f"An unkown error has occured while reading the measurements file. Traceback: \n {err}")
        # Perform some quick checks
        for i in ["sample", "metabolite", "isotopologue", "area", "corrected_area",
                  "isotopologue_fraction", "mean_enrichment"]:
            if i not in self.data.columns:
                raise ValueError(f"The column '{i}' is missing from the input dataset")
        if self.data.empty:
            raise ValueError("The input dataset seems empty")
        self.logger.info("Input data has been succesfully imported.")

    def import_template(self, template_path):
        """
        Import the template used to get metadata for plotting. File should be in xlsx format.

        :param template_path: path to template file
        """

        try:
            path = Path(template_path)
        except TypeError:
            raise TypeError("The input path must be a chain of characters")
        else:
            if not path.is_file():
                raise ValueError(f"Data file not found in: \n '{template_path}' ")
            if not path.suffix == ".xlsx":
                raise TypeError(f"The input template file '{template_path}' must be an excel file (.xlsx extension)")
        try:
            self.template = pd.read_excel(path)
        except Exception as err:
            raise RuntimeError(f"Unknown error while reading template file. Traceback: \n{err}")
        # Check all the necessary columns are present
        for i in ["condition", "condition_order", "time", "number_rep", "normalization"]:
            if i not in self.template.columns:
                raise ValueError(f"The column '{i}' is missing from the template file.")
        # Check for wrong types in the string columns
        self.logger.debug(f"Condition dtype: {self.template.condition.dtypes}"
                          f"Sample dtype: {self.template['sample'].dtypes}")
        for col in [self.template["condition"], self.template["sample"]]:
            wrong_types = [("line " + str(ind+2), i) for ind, i in enumerate(col)
                           if not isinstance(i, str)]
            # When shown in excel, the first line is composed of the headers and data starts line 2, so
            # we add 2 to start at the right place (enumerate starts from 0)
            if wrong_types:
                raise TypeError(f"The column {col} contains values that are not of the right type "
                                f"(should be strings): \n'{wrong_types}'")
        self.logger.debug(f"Condition order dtype: {self.template.condition_order.dtypes}"
                          f"\nTime dtype: {self.template.time.dtypes}"
                          f"\nNumber_Rep dtype: {self.template.number_rep.dtypes}")
        # Check for wrong types in the remaining columns. We want only ints and floats (standard or numpy)
        for col in [self.template["condition_order"], self.template["time"], self.template["number_rep"],
                    self.template["normalization"]]:
            wrong_types = [("line " + str(ind+2), i) for ind, i in enumerate(col)
                           if not isinstance(i, (int, np.intc, float, np.float_))]
            if wrong_types:
                raise TypeError(f"The column {col} contains values that are not of the right type "
                                f"(should be integers or floats): \n'{wrong_types}'")

    def generate_template(self):
        """Generate .xlsx template that user must fill"""

        self.logger.info("Generating template...")
        metadata = pd.DataFrame(columns=[
            "sample", "condition", "condition_order", "time", "number_rep", "normalization"])
        metadata["sample"] = natsorted(self.data["sample"].unique())
        metadata["condition"] = 'your_condition'
        metadata["condition_order"] = 1
        metadata["time"] = 1
        metadata["number_rep"] = 3
        metadata["normalization"] = 1.0
        metadata.to_excel(r'ModifyThis.xlsx', index=False)
        self.logger.info('Template has been generated')

    def _merge_data(self):
        """Merge the template with the input data to get our final dataframe"""

        self.logger.debug("Attempting to merge input data and template")
        for df in [self.data, self.template]:
            if df is None:
                raise RuntimeError(f"{df} is missing. Please import and try again.")
        try:
            self.final_data = self.data.merge(self.template)
        except Exception as merge_err:
            raise RuntimeError(f"There was a problem merging the template with the input data. "
                               f"Traceback: \n {merge_err}")
        else:
            self.logger.debug("Data has been merged.")

    def _normalize_data(self):
        """Normalize merged data by value in 'normalisation' column"""

        self.logger.debug("Attempting to normalize data")
        # As corrected areas are the only data points that are absolute and not relative, the normalization process
        # should only apply to them
        try:
            self.final_data["corrected_area"] = \
                self.final_data["corrected_area"] / self.final_data["normalization"]
        except Exception as norm_err:
            raise ValueError(f"There was an unknown error while normalizing the data. "
                             f"Traceback:\n {norm_err}")
        else:
            self.logger.debug("The corrected_area column has been normalized")

    def _generate_ids(self):
        """Generate an ID column for identifying each row uniquely"""

        self.logger.debug("Attempting to generate the IDs")
        self.final_data.condition = self.final_data.condition.str.replace("_", "-")
        try:
            self.final_data["ID"] = self.final_data.condition.apply(str) + "_T" + self.final_data.time.apply(str) + \
                                 "_" + self.final_data.number_rep.apply(str)
        except Exception as id_err:
            raise ValueError(f"Error while generating the ID column. Traceback: \n{id_err}")
        else:
            self.logger.debug("IDs have been generated")

    def _prepare_export(self):
        """
        Prepare data for export. Calculate means and sds for each data group.
        """
        for col in ["time", "number_rep"]:
            if self.final_data[col].dtypes != np.int64:
                try:
                    self.final_data[col].apply(np.int64)
                except Exception as convert_err:
                    raise RuntimeError(f"Error while converting {col} column to int64. Traceback: \n{convert_err}")
        self.final_data.drop(["derivative", "normalization", "Unnamed: 0", "residuum"], axis=1, inplace=True)
        for value in ["corrected_area", "isotopologue_fraction", "mean_enrichment"]:
            self.final_data = self.final_data.join(self.final_data.groupby(
                ["metabolite", "condition", "time", "isotopologue"])[value].mean(),
               on=["metabolite", "condition", "time", "isotopologue"],
               rsuffix="_mean")
        for value in ["corrected_area", "isotopologue_fraction", "mean_enrichment"]:
            self.final_data = self.final_data.join(self.final_data.groupby(
                ["metabolite", "condition", "time", "isotopologue"])[value].std(),
               on=["metabolite", "condition", "time", "isotopologue"],
               rsuffix="_std")
        self.final_data.fillna(0, inplace=True)
        self.final_data = self.final_data[["ID", "metabolite", "condition", "time", "isotopologue", "number_rep",
                                           "corrected_area", "corrected_area_mean", "corrected_area_std",
                                           "isotopologue_fraction", "isotopologue_fraction_mean",
                                           "isotopologue_fraction_std", "mean_enrichment", "mean_enrichment_mean",
                                           "mean_enrichment_std", "condition_order"]]
        self.final_data.sort_values(by=["metabolite", "condition", "time", "isotopologue"], inplace=True)
        self.final_data.set_index(["metabolite", "condition", "time", "number_rep", "isotopologue"], inplace=True)

    def compute_data(self):
        """Compute data and have it ready for export & use by the plotting module"""

        self.logger.info("Launching the computation of data...")
        self._merge_data()
        if self.final_data["normalization"].any() != 1:
            self._normalize_data()
        self._generate_ids()
        self._prepare_export()
        self.logger.info("Data has been computed. Ready for export and/or plotting.")

    def export_data(self, file_name):
        """Export data to tabular format"""

        self.final_data.to_csv(f"./{file_name}.tsv", sep="\t")
        self.logger.info("Clean data has been exported")
