'''
Module where functions for the general functioning of the platform are hosted
'''

if __name__ == '__main__':
    
    '''
    Enabling execution as __main__
    '''
    import os
    os.environ["GIT_PYTHON_REFRESH"] = "quiet"
    import git
    repo = git.Repo('.', search_parent_directories=True)
    os.chdir(repo.working_tree_dir)


'''
Importing modules and libraries
'''

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np
import SMARTControl.queries
import holoviews as hv
from scipy.interpolate import griddata
import xarray as xr
import geopandas as gpd
import folium
from pyproj import Geod
import json
import matplotlib.pyplot as plt
import geojsoncontour
import panel as pn
from datetime import datetime
import time

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
    Function that returns important variables to connect to the database using sqlalchemy API

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
    Session = sessionmaker(bind = engine)
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

def Process (df : pd.core.frame.DataFrame, Get_ : SMARTControl.queries.Get) :
    '''
    Function that process the input dataframe and prepare it to be appended to the PointsMeasurements table.  It first deploys the CheckDuplicateEntry function and checks if there is any duplicate entry , and then deploys the CompleteMissingDates function to fill gaps with numpy.nan.
    
    Parameters
    ----------
    df : pd.core.frame.DataFrame
    Get_ : SMARTControl.queries.Get

    Returns
    -------
    df : pd.core.frame.DataFrame
        file ready to be pushed to the database
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
        
def ControlPoints(n=18):
    '''
    Function to distribute fictious points in the river border and interpolate the levels
    Use n = 18 gives 18 points back. That is a perfect number.
    

    Parameters
    ----------
    n : int, optional
         The default is 18.

    Returns
    -------
    Control_df : pandas.core.frame.DataFrame
        Coordinates of the points that will be deployed in the boundary condition.
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
    Control_df = pd.DataFrame(control_points_list, columns = ['N', 'E'])
    return Control_df


def BoundaryCondition (Isolines_df, Control_df):
    '''
    Function to add the River head boundary to the Isolines query
    
    Parameters
    ----------
    Isolines_df : pandas.core.frame.DataFrame
        
    Control_df : pandas.core.frame.DataFrame
        
    Returns
    -------
    Isolines_Boundary_df : TYPE
        It returns the DataFrame isolines with the river head boundary included.

    '''
    cols = [col for col in Isolines_df.columns if col not in Control_df.columns]
    for col in cols:
        Control_df [col] = Isolines_df [Isolines_df.MonitoringPointID == 30][col].iloc[0]
    Isolines_df_ = Isolines_df [ Isolines_df['Type'] != 'Rh']
    Isolines_Boundary_df = pd.concat([Isolines_df_,Control_df])    
     
    return Isolines_Boundary_df

def LinearInterpolation (DataFrame : pd.core.frame.DataFrame , Longitude : str , Latitude : str):
    #Linear interpolation
    df = DataFrame.copy()
    points = np.array(df[[ Longitude , Latitude]])
    values = np.array(df.Value)
    minx, maxx = df.Lon.min(), df.Lon.max()
    miny, maxy =  df.Lat.min(), df.Lat.max()

    #improve method to determine the resolution dx = dy
    grid_x, grid_y = np.mgrid[minx:maxx:64j, miny:maxy:50j]
    grid_z = griddata(points, values, (grid_x, grid_y), method='linear')

    return grid_x, grid_y, grid_z

def Gradient (grid_x, grid_y, grid_z):
    '''
    Function to find the gradient of the potentiometric surface.

    Parameters
    ----------
    grid_x:  np.ndarray
    grid_y:  np.ndarray
    grid_z:  np.ndarray 
   
    Returns
    -------
    u: np.ndarray 
    v: np.ndarray 
    mag: np.ndarray 
    angle: np.ndarray 
    '''

    
    #gradient function
    PixelXSize = grid_x[:,0][0] - grid_x[:,0][1]
    PixelYSize = grid_y[:,0][0]- grid_y[:,1][0]
    PixelSize = np.mean([PixelXSize, PixelYSize])
    u , v = np.gradient(grid_z, PixelSize)
    mag = np.sqrt(u**2 + v**2)
    angle = (np.pi/2.) - np.arctan2(u/mag, v/mag)
    
    return u , v , mag, angle

def FixOutliers (Get_, threshold : int = 108):
    '''
    Function to reset outliers based on threshold. From quick analysis, when the diver depth is 12.4 in the Pirna Test site. The best is threshold is 108. The ouliers are values below what is expect and are obtained when the divers are exposed to the atmospheric pressure. In other words, when they are removed from the well and the reading is transmitted to the database.

    Parameters
    ----------
    Get_ : TYPE
        Parameter with connectiong.
    threshold : TYPE, optional
        DESCRIPTION. The default is 106 : int.

    Returns
    -------
    None.

    '''
    
    conn = Get_.connection    
    statement = f'''
    UPDATE PointsMeasurements
    SET   Value = NULL
    WHERE Value < {threshold}	
    '''
    conn.execute(statement)
    
    print('Update successfully executed')
    
    conn.close()


def FixValueByDate (Get_, MonitoringPointName , 
                    LowerBoundaryDate : pd._libs.tslibs.timestamps.Timestamp,
                    UpperBoundaryDate : pd._libs.tslibs.timestamps.Timestamp):
    '''
    Function to replace value to null using date interval.

    Parameters
    ----------
    Get_ : TYPE
        Parameter with connectiong.
    threshold : TYPE, optional
        DESCRIPTION. The default is 106 : int.

    Returns
    -------
    None.

    '''
    lts = int(int(LowerBoundaryDate.to_numpy()) / 1e9)
    uts = int(int(UpperBoundaryDate.to_numpy()) / 1e9)   
    
    Get_.MonitoringPointData()
    df = Get_.MonitoringPointData_df.copy()
    
    ID = df [df.MonitoringPointName == MonitoringPointName].MonitoringPointID.values[0]
    
    conn = Get_.connection    
    statement = f'''
    UPDATE PointsMeasurements
    SET Value = Null
    WHERE
    	MonitoringPointID = {ID} and TimeStamp BETWEEN {lts} and {uts}
    '''
    conn.execute(statement)
    
    print('Update successfully executed')
    
    fn = 'Data/LOG_UPDATE.txt' 
    txt = f'''
    \n\n\n\n\n
    *************************************Editting Database************************************* 
    
    MonitoringPoint ID = {ID} and Name = {MonitoringPointName} from date {LowerBoundaryDate} to {UpperBoundaryDate}
    time stamp {lts} to {uts} were set to Null at: {str(datetime.now())}

    
    \n\n\n\n\n
    *******************************************End*********************************************
    '''
    
    with open (fn , '+a') as f:
        f.write(txt)
        print(txt)
    conn.close()


class PrepareIsolines (SMARTControl.queries.Get):
    '''
    Old and inactive class
    '''

    def DataFrame (self, date_wid):
        '''
        Input with date_widget
        
        '''
                
        self.Isolines(Year = pd.to_datetime(date_wid).year,
                                  Month = pd.to_datetime(date_wid).month,
                                  Day = pd.to_datetime(date_wid).day,
                                  Hour = pd.to_datetime(date_wid).hour)
        
        
        
        map_df = self.Isolines_df.reset_index(drop = True)     
        df_ = ControlPoints()
        df = map_df.copy()
    
        df = BoundaryCondition(map_df, df_)
        
        df['Lon'], df ['Lat'] = hv.util.transform.lon_lat_to_easting_northing(df.E, df.N)
        if df [ ~ df.Value.isna()].shape[0] == 0 : #if every value is na we fill everything
            df = df.fillna(9999) # Improve this in the future
        
        self.Isolines_df = df
        self.date_wid = date_wid
        
        return df 

    def DataSet (self):
        
        df = self.Isolines_df.copy()
        
        grid_x, grid_y, grid_z = LinearInterpolation (df, 'Lon', 'Lat')
        
        u , v , mag, angle = Gradient (grid_x, grid_y, grid_z)
        
        #dataset
        ds =xr.Dataset(
            data_vars = dict (
                head = (['x','y'], grid_z),
                mag = (['x', 'y'], mag),
                angle =  (['x', 'y'], angle),
                ),
            coords = dict (
                Lon = (['x','y'], grid_x),
                Lat = (['x','y'], grid_y)
            )
        )
        return ds


text =  pn.pane.Markdown ('''
        # <center>Not enough data on this date</center>
        <br>
        ''',align = 'center', style = {'font-size' : '1.5em'})



def prepare_query (Get_ : SMARTControl.queries.Get, date_wid , crs_gcs : int = 4326):
    '''
    Function to interpolate data the cubic method and find the gradient of the potentiometric surface. 

    Parameters
    ----------
    Get_: SMARTControl.queries.Get
    crs_gcs = 4326 : int
    date_wid 
        date read from the dashboard widget
    
    Returns
    -------
    map_gdf : geopandas.geodataframe.GeoDataFrame 
    river_gage_gdf : geopandas.geodataframe.GeoDataFrame 
    '''
    
    if isinstance(date_wid, str):
            
        Get_.Isolines(Year = pd.to_datetime(date_wid).year,
                                  Month = pd.to_datetime(date_wid).month,
                                  Day = pd.to_datetime(date_wid).day,
                                  Hour = pd.to_datetime(date_wid).hour)
    else:
       try: 
           Get_.Isolines(Year = date_wid.year,
                         Month = date_wid.month,
                         Day = date_wid.day,
                         Hour = date_wid.hour)
       except Exception:
           Get_.Isolines(Year = date_wid.dt.year,
                         Month = date_wid.dt.month,
                         Day = date_wid.dt.day,
                         Hour = date_wid.dt.hour)
           
       
    
    df = Get_.Isolines_df.copy()
    
    river_gage_df = df.sort_values(by = 'E' , ascending = False).iloc[:1,:]
    
    if df.shape[0] < 3 :
        return text
    else:
        try : 
            df = df.dropna()
            df = df.dropna()
            df_ = ControlPoints()
            df = BoundaryCondition(df, df_).reset_index(drop = True)
            
            # Taking average values for the clustered GWM wells
            # df.loc [df.MonitoringPointName.str.len()>4 , 'cut'] = 1
            # df.loc [df.MonitoringPointName.str.len() <= 4 , 'cut'] = 0
            # gwms_mean = df[df.cut == 1].Value.mean()
            # df = df [~ df.index.isin (df[df.cut == 1].index[1:])]
            # df.loc [df.cut == 1, 'Value'] = gwms_mean
            # df = df.drop('cut', axis =1)
            
            #Removing GWM05, 03 and G21neu - Values are weird
            df = df.loc [df.MonitoringPointName != 'GWM05']
            df = df.loc [df.MonitoringPointName != 'GWM03']
            df = df.loc [df.MonitoringPointName != 'G21neu']
            
            map_df = df.copy()
            map_gdf = gpd.GeoDataFrame(map_df, geometry = gpd.points_from_xy (map_df.E, map_df.N), crs = crs_gcs).reset_index(drop = True)
            river_gage_gdf = gpd.GeoDataFrame(river_gage_df,
                                       geometry = gpd.points_from_xy (river_gage_df.E, river_gage_df.N),
                                       crs = crs_gcs
                                       ).reset_index(drop = True)
            
            return map_gdf , river_gage_gdf
        
        except ValueError:
            
            return text
        


def Interpolation_Gradient (map_gdf : gpd.geodataframe.GeoDataFrame , crs_utm : int = 25833, pixel_size : int = 20):
    '''
    Function to interpolate data the cubic method and find the gradient of the potentiometric surface. 

    Parameters
    ----------
    map_gdf : gpd.geodataframe.GeoDataFrame
    crs_utm = 25833 : int 
    pixel_size = 20 : int
   
    Returns
    -------
    grid_x_gcs: numpy.ndarray 
    grid_y_gcs: numpy.ndarray 
    grid_z_utm: numpy.ndarray 
    U: numpy.ndarray 
    V: numpy.ndarray 
    '''
    
    try:
        # 1. convert it to utm to get a real gradient
        map_gdf = map_gdf.to_crs(crs_utm)
        
        # 2. Linear interpolation 
        # 2.1 fetching converted points
        points_utm = np.array( pd.DataFrame ( 
                        {
                            'x' : map_gdf.geometry.x ,
                            'y' : map_gdf.geometry.y
                        }
                                     )
                     )
      
        
        # 2.2 Fetching values
        values = np.array(map_gdf.Value)
        
        # 2.3 
        # grid utm
        minx, maxx = map_gdf.geometry.x.min(), map_gdf.geometry.x.max()
        miny, maxy = map_gdf.geometry.y.min(), map_gdf.geometry.y.max()
        grid_x_utm , grid_y_utm = np.mgrid [minx:maxx:pixel_size, miny:maxy:pixel_size]  
        
        # grid gcs
        minx, maxx = map_gdf.E.min(), map_gdf.E.max()
        miny, maxy = map_gdf.N.min(), map_gdf.N.max()
        xx = np.linspace(minx, maxx,grid_x_utm.shape[0] )
        yy = np.linspace(miny, maxy,grid_x_utm.shape[1] )
        grid_x_gcs_ , grid_y_gcs_ = np.meshgrid(xx, yy)
        
        grid_x_gcs, grid_y_gcs = grid_x_gcs_.T , grid_y_gcs_.T
        
        
        # 2.4 interpolating - we're plotting only gcs 4326
        grid_z_utm = griddata(points_utm, values, (grid_x_utm, grid_y_utm), method='cubic')
        
        # 2.5 calculating the gradient - only for utm
        # the gradient is the hydraulic gradient for a given pixel size decomposed in u,v coords
        u, v = np.gradient(grid_z_utm, pixel_size)
        
        '''
        For Plotting it is necessary to multiply by minus 1
        
        '''
        U =  - u 
        V =  - v 
            
        return grid_x_gcs , grid_y_gcs , grid_z_utm, U , V
    
    except ValueError:
        return text

def arrow_head(grid_x : np.ndarray, 
               grid_y : np.ndarray,
               grid_z : np.ndarray,
               u : np.ndarray,
               v : np.ndarray ,
               scale : int = 50
                 ):
    '''
    Function to create arrow heads based on coordinates, gradient and a scale standard parameter.

    Parameters
    ----------
    grid_x:  np.ndarray
    grid_y:  np.ndarray
    grid_z:  np.ndarray
    u:  np.ndarray
    v:  np.ndarray
    scale: int
    
    Returns
    -------
    df : pandas.core.frame.DataFrame
        dataframe with information with geometric information of arrow heads
    '''
     
                 
    try : 
    
        df = pd.DataFrame ( { 
            
        'x' : grid_x.ravel(),
        'y' : grid_y.ravel(),
        'h' : grid_z.ravel() , 
        'u' : u.ravel(),
        'v' : v.ravel()
                            }
                          )
    
        500 > 10
        
        df ['head_x'] = df.x + df.u / 1e2 * scale
        df ['head_y'] = df.y + df.v / 1e2 * scale
        
        df = df.dropna().reset_index(drop = True)
        
        loc = [list(i[1].values) for i in df[['y', 'x']].iterrows()]
    
        uv = [list(i[1].values) for i in df[['head_y', 'head_x']].iterrows()]
    
        pairs = [(uv[i] , loc[i]) for i,_  in enumerate(loc)]
    
        geodesic = Geod(ellps='WGS84')
        df ['rotation']  = [geodesic.inv(pair[0][1], pair[0][0], pair[1][1], pair[1][0])[0] + 90 for pair in pairs]
    
        return df
    
    except ValueError:
        return text


def Folium_map (Get_ , zoom_start = 17):
    '''
    Function to create Folium map centered in the region of interest.

    Parameters
    ----------
    Get_: SMARTControl.queries.Get
    
    Returns
    -------
    Map: folium.folium.Map
    
    '''
    
    df = Get_.MonitoringPointData()
    map_center = df.N.mean(), df.E.mean() 
    
    TileLayer = folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
       )

    Map = folium.Map(location =map_center, tiles="OpenStreetMap", zoom_start = zoom_start)
    TileLayer.add_to(Map)
    return Map
        

def Folium_contour ( m : folium.folium.Map,
                    map_gdf : gpd.geodataframe.GeoDataFrame , 
                    river_gage_gdf: gpd.geodataframe.GeoDataFrame , 
                    grid_x : np.ndarray, grid_y : np.ndarray, grid_z : np.ndarray):
    '''
    Function to create a Folium contour map.

    Parameters
    ----------
    m: SMARTControl.queries.Get
    map_gdf: geopandas.geodataframe.GeoDataFrame , 
    grid_x:  numpy.ndarray
    grid_y:  numpy.ndarray
    grid_z:  numpy.ndarray
    
    Returns
    -------
    m: folium.folium.Map
    
    '''
    if grid_x is None:
        return text
    
    else:
        crs_gcs = 4326        
        
        #color map
        # orig_map=plt.cm.get_cmap('Blues')
        # reversed_map = orig_map.reversed()
        
        max_ = np.nanmax(grid_z)
        min_ = np.nanmin(grid_z)
        levels = list(np.linspace(min_, max_ , 6))
        contour = plt.contour(grid_x, grid_y, grid_z, linewidths = 2 , colors = 'steelblue', levels = levels)
        
        isolines_gdf = gpd.GeoDataFrame.from_features(
            json.loads(
                geojsoncontour.contour_to_geojson(
                    contour=contour,
                    min_angle_deg=3.0,
                    ndigits=5,
                    stroke_width=1))).set_crs(crs_gcs ) 
        
         
        plt.close()
            
        #reversing coordinates for folium (geodataframe is the contrary)
        points_line = isolines_gdf.apply(lambda x: [y for y in x['geometry'].coords], axis=1)
        lines_list = list()
        for row in points_line:
            lines_list.append( [(tup[1], tup[0]) for tup in row])
        isolines_gdf['lines'] = lines_list
    
        #reversing coordinates for folium (geodataframe is the contrary)
        points_line = isolines_gdf.apply(lambda x: [y for y in x['geometry'].coords], axis=1)
        lines_list = list()
        for row in points_line:
            lines_list.append( [(tup[1], tup[0]) for tup in row])
        isolines_gdf['lines'] = lines_list
    
        
        #delete fictious points from the boundary before plotting it       
        
        points_gdf = map_gdf [ map_gdf.MonitoringPointName != 'RG'] #deleting fictious points
        
        points_gdf = pd.concat ([points_gdf, river_gage_gdf])

        points_list = [list(i[1].values) for i in points_gdf[['N', 'E']].iterrows()]
        
        map_gdf['Value'] = np.round(map_gdf.Value, 2)
        i = 0
        try :
            for coordinates in points_list:
                # Place the markers with the popup labels and data
                m.add_child(
                    folium.Marker(
                        location = coordinates,
                        popup = 
                            f'''
                            <b>Well: </b>{map_gdf.MonitoringPointName[i]}<br>
                            <b>Head: </b>{map_gdf.Value[i]} m<br>
                            '''
                    )
                )
                i +=1
                    
            #adding isolines 
            for row in isolines_gdf.iterrows():
                row = row[1]    
                line = row.lines
                folium.PolyLine(line,
                                color = row.stroke,
                                weight = 3,
                                popup = f'''{row['level-value']}m'''
                                ).add_to(m)
        
            return m
        
        
        except ValueError:
            
            return text

def Folium_arrows(m : folium.folium.Map, arrows_df : pd.core.frame.DataFrame, sample_size = 20):
    
    try : 
        arrows_df = arrows_df.reset_index(drop = True)
        min_ , max_ = arrows_df.index.min(), arrows_df.index.max()
        size = int(max_ / 10)
        indexes = np.linspace(min_, max_ , size).astype('int64')
        # df = arrows_df.sample(n = sample_size).reset_index(drop = True)
        df = arrows_df [arrows_df.index.isin(indexes)].reset_index(drop = True)
        
        for i in range(df.shape[0]):
    
            coordinates=[(df['y'][i], df['x'][i]), (df['head_y'][i] , df['head_x'][i])]    
    
            folium.PolyLine(
                locations = coordinates,
                weight = 2,
                color = 'black'
                                 ).add_to(m)
        
            folium.RegularPolygonMarker(location = (df['head_y'][i] , df['head_x'][i]),
                                        color = 'black',
                                        fill = True,
                                        fill_color = 'black',
                                        fill_opacity = 1 ,
                                        number_of_sides = 3,
                                        radius = 2,
                                        rotation = df['rotation'][i]).add_to(m)
    
        return m
    
    except ValueError:
        return text
    
def HydraulicGradient (Get_ : SMARTControl.queries.Get , size : int = 2000):
    
    '''
    Function that process calculates and exports the hydraulic gradient for a pre-determined number of samples.
    
    Parameters
    ----------
    Get_ : SMARTControl.queries.Get
    size : int
        Number of random elements that will be sampled from the timeseries

    Returns
    -------
    df : pd.core.frame.DataFrame
        object with vectors coordinates
    '''
    
    
    start, end = Get_.StartEndDate(limit = 1)

    times1 = pd.date_range(start = start, end= '2016-10-30', freq = '1H')
    times2 = pd.date_range(start = '2019-05-30', end= end, freq = '1H')
    
    times= pd.Series(np.append(times1, times2))
    times_sample = times.sample(n=size)
    t0 = time.perf_counter()
    
    n = 0
    i = 0
       
    vectors_df = pd.DataFrame()
    
    for t in times_sample:
        Get_.Isolines(t.year, t.month, t.day, t.hour)
        if Get_.Isolines_df.shape[0] > 3:
            
            try: 
                
                map_gdf, river_gage_gdf = prepare_query (Get_, date_wid = t)
                grid_x , grid_y , grid_z, U , V = Interpolation_Gradient(map_gdf , crs_utm = 25833 , pixel_size = 10)
                
                
                df = arrow_head(grid_x , grid_y , grid_z , U , V).\
                    drop(['head_x', 'head_y', 'h', 'rotation'], axis=1).\
                        round(6)
                
                df = pd.DataFrame ( {
                    'x' : np.ravel(grid_x),
                    'y' : np.ravel(grid_y), 
                    'u' : np.ravel(U),
                    'v' : np.ravel(V)                
                    } ).round(6).dropna().reset_index(drop = True)
        
                    
                vectors_df = pd.concat([vectors_df, df])
                i+=1
            except Exception:
               n+=1
               continue
            
            if i%100 == 0:
                print(i)
        else:continue
    t1 = time.perf_counter()
    
    dt = str(datetime.now()).\
        replace(':','-').\
            replace(' ','_')

    fn = f'Data/PostProcessed/Vectors.csv'
    vectors_df.to_csv(fn, index = False)
    
    
    print('Total run time:',t1-t0, 'with {} exceptions'.format(n) )
    return dt
    