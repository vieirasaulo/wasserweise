'''
Module where the functions that support the update function are written
'''



# '''
# Enabling execution as __main__
# '''
# import os
# os.environ["GIT_PYTHON_REFRESH"] = "quiet"
# import git
# repo = git.Repo('.', search_parent_directories=True)
# os.chdir(repo.working_tree_dir)
# sys.path.append(repo.working_tree_dir)
# print(repo.working_tree_dir)


'''
Importing modules and libraries
'''
import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
import numpy as np
import pandas as pd
from datetime import datetime
import time
import SMARTControl.api as api
import SMARTControl.utils as utils
from SMARTControl.api import PegelAlarm
from SMARTControl.api import Inowas
import SMARTControl.queries
import git
from github import Github

fn = 'Data/LOG_UPDATE.txt' 
    
class GWL (Inowas):
    '''
    Inheriting the methods and attributes from api.INOWAS to apply update function
    '''
    
# Class for INOWAS is too complicated. it's better to use functions.
def Update (Process_df , Get_ ):
    
    if Process_df is not None:
        Process_df.to_sql(name="PointsMeasurements", con= Get_.connection, if_exists="append", index=False)
        print (f'Diver data updated from ID {Process_df.iloc[0,0]} to ID {Process_df.iloc[-1,0]}')
    else:     
        print ('Diver data is up-to-date')
    
def SequenceUpdate (sensor, sts , Get_): 
    with open(fn, 'a+') as f:
        t0 = time.perf_counter()
        
        ets = round(pd.to_datetime(datetime.now()).value / 1e9)
        SensorsAPI_df, Sensors_df = api.GetDivers(Get_.connection)
        variables =  Sensors_df [ Sensors_df.Diver == sensor].VariableName #indexing variables of interest
        
        #build on top of the request package and calculate the parameters to request multiple times
        for p in variables:
            t0 = time.perf_counter()
            
            r = GWL(Get_, sensor, p, sts, ets)
            r.Request()
            
            Process_df = utils.Process(r.Request_df , Get_)           


            if Process_df is None:
                t1 = time.perf_counter()
                last_update = pd.to_datetime(sts * 1e9) - pd.Timedelta(1, unit="h")
                txt = f'\nNo data for sensor {sensor} and parameter {p}. Last update was: {last_update}. Check the portal of UIT. Running time was in {round(t1-t0)} s'
                print (txt)
                f.write (txt)
            else:
                
                try: 
                                    
                    '''
                        
                    MISTAKE IN THE UPDATE FUNCTION
                    
                    Fix and Merge INOWAS here
                    '''
                    
                    Update(Process_df, Get_)
                    t1 = time.perf_counter()
                    txt = f'\nDiver data updated from ID {Process_df.iloc[0,0]} to ID {Process_df.iloc[-1,0]} for sensor {sensor} parameter {p} in {round(t1-t0)} s'
                    print (txt)    
                    f.write (txt)
                
                except Exception:
                    txt = f"\nFor a reason it didn't run for sensor {sensor} and parameter {p}. It could be that it is updated "
                    print (txt)    
                    f.write (txt)
        txt = f"\n End of Update for sensor {sensor}\n\n"
        print (txt)    
        f.write (txt)
            
def InowasLongAPItoSQL (Get_):
    
    t0 = time.perf_counter()
    DiversNextUpdate_df = Get_.DiverStatus()
    FunctioningDivers_df = DiversNextUpdate_df  [(DiversNextUpdate_df .IOT == 1) & (DiversNextUpdate_df.Functioning ==1)].reset_index (drop = True)
    
    if fn in os.listdir():
        with open(fn, 'a+') as f:
            f.write('\n\n')
    with open(fn, 'a+') as f:
        f.write('*************************************NEW RUN INOWAS*************************************')    
        now = datetime.now()
        txt = f'\n\nProgram run on the following date: {now}'
        print(txt)
        f.write(txt)
        
    for i in (FunctioningDivers_df.iterrows()):
        row = i[1]
        sensor, sts = row.DiverName, row.NextUpdate_ts
        if np.isnan(sts):
            sts = 1420934400
    
        SequenceUpdate (sensor, sts , Get_)
    
    t1 = time.perf_counter()
    with open(fn, 'a+') as f:
        txt = "\n#####################################END INOWAS######################################"
        print (txt)
        f.write(txt)
        txt = f"\nThe TOTAL for Diver's update running time was {round(t1-t0)} s"
        print (txt)
        f.write(txt)
    
    
    
class RL (PegelAlarm):
    '''
    Inheriting the methods and attributes from api.PagelAlarm to apply update function
    '''
    def Update (self):
                    
        if self.Process_df.shape[0]>0:
            self.Process_df.to_sql(name="PointsMeasurements", con= self.connection, if_exists="append", index=False)
            text = f'\n\nRiver data updated from ID {self.Process_df.iloc[0,0]} to ID {self.Process_df.iloc[-1,0]}'
            return text
        else:     
            text = '\n\nRiver data is up-to-date'
            return text                
            

    def RiverAPItoSQL (self):
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
            r = RL(self.Get_)
            r.Request()
            self.Process_df = utils.Process(r.Request_df,self.Get_)
            txt = self.Update( )        
            print(txt)
            f.write(txt)
            
            t1 = time.perf_counter()      
            
            txt = f"\n\nEnd of the update for PEGELALARM.AT. The running time was {round(t1-t0)} s"
            print (txt)
            f.write(txt)
            txt = "\n\n#####################################END PEGELALARM.AT######################################"
            print (txt)
            f.write(txt)     

def app_update (git_commit: bool , github_push : bool ):
    repo = git.Repo('.', search_parent_directories=True)
    os.chdir(repo.working_tree_dir)
    
    '''
    Instantiating the get class
    '''
    
    database_fn = 'Data/Database.db'
    Get = SMARTControl.queries.Get(database_fn)
    
    '''
    Update database locally
    '''
    r = RL(Get)
    print(r.url)
    r.Request()
    r.RiverAPItoSQL()
    InowasLongAPItoSQL(Get)

    dt = str(datetime.now()).\
    replace(':','-').\
        split('.')[0]
    commit_message = f'Database_LastUpdate-{dt}'
    
    if git_commit:
        '''
        Commit database locally
        '''
        #repo = git.Repo('.', search_parent_directories=True)
        #path = repo.working_tree_dir
        path = 'D:/Repos/PirnaCaseStudy'
        
        contents = os.listdir(path+'/Data')
        database_list = ['Data/'+file for file in contents if 'db' in file or 'LOG' in file]
        
        for i in range(len(database_list)):
            repo.index.add(database_list[i])
            repo.git.commit( '-m', commit_message)
    
    
    if github_push:
        '''
        Add to Github
        '''
        with open('D:\Repos\AccessToken.txt', 'r') as f:
        	token = f.readline()
        
        g = Github(token)    
        repo = g.get_user().get_repo('PirnaStudyCase')
        contents = repo.get_contents('Data')
        database_list = [file for file in contents if 'db' in file.path or 'LOG' in file.path]
        
        for i in range(len(database_list)):
        	repo.update_file(database_list[i].path, commit_message, commit_message, database_list[i].sha)