#%%
import pandas as pd
from config import *

""" For that file, I built a table with a [ACCIDENT_NO","VEHICLE_ID", "PERSON_ID"] granularity
I added to each line the concerning driver information to put in evidence a possible correlation between the driver's carateristics and the severity of the injury"""

#%%
raw_df = pd.read_csv(CFG.data_rootfolder / "person.csv")
df = raw_df

#%%
#Let's clean the column that will be used as indexes latter on
df["PERSON_ID"] = df["PERSON_ID"].str.replace(" ","")
df["VEHICLE_ID"] = df["VEHICLE_ID"].str.replace(" ","")

#%%
#Let's extract the drivers information on a separate dataframe
drivers_df = df[df["Road User Type Desc"]=="Drivers"]
drivers_df = drivers_df[["ACCIDENT_NO","VEHICLE_ID","AGE","SEX","PERSON_ID"]]
drivers_df = drivers_df.rename(columns={"AGE": "Driver Age", "SEX" :"Driver sex",})
drivers_df = drivers_df.set_index(["ACCIDENT_NO","VEHICLE_ID","PERSON_ID" ])

#%%
#Let's select some features 
df = df[["ACCIDENT_NO","PERSON_ID","VEHICLE_ID","SEX","AGE","INJ_LEVEL","SEATING_POSITION", "Road User Type Desc"]]

#%%
#Let's merge the 2 datasets and check for duplicates before setting the index
person_df = pd.merge(df, drivers_df, how="left", on=["ACCIDENT_NO", "VEHICLE_ID"])

#%%
#To confirm that the granularity of the Table is ["ACCIDENT_NO","VEHICLE_ID","PERSON_ID"], 
# we will check the number of duplicates on that subset 
discarded_duplicates = person_df.duplicated(subset=["ACCIDENT_NO","VEHICLE_ID","PERSON_ID"], keep="first")
print(f"number of duplicates : {discarded_duplicates.sum()}")
granularity =["ACCIDENT_NO","VEHICLE_ID","PERSON_ID"]

#%%
person_df= pd.merge(df, drivers_df, how="left", on=["ACCIDENT_NO", "VEHICLE_ID"])
person_df = person_df[~discarded_duplicates].set_index(granularity,verify_integrity=True )

#%%
PERSON_DATA = ProcessedFileData(raw_df=raw_df, df=person_df, granularity = granularity)

