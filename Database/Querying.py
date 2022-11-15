import CreateDatabase as db
import sqlalchemy as sqla
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd


path = 'D:\\Repos\\PirnaCaseStudy\\Database'
database_fn = 'Database.db'
database_path = path + '\\' + database_fn
engine = create_engine("sqlite:///{}".format(database_fn), echo = True)
connection = engine.connect()
base = declarative_base()

Session = sessionmaker(bind = db.engine)
session = Session()

# for s in session.query(Wells).all():
#     print(s.Name)

# S = session.query(db.DrillingTests, db.Drills).filter(db.Drills.Name == 'D-G01').all()

# for t, d in S:
#     print ("{} {} {} {} {}".format(t.ID, t.DrillID, d.ID, t.TypeID, d.Name))

#plotting query


class Querying():
    
    wells_results = session.query(db.Wells, db.Drills).join(db.Drills).all()
    wells_df = pd.DataFrame()
        
    def __init__(self):
        
        for w, d in self.wells_results:
            df = pd.DataFrame([[w.ID, w.Name, d.E, d.N]],
                              columns = ['WellID', 'WellName', 'E', 'N'])
            self.wells_df = pd.concat ([self.wells_df, df])
        self.wells_df = self.wells_df
            

    def Map (self, Date, Hour , VariableID):
        variables_df = pd.DataFrame()
        results = session.query(db.DiversMeasurements).\
            filter(db.DiversMeasurements.Date == pd.to_datetime(Date).date() ).\
                filter (db.DiversMeasurements.Hour == Hour).\
                    filter(db.DiversMeasurements.Variable == VariableID).all()
                    
        for row in results:
            df = pd.DataFrame(
                [[row.WellID, row.Date, row.Hour, row.Head]],
                columns = ['WellID', 'Date', 'Hour', 'Head']
                )
            variables_df = pd.concat([variables_df, df])
        df = pd.merge(variables_df, self.wells_df, on = "WellID")
        return df
        
    
    
    def HydroTest (self, DrillID, TestType):
        variables_df = pd.DataFrame()
        
        results = session.query(db.HydroTests, db.Drills, db.TestsType).\
            select_from(db.HydroTests).join(db.Drills).join(db.TestsType).\
                filter(db.HydroTests.DrillID == DrillID ).\
                    filter(db.HydroTests.TestTypeID == TestType)
         
        for ht, d, tt in results:               
            df = pd.DataFrame(
                [[d.Name, tt.Name, tt.Unit, ht.Depth, ht.Value]],
                columns = ['DrillName', 'TestType', 'Unit', 'Depth', 'Value']
                )
            variables_df = pd.concat([variables_df, df])
        return variables_df
    
    def ShowAttributes(self):
        print (self.wells_results)
        print (self.wells_df)
        
        
        


# 

#Create jupyter notebook teaching Clau how to query the .db file

df1 = Querying().Map('2015-02-01', 12, 0)  
df2 = Querying().HydroTest( 0 , TestType = 2)