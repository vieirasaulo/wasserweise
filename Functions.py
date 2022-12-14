import os

os.chdir('D:/Repos/PirnaCaseStudy/Database')

import requests
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
import sqlalchemy 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import numpy as np
import CreateDatabase as db
from datetime import timedelta
import time


def DbCon (database_fn):
    engine = create_engine("sqlite:///{}".format(database_fn), echo = False) #False to not show the output
    connection = engine.connect()
    base = declarative_base()
    Session = sessionmaker(bind = db.engine)
    session = Session()
      
    return engine, connection, base, session



class Handles:
    
    def __init__(self):
        self.instantiated = True
    
    def TimeToString (t: pd._libs.tslibs.timestamps.Timestamp):
        s = str(t)
        Y, m, d = s[:4], s[5:7], s[8:10]
        t = s[11:]
        T = f'{d}.{m}.{Y}T{t}'
        return T

    def GetMonitorintPointData (self, connection : sqlalchemy.engine.base.Connection):
        # transfer the data 
        #getting the information for the diver
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
        
        query_WithDivers = '''
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

        df = pd.read_sql(query, con = connection)
        df_ = pd.read_sql(query_WithDivers, con = connection).drop('ID', axis = 1)
        
        self.GageData = df [ df.Type == 'River Gage'].reset_index (drop = 1)
        
        self.MonitoringPoints_df = df
        
        self.PointsWithDivers_df = df_
        
        
        #Get last date for the functioning divers
        t_list = []
        epoch_list = []  # number of seconds that have elapsed since January 1, 1970 (midnight UTC/GMT)
        
        for i in df_.iterrows():
            row = i[1]
            t, ts = Handles.GetAPIDate (connection, row.MonitoringPointID.iloc[0])
            t_list.append(t)
            epoch_list.append(ts)
        
        df_['NextUpdate_t'] = t_list
        df_['NextUpdate_ts'] = epoch_list      

    
        self.DiversNextUpdate_df = df_
    
    
    def GetDivers (connection):
    
        request = requests.get('https://sensors.inowas.com/list').json()
        request_index = [ i for i in request if i['project'] == 'DEU1']
        SensorsAPI_df = pd.DataFrame(request_index)
     
        
        #INDEX PARAMETERS FROM DATABASE INSTEAD. LEAVE THERE ONLY PARAMETERS OF INTEREST THAT WILL BE ADDED        
        parameters_query = 'select * from Variables'
        parameters_db = pd.read_sql(parameters_query, con = connection)
        
        Sensors_df = pd.DataFrame()
        for i in SensorsAPI_df.iterrows():
            row = i[1]

            params = row['parameters']
            params = [i for i in params if i in parameters_db.Name.values]
            name = row['name']
            df_ = pd.DataFrame({'Name' : params, 'Diver' : name})
            Sensors_df = pd.concat([Sensors_df,df_])
        Sensors_df = Sensors_df.reset_index(drop = True)
        Sensors_df = pd.merge(Sensors_df, parameters_db[['ID', 'Name']], on = 'Name')
        Sensors_df.columns = ['VariableName', 'Diver', 'VariableID']
        
        return SensorsAPI_df, Sensors_df
    
    
    
    
    def GetDiverData (self, sensor, connection):
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
         	DiversName = '{sensor}'
        ''' 


        diver_df = pd.read_sql(diver_query, con = connection)
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
        
        self.DiverData = DiverData_df


        
    def CompleteMissingDates (df: pd.core.frame.DataFrame ):
        #drop missing values
        df = df.dropna()
        #round readings to hour
        df ['Time'] = pd.to_datetime(df.TimeStamp * 1e9)
        df.Time = df.Time.dt.round('h')
        
        #get the value measurement for that hour
        Values = df.groupby('Time').Value.mean()
        df = df.drop_duplicates('Time')
        df = df.drop('Value', axis = 1)
        
        df.loc [df ['Time'].isin ( Values.index), 'Value'] = Values.values
                
        #filling the missing dates readings with NAN
        timerange = pd.period_range(min(df.Time), max(df.Time), freq = 'H')
        timerange = timerange.to_timestamp()
        df = df.set_index ('Time')
        df = df.reindex(timerange, fill_value = np.nan)

        #rearranging dates and retrieving new series of timestamps
        df['Time'] = df.index
        df = df.reset_index (drop = True)
        df.TimeStamp = (df.Time.astype('int64') / 1e9)
        
        df['TimeStamp'] = pd.Series(df.TimeStamp, dtype='Int64')
        df['MonitoringPointID'] = pd.Series(df.MonitoringPointID, dtype='Int64')
        df['VariableID'] = pd.Series(df.VariableID, dtype='Int64')
        
        #fill missing values for absent dates
        df.MonitoringPointID = df.MonitoringPointID.fillna([i for i in df.MonitoringPointID.unique() if isinstance(i, np.int64)][0])
        df.VariableID = df.VariableID.fillna([i for i in df.VariableID.unique() if isinstance(i, np.int64)][0])
        df = df.drop('Time', axis = 1)
        
        return df

    
    def Process (df : pd.core.frame.DataFrame, connection : sqlalchemy.engine.base.Connection):
        df = Handles.CheckDuplicateEntry(connection = connection,
                                         MonitoringPointID = df.MonitoringPointID.unique()[0],
                                         VariableID = df.VariableID.unique()[0], df = df )
        try :
            df = Handles.CompleteMissingDates ( df = df)

        except Exception:
            df = df.copy()          
            
        update_id = Handles.GetUpdateID (connection = connection)        
        update_id = int(update_id)
        update_id = int(update_id) #update id for when there is data available

        df.insert (0, 'ID', np.arange(update_id, update_id + df.shape[0], 1)) 

        return df, update_id
    
    def GetVariableID (connection : sqlalchemy.engine.base.Connection, var : str ):
        query = 'SELECT * FROM Variables'
        df = pd.read_sql(query, con = connection)
        ID = df [df.Name == var].ID.iloc[0]
        
        return ID
        
    def CheckDuplicateEntry (connection : sqlalchemy.engine.base.Connection, MonitoringPointID : int, VariableID : int, df: pd.core.frame.DataFrame ):
        
        # double check if there is not a duplicated entry
        # retrieve the database for that well and parameter
        check_query = f'''
        SELECT * FROM PointsMeasurements 
        WHERE
            MonitoringPointID = {MonitoringPointID}
            AND VariableID = {VariableID}
        '''
        
        check_df = pd.read_sql(check_query, con = connection)
        check_df ['keys'] = check_df.MonitoringPointID.astype ('str') + '_' + check_df.TimeStamp.astype('str') + "_" + check_df.VariableID.astype('str')
        df['TimeStamp'] = df['TimeStamp'].astype('int64')
        df['keys'] = df.MonitoringPointID.astype ('str') + "_" + df.TimeStamp.astype('str') + "_" + df.VariableID.astype('str')
        
        df = df [~df['keys'].isin(check_df['keys'])]
        
        df = df.drop ('keys', axis=1).reset_index(drop = 1)
        
        return df
    
    def GetAPIDate ( connection : sqlalchemy.engine.base.Connection, MonitoringPointID : int):
        '''
        Function to get the last date in the database and pass it as a searching mechanism to retrieve the API
        It returns the first date and the first timestamp to search in the API
        '''
        
        query = f'''
        SELECT * FROM PointsMeasurements 
        WHERE
            MonitoringPointID = {MonitoringPointID}    
        ORDER BY TimeStamp DESC LIMIT 1
        '''
        
        
        last_date_df = pd.read_sql(query, con = connection)
        last_ts = last_date_df.iloc[0,2]
        last_t = pd.to_datetime(last_ts * 1e9)
        
        first_t = last_t + timedelta(hours=1) #first time - adding an hour to last time saved
        first_ts = int(first_t.value / 1e9) #converting to timestamp
        
        return first_t, first_ts
        

    
    def GetUpdateID  (connection : sqlalchemy.engine.base.Connection):
        last_id_query = 'SELECT ID FROM PointsMeasurements ORDER BY ID DESC LIMIT 1'
        update_id = pd.read_sql(last_id_query, con = connection).values[0][0] + 1
        
        return update_id   
    
    
class LongUpdateDiverData (Handles):
    
    '''
    Class with functions to update Diver Data per sensor and per parameter
    Because getting diver data can be tricky, The update here is not fully automatic. 
    We need to read the dates in DiversLastUpdate_df before we update
    That is to give more ability to fix errors in jupyter notebooks
    '''
    
    
    def __init__ (self, handles_, sensor : str, connection  : sqlalchemy.engine.base.Connection):
            
        self.DiverData = handles_.DiverData           
        
        SensorsAPI_df, Sensors_df  = Handles.GetDivers (connection)
        
        parameters = Sensors_df [Sensors_df['Diver'] == sensor]

        self.sensors = Sensors_df
        self.parameters = parameters
        self.connection = connection
        

    def Request(self, sensor, parameter : str, sts : int, ets : int):
        
        
        url = f'https://sensors.inowas.com/sensors/project/DEU1/sensor/{sensor}/parameter/{parameter}?timeResolution=RAW&dateFormat=epoch&start={sts}&end={ets}&gt=-100.0'
        r = requests.get(url).json()
        
        df = pd.DataFrame(r)
        try :
            df.columns = ['TimeStamp', 'Value']
            
            df ['MonitoringPointID'] = self.DiverData['MonitoringPointID'].iloc[0]
            df ['VariableID'] = self.parameters [self.parameters.VariableName == parameter].VariableID.iloc[0]
            
            df = df [['MonitoringPointID','TimeStamp', 'VariableID', 'Value']]
            
            ReferenceAltitude = self.DiverData.ReferenceAltitude.iloc [0]
            DiverDepth = self.DiverData.DiverDepth.iloc [0]
            
            if parameter == 'h_level':
                head = ReferenceAltitude - DiverDepth + df.Value
                df = df.drop('Value', axis=1)
                df['Value'] = head
                        
            self.Request_df = df
            self.sensor = sensor
            self.parameter = parameter
        
        except Exception:
            print('\nNo data retrieved')
            self.Request_df = None
        
    def Process (self):
        
        if self.Request_df is None:
            self.Process_df =  None
        else:
            df = self.Request_df
            df, update_id = Handles.Process(df, connection = self.connection)        
            self.Process_df =  df
        
        
    def Update (self):
        
        if self.Process_df is not None:
            self.Process_df.to_sql(name="PointsMeasurements", con= self.connection, if_exists="append", index=False)
            print (f'Diver data updated from ID {self.Process_df.iloc[0,0]} to ID {self.Process_df.iloc[-1,0]}')
        else:     
            print ('Diver data is up-to-date')

        
class UpdateRiverData (Handles):
    
    '''
    Fully automated update of diver data    
    '''
    
    def __init__ (self, handles_, connection  : sqlalchemy.engine.base.Connection):
        
        #import instance variables to this class
        self.GageData = handles_.GageData
               
        GageID = self.GageData.MonitoringPointID.iloc[0]
        
        t0, ts0 = Handles.GetAPIDate (connection = connection, MonitoringPointID = GageID)
        
        t0 = Handles.TimeToString(t0)
        t1 = Handles.TimeToString(pd.to_datetime(datetime.now()).round('s'))
        
        parameter = f'&loadStartDate={t0}%2B0200&loadEndDate={t1}%2B0200'
        url = f'https://api.pegelalarm.at/api/station/1.0/a/saulo_filho_tudresden/height/501040-de/history?granularity=hour&{parameter}'
        
        self.url = url
        self.connection = connection
           
    def Request(self):
        #get data from API and return a data frame
        r = requests.get(self.url)
        data_dict = r.json()['payload']['history']
        df = pd.DataFrame(data_dict)
        df.sourceDate = df.sourceDate.str.split('+', expand = True)[0]
        df['Time'] = pd.to_datetime(df['sourceDate'], dayfirst = True)
        df.columns = ['Value' , 0, 'Time']
        
        df['TimeStamp'] = np.round(df.Time.astype('int64') / 1e9)
        df ['VariableID'] = Handles.GetVariableID(connection = self.connection, var = 'Rh')
        df ['MonitoringPointID'] = self.GageData.MonitoringPointID.iloc[0]
        
        df = df [['MonitoringPointID','TimeStamp', 'VariableID', 'Value']]
        
        river_head = self.GageData.ReferenceAltitude.iloc[0] + df.Value / 100 #convert from cm to m
        df['Value'] = river_head
        
        self.Request_df = df
       
    
    def Process (self):
                
        df = self.Request_df 
        df, update_id = Handles.Process(df, connection = self.connection)          
        self.Process_df = df      
            
    def Update (self):
        
        if self.Process_df.shape[0]>0:
            self.Process_df.to_sql(name="PointsMeasurements", con= self.connection, if_exists="append", index=False)
            print (f'River data updated from ID {self.Process_df.iloc[0,0]} to ID {self.Process_df.iloc[-1,0]}')
        else:     
            print ('River data is up-to-date')
        
        

database_fn = 'd:/repos/pirnacasestudy/data/database.db'
fn = 'LOG_UPDATE.txt' 

def RiverAPItoSQL (database_dn = database_fn):
    if fn in os.listdir():
        with open(fn, 'a+') as f:
            f.write('\n\n\n\n\n\n\n')
    with open(fn, 'a+') as f:
        
        t0 = time.perf_counter()
        f.write('*************************************NEW RUN PEGELALARM.AT*************************************') 
        now = datetime.now()
        txt = f'\n\nProgram run on the following date: {now}'
        print(txt)
        f.write(txt)
        engine, connection, base, session = DbCon(database_fn)
        handles = Handles()
        handles.GetMonitorintPointData(connection = connection)
        api = UpdateRiverData(handles, connection)
        api.Request( )
        api.Process( )
        api.Update( )
        t1 = time.perf_counter()      
        
        txt = f"\n\nEnd of the update for PEGELALARM.AT. The running time was {round(t1-t0)} s"
        print (txt)
        f.write(txt)
        txt = "\n\n#####################################END PEGELALARM.AT######################################"
        print (txt)
        f.write(txt)     

def SequenceUpdate (sensor, sts, connection, handles, database_fn = database_fn,): 
    with open(fn, 'a+') as f:
        t0 = time.perf_counter()
        handles.GetDiverData(sensor = sensor, connection = connection)
        api  = LongUpdateDiverData(handles, sensor, connection = connection)
        ets = round(pd.to_datetime(datetime.now()).value / 1e9)
        for p in api.parameters.VariableName:
            t0 = time.perf_counter()
            api.Request(sensor, p, sts, ets)
            api.Process()
            if api.Process_df is None:
                t1 = time.perf_counter()
                last_update = pd.to_datetime(sts * 1e9) - pd.Timedelta(1, unit="h")
                txt = f'\nNo data for sensor {sensor} and parameter {p}. Last update was: {last_update}. Check the portal of UIT. Running time was in {round(t1-t0)} s'
                print (txt)
                f.write (txt)
            else:
                try: 
                    api.Update()
                    t1 = time.perf_counter()
                    txt = f'\nRiver data updated from ID {api.Process_df.iloc[0,0]} to ID {api.Process_df.iloc[-1,0]} for sensor {sensor} parameter {p} in {round(t1-t0)} s'
                    print (txt)    
                    f.write (txt)
                except Exception:
                    txt = f"\nFor a reason it didn't run for sensor {sensor} and parameter {p}. It could be that it is updated "
                    print (txt)    
                    f.write (txt)
        txt = f"\n\n End of Update for sensor {sensor}"
        print (txt)    
        f.write (txt)
           
    
def InowasLongAPItoSQL (database_fn = database_fn):
    t0 = time.perf_counter()
    engine, connection, base, session = DbCon(database_fn)
    h = Handles ()
    SensorsAPI_df, Sensors_df = Handles.GetDivers(connection)
    h.GetMonitorintPointData (connection)
    DiversNextUpdate_df = h.DiversNextUpdate_df 
    FunctioningDivers_df = DiversNextUpdate_df  [(DiversNextUpdate_df .IOT == 1) & (DiversNextUpdate_df.Functioning ==1)].reset_index (drop = True)
    
    if fn in os.listdir():
        with open(fn, 'a+') as f:
            f.write('\n\n\n\n\n\n\n')
    with open(fn, 'a+') as f:
        f.write('*************************************NEW RUN INOWAS*************************************')    
        now = datetime.now()
        txt = f'\n\nProgram run on the following date: {now}'
        print(txt)
        f.write(txt)
        
    for i in (FunctioningDivers_df.iterrows()):
        row = i[1]
        sensor, sts = row.DiverName, row.NextUpdate_ts
        SequenceUpdate (sensor, sts, connection, handles = h )
    
    t1 = time.perf_counter()
    with open(fn, 'a+') as f:
        txt = "\n#####################################END INOWAS######################################"
        print (txt)
        f.write(txt)
        txt = f"\nThe TOTAL for Diver's update running time was {round(t1-t0)} s"
        print (txt)
        f.write(txt)
    
if __name__ == '__main__':
    RiverAPItoSQL()
    InowasLongAPItoSQL (database_fn = database_fn)
    
