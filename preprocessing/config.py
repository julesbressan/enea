#%%
from typing import Any, DefaultDict
from pydantic import BaseModel
from pathlib import Path
from typing import Optional
from functools import reduce
import pandas as pd
import numpy as np
import os 
import re
import json
import logging

#change this to locate your raw data folder
DATA_ROOTFOLDER = Path("/Users/julesbressan/data/ACCIDENT")

FOLDER_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = Path(os.path.dirname(FOLDER_DIR))
SELECTED_FILES_FEATURES = json.load(open(FOLDER_DIR / "selected_files_features.json"))
FILES_KEYS = json.load(open(FOLDER_DIR/"files_keys.json"))
FEATURES_UNKNOWN_VALUES = json.load(open(FOLDER_DIR/"features_unknown_values.json"))

PROCESSED_DATA_FOLDER = Path(ROOT_DIR / "processed_data.csv")


class FileData(BaseModel):
    df: Any = None
    filename : str 
    granularity: Optional[list]
    modified_columns : list = [] 

def get_file_data(file_name: str )-> tuple:
    raw_df = pd.read_csv(DATA_ROOTFOLDER / file_name, low_memory=False)
    df = raw_df.loc[:,SELECTED_FILES_FEATURES[file_name]]
    return df, raw_df
    
def replace_unknown_to_nan_and_clean_spaces (df: pd.DataFrame) -> pd.DataFrame:
    df_ = df.loc[:,:]
    for column_name in df.columns:
        serie = df_.loc[:,column_name]
        if pd.api.types.is_numeric_dtype(serie.dtype):
            serie = serie.replace(float(FEATURES_UNKNOWN_VALUES[column_name]), np.nan)
                
        elif pd.api.types.is_string_dtype(serie.dtype): # Object
            regex= r"^\s*(" + re.escape(FEATURES_UNKNOWN_VALUES[column_name]) + r")*\s*$"
            serie = serie.replace(regex, np.nan, regex=True)
            
            serie = serie.replace(r"\s+", "", regex=True) # containg 1 or more spaces
        df_[column_name] = serie
    return df_
        
def reduce_nb_categories_for_categorical_feature(df : pd.DataFrame, filename: str) -> tuple:
    modified_columns = []
    INGNORED_COLUMNS = ["ACCIDENTDATE", "ACCIDENTTIME"] 
    for feature  in df.columns :
        if feature in FILES_KEYS[filename] + INGNORED_COLUMNS:
            continue 
        serie = df[feature]
        
        if pd.api.types.is_object_dtype(serie.dtype): 
        
            cumulated_category_weights = serie.value_counts().cumsum()/len(serie)
            #we keep the categories holding more than 95% of the values 
            selected_categories = cumulated_category_weights[cumulated_category_weights <= 0.95] 
            
            #We replace if there is more than 10 features and if we can cover more than 95% of the lines with just some features
            if len(selected_categories)<len(serie.value_counts()) and len(serie.value_counts()) >= 10 : 
                logging.warning(f"{serie.name} will get simplified categories")
                modified_columns.append(feature)
                def simplify_category(category:str) -> str: 
                    if category in selected_categories:
                        return category
                    else :
                        return "Other" 
                
                df[feature]= serie.apply(lambda x: simplify_category(x))
    return df, modified_columns
        
def check_and_set_keys(df: pd.DataFrame,filename: str,) -> pd.DataFrame:
    keys = FILES_KEYS[filename]
    
    duplicates = df[keys].duplicated(keep="last")
        
    ratio_of_duplicates_on_key = duplicates.sum()/len(df)

    if  ratio_of_duplicates_on_key == 0:
        return df, ratio_of_duplicates_on_key
    
    elif ratio_of_duplicates_on_key <= 0.2: 
        logging.info(f"{keys} is forced as a key for {filename}")
        df = df[~duplicates]
        return df, ratio_of_duplicates_on_key
    else :
        logging.error(f"{keys} isn't the key of df, too many duplicates: {ratio_of_duplicates_on_key} ratio")
        raise ValueError()

def clean_keys(df: pd.DataFrame,filename: str) -> pd.DataFrame:
    keys = FILES_KEYS[filename]
    logging.info(f"Cleaning {keys} for {filename}")
    for key in keys : 
        df[key] = df[key].str.replace(" ","")
    return df 
    
def remove_sparse_columns(df: pd.DataFrame,filename: str) -> pd.DataFrame:
    sparsity_columns = {column:df[column].isna().sum()/len(df) for column in df.columns}
    sparse_columns = [column for column in sparsity_columns.keys() if sparsity_columns[column] > 0.25]
    
    if sparse_columns: 
        logging.warning(f"Removing sparse columns {sparse_columns} for {filename}")
        return df.drop(columns = sparse_columns)
    return df

#%%
def process_generic_file_data():

    processed_file_data = {}
    for filename in SELECTED_FILES_FEATURES.keys(): 
        
        df, raw_df = get_file_data(filename)
        df = replace_unknown_to_nan_and_clean_spaces(df)
        df, modified_columns = reduce_nb_categories_for_categorical_feature(df, filename)
        
        df = clean_keys(df, filename)
        df, duplicates_ratio = check_and_set_keys(df, filename)
        df = remove_sparse_columns(df, filename)
        
        file_data = FileData(filename = filename, 
                             df = df, 
                             granularity = FILES_KEYS[filename],
                             modified_columns=modified_columns, 
                             duplicates_ratio=duplicates_ratio )
        
        processed_file_data[filename]=file_data 
    
    return processed_file_data 
        
   
processed_file_data = process_generic_file_data()              
# %%
def merge_file_data(processed_file_data):
     
    dfs = [filedata.df for filedata in processed_file_data.values() if filedata.granularity == ["ACCIDENT_NO"] ]
    
    df_merged = reduce(lambda  left,right: pd.merge(left,right,on=["ACCIDENT_NO"],
                                            how='outer'), dfs)
    
    vehicle_df = processed_file_data["VEHICLE.csv"].df
    
    df_merged = pd.merge(vehicle_df,df_merged,on=["ACCIDENT_NO"],how='outer')
    
    person_df = processed_file_data["PERSON.csv"].df
    
    df_merged = pd.merge(person_df,df_merged,on=["ACCIDENT_NO", "VEHICLE_ID"],how='outer')
    
    return df_merged

merged = merge_file_data(processed_file_data) 
# %%


def categorise_tare_weight(df):
    splits = df[df.TARE_WEIGHT !=0 ].TARE_WEIGHT.describe().loc[["25%", "50%", "75%"]]

    def weight_categories(weight: float) -> str:
        if weight <= splits["25%"]:
            return "light"
        elif  splits["25%"]< weight <= splits["75%"]:
            return "mid"
        else :
            return "heavy"
        
    df.loc[:,"TARE_WEIGHT"] = df.TARE_WEIGHT.apply(lambda x: weight_categories(x) )
    return df 


# %%
def main():
    processed_file_data = process_generic_file_data() 
    merged = merge_file_data(processed_file_data) 
    merged = merged.dropna() #we can come back later on that choice
    
    #some categorization operations on some specific features
    merged = categorise_tare_weight(merged)
    
    
    
    
    
    merged.to_csv(PROCESSED_DATA_FOLDER, index=False)
# %%
if __name__ == '__main__':
    main()
# %%
