import os
from datetime import datetime, timedelta
import time
import requests
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import CreateDatabase as db
from sqlalchemy.orm import sessionmaker


def ControlPoints(n=18):
    '''
    Function to distribute fictious points in the river border and interpolate the levels
    Use n = 18 gives 18 points back. That is a perfect number.
    '''
    ControlPoint = [50.96454391, 13.92163433] #fictious point close to the site
    river_angle = 9.8 #angles with the east in degrees
    river_anglerad = river_angle * 2 * np.pi / 360 #angle in rad
    hypotenuse = 3e-4 #distance between points
    dx = np.cos(river_anglerad) * hypotenuse
    dy = np.sin(river_anglerad) * hypotenuse
    x = np.arange(ControlPoint[1], ControlPoint[1] + (n)*dx , dx)
    y = np.arange(ControlPoint[0], ControlPoint[0] + (n)*dy , dy)
    control_points_list = [[y[i],x[i]] for i,j in enumerate(x)]
    df = pd.DataFrame(control_points_list, columns = ['y', 'x'])
    return df

            


def GetDiverData (sensor, connection):
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
    
    return MonitoringPointID, MonitoringPointName, DiverDepth, ReferenceAltitude, WellDepth


def PrepareDiverData (connection, sensor, p, sts, ets, MonitoringPointID, ReferenceAltitude, DiverDepth, VariableID ):
    url = f'https://sensors.inowas.com/sensors/project/DEU1/sensor/{sensor}/parameter/{p}?timeResolution=RAW&dateFormat=epoch&start={sts}&end={ets}&gt=-100.0'
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
            
    #adding columns present in the database
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
        if row.keys in check_key: #if any row of the df is present already in the database, drop it
            df = df.drop( [index] , axis=0) 
        

    #Organize the df using this columns: MonitoringPointID, TimeStamp, VariableID, Value
    #still need to add the ID
    df = df[[ 'MonitoringPointID', 'TimeStamp', 'VariableID', 'Value']]
    
    df.Value = np.round(df.Value,2)
    
    return df


        
            
def LongUpdatePInw(database_fn, sensor, sts, ets, test : bool): 
    "Function to update Parameters from Inowas API"
    
    
    engine = create_engine("sqlite:///{}".format(database_fn), echo = False) #False to not show the output
    connection = engine.connect()
    t0 = time.perf_counter()
    
    #query the sensors available in the api
    request = requests.get('https://sensors.inowas.com/list').json()
    request_index = [ i for i in request if i['project'] == 'DEU1']
    sensors_df = pd.DataFrame(request_index)
 
    
    #INDEX PARAMETERS FROM DATABASE INSTEAD. LEAVE THERE ONLY PARAMETERS OF INTEREST THAT WILL BE ADDED        
    parameters_query = 'select Name from Variables'
    parameters_db = pd.read_sql(parameters_query, con = connection)
    parameters_df = sensors_df [ sensors_df.name == sensor].parameters.reset_index(drop=True)
    parameters = [i for i in parameters_df.values[0] if i in parameters_db.Name.values]
    
    # loop though each parameter of this sensor
    for p in parameters:        
        #getting the index for the variable name 
        vars_query = f"SELECT * FROM Variables WHERE Variables.Name = '{p}'"
        vars_df = pd.read_sql(vars_query, con = connection)
        VariableID = vars_df.ID.values[0]
        
        t1 = time.perf_counter() - t0
        MonitoringPointID, MonitoringPointName, DiverDepth, ReferenceAltitude, WellDepth = GetDiverData(sensor, connection)
        print(f'\n\n\n Got diver data for sensor {sensor}, Well {MonitoringPointName}, parameter {p}, time = {round(t1)} s')
        
        t2 = time.perf_counter() - t0
        df = PrepareDiverData (connection, sensor, p, sts, ets, MonitoringPointID, ReferenceAltitude, DiverDepth, VariableID )
        print(f'\n\n\n Data Prepared for sensor {sensor}, Well {MonitoringPointName}, parameter {p}, time = {round(t2)} s')
        
        # return(df.columns)
        t3 = time.perf_counter() - t0
        InputDatabase(df, connection, test, db.PointsMeasurements)
        print (f"\n\n\n Database Updated, time = {round(t3)}' s")
    # return(parameters)



    
