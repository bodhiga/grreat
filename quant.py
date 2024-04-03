import os
import pandas as pd
import seaborn as sns

import analysis as analysis

import indicator as indicator
from indicators import health
from indicators import adolescents
from indicators import satisfaction
from indicators import influencers
from indicators import baseline

_output = './output'
_figures ='./output/figures'
_data = './output/data'
_raw = './raw'

if not os.path.exists(_output):
   os.mkdir(_output)

if not os.path.exists(_figures):
    os.mkdir(_figures)

if not os.path.exists(_data):
    os.mkdir(_data)

if not os.path.exists(_raw):
   os.mkdir(_raw)

df = adolescents.load("./Adolescent Survey_2022_20_09_10_37.sav", endline=False)
eadf = adolescents.load("./UNICEF Tz_GRREAT Endline  Adolescents Survey_20240325.xlsx", endline=True)
hdf = health.load('./Health Facility_2022_22_09_10_52.sav', endline=False)

csdf = satisfaction.load('./Customer Satisfaction_2022_20_09_10_29.xlsx',
                         endline=False)
endline_csdf = satisfaction.load('./UNICEF_Tz-_GRREAT_Endline_-_Customer_Satisfaction_Survey_-_all_versions_-_labels_-_2024-03-20-12-39-15.xlsx',
                                 endline=True)

cidf = influencers.load('./Community_2022_22_09_10_51.sav')

bdf = baseline.load("./GIRLS EMPOWEMENT.dta")

indicator.process(adf=df,
                  eadf=eadf,
                  hdf=hdf,
                  cidf=cidf,
                  csdf=csdf,
                  ecsdf=endline_csdf,
                  bdf=bdf)

# NOTE Print a table for
table_1100a = pd.concat([health.indicator_1100a(hdf), hdf], axis=1)
table_1100a = table_1100a[["regions", "Q_3", 0]]
table_1100a.to_excel('./output/table_1100a.xlsx')

print()

print('Community Influencers survey, breakdown')
analysis.breakdown(cidf, ['sex', 'regions'])
print()

print('Customer Satisfaction survey, breakdown')
analysis.breakdown(csdf, ['sex', 'regions'])
print()


# ## TO GENERATE THE CHARACTERISTICS TABLE
_rows = [
   'agegroup',
   'sex',
   'schooling',
   'education',
   'occupation',
         ]
_row_labels = [
   'Age Group',
   'Sex',
   'Still schooling',
   'Highest Achieved Level of Education',
   'Occupation',
]

_columns = ['sex', 'regions']

filtered_df = df[df['agegroup'].isin(['10-14', '15-19'])]

def _aggfunc(x):
   count = len(x)
   percent = 100 * count / len(filtered_df)
   return "{n} ({p:.1f}%)".format(n=count, p=percent)


for idx, r in enumerate(_rows):
   result = pd.concat(
      [pd.concat([pd.DataFrame([[]], columns=[], index=[_row_labels[idx]])] + [pd.crosstab(filtered_df[r], filtered_df[c], values=filtered_df["sex"], aggfunc=_aggfunc, margins=(cidx + 1 == len(_columns))) for cidx, c in enumerate(_columns)], axis=1)])
   result.to_excel('./output/characterstics_{}.xlsx'.format(r))

indicator.dashboard(adf=df, hdf=hdf, cidf=cidf, csdf=csdf, bdf=bdf)

adf = df
indicator.gei_breakdown(adf.loc[(adf["sex"] == "Female") & (adf['agegroup'].isin(['10-14', '15-19']))])

demos = indicator.demographics(filtered_df)
demos.to_excel('./output/demographics.xlsx')


print('Adolescents survey, breakdown')
analysis.breakdown(filtered_df, ['sex', 'regions',
                        ['Q_3', 'Q_4', 'Q_5', 'Q_6'], # district, ward, village etc.
                        ['Q_3', 'Q_4', 'Q_5'],
                        ])


filtered_df.to_excel('./raw/adolescents.xlsx')
hdf.to_excel('./raw/health.xlsx')
cidf.to_excel('./raw/influencers.xlsx')
