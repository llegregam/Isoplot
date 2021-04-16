""" Module for deploying pytest tests"""

import pytest
from pandas.api.types import is_numeric_dtype, is_string_dtype
from numpy import int64, unicode_

from isoplot.main.dataprep import IsoplotData


@pytest.fixture(scope='function', autouse=True)
def df():
    df = IsoplotData(r".\test_data\160419_T_Daubon_MC_principale_res.csv")
    return df

@pytest.fixture(scope='function', autouse=True)
def columns():
    columns = ["sample", "metabolite", "area", "corrected_area", "isotopologue_fraction", "mean_enrichment"]
    return columns

@pytest.fixture(scope='function', autouse=True)
def sample_names():
    sample_names = ['110419_T0_Cont_1_2',
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
    return sample_names


class Test_dataprep:

    def test_initial_df(self, df, columns, sample_names):

        df.get_data()

        assert not df.data.empty
        assert all(item in df.data.columns for item in columns)
        assert all(item in list(df.data["sample"]) for item in sample_names)

        for col in ["area", "corrected_area", "isotopologue_fraction", "mean_enrichment"]:
            assert is_numeric_dtype(df.data[col])
        for col in ["sample", "metabolite"]:
            assert is_string_dtype(df.data[col])

    def test_template(self, df, sample_names):

        df.get_template(r".\test_data\modified_for_testing.xlsx")

        assert not df.template.empty
        assert all(item in set(df.template["sample"]) for item in sample_names)
        assert is_numeric_dtype(df.template["time"])
        assert is_numeric_dtype(df.template["number_rep"])
        assert is_string_dtype(df.template["condition"])

    def test_merge(self, df):

        df.get_data()
        df.get_template(r".\test_data\modified_for_testing.xlsx")
        df.merge_data()

        assert hasattr(df, "dfmerge")

        for col in df.dfmerge.columns:
            if col in df.data.columns:
                assert df.data[col].sort_values().values.all() == df.dfmerge[col].sort_values().values.all()
            elif col in df.template.columns:
                assert df.template[col].sort_values().values.all() == df.dfmerge[col].sort_values().values.all()
            else:
                raise KeyError(f"{col} not found in columns")

    def test_prep_data(self, df):

        df.get_data()
        df.get_template(r".\test_data\modified_for_testing.xlsx")
        df.merge_data()
        df.prepare_data(False)

        assert ~df.dfmerge.isna().values.any()
        assert df.dfmerge["time"].dtype == int64
        assert df.dfmerge["number_rep"].dtype == int64
        for value in df.dfmerge["ID"]:
            assert type(value) is str

        for ids in df.dfmerge["ID"]:
            assert len(ids.split("_")) == 3