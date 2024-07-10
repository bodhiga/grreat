import warnings

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

# Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

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
ehdf = health.load('./UNICEF_Tz-_GRREAT_Endline_-_Health_Facility_Checklist_-_all_versions_-_labels_-_2024-03-28-09-01-12.xlsx', endline=True)

csdf = satisfaction.load('./Customer Satisfaction_2022_20_09_10_29.xlsx',
                         endline=False)
endline_csdf = satisfaction.load('./UNICEF_Tz-_GRREAT_Endline_-_Customer_Satisfaction_Survey_-_all_versions_-_labels_-_2024-03-20-12-39-15.xlsx',
                                 endline=True)

cidf = influencers.load('./Community_2022_22_09_10_51.sav', endline=False)
ecidf = influencers.load_endline(
   female="./UNICEF Tz_GRREAT Endline Community Influencers Tool Female_2024-03-27.xlsx",
   male="./UNICEF Tz-_GRREAT Endline Community Influencers Tool_Male_2024-03-27.xlsx"
)

bdf = baseline.load("./GIRLS EMPOWEMENT.dta")

indicator.process(adf=df,
                  eadf=eadf,
                  hdf=hdf,
                  ehdf=ehdf,
                  cidf=cidf,
                  ecidf=ecidf,
                  csdf=csdf,
                  ecsdf=endline_csdf,
                  bdf=bdf)

health.table_1100a(hdf, endline=False, out='table_1100a_midline.xlsx')
health.table_1100a(ehdf, endline=True, out='table_1100a_endline.xlsx')

# print('Community Influencers survey, breakdown')
# analysis.breakdown(ecidf, ['sex', 'regions'])
# print()

# print('Customer Satisfaction survey, breakdown')
# analysis.breakdown(csdf, ['sex', 'regions'])
# print()


## TO GENERATE THE CHARACTERISTICS TABLE
def characteristics_table(df, endline):
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
   filtered_df = df
   # filtered_df = df[df['agegroup'].isin(['10-14', '15-19'])] # TODO

   def _aggfunc(x):
      count = len(x)
      percent = 100 * count / len(filtered_df)
      return "{n} ({p:.1f}%)".format(n=count, p=percent)

   for idx, r in enumerate(_rows):
      result = pd.concat(
         [pd.concat([pd.DataFrame([[]], columns=[], index=[_row_labels[idx]])] + [pd.crosstab(filtered_df[r], filtered_df[c], values=filtered_df["sex"], aggfunc=_aggfunc, margins=(cidx + 1 == len(_columns))) for cidx, c in enumerate(_columns)], axis=1)])
      result.to_excel('./output/characteristics_{study}_{r}.xlsx'.format(study=('midline' if not endline else 'endline'), r=r))

# characteristics_table(df, endline=False)
# characteristics_table(eadf, endline=True)
# import pdb; pdb.set_trace()

indicator.dashboard(adf=df, eadf=eadf, hdf=hdf, ehdf=ehdf, cidf=cidf, ecidf=ecidf, csdf=csdf, ecsdf=endline_csdf, bdf=bdf) # TODO

adf = df
indicator.gei_breakdown(
   adf.loc[(adf["sex"] == "Female") & (adf['agegroup'].isin(['10-14', '15-19']))],
   eadf.loc[(eadf["sex"] == "Female") & (eadf['agegroup'].isin(['10-14', '15-19']))],

                        )

# demos = indicator.demographics(filtered_df)
# demos.to_excel('./output/demographics.xlsx')


# TODO
# print('Adolescents survey, breakdown')
# analysis.breakdown(filtered_df, ['sex', 'regions',
#                         ['Q_3', 'Q_4', 'Q_5', 'Q_6'], # district, ward, village etc.
#                         ['Q_3', 'Q_4', 'Q_5'],
#                         ])


# filtered_df.to_excel('./raw/adolescents.xlsx')
# hdf.to_excel('./raw/health.xlsx')
# cidf.to_excel('./raw/influencers.xlsx')
