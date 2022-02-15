#%%
import pandas as pd 
import numpy as np
from functools import reduce
import re
import matplotlib.pyplot as plt 
from config import CFG
#%%
from accident import ACCIDENT_DATA
from accident_location import ACCIDENT_LOCATION_DATA
from atm_conditions import ATM_COND_DATA
from nodes import NODE_DATA
from person import PERSON_DATA
from road_conditions import ROAD_COND_DATA
from vehicle import VEHICLE_DATA

# %%
data = [ACCIDENT_DATA, ACCIDENT_LOCATION_DATA, 
        ATM_COND_DATA, NODE_DATA, PERSON_DATA, ROAD_COND_DATA, VEHICLE_DATA]
# %%
""" Let's first merge the tables with the same granularity : ACCIDENT_NO """

dfs = [filedata.df.reset_index() for filedata in data if filedata.granularity == ["ACCIDENT_NO"] ]
# %%
df_merged = reduce(lambda  left,right: pd.merge(left,right,on=["ACCIDENT_NO"],
                                            how='outer'), dfs)

""" Let's first merge the resulting table with vehicle data """
# %%
pre_merge_vehicle = VEHICLE_DATA.df.reset_index()
df_merged = pd.merge(pre_merge_vehicle,df_merged,on=["ACCIDENT_NO"], how='outer')


""" Let's first merge the resulting table with person data """
# %%
pre_merge_person = PERSON_DATA.df.reset_index()
df_merged_all_data = pd.merge(pre_merge_person,df_merged,on=["ACCIDENT_NO", "VEHICLE_ID"], how='outer')

# %%
df_merged_all_data = df_merged_all_data.set_index(["ACCIDENT_NO", "VEHICLE_ID", "PERSON_ID"], verify_integrity=True) 

# %%
# let's clean out unknown values
df_merged_all_data_replaced = df_merged_all_data

column_types = df_merged_all_data_replaced.dtypes.astype(str).to_dict()
unknown_codes = {'SEX': 'U',
 'AGE': '999',
 'SEATING_POSITION': 'NK',
 'Road User Type Desc': 'Not known',
 'Driver Age': '999',
 'Driver sex': 'U',
 'Road Surface Type Desc': 'Unknown',
 'VEHICLE_BODY_STYLE': 'Unknown',
 'VEHICLE_MAKE': 'Unknown',
 'INJ_LEVEL':'999',
 'VEHICLE_POWER': '999',
 'Vehicle Type Desc': 'Unknown',
 'TARE_WEIGHT': '999',
 'LEVEL_OF_DAMAGE': '999',
 'Accident Type Desc': 'Unknown',
 'Day Week Description': 'Unknown',
 'DCA Description': 'Unknown',
 'Light Condition Desc': 'Unknown',
 'NODE_ID': '0',
 'NO_OF_VEHICLES': '999',
 'NO_PERSONS': '999',
 'POLICE_ATTEND': '9',
 'Road Geometry Desc': 'Unknwon',
 'SPEED_ZONE': '999',
 'ACCIDENTDAYNUMBER': '999',
 'ACCIDENTHOUR': '999',
 'ROAD_TYPE': 'Unknown',
 'Atmosph Cond Desc': 'Not known',
 'LGA_NAME': 'object',
 'REGION_NAME': '999',
 'DEG_URBAN_NAME': '999',
 'Lat': '0',
 'Long': '0',
 'POSTCODE_NO': '0',
 'Surface Cond Desc': 'Unknown'}

def replace_unknown_to_nan_and_clean_spaces (serie: pd.Series) -> pd.Series:
        if column_types[column_name] == 'float64':
                serie = serie.replace(float(unknown_codes[column_name]), np.nan)
        else : 
                regex= r"^\s*(" + re.escape(unknown_codes[column_name]) + r")*\s*$"
                serie = serie.replace(regex, np.nan, regex=True)
                
                serie = serie.replace(r"\s+", "", regex=True) # containg 1 or more spaces
        return serie

for column_name in df_merged_all_data_replaced.columns:
        
        df_merged_all_data_replaced[column_name] = replace_unknown_to_nan_and_clean_spaces (df_merged_all_data_replaced[column_name])

""" Now that we handled Unknown values, let's drop sparse columns """
# %%
sparsity_columns = {column:df_merged_all_data_replaced[column].isna().sum()/len(df_merged_all_data_replaced) for column in df_merged_all_data_replaced.columns}
# %%
plt.bar(sparsity_columns.keys(), sparsity_columns.values())
plt.xticks(rotation=90)

# VEHICLE_POWER is discarded
# %%
sparse_columns = [column for column in sparsity_columns.keys() if sparsity_columns[column] > 0.25]
# %%
df_merged_all_data_replaced= df_merged_all_data_replaced.drop(columns=sparse_columns)


""" We can now drop rows with missing values : we make sure that we will still have enough data.  
If needed we can fill those NaN values later to get more data"""
# %%
df_merged_all_data_full = df_merged_all_data_replaced.dropna(axis=0, how="any")
len(df_merged_all_data_full)/len(df_merged_all_data_replaced)
# %%


df_merged_all_data_full.to_csv(CFG.data_rootfolder / CFG.processed_data_file_name)


""" if __name__ == '__main__':
output_name = "processed_data.csv"
df_merged_all_data_full.to_csv(CFG.data_rootfolder / output_name)
        #print(f"{output_name} written at {CFG.data_rootfolder}") """
        
# %%
