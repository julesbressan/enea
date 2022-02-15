#%%
import pandas as pd
from config import *

#%%
raw_df = pd.read_csv(CFG.data_rootfolder/"VEHICLE.csv")
df = raw_df

#%%
#Let's select some features
df = df[["ACCIDENT_NO","VEHICLE_ID", "Road Surface Type Desc","VEHICLE_BODY_STYLE", "VEHICLE_MAKE","VEHICLE_POWER","Vehicle Type Desc","TARE_WEIGHT","LEVEL_OF_DAMAGE"]]
granularity =["ACCIDENT_NO","VEHICLE_ID"]
df = df.set_index(["ACCIDENT_NO","VEHICLE_ID"], verify_integrity=True)

#%%
VEHICLE_DATA = ProcessedFileData(raw_df=raw_df,df= df, granularity=granularity) 