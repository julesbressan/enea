import pandas as pd
from config import * 


raw_df = pd.read_csv(CFG.data_rootfolder / "SUBDCA.csv")
df = raw_df 

df = df.drop(columns = ["SUB_DCA_SEQ", "SUB_DCA_CODE"]).set_index("ACCIDENT_NO", verify_integrity=True)

SUBDCA_DATA = ProcessedFileData(raw_df=raw_df, df = df)