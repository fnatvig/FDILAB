import pandas as pd
from Preprocessor import *

def filter(toggle, data):
    if toggle:
        print(data)

def train():
    raw_data = pd.read_excel("data_exports/data_export.xlsx")
    pre = Preprocessor(pd.DataFrame())
    data = pre.disassemble(raw_data)
    print(data)

# train()