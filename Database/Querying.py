import os
import re
import CreateDatabase as db
import sqlalchemy as sqla
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import time

'''
I can query a first level and then index dates and variables to optimize time on the dashboard
This querying could be a global variable that I query from it
'''



class TimeSeries:
    #store dataframes here
    Runs = {}
    def __init__ (self, database_fn, filterVariable) :
            
        engine = create_engine("sqlite:///{}".format(database_fn), echo = False) #False to not show the output
        connection = engine.connect()
        base = declarative_base()
        Session = sessionmaker(bind = db.engine)
        session = Session()
        start_time = time.perf_counter()
        
        if filterVariable in self.Runs:
            pass #gain computer time
            self.DataFrame = self.Runs[filterVariable]
            print('\n\n ******************** DataFrame already generated **********************\n\n\n')
        else:                    
            query = '''
            SELECT 
                DiversMeasurements.ID, DiversMeasurements.Date, DiversMeasurements.Variable, DiversMeasurements.Value,
                Wells.ID, Wells.Name, Wells.DrillID,
                Drills.ID, Drills.E, Drills.N
            FROM 
            	DiversMeasurements
            JOIN
            	Wells ON DiversMeasurements.WellID = Wells.ID
            JOIN
                Drills ON Wells.ID = Drills.ID
            WHERE
                Variable = {} '''.format(filterVariable)
            
            
            DataFrame = pd.read_sql(query, con = connection)
            DataFrame = DataFrame.iloc[:,1:]
            DataFrame = DataFrame.loc[:, ~DataFrame.columns.duplicated()]
            DataFrame.Date = pd.to_datetime(DataFrame.Date)
            DataFrame.Date = pd.to_datetime(DataFrame.Date)
            end_time = time.perf_counter()
            #store run in class dictionary
            self.Runs [filterVariable] = DataFrame            
            self.DataFrame = DataFrame
            self.RunTime = end_time - start_time

class Isolines:
    #store dataframes here
    Runs = {}
    def __init__ (self, database_fn, Variable, Year, Month, Day, Hour) :
    
        engine = create_engine("sqlite:///{}".format(database_fn), echo = False) #False to not show the output
        connection = engine.connect()
        base = declarative_base()
        Session = sessionmaker(bind = db.engine)
        session = Session()
        start_time = time.perf_counter()
        
        datetime = pd.to_datetime(f'{Year}-{Month}-{Day} {Hour}')
        l_ts = pd.to_datetime(f'{Year}-{Month}-{Day} {Hour-1}:30').value
        u_ts = pd.to_datetime(f'{Year}-{Month}-{Day} {Hour}:30').value
        

        #generating Key for the class dictionary
        Runs_key = f'{datetime}-{Variable}'
        
        
        if Runs_key not in self.Runs:
            query = f'''
            SELECT 
            	DiversMeasurements.WellID, DiversMeasurements.TimeStamp, DiversMeasurements.Variable, DiversMeasurements.Value,
            	Wells.ID, Wells.Name, Wells.DrillID, Drills.ID, Drills.E, Drills.N,
            	VariablesDivers.ID, VariablesDivers.Name
            FROM 
                DiversMeasurements
            JOIN
                Wells ON DiversMeasurements.WellID = Wells.ID
            JOIN
                Drills ON Wells.DrillID = Drills.ID	
            JOIN	
                VariablesDivers ON 	DiversMeasurements.Variable = VariablesDivers.ID
            WHERE
            	Variable = {Variable} AND TimeStamp BETWEEN {l_ts} AND {u_ts}
            '''
            
            
            DataFrame = pd.read_sql(query, con = connection)
        
            cols = list(DataFrame.columns)
            cols[5] =  'WellName'
            cols[-1] = 'VariableName'
            DataFrame.columns = cols
            DataFrame = DataFrame.loc [:, ~DataFrame.columns.duplicated()].drop('DrillID', axis = 1)

            #saving constant variables to store it as class attribute

            VariableName = DataFrame.VariableName.unique()[0]
            #dropping constant variable
            DataFrame = DataFrame.drop(['VariableName', 'TimeStamp', 'Variable'], axis = 1) 
            
#             DataFrame.columns = cols
#             selection = ['ID', 'Name', 'Date', 'Hour', 'Variable', 'Value', 'E', 'N']
                                   
#             DataFrame = DataFrame[selection]
            
#             DataFrame.columns = ['ID', 'DrillID', 'Name', 'Date', 'Hour', 'Variable', 'Value', 'E', 'N']
            
#             DataFrame.drop(DataFrame.iloc[:,1].name, axis = 1, inplace = True)
            
            # print(query)
            end_time = time.perf_counter()
            self.RunTime = end_time - start_time
            self.DataFrame = DataFrame
            self.datetime = datetime
            self.VariableID = Variable
            # self.VariableName = VariableName
            #adding run to class attribute
            self.Runs [Runs_key] = {'DataFrame' : DataFrame,
                                    'Datetime' : datetime,
                                    'VariableID' : Variable,
                                    'VariableName' : VariableName} #store in class variable
            # print(self.Runs)
            
        #conditional to retrieve dataframe from class attribute
        #gain computer time
        else:
            #getting object's attributes
            self.DataFrame = self.Runs[Runs_key]['DataFrame']
            self.Datetime = self.Runs[Runs_key]['Datetime']
            self.VariableID = self.Runs[Runs_key]['VariableID']
            self.VariableName = self.Runs[Runs_key]['VariableName']
                
            
            print('\n\n ******************** DataFrame already generated **********************\n\n\n')
           


class HydroProfile:
    #store dataframes here
    Runs = {}
    def __init__ (self, database_fn) :
    
        engine = create_engine("sqlite:///{}".format(database_fn), echo = False) #False to not show the output
        connection = engine.connect()
        base = declarative_base()
        Session = sessionmaker(bind = db.engine)
        session = Session()
        start_time = time.perf_counter()
        
        if 'DataFrame' in self.Runs:
            pass #gain computer time
            self.DataFrame = self.Runs['DataFrame']
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
            self.Runs ['DataFrame'] = DataFrame #store in class variable


database_fn = 'database.db'

engine = create_engine("sqlite:///{}".format(database_fn), echo = False) #False to not show the output
connection = engine.connect()
base = declarative_base()
Session = sessionmaker(bind = db.engine)
session = Session()
start_time = time.perf_counter()



query = Isolines(database_fn, 0, 2015, 12, 12, 12)
df = query.DataFrame