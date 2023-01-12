import time
import SMARTControl as sc
import pandas as pd
import numpy as np

database_fn = 'Database.db'
Get = sc.queries.Get(database_fn) #instantiates the Get class
start, end = Get.StartEndDate(limit = 3)

# Get.Isolines(2019,7,20,0)
# print(Get.Isolines_df)

times1 = pd.date_range(start = start, end= '2016-10-30', freq = '1H')
times2 = pd.date_range(start = '2019-05-30', end= end, freq = '1H')

times= pd.Series(np.append(times1, times2))
times_sample = times.sample(n=2000, random_state=6)
t0 = time.perf_counter()

n = 0
i = 0
vectors_df = pd.DataFrame()

for t in times_sample:
    Get.Isolines(t.year, t.month, t.day, t.hour)
    if Get.Isolines_df.shape[0] > 3:
        
        try: 
            
            map_gdf, river_gage_gdf = sc.utils.prepare_query (Get, date_wid = t)
            grid_x , grid_y , grid_z, U , V = sc.utils.Interpolation_Gradient(map_gdf , crs_utm = 25833 , pixel_size = 10)
            
            
            df = sc.utils.arrow_head(grid_x , grid_y , grid_z , U , V).\
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

# vectors_df.to_csv('Vectors.csv', index = False)

print('Total run time:',t1-t0, 'with {} exceptions'.format(n) )