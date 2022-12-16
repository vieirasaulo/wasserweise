import os
from datetime import datetime, timedelta
import time
import requests
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import CreateDatabase as db
from sqlalchemy.orm import sessionmaker




#automatic update for the last 15 days - use the last date here

def UpdateInwP(database_fn): 
    "Function to update Parameters from Inowas API"
    
    
    engine = create_engine("sqlite:///{}".format(database_fn), echo = False) #False to not show the output
    connection = engine.connect()
    start_time = time.perf_counter()
    
    
    
    #query the sensors available in the api
    request = requests.get('https://sensors.inowas.com/list').json()
    request_index = [ i for i in request if i['project'] == 'DEU1']
    sensors_df = pd.DataFrame(request_index)
 
    
        
    #loop through sensors
    i = 0
    j = 0
    for sensor in sensors_df.name.unique(): 
        sensor = 'I-2' #delete here
        
        
        '''
        INDEX PARAMETERS FROM DATABASE INSTEAD. LEAVE THERE ONLY PARAMETERS OF INTEREST THAT WILL BE ADDED        
        '''
        
        
        
        parameters = sensors_df [ sensors_df.name == sensor].parameters
        #loop though each parameter of this sensor
        for p in parameters.values[0]:        
            p = 'h_level'
            
            #getting the index for the variable name 
            vars_query = f"SELECT * FROM Variables WHERE Variables.Name = '{p}'"
            vars_df = pd.read_sql(vars_query, con = connection)
            VariableID = vars_df.ID.values[0]
            
            
            #transfer the data 
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
            #read the last date in the table for each one of the sensors when this parameter was updated
            
            last_date_query = f'''
            SELECT * FROM PointsMeasurements 
            WHERE
            	MonitoringPointID = {MonitoringPointID}
            
            ORDER BY TimeStamp DESC LIMIT 1
            '''
            
            
            last_date_df = pd.read_sql(last_date_query, con = connection)
            last_ts = last_date_df.iloc[0,2]
            last_t = pd.to_datetime(last_ts * 1e9)
            
            first_t = last_t + timedelta(hours=1) #first time - adding an hour to last time saved
            first_ts = int(first_t.value / 1e9) #converting to timestamp
            
            last_id_query = 'SELECT ID FROM PointsMeasurements ORDER BY ID DESC LIMIT 1'
            last_id = pd.read_sql(last_id_query, con = connection).values[0][0]
        
            #request this data from INOWAS API and store in a dataframe
            
            url = f'https://sensors.inowas.com/sensors/project/DEU1/sensor/{sensor}/parameter/{p}?timeResolution=RAW&dateFormat=epoch&start={first_ts}&gt=-100.0'
        
            
            r = requests.get(url).json()
            
            df = pd.DataFrame(r)
            df.columns = ['TimeStamp', 'Value']
            
            
            #round readings to hour
            df ['Time']= pd.to_datetime(df.TimeStamp * 1e9)
            df.Time = df.Time.dt.round('h')
            
            #get the value measurement for that hour
            Values = df.groupby('Time').Value.mean()
            df = df.drop_duplicates('Time')
            df = df.drop('Value', axis = 1)
            df.loc [df.Time == Values.index , 'Value'] = Values.values
            
            #filling the missing dates readings with NAN
            
            timerange = pd.period_range(min(df.Time), max(df.Time), freq = 'H')
            timerange = timerange.to_timestamp()
            
            df = df.set_index ('Time')
            
            df = df.reindex(timerange, fill_value = np.nan)
            
            #rearranging dates and retrieving new series of timestamps
            df['Time'] = df.index
            df = df.reset_index (drop = True)
            df.TimeStamp = df.Time.astype('int64') / 1e9
                        

            
            #Convert diver readings to head measurement
            if p == 'h_level':
                head = ReferenceAltitude - DiverDepth + df.Value
                df = df.drop('Value', axis=1)
                df['Value'] = head
            
            
            df['MonitoringPointID'] = MonitoringPointID
            df['VariableID'] = VariableID
            
            # double check if there is not a duplicated entry
            # retrieve the database for that well and parameter
            check_query = f'''
            SELECT * FROM PointsMeasurements 
            WHERE
            	MonitoringPointID = {MonitoringPointID}
                AND VariableID = {VariableID}
            '''
            check_df = pd.read_sql(check_query, con = connection)
            check_key = check_df.MonitoringPointID.astype ('str') + '_' + check_df.TimeStamp.astype('str') + "_" + check_df.VariableID.astype('str')
            df['keys'] = df.MonitoringPointID.astype ('str') + "_" + df.TimeStamp.astype('str') + "_" + df.VariableID.astype('str')
            
            
            i = 0
            for row in df.iterrows():
                index = row[0]
                row = row[1]
                if row.keys in check_key: 
                    df = df.drop( [index] , axis=0)
                    
            
                    
            df['ID'] = np.arange(last_id + 1, last_id+1 + df.shape[0], 1)
            
            #Organize the df using this columns: ID, MonitoringPOintID, TimeStamp, VAriableID, Value
            df = df[[ 'ID', 'MonitoringPointID', 'TimeStamp', 'VariableID', 'Value']]
            

              
                
            # pd.to_datetime(f '{df.Time.dt.year}-{df.Time.dt.month}-{df.Time.dt.day}')
            # 
            
            #value converted

            
            return df
            
            j += 1
            if j>0: break
            
            
        i += 1
        if i>0:
            break
            