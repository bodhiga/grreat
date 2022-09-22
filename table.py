import pandas as pd
import numpy as np

def crosstab(df, value, row, columns):
    values = df[value]
    cols = []
    for col in columns:
        cols.append(df[col])

    return pd.crosstab(df[row], cols,
                       values=values,
                       aggfunc=np.mean,
                       )

def crosstab_to_xlsx(df, file_path):
    df.to_excel(file_path)
