import os
import sys

import pandas as pd
import numpy as np

from sqlalchemy import MetaData, Table
import git

repo = git.Repo('.', search_parent_directories=True)
os.chdir(repo.working_tree_dir)

import SMARTControl as sc


database_fn = 'Database.db'

Get = sc.queries.Get(database_fn) #instantiates the Get class 

# Get.MonitoringPointData()
# df = Get.MonitoringPointData_df.copy()
# d = df [df.MonitoringPointName == 'G01'].MonitoringPointID.values[0]
'''
TimeSeries
'''
# Get.LongTimeSeries(7)
# df = Get.LongTimeSeries_df
# df = df.sort_values(by= 'Date')
# df.plot('Date', 'Value', 'scatter', figsize = (20,10), alpha = 0.1)

# sc.utils.RemoveOutliers(Get, 108)

# Get.ShortTimeSeries(FilterVariableID = 0,
#                     FilterMonitoringPoint = 'G21neu')
# df = Get.ShortTimeSeries_df
# arrows_df = df.copy()

# min_ , max_ = 0, arrows_df.shape[0]
# size = int(max_ / 2)
# indexes = np.linspace(min_, max_ , size)
# # df = arrows_df.sample(n = sample_size).reset_index(drop = True)
# df = arrows_df [arrows_df.index.isin(indexes)].reset_index(drop = True)

# df.plot('Date', 'Value', 'scatter', figsize = (20,10), alpha = 0.9)

# df_ = df [df.Date.dt.hour.diff() > 1]

# df_ = utils.Process(df, Get)


# df2 = pd.read_csv('Data/Tables/Old/PointsMeasurements.csv')

# bound_id = 1043069
# df2 = df2 [~ (df2.ID > bound_id)]
# df2['Date'] = pd.to_datetime(df2.TimeStamp * 1e9)
# df2_ = df2 [df2.MonitoringPointID == 0]
# df2 = df2.drop('Date', axis = 1)

# df2.to_csv('Data/Tables/PointsMeasurements.csv', index = False)

# Get.Isolines(2021,12,20, 12)
# df = Get.Isolines_df
# df_ = Get.DiverStatus()
# df['DiverReading'] = - df.CaseTop + df.DiverDepth + df.Value

# api = sc.api.Inowas(Get, sensor = 'I-2', parameter = 'h_level' , sts = 1670403600, ets = 1670536800)
# api.ones1p_url

# api.Request ()
# api.Request_df
# df = api.Request_df.copy()
# # df = df.loc [ (~df.Value.isnull()) ].reset_index(drop = True)
# df

#change variable id in the pointsmeasurements table
# df = pd.read_csv('Data/Tables/PointsMeasurements.csv')
# df = df [df.VariableID != 9]
# df.to_csv('Data/Tables/PointsMeasurements.csv', index = False)

# r = sc.api.PegelAlarm(Get)
# r.Request()
# df = r.Request_df.copy()
# df #error here

# Get.MonitoringPointData(GageData = 1)
# df_mon = Get.MonitoringPointData_df


############
# df = pd.read_csv('Data/Tables/PointsMeasurements.csv')
# df.to_sql(name="PointsMeasurements", con= Get.connection, if_exists="append", index=False)

# Get.APIDate(1)

# df = Get.DiverStatus()

# t, ts = Get.APIDate (row.MonitoringPointID)



### Deleting 




# initialize the Metadata Object
# engine = Get.engine
# meta = MetaData(bind=engine)
# MetaData.reflect(meta)
# # n = UpdateID  
# n = 0
# table = Table('PointsMeasurements', meta, autoload=True)
# d = table.delete().where(table.c.ID >= n)
# d.execute()
