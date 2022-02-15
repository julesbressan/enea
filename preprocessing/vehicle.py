#%%
import pandas as pd
from config import *

#%%
raw_df = pd.read_csv(CFG.data_rootfolder/"VEHICLE.csv")
df = raw_df

#%%
#Let's select some features
df = df[["ACCIDENT_NO","VEHICLE_ID", "Road Surface Type Desc","VEHICLE_POWER","Vehicle Type Desc","TARE_WEIGHT"]]


#%%
#let's categorise vehicle TARE_WEIGHT
splits = df[df.TARE_WEIGHT !=0 ].TARE_WEIGHT.describe().loc[["25%", "50%", "75%"]]

def weight_categories(weight: float) -> str:
    if weight <= splits["25%"]:
        return "light"
    elif  splits["25%"]< weight <= splits["75%"]:
        return "mid"
    else :
        return "heavy"
    
#%%
df["weight_category"] = df.TARE_WEIGHT.apply(lambda x: weight_categories(x) )
df.drop(columns="TARE_WEIGHT")



#%%
#let's simplify car type categories by only keeping the 10 first that represent more than 95 % of the accidents 

#print((df["Vehicle Type Desc"].value_counts()/len(df["Vehicle Type Desc"]))[:10].sum())

simplified_categories = df["Vehicle Type Desc"].value_counts().index[:10]

def type_categories(category):
    if category in simplified_categories
        return category
    else :
        return "Other" 

df["weight_category"] = df.TARE_WEIGHT.apply(lambda x: weight_categories(x) )
df.drop(columns="TARE_WEIGHT")

#%%
granularity =["ACCIDENT_NO","VEHICLE_ID"]
df = df.set_index(granularity, verify_integrity=True)

#%%
VEHICLE_DATA = ProcessedFileData(raw_df=raw_df,df= df, granularity=granularity) 