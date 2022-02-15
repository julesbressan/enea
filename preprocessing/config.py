from typing import Any
from pydantic import BaseModel
from pathlib import Path
from typing import Optional
import pandas as pd
import os 



class ProcessedFileData(BaseModel):
    raw_df: Optional[Any]
    df: Any
    granularity: Optional[list]
    
class Config(BaseModel):
    data_rootfolder = Path("/Users/julesbressan/data/ACCIDENT")
    processed_data_file_name: str = "processed_data.csv"
    
CFG = Config()
