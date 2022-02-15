#%%
import pandas as pd
from config import *

#%%
raw_df_atm_conditions = pd.read_csv(CFG.data_rootfolder / "ATMOSPHERIC_COND.csv")

#%%
#Let's check granularity 
accident_duplicates = raw_df_atm_conditions["ACCIDENT_NO"].duplicated(keep=False)
print(accident_duplicates.sum())

accident_seq_duplicates = raw_df_atm_conditions[["ACCIDENT_NO", "ATMOSPH_COND_SEQ"]].duplicated(keep=False)
print(accident_seq_duplicates.sum())

# granularity of raw data is ["ACCIDENT_NO", "ATMOSPH_COND_SEQ"] : this is because 
# we might have several atm conditions associated to a same accident .
# 
# But we can see that this only concerns 6428/2 = 3214 accidents. 
# we could create new categories of atm conditions by writing them as "clear-windy" to keep our granularity to ACCIDENT_NO
# But we don't want to over complexify by creating too many categories 
#
#To keep granularity as ACCIDENT_NO, I decided to keep only the last element of the sequence 

df=raw_df_atm_conditions[~raw_df_atm_conditions.duplicated(subset="ACCIDENT_NO", keep="last")] 

#Our new df granularity is ACCIDENT_NO
granularity = ["ACCIDENT_NO"]
#%%
# Clean out NaN values as 9 = 'Not known'
df = df[df["ATMOSPH_COND"] != 9]

#%%
df = df[["ACCIDENT_NO", "Atmosph Cond Desc"]]

#%%
df = df.set_index("ACCIDENT_NO", verify_integrity=True)


#%%
ATM_COND_DATA = ProcessedFileData(df=df, raw_df=raw_df_atm_conditions, granularity = granularity)

