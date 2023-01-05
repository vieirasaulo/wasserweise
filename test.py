import os
import sys
path = 'D:\\Repos\\PirnaCaseStudy'
sys.path.append(path) #indicate the the repository is
import SmartControl as sc


database_fn = 'Data/Database.db'
os.chdir(path)


Get = sc.queries.Get(database_fn) #instantiates the database 
api = sc.api.Inowas(Get, sensor = 'I-2', parameter = 'h_level' , sts = 1670403600, ets = 1670536800)
api.ones1p_url

api.Request ()
api.Request_df
df = api.Request_df.copy()
df = df.loc [ (~df.Value.isnull()) ].reset_index(drop = True)
df
