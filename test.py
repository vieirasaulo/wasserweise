import os 
import matplotlib.pyplot as plt
from sympy import *
import json
import geojsoncontour
import folium
import geopandas as gpd
from pyproj import Geod

import sys
import os
import pandas as pd
import geopandas as gpd
from scipy.interpolate import griddata

path = 'd:/repos/pirnacasestudy'
sys.path.append('d:/repos/pirnacasestudy')
import SmartControl as sc

os.chdir(path)
Get = sc.queries.Get('Data/database.db')

date_wid = '2022/12/12 12:00:00'


map_gdf = sc.utils.prepare_query (Get, date_wid )
grid_x_gcs , grid_y_gcs , grid_z_gcs, U , V = sc.utils.Interpolation_Gradient (map_gdf , crs_utm = 25833 , pixel_size = 10)

x = grid_x_gcs
y = grid_y_gcs


map_center = map_gdf.N.mean(), map_gdf.E.mean() #in folium y comes before x

m = folium.Map(location = map_center, zoom_start=15)

arrows_df = sc.utils.arrow_head (grid_x_gcs , grid_y_gcs , grid_z_gcs, U , V)




    
# Get.LongTimeSeries(0)
# Get.ShortTimeSeries(FilterVariableID = 0, FilterMonitoringPoint = 'G01')

Get.Isolines(2022, 12, 12, 0)
# Get.HydroProfile()

# df = Get.Isolines_df
# control_df = sc.utils.ControlPoints()
# bound_df = sc.utils.BoundaryCondition(Isolines_df = df, Control_df = control_df)

# Get.StartEndDate()


# prepare = sc.utils.PrepareIsolines(database_fn)
# df = prepare.DataFrame('2022-12-10 12')
# ds = prepare.DataSet()

# ds.hvplot.contour(
#     z='head', x='Lon', y='Lat', levels = 5,
#     title='Pirna',
#     cmap='Blues',
#     height = 500, width = 1200
    
#     )