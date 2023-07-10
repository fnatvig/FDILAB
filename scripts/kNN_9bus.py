import pandas as pd
from Preprocessor import *

def filter(toggle, data):
    if toggle:
        if data.iloc[0]["label"] == "attack":
            return "attack"
        else: 
            return "no attack"

def train():
    raw_data = pd.read_excel("data_exports/data_export.xlsx")
    pre = Preprocessor(pd.DataFrame())
    data = pre.disassemble(raw_data)
    print(data)

# train()