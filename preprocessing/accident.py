#%%
import pandas as pd
from datetime import datetime
import calendar
from config import *
#%%
print("Importing accident raw data...")
raw_df_accident = pd.read_csv(CFG.data_rootfolder / "ACCIDENT.CSV")
df_accident = raw_df_accident

#%%
#Let's check granularity 
duplicates = raw_df_accident["ACCIDENT_NO"].duplicated(keep=False)
#print(duplicates.sum())
#We deduce that granularity is ACCIDENT_NO
granularity=["ACCIDENT_NO"]
#%%
# Some columns are used to describe some encoded columns
encoded_columns = [
    "ACCIDENT_TYPE",
    "DAY_OF_WEEK",
    "DCA_CODE",
    "LIGHT_CONDITION",
    "ROAD_GEOMETRY",
]
description_columns = [
    "Accident Type Desc",
    "Day Week Description",
    "DCA Description",
    "Light Condition Desc",
    "Road Geometry Desc",
]

#%%
# To deal with time data, we'll create some categorical features : hour of the day when the accident happened [ACCIDENTHOUR],
# Day of the year when the accident happened [ACCIDENTDAYNUMBER]

df_accident["ACCIDENTDATETIME"] = (
    df_accident["ACCIDENTDATE"] + " " + df_accident["ACCIDENTTIME"]
)
print("Creating a datetime column (might take some time)...")
df_accident["ACCIDENTDATETIME"] = pd.to_datetime(
    df_accident["ACCIDENTDATETIME"]
)  # It takes a bit of time because we let it guess the format as there is diferent formats(%Y-%m-%d %H:%M:%S",%Y/%m/%d %H:%M:%S" ...)

# To keep day number of the year constant, we'll watch out for peak years and 29th of february
def day_nb_of_the_year(date: datetime) -> int:
    raw_day_number = int(date.strftime("%j"))

    if calendar.isleap(date.year) and raw_day_number >= 60:
        if raw_day_number == 60:  # 29/02/xxxx
            return 366
        else:
            return raw_day_number - 1
    return raw_day_number

#%%
print("Creating daynumber and accidenthour columns from datetime column...")
df_accident["ACCIDENTDAYNUMBER"] = df_accident["ACCIDENTDATETIME"].apply(
    lambda x: day_nb_of_the_year(x)
)

df_accident["ACCIDENTHOUR"] = df_accident["ACCIDENTDATETIME"].apply(lambda x: x.hour)

#%%
# We can now drop the columns we don't want to keep
redundant_columns = ["NO_PERSONS_NOT_INJ","NO_PERSONS_INJ_2","NO_PERSONS_INJ_3",	"NO_PERSONS_KILLED", "SEVERITY"]
quantitative_time_columns = ["ACCIDENTTIME", "ACCIDENTDATE", "ACCIDENTDATETIME" ]
non_crash_related_columns = [
    "EDITION",
    "PAGE",
    "DIRECTORY",
    "GRID_REFERENCE_X",
    "GRID_REFERENCE_Y",
]

#%%
df_accident = df_accident.drop(
    columns=non_crash_related_columns
    + encoded_columns
    + quantitative_time_columns
    + redundant_columns
).set_index(granularity, verify_integrity=True)

#%%
ACCIDENT_DATA = ProcessedFileData(
    raw_df=raw_df_accident, df=df_accident, granularity = granularity
)
