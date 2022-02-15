#%%
import pandas as pd
from config import *

#%%
raw_df = pd.read_csv(CFG.data_rootfolder / "ROAD_SURFACE_COND.csv")
df = raw_df

#%%
#Let's check granularity 
accident_duplicates = raw_df["ACCIDENT_NO"].duplicated(keep=False)
print(accident_duplicates.sum())

accident_seq_duplicates = raw_df[["ACCIDENT_NO", "SURFACE_COND_SEQ"]].duplicated(keep=False)
print(accident_seq_duplicates.sum())

# granularity of raw data is ["ACCIDENT_NO", "ATMOSPH_COND_SEQ"] : this is because 
# we might have several atm conditions associated to a same accident .
# 
# But we can see that this only concerns 2634/2 = 1317 accidents. 
# we could create new categories of road conditions by writing them as "muddy-wet" to keep our granularity to ACCIDENT_NO
# But we don't want to over complexify by creating too many categories 
#
#To keep granularity as ACCIDENT_NO, I decided to keep only the last element

df=raw_df[~raw_df.duplicated(subset="ACCIDENT_NO", keep="last")] 

#Our new df granularity is ACCIDENT_NO
granularity = ["ACCIDENT_NO"]

#%%
df = raw_df[["ACCIDENT_NO", "Surface Cond Desc"]]
df = df[~df["ACCIDENT_NO"].duplicated(keep="first")].set_index(granularity, verify_integrity=True)

#%%
ROAD_COND_DATA = ProcessedFileData(
    df=df, raw_df=raw_df, granularity=granularity
)

