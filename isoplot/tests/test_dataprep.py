""" Module for deploying pytest tests"""
from pathlib import Path

import pytest
from pandas.api.types import is_numeric_dtype, is_string_dtype
from numpy import int64

from isoplot.main.dataprep import IsoplotData


@pytest.fixture(scope='function', autouse=True)
def data_object():
    return IsoplotData(Path(r".\test_data\160419_T_Daubon_MC_principale_res.csv").absolute())


@pytest.fixture(scope='function', autouse=True)
def columns():
    return ["sample", "metabolite", "area", "corrected_area", "isotopologue_fraction", "mean_enrichment"]


@pytest.fixture(scope='function', autouse=True)
def sample_names():
    return ['110419_T0_Cont_1_2',
            '110419_T0_Cont_2_8',
            '110419_T0_Cont_3_9',
            '110419_T24_Cont_1_27',
            '110419_T24_Cont_2_28',
            '110419_T24_Cont_3_29',
            '110419_T48_Cont_1_47',
            '110419_T48_Cont_2_48',
            '110419_T48_Cont_3_49',
            '110419_T0_A_1_11',
            '110419_T0_A_2_12',
            '110419_T0_A_3_13',
            '110419_T24_A_1_31',
            '110419_T24_A_2_32',
            '110419_T24_A_3_33',
            '110419_T48_A_1_51',
            '110419_T48_A_2_52',
            '110419_T48_A_3_53',
            '110419_T0_B_1_15',
            '110419_T0_B_2_16',
            '110419_T0_B_3_17',
            '110419_T24_B_1_35',
            '110419_T24_B_2_36',
            '110419_T24_B_3_37',
            '110419_T48_B_1_55',
            '110419_T48_B_2_56',
            '110419_T48_B_3_57',
            '110419_T0_AB_1_19',
            '110419_T0_AB_2_20',
            '110419_T0_AB_3_21',
            '110419_T24_AB_1_39',
            '110419_T24_AB_2_40',
            '110419_T24_AB_3_41',
            '110419_T48_AB_1_59',
            '110419_T48_AB_2_60',
            '110419_T48_AB_3_61']


class TestDataprep:

    def test_initial_df(self, data_object, columns, sample_names):

        data_object.get_data()

        assert not data_object.data.empty
        assert all(item in data_object.data.columns for item in columns)
        assert all(item in list(data_object.data["sample"]) for item in sample_names)

        for col in ["area", "corrected_area", "isotopologue_fraction", "mean_enrichment"]:
            assert is_numeric_dtype(data_object.data[col])
        for col in ["sample", "metabolite"]:
            assert is_string_dtype(data_object.data[col])

    def test_validate_template(self, data_object, sample_names):

        data_object.get_template(r".\test_data\modified_for_testing.xlsx")

        assert not data_object.template.empty
        assert all(item in set(data_object.template["sample"]) for item in sample_names)
        assert is_numeric_dtype(data_object.template["time"])
        assert is_numeric_dtype(data_object.template["number_rep"])
        assert is_string_dtype(data_object.template["condition"])

    def test_merge_function(self, data_object):

        data_object.get_data()
        data_object.get_template(r".\test_data\modified_for_testing.xlsx")
        data_object.merge_data()

        assert hasattr(data_object, "dfmerge")

        for col in data_object.dfmerge.columns:
            if col in data_object.data.columns:
                assert data_object.data[col].sort_values().values.all() == data_object.dfmerge[
                    col].sort_values().values.all()
            elif col in data_object.template.columns:
                assert data_object.template[col].sort_values().values.all() == data_object.dfmerge[
                    col].sort_values().values.all()
            else:
                raise KeyError(f"{col} not found in columns")

    def test_prepare_data_function(self, data_object):

        data_object.get_data()
        data_object.get_template(r".\test_data\modified_for_testing.xlsx")
        data_object.merge_data()
        data_object.prepare_data(False)

        assert ~data_object.dfmerge.isna().values.any()
        assert data_object.dfmerge["time"].dtype == int64
        assert data_object.dfmerge["number_rep"].dtype == int64
        for value in data_object.dfmerge["ID"]:
            assert type(value) is str

        for ids in data_object.dfmerge["ID"]:
            assert len(ids.split("_")) == 3
