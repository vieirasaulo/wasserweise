import CreateDatabase as db
import sqlalchemy as sqla
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import time


path = 'D:\\Repos\\PirnaCaseStudy\\Database'
database_fn = 'Database.db'
database_path = path + '\\' + database_fn
# engine = create_engine("sqlite:///{}".format(database_fn), echo = True)
# connection = engine.connect()
# base = declarative_base()

# Session = sessionmaker(bind = db.engine)
# session = Session()



# results = session.query(db.DiversMeasurements, db.Wells, db.Drills).\
#     select_from (db.DiversMeasurements).\
#         join(db.Wells).join(db.Drills)
            

# results_filter1 = results.filter(db.DiversMeasurements.Date == pd.to_datetime('2019-12-01')).all()

 # = results.filter(db.DiversMeasurements.Date == pd.to_datetime('2019-12-01')).all()

# df = pd.DataFrame(results_filter1)
'''
I can query a first level and then index dates and variables to optimize time on the dashboard
This querying could be a global variable that I query from it
'''



class Query:

    '''
    function to initiate the query and save it as an attribute
    only the classes from the CreateDatabase.py can be passed here
    We need to import the CreateDatabase.py to use the classes
    
    Creating and instance method that queries three tables
    The order of the tables matter
    For querying the well coordinates:
        put db.DiversMeasurements, db.Wells, db.Drills
    
    '''
    def __init__ (self, database_fn, controltable, table1 = None, table2 = None ):
        
        engine = create_engine("sqlite:///{}".format(database_fn), echo = False) #False to not show the output
        connection = engine.connect()
        base = declarative_base()
        Session = sessionmaker(bind = db.engine)
        session = Session()
        start_time = time.perf_counter()
        
        
        tables_list = list(filter(lambda item: item is not None,
                                   [controltable, table1, table2]
                                   )
                            )
        QuerySize = len(tables_list)
        
        if table1 and table2 is None:
            results = session.query(controltable)
        
        if table2 is None:
            results = session.query(controltable, table1).\
                select_from (controltable).\
                    join(table1)
                        
            query_time = time.perf_counter()
            print('Query for 2 tables done')
            print(f'Query time is {query_time - start_time}')
            
        else:
            results = session.query(controltable, table1, table2).\
                select_from (controltable).\
                    join(table1).\
                        join(table2)
            query_time = time.perf_counter()
            print('Query for 3 tables done')
            print(f'Query time is {query_time - start_time}')
            
        self.results = results
        self.connection = connection
        self.base = base 
        self.session = session 
        self.controltable = controltable
        self.table1 = table1
        self.table2 = table2
        self.QuerySize = QuerySize
           
    def Filters (self, filtercol1_filter1_dict, filtercol2_filter2_dict = None,filtercol3_filter3_dict = None):
       
        filters_list = list(filter(lambda item: item is not None,
                                   [filtercol1_filter1_dict, filtercol2_filter2_dict, filtercol3_filter3_dict]
                                   )
                            )   

        filters_length = len(filters_list)
        
        
        bug_message = '''
              Here the arguments are dictionaries with elements that come from
              the class attribute from the CreateDataBase.py (column name).
              The syntax is, for instance: 
                  Filters({db.DiversMeasurement.Date : pd.to_datetime('12/29/2019').date()})
              '''
              
        self.filters_list = filters_list
        self.filters_length = filters_length
        
        try:
            filters1 = list(filters_list[0].items())[0]
            filtercol1 , filter1 = filters1[0], filters1[1]
                                              
            if filters_length == 1:
                results = self.results.\
                    filter(filtercol1 == filter1)
                self.results = results
                return results
                
            else: #three options here        
                
                try: #two if it opens
                    filters2 = list(filters_list[1].items())[0]
                    filtercol2 , filter2 = filters2[0], filters2[1]    
                    
                    if filters_length == 2:
                        results = self.results.\
                            filter(filtercol1 == filter1 ).\
                                filter (filtercol2 == filter2 )
                                
                        self.results = results
                        return results
                        
                    if filters_length == 3:
                        
                        filters3 = list(filters_list[2].items())[0]
                        filtercol3 , filter3 = filters3[0], filters3[1]
                        
                        results = self.results.\
                            filter(filtercol1 == filter1 ).\
                                filter (filtercol2 == filter2 ).\
                                    filter (filtercol3 == filter3)
                                    
                        self.results = results
                        return results
                        

                except Exception as e: 
                    print('\n\n\n\n BUG1 \n\n\n\n')
                    print(e)
                    # print(bug_message)
                    
                
        except: 
            # print(bug_message)            
            print('\n\n\n\n BUG2 \n\n\n\n')
   
    
   
   def (self, filtercol1_filter1_dict, filtercol2_filter2_dict = None,filtercol3_filter3_dict = None):
      
       filters_list = list(filter(lambda item: item is not None,
                                  [filtercol1_filter1_dict, filtercol2_filter2_dict, filtercol3_filter3_dict]
                                  )
                           )

       filters_length = len(filters_list)
       
       
       bug_message = '''
             Here the arguments are dictionaries with elements that come from
             the class attribute from the CreateDataBase.py (column name).
             The syntax is, for instance: 
                 Filters({db.DiversMeasurement.Date : pd.to_datetime('12/29/2019').date()})
             '''
             
       self.filters_list = filters_list
       self.filters_length = filters_length
                      
        try:
            filters1 = list(filters_list[0].items())[0]
            filtercol1 , filter1 = filters1[0], filters1[1]
                                              
            if filters_length == 1:
                results = self.results.\
                    filter(filtercol1 == filter1)
                self.results = results
                return results
                
            else: #three options here        
                
                try: #two if it opens
                    filters2 = list(filters_list[1].items())[0]
                    filtercol2 , filter2 = filters2[0], filters2[1]    
                    
                    if filters_length == 2:
                        results = self.results.\
                            filter(filtercol1 == filter1 ).\
                                filter (filtercol2 == filter2 )
                                
                        self.results = results
                        return results
                        
                    if filters_length == 3:
                        
                        filters3 = list(filters_list[2].items())[0]
                        filtercol3 , filter3 = filters3[0], filters3[1]
                        
                        results = self.results.\
                            filter(filtercol1 == filter1 ).\
                                filter (filtercol2 == filter2 ).\
                                    filter (filtercol3 == filter3)
                                    
                        self.results = results
                        return results
                        

                except Exception as e: 
                    print('\n\n\n\n BUG1 \n\n\n\n')
                    print(e)
                    # print(bug_message)
                    
                
        except: 
            # print(bug_message)            
            print('\n\n\n\n BUG2 \n\n\n\n')
   
    def DataFrame (self, ListOfColumns):
        
        df = pd.DataFrame()
        
        if self.QuerySize == 3:
            for i, j, k in self.results.all():
                try: 
                    columns = [i for i in ListOfColumns if i in dir(i) or dir(j) or dir(k)]
                    columns.sort, ListOfColumns.sort()
                    if ListOfColumns == columns:
                        
                        i_columns =  [it for it in dir(i) if it in ListOfColumns]
                        j_columns =  [it for it in dir(j) if it in ListOfColumns]
                        k_columns =  [it for it in dir(k) if it in ListOfColumns]
                    
                        i_values = [getattr (i, attr) for attr in i_columns]
                        j_values = [getattr (j, attr) for attr in j_columns]
                        k_values = [getattr (k, attr) for attr in k_columns]
                        
                        cols_list = i_columns + j_columns + k_columns
                        values_list = i_values + j_values + k_values
                        
                        df_ =  pd.DataFrame ([values_list],
                                              columns = cols_list)
                        
                        df = pd.concat([df, df_])
                                
                except Exception as e: 
                    print(e)
                
        else:
            if self.QuerySize == 2:
                for i, j in self.results.all():
                    i_columns =  [it for it in dir(i) if it in ListOfColumns]
                    j_columns =  [it for it in dir(j) if it in ListOfColumns]
                    i_values = [getattr (i, attr) for attr in i_columns]
                    j_values = [getattr (j, attr) for attr in j_columns]
        
                                
                    cols_list = i_columns + j_columns 
                    values_list = i_values + j_values
                    
                    df_ =  pd.DataFrame ([values_list],
                                          columns = cols_list)
                    
                    df = pd.concat([df, df_])
                self.df = df
                return(df)
            else:
                for i, j in self.results.all():
                    i_columns =  [it for it in dir(i) if it in ListOfColumns]
                    i_values = [getattr (i, attr) for attr in i_columns]
                    cols_list = i_columns + j_columns 
                    values_list = i_values + j_values
                    df_ =  pd.DataFrame ([values_list],
                                          columns = cols_list)
                    df = pd.concat([df, df_])
                self.df = df
                return(df)
            
        self.dataframe = df
        return(df)
    
    # def Map (self, Date, Hour , VariableID):
        # variables_df = pd.DataFrame()
        # results = session.query(db.DiversMeasurements).\
        #     filter(db.DiversMeasurements.Date == pd.to_datetime(Date).date() ).\
        #         filter (db.DiversMeasurements.Hour == Hour).\
        #             filter(db.DiversMeasurements.Variable == VariableID).all()
                    




engine = create_engine("sqlite:///{}".format(database_fn), echo = False) #False to not show the output
connection = engine.connect()
base = declarative_base()
Session = sessionmaker(bind = db.engine)
session = Session()


'''
Query1
Retrieving diver data to plot map
'''

# ListOfColumns = [ 'Date', 'Name','Hour', 'Head', 'WellID', 'E', 'N']

# filter1 = {db.DiversMeasurements.Date : pd.to_datetime('2020-01-20').date()}
# filter2 =  { db.DiversMeasurements.Hour : 12 }
# filter3 = {db.DiversMeasurements.Variable : 0}

# controltable, table1, table2 = db.DiversMeasurements, db.Wells, db.Drills
# x = Query(database_fn, db.DiversMeasurements, db.Wells, db.Drills)
# x = x.Filters(filter1, filter2, filter3)

# df = x.DataFrame(ListOfColumns)
# df 

'''
Query2
Retrieving well data to plot time series
'''

# ListOfColumns = [ 'Date', 'Name', 'Hour', 'Head', 'WellID']
# filter1 = {db.DiversMeasurements.WellID : 0}
# filter2 = {db.DiversMeasurements.Variable : 0}

# x = Query(database_fn, db.DiversMeasurements, db.Wells)
# x = x.Filters(filter1, filter2)
# df = pd.read_sql(x, connection)




# with engine.connect().execution_options(autocommit=True) as conn:
#     df = pd.read_sql(f"""SELECT * FROM DiversMeasurements WHERE WellID = 0""", con = conn)
#     plt.plot(df.Date, df.Head)

# x.DataFrame(ListOfColumns)d


# x.results.filter_by(db.DiversMeasurements.ID==2)

query = '''
SELECT * FROM DiversMeasurements as DM
JOIN Wells as W
ON DM.WellID = W.ID
WHERE Variable = 0
'''

query = '''
SELECT DiversMeasurements.ID, DiversMeasurements.Date, DiversMeasurements. Head, Wells.ID, Wells.Name
FROM 
	DiversMeasurements
JOIN
	Wells ON DiversMeasurements.WellID = Wells.ID
WHERE
	Variable = 0 and WellID = 0
'''


query = '''
SELECT 
DiversMeasurements.Date, DiversMeasurements.Head, DiversMeasurements.Head, Wells.ID, Wells.Name, Wells.DrillID, Drills.ID, Drills.E, Drills.N
FROM 
	DiversMeasurements
JOIN
	Wells ON DiversMeasurements.WellID = Wells.ID
JOIN
	Drills ON Wells.DrillID = Drills.ID	
WHERE
	Variable = 0 and WellID = 0
'''

df = pd.read_sql(query, con = connection)


# df1 = x.DataFrame()



# ListOfColumns = ['WellID', 'Date', 'Hour', 'Head', 'DrillID', 'E', 'N']

# controltable, table1, table2 = db.DiversMeasurements, db.Wells, db.Drills
# x = Query(database_fn, db.DiversMeasurements, db.Wells, db.Drills)
# x.Filters({db.DiversMeasurements.Date : pd.to_datetime('2020-01-20').date()},
#                   { db.DiversMeasurements.Hour : 12 },
#                   {db.DiversMeasurements.Variable : 0})

# df = x.DataFrame(ListOfColumns)


# df = pd.DataFrame()
# for i, j, k in x.results:
#     try: 
#         columns = [i for i in ListOfColumns if i in dir(i) or dir(j) or dir(k)]
#         columns.sort, ListOfColumns.sort()
#         if ListOfColumns == columns:
            
#             i_columns =  [it for it in dir(i) if it in ListOfColumns]
#             j_columns =  [it for it in dir(j) if it in ListOfColumns]
#             k_columns =  [it for it in dir(k) if it in ListOfColumns]
        
#             i_values = [getattr (i, attr) for attr in i_columns]
#             j_values = [getattr (j, attr) for attr in j_columns]
#             k_values = [getattr (k, attr) for attr in k_columns]
            
#             cols_list = i_columns + j_columns + k_columns
#             values_list = i_values + j_values + k_values
            
#             df_ =  pd.DataFrame ([values_list],
#                                   columns = cols_list)
            
#             # df_ = 
            
#             df = pd.concat([df, df_])
        
#     except Exception as e: 
        
#         print(e)
# df
# # d = x.results
    
# class Filters (Query):
#     '''
#     Class inherited from Query.
#     This class can only be filtered with the control table
    
#     Here the arguments are dictionaries with elements that come from
#     the class attribute from the CreateDataBase.py (column name).
    
#     The syntax is, for instance: Filters({db.DiversMeasurement.Date : pd.to_datetime('12/29/2019').date()})
        
#         for instance: db.DiversMeasurement could be filtercol1.
#         The filter is the value that will be looked up in this list
        
        
        

        
#         init function to pass the parent class attributes to chield
#         Query.__init__ (self, database_fn, controltable, table1, table2 = None )
#     '''

    
#     def __init__ (self, database_fn ,controltable, table1, table2,
#                   filtercol1_filter1_dict,
#                   filtercol2_filter2_dict = None,
#                   filtercol3_filter3_dict = None):
        
#         super().__init__()

#         filters_list = list(filter(
#             lambda item: item is not None, 
#             [self.filtercol1_filter1_dict, self.filtercol2_filter2_dict, self.filtercol3_filter3_dict]
#                                                 )
#                                          )
#         filters_length = len(filters_list)

        
#         bug_message = '''
#               Here the arguments are dictionaries with elements that come from
#               the class attribute from the CreateDataBase.py (column name).
#               The syntax is, for instance: 
#                   Filters({db.DiversMeasurement.Date : pd.to_datetime('12/29/2019').date()})
#               '''
#         self.filters_list = filters_list
#         self.filters_length = filters_length
#         try:
            
#             filters1 = list(filters_list[0].items())[0]
#             filtercol1 , filter1 = filters1[0], filters1[1]
                                              
#             if filters_length == 1:
#                 results = self.results.\
#                     filter(filtercol1 == filter1).all()
#                 self.results = results
                
#             else: #three options here        
                
#                 try: #two if it opens
#                     filters2 = list(filters_list[1].items())[0]
#                     filtercol2 , filter2 = filters2[0], filters2[1]    
                    
#                     if filters_length == 2:
#                         results = self.results.\
#                             filter(db.filtercol1 == filter1 ).\
#                                 filter (db.filtercol2 == filter2 ).all()
                                
#                         self.results = results
                    
#                     if filters_length == 3:
                        
#                         filters3 = list(filters_list[2].items())[0]
#                         filtercol3 , filter3 = filters3[0], filters3[1]
                        
                        
#                         results = self.results.\
#                             filter(db.DiversMeasurements.Date == filter1 ).\
#                                 filter (db.DiversMeasurements.Hour == filter2 ).\
#                                     filter (db.DiversMeasurements.Variable == filter3).all()
                        
                                    
#                         # self.results = results
                
#                 except Exception as e: 
#                     print('\n\n\n\n BUG1 \n\n\n\n')
#                     print(e)
#                     # print(bug_message)
                    
                
#         except: 
#             # print(bug_message)            
#             print('\n\n\n\n BUG2 \n\n\n\n')

            

           


# print(results.filters_length, results.filters_list)
        
            
                
   


            # if filters_length == 3:
            #         filters2 = list(filters_list.items())[1]
            #         filtercol2 , filter2 = filters2[0], filters2[1]
  
                
            #         filters_list = list(filtercol2b_filter2b_dict.items())[0] #getting items list
            #         filtercol2b , filter2b = filters_list[0], filters_list[1] #attributing values to new variable
            
            
            
            
        #     self.results = results

                
                
        # except Exception:
        #     print(bug_message)
                        

        # #3 filters case
        # try:
        #     #if None here, it will try the 2 filters case
        #     filtercol2_filter2_dict.items()
        #     filtercol3_filter3_dict.items()
            
            
        #     #defining filters
        #     filters_list = list(filtercol2_filter2_dict.items())[0]
        #     filtercol2 , filter2 = filters_list[0], filters_list[1]                      
        #     filters_list = list(filtercol3_filter3_dict.items())[0]
        #     filtercol3 , filter3 = filters_list[0], filters_list[1]
            
            
        #     results = self.results.\
        #         filter(filtercol1 == filter1 ).\
        #             filter (filtercol2 == filter2 ).\
        #                 filter(filtercol3 == filter3 ).all()

        # except Exception:
        #     #1 filter case:
        #     if filtercol2_filter2_dict and filtercol2_filter2_dict is None:

            
        #     #2 filters case.
        #     else:
        #         #getting rid of None filter
        #         filtercol2b_filter2b_dict = list(filter(
        #             lambda item: item is not None, 
        #             [filtercol2_filter2_dict, filtercol2_filter2_dict]
        #                                                 )
        #                                          )[0] #returning the only value of the list
                
        #         try:

        #             filters_list = list(filtercol2b_filter2b_dict.items())[0] #getting items list
        #             filtercol2b , filter2b = filters_list[0], filters_list[1] #attributing values to new variable
                    
        #             results = self.results.\
        #                 filter(filtercol1 == filter1 ).\
        #                     filter (filtercol2b == filter2b ).all()
                        
        #             self.results = results

        #         except Exception:
        #             print('''filter must be a dictionary''')
                                                    

            
        


# df1 = Query()  





# '2015-02-01', 12, 0''
    # def Map 



    # def DataFrame ():
        
    #     for row in results:
    #         df = pd.DataFrame(
    #             [[row.WellID, row.Date, row.Hour, row.Head]],
    #             columns = ['WellID', 'Date', 'Hour', 'Head']
    #             )
    #         variables_df = pd.concat([variables_df, df])
    #     df = pd.merge(variables_df, self.wells_df, on = "WellID")
        
    #     return df
            
    
    
    # def HydroTest (self, DrillID, TestType):
    #     variables_df = pd.DataFrame()
        
    #     results = session.query(db.HydroTests, db.Drills, db.TestsType).\
    #         select_from(db.HydroTests).join(db.Drills).join(db.TestsType).\
    #             filter(db.HydroTests.DrillID == DrillID ).\
    #                 filter(db.HydroTests.TestTypeID == TestType)
         
    #     for ht, d, tt in results:               
    #         df = pd.DataFrame(
    #             [[d.Name, tt.Name, tt.Unit, ht.Depth, ht.Value]],
    #             columns = ['DrillName', 'TestType', 'Unit', 'Depth', 'Value']
    #             )
    #         variables_df = pd.concat([variables_df, df])
    #     return variables_df
    
#     def ShowAttributes(self):
#         print (self.wells_results)
#         print (self.wells_df)
        
        
        




# class Querying():
    
#     #define the largest attribute here    
#     #keep 
#     QueryResults = session.query(db.Wells, db.Drills).join(db.Drills).all() #class variable
#     wells_df = pd.DataFrame()
        
#     def __init__(self):
        
#         for w, d in self.wells_results:
#             df = pd.DataFrame([[w.ID, w.Name, d.E, d.N]],
#                               columns = ['WellID', 'WellName', 'E', 'N'])
#             self.wells_df = pd.concat ([self.wells_df, df])
#         self.wells_df = self.wells_df
            

    # def Map (self, Date, Hour , VariableID):
    #     variables_df = pd.DataFrame()
    #     results = session.query(db.DiversMeasurements).\
    #         filter(db.DiversMeasurements.Date == pd.to_datetime(Date).date() ).\
    #             filter (db.DiversMeasurements.Hour == Hour).\
    #                 filter(db.DiversMeasurements.Variable == VariableID).all()
                    
        # for row in results:
        #     df = pd.DataFrame(
        #         [[row.WellID, row.Date, row.Hour, row.Head]],
        #         columns = ['WellID', 'Date', 'Hour', 'Head']
        #         )
        #     variables_df = pd.concat([variables_df, df])
        # df = pd.merge(variables_df, self.wells_df, on = "WellID")
        # return df
        
    
    
    # def HydroTest (self, DrillID, TestType):
#         variables_df = pd.DataFrame()
        
#         results = session.query(db.HydroTests, db.Drills, db.TestsType).\
#             select_from(db.HydroTests).join(db.Drills).join(db.TestsType).\
#                 filter(db.HydroTests.DrillID == DrillID ).\
#                     filter(db.HydroTests.TestTypeID == TestType)
         
#         for ht, d, tt in results:               
#             df = pd.DataFrame(
#                 [[d.Name, tt.Name, tt.Unit, ht.Depth, ht.Value]],
#                 columns = ['DrillName', 'TestType', 'Unit', 'Depth', 'Value']
#                 )
#             variables_df = pd.concat([variables_df, df])
#         return variables_df
    
#     def ShowAttributes(self):
#         print (self.wells_results)
#         print (self.wells_df)
        
        
        



#Create jupyter notebook teaching Clau how to query the .db file

# df1 = Querying().Map('2015-02-01', 12, 0)  
# df2 = Querying().HydroTest( 0 , TestType = 2)


        #     '''
        #     Only DiversMap Class have the results changed
        #     '''
        #     self.results = results 
        # except ValueError:
        #     print('Error in your query. This is a function to query only diver data')
            
        #     print('''\nFor querying the well coordinates:
        #           Use que Query function with the following arguments:
        #               db.DiversMeasurements, db.Wells, db.Drills
        #               Then Filter the dates, hours and Variable ID
        #               ''')
      