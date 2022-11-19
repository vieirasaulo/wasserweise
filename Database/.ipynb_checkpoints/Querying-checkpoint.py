import re
import CreateDatabase as db
import sqlalchemy as sqla
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import time


path = 'D:\\Repos\\PirnaCaseStudy\\Database'
database_fn = 'Database.db'
database_path = path + '\\' + database_fn
engine = create_engine("sqlite:///{}".format(database_fn), echo = False) #False to not show the output
connection = engine.connect()
base = declarative_base()
Session = sessionmaker(bind = db.engine)
session = Session()
start_time = time.perf_counter()


'''
I can query a first level and then index dates and variables to optimize time on the dashboard
This querying could be a global variable that I query from it
'''



class TimeSeries:
    #store dataframes here
    Runs = {}
    def __init__ (self, database_fn, filterVariable, filterWellID) :
            
        engine = create_engine("sqlite:///{}".format(database_fn), echo = False) #False to not show the output
        connection = engine.connect()
        base = declarative_base()
        Session = sessionmaker(bind = db.engine)
        session = Session()
        start_time = time.perf_counter()
        
        if filterWellID in self.Runs:
            pass #gain computer time
            self.DataFrame = self.Runs[filterWellID]
            print('\n\n ******************** DataFrame already generated **********************\n\n\n')
        else:                    
            query = '''
            SELECT 
                DiversMeasurements.ID, DiversMeasurements.Date, DiversMeasurements.Variable, DiversMeasurements.Value,
                Wells.ID, Wells.Name
            FROM 
            	DiversMeasurements
            JOIN
            	Wells ON DiversMeasurements.WellID = Wells.ID
            WHERE
                Variable = {} and WellID = {}'''.format(filterVariable, filterWellID)
            
            
            DataFrame = pd.read_sql(query, con = connection)
            DataFrame = DataFrame.iloc[:,1:]
            end_time = time.perf_counter()
            #store run in class dictionary
            self.Runs [filterWellID] = DataFrame            
            self.DataFrame = DataFrame
            self.RunTime = end_time - start_time

class PotentiometricMap:
    #store dataframes here
    Runs = {}
    def __init__ (self, database_fn, filterVariable, Year, Month, Day, FilterHour) :
    
        engine = create_engine("sqlite:///{}".format(database_fn), echo = False) #False to not show the output
        connection = engine.connect()
        base = declarative_base()
        Session = sessionmaker(bind = db.engine)
        session = Session()
        start_time = time.perf_counter()
        
        date = pd.to_datetime(f'{Year}-{Month}-{Day}').date()
        year, day = str(Year), str(Month)
        if Month<10:
            Month = f'0{str(Month)}'
        
        
        if date in self.Runs:
            pass #gain computer time
            self.DataFrame = self.Runs[date]
            print('\n\n ******************** DataFrame already generated **********************\n\n\n')
        else:                    
            query = f'''
            SELECT 
            	DiversMeasurements.Date, DiversMeasurements.Hour, DiversMeasurements.Variable, DiversMeasurements.Value,
                Wells.ID, Wells.Name, Wells.DrillID, Drills.ID, Drills.E, Drills.N
            FROM 
            	DiversMeasurements
            JOIN
            	Wells ON DiversMeasurements.WellID = Wells.ID
            JOIN
            	Drills ON Wells.DrillID = Drills.ID	
            WHERE
            	Variable = {filterVariable} and Date = '{Year}-{Month}-{Day}' and Hour = {FilterHour}
            '''
            
            #parsing query to get col names
            q = query.split('\n')
            l1 = q[2].split(',')
            l2 = q[3].split(',')
            l = l1 + l2

            cols = [re.sub("[\t ]", '', i) for i in l if '.' in i]
            cols = [i.split('.')[1] for i in cols]
            
            DataFrame = pd.read_sql(query, con = connection)
            DataFrame.columns = cols
            selection = ['ID', 'Name', 'Date', 'Hour', 'Variable', 'Value', 'E', 'N']
                                   
            DataFrame = DataFrame[selection]
            
            DataFrame.columns = ['ID', 'DrillID', 'Name', 'Date', 'Hour', 'Variable', 'Value', 'E', 'N']
            
            DataFrame.drop(DataFrame.iloc[:,1].name, axis = 1, inplace = True)
            
            print(query)
            end_time = time.perf_counter()
            self.RunTime = end_time - start_time
            self.DataFrame = DataFrame
            self.Runs [date] = DataFrame #store in class variable
 




class HydroProfile:
    #store dataframes here
    Runs = {}
    def __init__ (self, database_fn, DrillID) :
    
        engine = create_engine("sqlite:///{}".format(database_fn), echo = False) #False to not show the output
        connection = engine.connect()
        base = declarative_base()
        Session = sessionmaker(bind = db.engine)
        session = Session()
        start_time = time.perf_counter()
        
        if DrillID in self.Runs:
            pass #gain computer time
            self.DataFrame = self.Runs[DrillID]
            print('\n\n ******************** DataFrame already generated **********************\n\n\n')
        else:                    
            query = f'''
            SELECT
            	HydroTests.ID, HydroTests.DrillID, HydroTests.TestTypeID, HydroTests.Depth, HydroTests.Value,
            	TestsType.ID, TestsType.Unit, TestsType.Name, TestsType.Variable,
            	Drills.ID, Drills.Name, Drills.Depth, Drills.Well, Drills.E, Drills.N
            
            FROM 
            	HydroTests
            JOIN
            	TestsType ON HydroTests.TestTypeID = TestsType.ID
            JOIN
            	Drills ON HydroTests.DrillID = Drills.ID	
            WHERE
            	DrillID = {DrillID}
            '''
            
            q = query.split('\n')
            l1 = q[2].split(',')
            l2 = q[3].split(',')
            l3 = q[4].split(',')
            l = l1 + l2 + l3
            
            cols = [re.sub("[\t ]", '', i) for i in l if '.' in i]
            cols = [i.replace('.', '_') for i in cols]


            DataFrame = pd.read_sql(query, con = connection)
            DataFrame.columns = cols
            selection =  ['HydroTests_DrillID', 'HydroTests_Depth', 'TestsType_Unit', 'TestsType_Name',
                          'TestsType_Variable', 'HydroTests_Value', 'Drills_ID', 'Drills_Name', 
                          'Drills_Depth', 'Drills_E', 'Drills_N']  
     
                              
            DataFrame = DataFrame[selection]
            DataFrame.columns = [i.split('_')[1] for i in selection]
            
            print(query)
            end_time = time.perf_counter()
            self.RunTime = end_time - start_time
            self.DataFrame = DataFrame
            self.Runs [DrillID] = DataFrame #store in class variable
 

x = TimeSeries(database_path, 0, 0)
x = TimeSeries(database_path, 0, 0)
dfX = x.DataFrame

y = PotentiometricMap(database_path, filterVariable = 0, Year = 2015, Month = 1, Day = 30, FilterHour = 12)
dfY= y.DataFrame

z = HydroProfile(database_path, 0)
dfZ= z.DataFrame


