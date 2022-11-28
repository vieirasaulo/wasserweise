import CreateDatabase as db
import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os
import random
import numpy as np

# new session
Session = sessionmaker(bind = db.engine)
session = Session()




path = 'D:\\Repos\\PirnaCaseStudy\\Data\\Databases'
Tables_list = ['Divers', 'WellDiver', 'TestsType', 
                'HydroTests', 'Drills', 'Wells', 
                'VariablesDivers' , 'DiversMeasurements1']

os.chdir(path)

'''
generate .csv files
'''
# for sheet in Tables_list:
#     df = pd.read_excel('TablesDatabase.xlsx', sheet_name = sheet)
#     df.to_csv(f'{sheet}.csv', index = False)


def InputDatabase (table , func ):
    df = pd.read_csv(f'{table}.csv') #iterator here #need to convert str to var
    # df = df.sample(n=10)
    columns = df.columns
    
    #modify the table. Convert interger to bites in binary columns
    if table != 'DiversMeasurements':
        for col in columns:
            unique = df[col].unique()
            if np.array_equal(unique, unique.astype(bool)): #True for binary arrays
                if col == 'Variable':
                    continue #don't want binary here
                li = [x.to_bytes(2, byteorder = 'big') for x in df[col]]
                df[col] = li
    else:
        df['TimeStamp'] = pd.to_datetime(df['Time'])
    #input data
    for i, row in enumerate(df.iterrows()):
        values = row[1]
               
        tr = func(*values)
        session.add(tr)   
    session.commit()
    




'''
Uncomment below the inputs wanted
'''
# InputDatabase(Tables_list[0], db.Divers)

# InputDatabase(Tables_list[1], db.WellDiver)

# InputDatabase(Tables_list[2], db.TestsType)

# InputDatabase(Tables_list[3], db.HydroTests)

# InputDatabase(Tables_list[4], db.Drills)

# InputDatabase(Tables_list[5], db.Wells)

# InputDatabase(Tables_list[6], db.VariablesDivers)

# InputDatabase(Tables_list[7], db.DiversMeasurements)
