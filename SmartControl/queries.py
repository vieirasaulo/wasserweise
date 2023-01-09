import time
from datetime import timedelta
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import SMARTControl.CreateDatabase as CreateDatabase

class Get:
    def __init__ (self, database_fn : str):
        '''
        Function that returns important variables to connect to the database using sqlaclchemy API

        Parameters
        ----------
        database_fn : str
            path to the database.

        Returns
        -------
        engine :  sqlalchemy.engine.base.Engine
            engine determines the type of connection.
        connection : sqlalchemy.engine.base.Connection
            connection is the one that is mostly used. It will be used to pass SQL statements into pandas to retrieve a dataframe.
        base : sqlalchemy.orm.decl_api.DeclarativeMeta
        session : sqlalchemy.orm.session.Session
            Session can be used to edit and update the database for more specific purposes.
        '''

        engine = create_engine("sqlite:///{}".format(database_fn), echo = False) #False to not show the output
        connection = engine.connect()
        Session = sessionmaker(bind = CreateDatabase.engine)
        session = Session()
          
        self.engine = engine
        self.connection = connection
        self.session = session
        
        '''
        store dataframes here
        '''
        
        self.LongTimeSeries_Runs = {}      
        self.ShortTimeSeries_Runs = {}      
        self.Isolines_Runs = {}      
        self.HydroProfile_Runs = {}      

        
    
    def VariableID (self, var : str ):
        '''
        Function to return the ID of a specific variable as integer.
    
        Parameters
        ----------
        connection : sqlalchemy.engine.base.Connection
            DESCRIPTION.
        var : str
            The name of the variable whose ID will be retrieved.
    
        Returns
        -------
        ID : int
            the ID of a specific variable as integer.
        '''
        query = 'SELECT * FROM Variables'
        df = pd.read_sql(query, con = self.connection)
        ID = df [df.Name == var].ID.iloc[0]
        
        return ID
    
    def APIDate (self, MonitoringPointID : int):
        '''    
        Function to get the last date in the database and pass it as a searching mechanism to retrieve the API
        It returns the first date and the first timestamp to search in the API
        
        Parameters
        ----------
        connection : sqlalchemy.engine.base.Connection
        MonitoringPointID : int
    
        Returns
        -------
        first_t : pandas._libs.tslibs.timestamps.Timestamp
            The time stamp in a readable format
        first_ts : int
            Unix time stamp, also known as epoch.
        '''
        
        query = f'''
        SELECT * FROM PointsMeasurements 
        WHERE
            MonitoringPointID = {MonitoringPointID}    
        ORDER BY TimeStamp DESC LIMIT 1
        '''
    
        last_date_df = pd.read_sql(query, con = self.connection)
        try:
            last_ts = last_date_df.iloc[0,2]
            last_t = pd.to_datetime(last_ts * 1e9)
            
            first_t = last_t + timedelta(hours=1) #first time - adding an hour to last time saved
            first_ts = int(first_t.value / 1e9) #converting to timestamp
            return first_t, first_ts
        
        except Exception:
            first_t, first_ts = None, None
            return first_t, first_ts
    
    def StartEndDate ( self, limit = 50):
        '''    
        Function to get the start and end date of the database
        
        Parameters
        ----------
        limit: int , optional
            the number of entries that will be skiped
            this will help to avoid missing values from divers when querying isolines
        
        Returns
        -------
        t0: pandas._libs.tslibs.timestamps.Timestamp
            starting date
        t1: int
           ending date
        '''
        
        t0_q = '''SELECT 
                    TimeStamp FROM PointsMeasurements 
                ORDER BY
                    TimeStamp ASC LIMIT 1'''
        
        t1_q = f'''SELECT VariableID, TimeStamp FROM PointsMeasurements 
                WHERE
                    VariableID = 0
                ORDER BY
                    TimeStamp DESC LIMIT {limit}'''
        
        t0 = pd.read_sql(t0_q, con = self.connection).values[0][0]
        t1 = pd.read_sql(t1_q, con = self.connection).values[limit-1][1]
        
        t0 = pd.to_datetime(t0*1e9)
        t1 = pd.to_datetime(t1*1e9)
        
        return t0, t1    
    
    
    def UpdateID  (self):
        '''
        
        Function to get the last update from the PointsMeasurements table
        
        Parameters
        ----------
        connection : sqlalchemy.engine.base.Connection
    
        Returns
        -------
        update_id : int
            The next ID that will be used to update the table in the automatic functions
        '''
    
        last_id_query = 'SELECT ID FROM PointsMeasurements ORDER BY ID DESC LIMIT 1'
        update_id = pd.read_sql(last_id_query, con = self.connection).values[0][0] + 1
        return update_id    
    
    def MonitoringPointData (self, GageData : bool = None):
        '''
        Function to retrieve information about all the monitoring points

        Parameters
        ----------
        GageData : bool, optional
            DESCRIPTION. The default is None.
            If True, it saves as a class attribute only the Gage Data

        Returns
        -------
        MonitoringPointData_df : pandas.core.frame.DataFrame
            Dataframe containing data concerning all the Monitoring Points.
        '''
    
    
        query = '''
        SELECT 
            MonitoringPoints.ID as MonitoringPointID, MonitoringPoints.PointID,	MonitoringPoints.Name as MonitoringPointName,
            MonitoringPoints.ReferenceAltitude, MonitoringPoints.Type, MonitoringPoints.TypeOfAltitude,
            Points.ID as PointsID, Points.E, Points.N
        FROM
            MonitoringPoints
        JOIN
            Points ON MonitoringPoints.PointID = Points.ID
        ''' 
        df = pd.read_sql(query, con = self.connection)
        
        # df = df.iloc[:]
        
        if GageData:
            self.MonitoringPointData_df = df
            gage_df = df [ df.Type == 'River Gage'].reset_index (drop = 1)
            self.GageData = gage_df
        else: 
            self.MonitoringPointData_df = df
        return df
    
    def DiverData (self, SensorName : str):
        '''
        Get class method to retrieve sensor data
    
        Parameters
        ----------
        SensorName : str
    
        Returns
        -------
        DiverData_df : pandas.core.frame.DataFrame
            Dataframe to merge well and diver data
    
        '''
    
        # transfer the data 
        #getting the information for the diver
        diver_query = f'''
        SELECT 
         	WellDiver.ID, WellDiver.DiverID, WellDiver.MonitoringPointID, WellDiver.DiverDepth, WellDiver.MonitoringPointName,
         	Divers.ID AS DiversID , Divers.Name AS DiversName,
         	MonitoringPoints.ID, MonitoringPoints.ReferenceAltitude, MonitoringPoints.Depth
        FROM
         	WellDiver
        JOIN
         	Divers ON WellDiver.DiverID = Divers.ID
        JOIN 
         	MonitoringPoints ON WellDiver.MonitoringPointID = MonitoringPoints.ID
        WHERE
         	DiversName = '{SensorName}'
        ''' 
    
    
        diver_df = pd.read_sql(diver_query, con = self.connection)
        #getting the well where the diver is installed
        MonitoringPointID = diver_df.MonitoringPointID.values[0]
        MonitoringPointName = diver_df.MonitoringPointName.values[0]
        DiverDepth = diver_df.DiverDepth.values[0]
        ReferenceAltitude = diver_df.ReferenceAltitude.values[0]
        WellDepth = diver_df.Depth.values[0]
        
        DiverData_df = pd.DataFrame( {'MonitoringPointID' : [MonitoringPointID],
                            'MonitoringPointName' : [MonitoringPointName], 
                            'DiverDepth' : [DiverDepth], 
                            'ReferenceAltitude' : [ReferenceAltitude], 
                            'WellDepth' : [WellDepth]})
        
        return DiverData_df
    
    def DiverStatus (self):
        '''
        Get class method 
        
        Parameters
        -------
            None. It just requires the Get class to be instantiated.
            
        Returns
        -------
        df : pandas.core.frame.DataFrame
            Dataframe joining divers, wells, drills and the current status with regards to the divers' last update.
        '''
        
    
        query = '''
        SELECT 
            MonitoringPoints.ID as MonitoringPointID, MonitoringPoints.PointID,	MonitoringPoints.Name as MonitoringPointName,
            MonitoringPoints.ReferenceAltitude, MonitoringPoints.Type, MonitoringPoints.TypeOfAltitude,
            WellDiver.ID, WellDiver.MonitoringPointID, WellDiver.DiverID,
            Divers.ID, Divers.Name as DiverName, Divers.IOT, Divers.Functioning,
            Points.ID as PointsID, Points.E, Points.N
        FROM
            MonitoringPoints
        JOIN
            WellDiver ON MonitoringPoints.ID = WellDiver.MonitoringPointID
        JOIN
            Divers ON WellDiver.DiverID = Divers.ID
        JOIN
            Points ON MonitoringPoints.PointID = Points.ID       
        '''
        df = pd.read_sql(query, con = self.connection).drop('ID', axis = 1)
        
        df = df.iloc[:,1:]
    
        #Get last date for the functioning divers
        t_list = []
        epoch_list = []  # number of seconds that have elapsed since January 1, 1970 (midnight UTC/GMT)
        
        for i in df.iterrows():
            row = i[1]
            t, ts = self.APIDate (row.MonitoringPointID)
            t_list.append(t)
            epoch_list.append(ts)
        
        df['NextUpdate_t'] = t_list
        df['NextUpdate_ts'] = epoch_list      
    
        self.DiverStatus_df = df
        return df
       
    def Table (self, TableName : str):
        '''
        Retrieves the entire raw table from database
        
        Parameters
        ----------
        TableName : str
        
        Returns
        -------
        df : pd.core.frame.DataFrame
            table
        '''
        
        q = f'SELECT * from {TableName}'
        df = pd.read_sql(q, con = self.connection)
        return df
        
    def CheckDuplicateEntry (self, MonitoringPointID : int, VariableID : int, df: pd.core.frame.DataFrame ):
        '''
        It checks duplicate entries in the PointsMeasurements table and drop these values
        
        Parameters
        ----------
        connection : sqlalchemy.engine.base.Connection
        MonitoringPointID : int
        VariableID : int
        df : pd.core.frame.DataFrame

        Returns
        -------
        df : pd.core.frame.DataFrame
            dataframe with less or equal number of rows than the input frame.
        '''
        
        # double check if there is not a duplicated entry
        # retrieve the database for that well and parameter
        check_query = f'''
        SELECT * FROM PointsMeasurements 
        WHERE
            MonitoringPointID = {MonitoringPointID}
            AND VariableID = {VariableID}
        '''
        
        check_df = pd.read_sql(check_query, con = self.connection)
        check_df ['keys'] = check_df.MonitoringPointID.astype ('str') + '_' + check_df.TimeStamp.astype('str') + "_" + check_df.VariableID.astype('str')
        df['TimeStamp'] = df['TimeStamp'].astype('int64')
        df['keys'] = df.MonitoringPointID.astype ('str') + "_" + df.TimeStamp.astype('str') + "_" + df.VariableID.astype('str')
        
        df = df [~df['keys'].isin(check_df['keys'])]
        
        df = df.drop ('keys', axis=1).reset_index(drop = 1)
        
        return df
    
    def LongTimeSeries (self, FilterVariableID : int):

        '''
        Long query for the PointsMeasurements. Query gets stored in the attribute Runs
        If the variable is run. It will be retrieved faster next time because it is store within a class attribute Runs : dict.

        Parameters
        ----------
        Get_ : 
            Get intance variable
        
        connection : sqlalchemy.engine.base.Connection
            
        FilterVariableID : int

        Returns
        -------
            Nothing. The resultant query is stored in a pandas.core.frame.DataFrame format as a class attribute.
        
        Examples
        -------   
        q = TimeSeriesLong (connection, 0) 
        df = q.DataFrame #Retrieving dataframe
                
        '''
            
        start_time = time.perf_counter()
        
        Runs_key = FilterVariableID
        
        if Runs_key not in self.LongTimeSeries_Runs:
            query = f'''
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
                VariableID = {FilterVariableID} '''
            
            
            DataFrame = pd.read_sql(query, con = self.connection)
            DataFrame = DataFrame.iloc[:,1:]
            DataFrame = DataFrame.loc[:, ~DataFrame.columns.duplicated()]
            DataFrame ['Date'] = pd.to_datetime(DataFrame.TimeStamp * 1e9)
            end_time = time.perf_counter()
            #store run in class dictionary
            self.LongTimeSeries_Runs [FilterVariableID] = DataFrame            
            self.LongTimeSeries_df = DataFrame
            self.RunTime = end_time - start_time
            
        else:                    
            self.LongTimeSeries_df = self.LongTimeSeries_Runs[Runs_key]
                
            
    def ShortTimeSeries (self, FilterVariableID : int, FilterMonitoringPoint : str):
        '''
        Query for the PointsMeasurements per well. The resultant query is stored in a pandas.core.frame.DataFrame format as a class attribute.

        Parameters
        ----------
        connection : sqlalchemy.engine.base.Connection
        FilterVariableID : int
        FilterMonitoringPoint : str

        Returns
        -------
            Nothing. The resultant query is stored in a pandas.core.frame.DataFrame format as a class attribute.

        '''
                        
        start_time = time.perf_counter()
        
        Runs_key = f'{FilterVariableID}_{FilterMonitoringPoint}' 
        
        if Runs_key not in self.ShortTimeSeries_Runs:
            query = f'''
            SELECT 
            	PointsMeasurements.ID, PointsMeasurements.MonitoringPointID, PointsMeasurements.TimeStamp, PointsMeasurements.VariableID, PointsMeasurements.Value,
            	MonitoringPoints.ID, MonitoringPoints.Name as MonitoringPointName, MonitoringPoints.PointID,
            	Points.ID, Points.E, Points.N
            FROM 
            	PointsMeasurements
            JOIN
            	MonitoringPoints ON PointsMeasurements.MonitoringPointID = MonitoringPoints.ID
            JOIN
            	Points ON MonitoringPoints.PointID = Points.ID
            WHERE
                VariableID = {FilterVariableID} AND MonitoringPoints.Name = '{FilterMonitoringPoint}' '''
            
            
            DataFrame = pd.read_sql(query, con = self.connection)
            DataFrame = DataFrame.iloc[:,1:]
            DataFrame = DataFrame.loc[:, ~DataFrame.columns.duplicated()]
            DataFrame ['Date'] = pd.to_datetime(DataFrame.TimeStamp * 1e9)
            
            cols = ['MonitoringPointID', 'MonitoringPointName' ,'TimeStamp', 'Date', 
                    'VariableID', 'Value', 'E', 'N']
            
            DataFrame = DataFrame [cols]
            
            end_time = time.perf_counter()
            #store run in class dictionary
            self.ShortTimeSeries_Runs [Runs_key] = DataFrame            
            self.ShortTimeSeries_df = DataFrame
            self.RunTime = end_time - start_time
            
        else:                    
            DataFrame = self.ShortTimeSeries_Runs[Runs_key]
            self.ShortTimeSeries_df = DataFrame

    
    def Isolines(self , Year, Month, Day, Hour):

        '''
        Query used to retrieve monitoring data for a given variable and time.
       

        Parameters
        ----------
        connection : sqlalchemy.engine.base.Connection
        Year : int
        Month : int
        Day : int
        Hour : int
        
        Returns
        -------
            Nothing. The resultant query is stored in a pandas.core.frame.DataFrame format as a class attribute.
        '''
    
        start_time = time.perf_counter()

        if Hour < 10:
            Hour = '0'+str(Hour)
    
        datetime = pd.to_datetime(f'{Year}-{Month}-{Day} {Hour}')
        
        l_t = datetime - timedelta (hours = 0.5)
        u_t = datetime + timedelta (hours = 0.5)
        
        l_ts = int(l_t.value / 1e9)
        u_ts = int(u_t.value / 1e9)
               
        #generating Key for the class dictionary
        Runs_key = str(datetime)

        
        if Runs_key not in self.Isolines_Runs:
            #START FROM HERE - LINE WHERE 99
            query = f'''
            SELECT 
            	PointsMeasurements.MonitoringPointID, PointsMeasurements.TimeStamp, PointsMeasurements.VariableID, PointsMeasurements.Value,
            	MonitoringPoints.ID, MonitoringPoints.Name as MonitoringPointName, MonitoringPoints.PointID, 
            	Points.ID, Points.E, Points.N, 
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
            
            '''
            query to retrieve more data and check wrong values that are requested from INOWAS api
            It reduces the number of row of the query because the join function cuts out rows that have no divers
            '''
            
            query_debug = f'''
            SELECT 
            	PointsMeasurements.MonitoringPointID, PointsMeasurements.TimeStamp, PointsMeasurements.VariableID, PointsMeasurements.Value,
            	MonitoringPoints.ID, MonitoringPoints.Name as MonitoringPointName, MonitoringPoints.PointID, MonitoringPoints.ReferenceAltitude as CaseTop, 
            	Points.ID, Points.E, Points.N, 
            	Variables.ID, Variables.Name AS Type,
            	WellDiver.DiverID, WellDiver.DiverDepth, WellDiver.MonitoringPointID AS MonitoringPointID2,
            	Divers.ID, Divers.Name as DiverName
            FROM 
            	PointsMeasurements
            JOIN
            	MonitoringPoints ON PointsMeasurements.MonitoringPointID = MonitoringPoints.ID
            JOIN
            	Points ON MonitoringPoints.PointID = Points.ID	
            JOIN	
            	Variables ON PointsMeasurements.VariableID = Variables.ID
            JOIN
            	WellDiver ON PointsMeasurements.MonitoringPointID = MonitoringPointID2
            JOIN
            	Divers ON WellDiver.DiverID = Divers.ID
            WHERE
                TimeStamp BETWEEN {l_ts} AND {u_ts}
            '''
            
            cols = ['MonitoringPointID', 'MonitoringPointName', 'Time', 'Type', 'Value', 'E', 'N']
            cols_debug = ['MonitoringPointID', 'MonitoringPointName', 'DiverName', 'Time', 'Type', 'CaseTop', 'DiverDepth', 'Value', 'E', 'N']
            
            '''
            change here once it's fixed
            '''
            DataFrame = pd.read_sql(query, con = self.connection)
            DataFrame = DataFrame [DataFrame.VariableID.isin([0,7])] #indexing head and raingage
            DataFrame['Time'] = pd.to_datetime(DataFrame.TimeStamp * 1e9)
            # indexing columns    
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

            end_time = time.perf_counter()
            self.RunTime = end_time - start_time
            self.Isolines_df = DataFrame
            self.datetime = datetime
            # self.VariableName = VariableName
            #adding run to class attribute
            self.Isolines_Runs [Runs_key] = DataFrame #store in class variable

        #conditional to retrieve dataframe from class attribute! it minimizes querying time
        else:
            #getting object's attributes
            self.Isolines_df = self.Isolines_Runs[Runs_key]           
    
    
    def HydroProfile (self):
        '''
        Long query for the hydrogeological profiles. They can be index by drill.

        Parameters
        ----------
        connection : sqlalchemy.engine.base.Connection

        Returns
        -------
            Nothing. The resultant query is stored in a pandas.core.frame.DataFrame format as a class attribute.

        '''
    
        start_time = time.perf_counter()

        
        if 'HydroProfile' in self.HydroProfile_Runs:
            self.HydroProfile_df = self.HydroProfile_Runs['HydroProfile']
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
            
            DataFrame = pd.read_sql(query, con = self.connection)
            cols = ['ID', 'PointID', 'DrillName', 'TestType','Unit', 'Depth', 'MonitoringPoint',
                    'Value', 'E', 'N']
            DataFrame = DataFrame[cols]

            end_time = time.perf_counter()
            self.RunTime = end_time - start_time
            self.HydroProfile_df = DataFrame
            self.HydroProfile_Runs ['HydroProfile'] = DataFrame #store in class variable

    



#Local tests
# if __name__ == '__main__':
        

        
    # engine, connection, session = u.DbCon(database_fn)
    
    
    # map_query = Isolines(connection,
    #                        # Variable = var_id,
    #                        Year = pd.to_datetime(date_wid).year,
    #                        Month = pd.to_datetime(date_wid).month,
    #                        Day = pd.to_datetime(date_wid).day,
    #                        Hour = pd.to_datetime(date_wid).hour)
        
    # map_df = map_query.DataFrame.reset_index(drop = True)    
    
    
    
    # map_query = Isolines(connection,
    #                         # Variable = var_id,
    #                         Year = pd.to_datetime(date_wid).year,
    #                         Month = pd.to_datetime(date_wid).month,
    #                         Day = pd.to_datetime(date_wid).day,
    #                         Hour = pd.to_datetime(date_wid).hour)
        
    # map_df = map_query.DataFrame.reset_index(drop = True)    