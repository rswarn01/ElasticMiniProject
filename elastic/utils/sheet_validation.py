import pandas as pd
import re
import numpy as np
from typing import List, Iterable
from elastic.utils import Response


def get_df_from_excel_sheet(
    file: bytes, sheet_name: list = None, keep_default_na: bool = False, **kwargs
):
    """Returns JSON representation from the default excel sheet

    Args:
        file (BytesIO): Excel file to convert
        keep_default_na (bool, optional): If True, consider 'NA' 'N/A' and Invalid entries as null. Defaults to False.
        empty string is always considered as null

    Returns:
        list: list of rows in the excel file
    """
    # get excel data from cache
    cache_key = None
    # if refresh_module == 'design':
    #     cache_key = get_refresh_design_excel_cache_key(scenario_name)
    #     sheet_df_dict = cache.get(cache_key)
    # if refresh_module == 'transition':
    #     pass
    # if refresh_module == 'plan':
    #     pass

    # if sheet_df_dict:
    #     # print(sheet_df_dict)
    #     redis.delete_pattern(cache_key)
    #     return sheet_df_dict,cache_key

    # convert empty string (only) into null
    na_values = [""]
    if keep_default_na:
        na_values = None

    # convert excel file pandas data frame
    # check if file is correct and has all the required sheets
    xlsx = pd.ExcelFile(file)
    sheet_names_from_excel = xlsx.sheet_names
    if not sheet_name:
        sheet_name = xlsx.sheet_names
    if isinstance(sheet_name, Iterable):
        sheet_diff = set(sheet_name).difference(set(sheet_names_from_excel))
        invalid_sheets = set(sheet_names_from_excel).difference(set(sheet_name))
    else:
        sheet_diff = set([sheet_name]).difference(set(sheet_names_from_excel))
        invalid_sheets = set(sheet_names_from_excel).difference(set([sheet_name]))

    if sheet_diff:
        return {"invalid_sheets": list(invalid_sheets)}
    if sheet_name:
        sheet_df = pd.read_excel(
            xlsx,
            na_values=na_values,
            sheet_name=sheet_name,
            keep_default_na=keep_default_na,
            # dtype=str,
            **kwargs,
        )
    else:
        sheet_df = pd.read_excel(
            xlsx,
            na_values=na_values,
            keep_default_na=keep_default_na,
            **kwargs,
        )
    pd.set_option("display.max_columns", 200)
    pd.set_option("display.max_rows", 100)

    if not isinstance(sheet_df, dict):
        sheet_df.replace({np.nan: None}, inplace=True)
        sheet_df.dropna(how="all", inplace=True)
    else:  # case when multiple sheets are read at a time
        for sheet in sheet_df:
            sheet_df[sheet].replace({np.nan: None}, inplace=True)
            sheet_df[sheet].dropna(how="all", inplace=True)

    # logging.info("--------------------------------------------")
    # logging.info(sheet_df)
    # logging.info("--------------------------------------------")
    return sheet_df
