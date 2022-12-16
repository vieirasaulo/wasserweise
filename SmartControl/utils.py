import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy 
from sqlalchemy.orm import sessionmaker
import numpy as np
import CreateDatabase as db
import queries as q



def TimeToString (t: pd._libs.tslibs.timestamps.Timestamp):
    '''
    convert pandas timestamp to string to be passed into the pegel api 
    
    Parameters
    ----------
    t : pd._libs.tslibs.timestamps.Timestamp
        DESCRIPTION.

    Returns
    -------
    T : TYPE
        DESCRIPTION.

    '''
    s = str(t)
    Y, m, d = s[:4], s[5:7], s[8:10]
    t = s[11:]
    T = f'{d}.{m}.{Y}T{t}'
    
    return T

def DbCon (database_fn : str):
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
    Session = sessionmaker(bind = db.engine)
    session = Session()
      
    return engine, connection, session

       
       
def CompleteMissingDates (df: pd.core.frame.DataFrame ):
    '''
    Fill time gaps with NAN for hourly data from unix time stamp column
    Requirements 
        Column names should match the database's.
        
        'TimeStamp' as integer for the time column
        'Value'
        'MonitoringPointID' 
        'VariableID'

    Parameters
    ----------
    df : pd.core.frame.DataFrame
        request from the api

    Returns
    -------
    df : pd.core.frame.DataFrame
        file almost ready to be pushed to the database
    '''
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

def Process (df : pd.core.frame.DataFrame, Get_ ) :
    
    '''
    Function that process the input dataframe and prepare it to be inputed in the PointsMeasurements table
    It first deployes the CheckDuplicateEntry function and checks if there is any duplicate entry 
    It uses the CompleteMissingDates and fill gaps with NAN
    
    
    '''  
    if df is None : #if the requested_df is None than the process_df is also none
        return None
    else:
        df = Get_.CheckDuplicateEntry(MonitoringPointID = df.MonitoringPointID.unique()[0],
                                 VariableID = df.VariableID.unique()[0],
                                 df = df )
        try :
            df = CompleteMissingDates ( df = df)
    
        except Exception:
            df = df.copy()          
            
        update_id = Get_.UpdateID ()        
        update_id = int(update_id)
        update_id = int(update_id) #update id for when there is data available
    
        df.insert (0, 'ID', np.arange(update_id, update_id + df.shape[0], 1)) 
    
        return df
        
    

    

    

    