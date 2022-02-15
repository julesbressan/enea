#%%
from config import *
import pandas as pd

"""We are just looking at ROAD_TYPE here, other features are redundant with the rest of the files"""

#%%
raw_df = pd.read_csv(CFG.data_rootfolder / "ACCIDENT_LOCATION.csv")
df = raw_df

#%%
# Checking granularity
duplicates =raw_df["ACCIDENT_NO"].duplicated(keep=False)
print(f"number of duplicates {duplicates.sum()}")
#We deduce that granularity is ACCIDENT_NO
granularity=["ACCIDENT_NO"]

#%%
df = df[["ACCIDENT_NO","ROAD_TYPE"]].set_index(granularity,verify_integrity=True)


#%%
ACCIDENT_LOCATION_DATA = ProcessedFileData(raw_df=raw_df, df= df, granularity = granularity)