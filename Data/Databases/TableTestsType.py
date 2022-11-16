import pandas as pd
import os

os.chdir('D:/Repos/PirnaCaseStudy/Data/Databases')
os.listdir()


Overview_df = pd.read_excel('V1_AquiferCharact_Database.xlsx', sheet_name =  'Overview')

Drills_df = pd.read_excel('TablesDatabase.xlsx', sheet_name =  'Drills')
TestsType_df = pd.read_excel('TablesDatabase.xlsx', sheet_name =  'TestsType')

df = pd.melt(Overview_df, id_vars = ['ID'],
             value_vars = Overview_df.columns[1:-1],
             var_name = 'Type')

df = df.replace(['EC log*', 'Resistivity*'], ['EC log', 'Resistivity'])


df = df.loc[df.value != 'NO'].drop('value', axis=1).rename(columns = {'ID' : 'Name'})

df = df.merge(TestsType_df, left_on = 'Type', right_on = 'Name')
df = df[['Name_x', 'ID']].rename(
    columns = {'Name_x' : 'Name',
                'ID' : 'TypeID'
    })


df = df.replace (
    ['G4', 'G1', 'G2', 'G5', 'G3'],
    ['G04', 'G01', 'G02', 'G05', 'G03'])

df.Name = 'D-' + df.Name

df = df.merge(Drills_df[['Name', 'ID']] ,
                on = 'Name'
                ).rename(columns = {
                    'ID': 'DrillID'
                      })#[['DrillID', 'TypeID']]#.drop('Name', axis = 1)
                  
df.to_csv('DrillingTests.csv')