"""Testing module for isoplot's Data Handler"""

import os
from pathlib import Path
import tempfile

import pytest
import pandas as pd

from ..base.data_handler import DataHandler


@pytest.fixture(scope='function', autouse=True)
def data_object():
    return DataHandler(True)


@pytest.fixture(scope='function', autouse=True)
def path_to_data():
    return Path("./isoplot/tests/test_data/isocor_data.tsv").resolve()


@pytest.fixture(scope='function', autouse=True)
def path_to_template():
    return Path("./isoplot/tests/test_data/template.xlsx").resolve()


@pytest.fixture(scope='function', autouse=True)
def normalization_test_proper_values(data_object, path_to_data, path_to_template):
    data_object.import_isocor_data(path_to_data)
    data_object.import_template(path_to_template)
    data_object._merge_data()
    corrected_area = data_object.individual_data["corrected_area"].values
    test_values = [1, 2, 5, 10, 16, 32, 1.5, 10.125, 100.18585]
    results = {val: corrected_area / val for val in test_values}
    return results


class TestDataHandler:

    # TODO: Modify tests to include testing for the 2 new dataframes (means and sds)
    def test_isocor_data_import(self, data_object, path_to_data):

        data_object.import_isocor_data(path_to_data)
        assert hasattr(data_object, "data")
        dataframe = pd.read_csv(path_to_data, sep="\t")
        compared = data_object.data.compare(dataframe)
        assert compared.empty

    def test_template_import(self, data_object, path_to_data, path_to_template):

        data_object.import_isocor_data(path_to_data)
        data_object.import_template(path_to_template)
        assert hasattr(data_object, "template")
        template = pd.read_excel(path_to_template)
        compared = data_object.template.compare(template)
        assert compared.empty

    def test_template_generation(self, data_object, path_to_data):

        data_object.import_isocor_data(path_to_data)
        home = Path(".").resolve()
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            data_object.generate_template()
            template = pd.read_excel("ModifyThis.xlsx")
            os.chdir(home)
        for col in template.columns:
            assert col in ["sample", "condition", "condition_order", "time", "number_rep", "normalization"]
        for sample in template["sample"]:
            assert sample in data_object.data["sample"].values
        for condition in template["condition"]:
            assert condition == "your_condition"
        for time in template["time"]:
            assert time is 1
        for rep in template["number_rep"]:
            assert rep is 3
        for norm in template["normalization"]:
            assert norm is 1

    def test_merge(self, data_object, path_to_data, path_to_template):

        data_object.import_isocor_data(path_to_data)
        data_object.import_template(path_to_template)
        data_object._merge_data()
        cols = ['sample', 'metabolite', 'derivative', 'isotopologue', 'area',
                'corrected_area', 'isotopologue_fraction', 'residuum', 'mean_enrichment',
                'condition', 'condition_order', 'time', 'number_rep', 'normalization']
        for col in cols:
            assert col in data_object.individual_data.columns
            assert not data_object.individual_data[col].empty

    @pytest.mark.parametrize("value", [
        1,
        2,
        5,
        10,
        16,
        32,
        1.5,
        10.125,
        100.18585
    ])
    def test_normalization(self, data_object, path_to_data, path_to_template, normalization_test_proper_values, value):

        data_object.import_isocor_data(path_to_data)
        data_object.import_template(path_to_template)
        data_object._merge_data()
        data_object.individual_data["normalization"] = value
        data_object._normalize_data()
        assert data_object.individual_data["corrected_area"].values.all() == normalization_test_proper_values[
            value].all()

    def test_compute_means(self, data_object, path_to_data, path_to_template):

        data_object.import_isocor_data(path_to_data)
        data_object.import_template(path_to_template)
        data_object._merge_data()
        data_object._compute_means()
        assert hasattr(data_object, "mean_data")
        for val in [
            "corrected_area_mean",
            "isotopologue_fraction_mean",
            "mean_enrichment_mean",
            "corrected_area_sd",
            "isotopologue_fraction_sd",
            "mean_enrichment_sd"
        ]:
            assert val in data_object.mean_data.columns

    def test_missing_column_get(self, data_object, path_to_data, path_to_template):

        data_object.import_isocor_data(path_to_data)
        data_object.import_template(path_to_template)
        data_object._merge_data()
        data_object._compute_means()
        data_object._get_missing_column()
        assert "condition_order" in data_object.mean_data.columns
