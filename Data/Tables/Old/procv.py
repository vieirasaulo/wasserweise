import pandas as pd
import os


os.chdir('D:/Repos/PirnaCaseStudy/Data/Databases')
df1 = pd.read_excel('TablesDatabase.xlsx', sheet_name =  'WellDiver')

Wells_df = pd.read_excel('TablesDatabase.xlsx', sheet_name = 'Wells')

Wells_df_ = Wells_df[['ID', 'Name']].rename(columns = {'ID' : 'WellID'})
df1 = df1.rename(columns = {'WellName': 'Name'})

df = Wells_df_.merge(df1, on = 'Name')


df.WellID_x.to_csv('wellid.csv', index = False)