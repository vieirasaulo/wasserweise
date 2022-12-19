import os 

os.chdir ('d:/repos/pirnacasestudy')

import sys
import pandas as pd
import SmartControl as sc


path = 'D:\\Repos\\PirnaCaseStudy\\Data'
database_fn = 'Database.db'
database_fn = path + '\\' + database_fn

# engine, connection, base, session = sc.Functions.DbCon(database_fn)
# q = sc.Querying.TimeSeriesLong(connection = connection, FilterVariable =0 , FilterMonitoringPoint = 0)

