#%%
import pandas as pd
from config import *

raw_df = pd.read_csv(CFG.data_rootfolder / "NODE.csv")
df = raw_df
raw_df.head()

#%%
#Let's check granularity 
accident_duplicates = raw_df["ACCIDENT_NO"].duplicated(keep=False)
print(accident_duplicates.sum())

accident_postcode_duplicates = raw_df[["ACCIDENT_NO", "POSTCODE_NO",]].duplicated(keep=False)
print(accident_postcode_duplicates.sum())

accident_postcode_degurbanname_duplicates = raw_df[["ACCIDENT_NO", "POSTCODE_NO","DEG_URBAN_NAME"]].duplicated(keep=False)
print(accident_postcode_degurbanname_duplicates.sum())

# granularity of raw data is ["ACCIDENT_NO", "POSTCODE_NO","DEG_URBAN_NAME"] 
# 
# But considering the number and the nature, 
# (why an accident would be located at several post codes?) 
# it seemed to be that it was corrupted data and I decided 
# not to take those duplicates in order to have an ACCIDENT_NO granularity


df=df = df[~df["ACCIDENT_NO"].duplicated(keep=False)]

#Our new df granularity is ACCIDENT_NO
granularity = ["ACCIDENT_NO"]

#%%
discarded_columns = ["VICGRID94_X","VICGRID94_Y", "LGA_NAME_ALL","NODE_TYPE", "NODE_ID"]

df = df.drop(columns = discarded_columns).set_index(granularity, verify_integrity=True)

#%%
NODE_DATA = ProcessedFileData(raw_df=raw_df, df=df, granularity = granularity)

# %%
