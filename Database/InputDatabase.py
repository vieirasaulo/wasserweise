import CreateDatabase as db
import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os
import random


#new session
Session = sessionmaker(bind = db.engine)
session = Session()


#MeasurementsType
'''
Check Here
'''
Measurements_list = ['HPT', 'Slug Test', X`'DPIL', 'Pumping Test']

for i, Measurement in enumerate(Measurements_list):
    tr = db.MeasurementsType(i, Measurement)
    session.add(tr)
    


#Divers


#VariablesDivers


#Drills


#VariablesDivers



#Drills
path = 'D:\\Repos\\PirnaCaseStudy\\Data\\Databases'
os.chdir(path)
df = pd.read_csv('Drills.csv')
df['Measurement'][0]=1
df = df.fillna(0) #all that is na does not exist - false - not present
df['Measurement'] = df['Measurement'].astype(int)

for i, row in enumerate(df.iterrows()):
    row = row[1]    
    DrillID = i#.to_bytes(2, byteorder = 'big')
    DrillName = str(row[0])
    DescriptionData = row[1].to_bytes(2, byteorder = 'big')
    Well = row[2].to_bytes(2, byteorder = 'big')
    Measurement = row[3].to_bytes(2, byteorder = 'big')
    E = row[4]
    N = row[5]
    Depth = row[6]
    
    tr = db.Drills(DrillID, DrillName, DescriptionData, Well, Measurement, E, N, Depth)
    session.add(tr)
    



# DrillMeasurements



# Wells

# WellDiver


# DiverMeasurements


session.commit()


    