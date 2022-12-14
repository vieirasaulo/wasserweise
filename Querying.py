import CreateDatabase as db
from sqlalchemy import create_engine
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
        start_time = time.perf_counter()
        
        if filterVariable not in self.Runs:
            query = '''
            SELECT 
            	PointsMeasurements.ID, PointsMeasurements.MonitoringPointID, PointsMeasurements.TimeStamp, PointsMeasurements.VariableID, PointsMeasurements.Value,
            	MonitoringPoints.ID, MonitoringPoints.Name, MonitoringPoints.PointID,
            	Points.ID, Points.E, Points.N
            FROM 
            	PointsMeasurements
            JOIN
            	MonitoringPoints ON PointsMeasurements.MonitoringPointID = MonitoringPoints.ID
            JOIN
            	Points ON MonitoringPoints.PointID = Points.ID
            WHERE
                VariableID = {} '''.format(filterVariable)
            
            
            DataFrame = pd.read_sql(query, con = connection)
            DataFrame = DataFrame.iloc[:,1:]
            DataFrame = DataFrame.loc[:, ~DataFrame.columns.duplicated()]
            DataFrame ['Date'] = pd.to_datetime(DataFrame.TimeStamp * 1e9)
            end_time = time.perf_counter()
            #store run in class dictionary
            self.Runs [filterVariable] = DataFrame            
            self.DataFrame = DataFrame
            self.RunTime = end_time - start_time
            
        else:                    
            self.DataFrame = self.Runs[filterVariable]
            print('\n\n ******************** DataFrame already generated **********************\n\n\n')


class Isolines:
    #store dataframes here
    Runs = {}
    def __init__ (self, database_fn, Year, Month, Day, Hour) :
    
        engine = create_engine("sqlite:///{}".format(database_fn), echo = False) #False to not show the output
        connection = engine.connect()
        start_time = time.perf_counter()
        
        Lh = Hour-1 #lower limit for searching hour. still need to add 30 min
        if Hour < 10:
            Hour = '0'+str(Hour)
            Lh =  '0'+str(Lh)
        else: 
            Hour = str(Hour)
            Lh = str(Lh)
        datetime = pd.to_datetime(f'{Year}-{Month}-{Day} {Hour}')
        l_ts = int(pd.to_datetime(f'{Year}-{Month}-{Day} {Lh}:30').value /1e9)
        u_ts = int(pd.to_datetime(f'{Year}-{Month}-{Day} {Hour}:30').value / 1e9)
        
        Runs_key = str(datetime)
        #generating Key for the class dictionary
        
        
        
        if Runs_key not in self.Runs:
            #START FROM HERE - LINE WHERE 99
            query = f'''
            SELECT 
            	PointsMeasurements.MonitoringPointID, PointsMeasurements.TimeStamp, PointsMeasurements.VariableID, PointsMeasurements.Value,
            	MonitoringPoints.ID, MonitoringPoints.Name as MonitoringPointName, MonitoringPoints.PointID, Points.ID, Points.E, Points.N,
            	Variables.ID, Variables.Name AS Type
            FROM 
            	PointsMeasurements
            JOIN
            	MonitoringPoints ON PointsMeasurements.MonitoringPointID = MonitoringPoints.ID
            JOIN
            	Points ON MonitoringPoints.PointID = Points.ID	
            JOIN	
            	Variables ON PointsMeasurements.VariableID = Variables.ID
            WHERE
                TimeStamp BETWEEN {l_ts} AND {u_ts}
            '''
    
            DataFrame = pd.read_sql(query, con = connection)
            DataFrame = DataFrame [DataFrame.VariableID.isin([0,9])]
        
            # indexing columns    
            cols = ['MonitoringPointID', 'MonitoringPointName', 'Time', 'Type', 'Value', 'E', 'N']

            #dropping constant variable
            DataFrame['Time'] = pd.to_datetime(DataFrame.TimeStamp * 1e9)
            DataFrame = DataFrame[cols]
            
            # taking average values for duplicated values
            if DataFrame.duplicated(subset = ['MonitoringPointName']).any():
                v = DataFrame.groupby('MonitoringPointName').Value.mean().values
                t = DataFrame.groupby('MonitoringPointName')['Time'].mean().values
                df = DataFrame.drop_duplicates(subset = ['MonitoringPointID'])
                df = df.drop(['MonitoringPointID', 'Time'], axis = 1)
                df['Value'] = v
                df['Time'] = t
                DataFrame = df.copy()
                
            
                        
            print(query)
            end_time = time.perf_counter()
            self.RunTime = end_time - start_time
            self.DataFrame = DataFrame
            self.datetime = datetime
            # self.VariableName = VariableName
            #adding run to class attribute
            self.Runs [Runs_key] = {'DataFrame' : DataFrame} #store in class variable
            
        #conditional to retrieve dataframe from class attribute
        #gain computer time
        else:
            #getting object's attributes
            self.DataFrame = self.Runs[Runs_key]

            
            print('\n\n ******************** DataFrame already generated **********************\n\n\n')
           


class HydroProfile:
    #store dataframes here
    Runs = {}
    def __init__ (self, database_fn) :
    
        engine = create_engine("sqlite:///{}".format(database_fn), echo = False) #False to not show the output
        connection = engine.connect()
        start_time = time.perf_counter()
        
        if 'DataFrame' in self.Runs:
            pass #gain computer time
            self.DataFrame = self.Runs['DataFrame']
            print('\n\n ******************** DataFrame already generated **********************\n\n\n')
        else:                    
            query = '''
            SELECT
            	DrillingTests.ID, DrillingTests.PointID, DrillingTests.TestTypeID, DrillingTests.Depth, DrillingTests.Value,
            	TestsType.ID AS TestTypeID, TestsType.Unit, TestsType.Name as TestType, TestsType.ShortName,
            	Points.ID AS PointID2, Points.Name as DrillName, Points.Depth, Points.MonitoringPoint, Points.E, Points.N
            
            FROM 
            	DrillingTests
            JOIN
            	TestsType ON DrillingTests.TestTypeID = TestsType.ID
            JOIN
            	Points ON DrillingTests.PointID = Points.ID	
            '''
            
            DataFrame = pd.read_sql(query, con = connection)
            cols = ['ID', 'PointID', 'DrillName', 'TestType','Unit', 'Depth', 'MonitoringPoint',
                    'Value', 'E', 'N']
            DataFrame = DataFrame[cols]
            DataFrame.MonitoringPoint = [int.from_bytes(i, byteorder = 'big') for i in DataFrame.MonitoringPoint]
            
            print(query)
            end_time = time.perf_counter()
            self.RunTime = end_time - start_time
            self.DataFrame = DataFrame
            self.Runs ['DataFrame'] = DataFrame #store in class variable
