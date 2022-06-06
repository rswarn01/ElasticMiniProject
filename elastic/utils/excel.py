from pandas.core.frame import DataFrame
import pandas as pd
import numpy as np


def convert_to_json(df, cat_cols=11):

    df2 = df.iloc[:, :cat_cols].copy()
    df2["ROW_DATA"] = df.iloc[:, cat_cols:].apply(lambda x: x.to_json(), axis=1)
    return df2


def get_df_from_excel(
    file: bytes, sheet_name: str = None, keep_default_na: bool = False, **kwargs
) -> DataFrame:
    """Returns JSON representation from the default excel sheet
    Args:
        file (BytesIO): Excel file to convert
        keep_default_na (bool, optional): If True, consider 'NA' 'N/A' and Invalid entries as null. Defaults to False.
        empty string is always considered as null
    Returns:
        list: list of rows in the excel file
    """

    # convert empty string (only) into null
    na_values = [""]
    if keep_default_na:
        na_values = None

    # convert excel file pandas data frame
    if sheet_name:
        sheet_df = pd.read_excel(
            file,
            na_values=na_values,
            sheet_name=sheet_name,
            keep_default_na=keep_default_na,
            skiprows=1,
            **kwargs,
        )
    else:
        sheet_df = pd.read_excel(
            file,
            na_values=na_values,
            keep_default_na=keep_default_na,
            skiprows=0,
            **kwargs,
        )
    # Drop first column in sheet
    # sheet_df = sheet_df.iloc[:, 1:]
    sheet_df = trim_all_columns(sheet_df)

    sheet_df.replace({np.nan: None}, inplace=True)
    return sheet_df.dropna(how="all")


def trim_all_columns(df):
    """
    Trim whitespace from ends of each value across all series in dataframe
    """
    trim_strings = lambda x: x.strip() if isinstance(x, str) else x
    return df.applymap(trim_strings)
