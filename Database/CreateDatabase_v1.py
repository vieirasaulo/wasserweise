import sqlalchemy as sqla
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, String, Integer, Float, LargeBinary, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd

database_fn = 'test1.sb'
path = 'D:\\Repos\\PirnaCaseStudy\\Database'
database_path = path + '\\' + database_fn

engine = create_engine("sqlite:///{}".format(database_fn), echo = True)
connection = engine.connect()
base = declarative_base()


class MeasurementsType (base):
    __tablename__ = 'MeasurementsType'
    connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    ID = Column(Integer, primary_key = True)
    Name = Column(String(32), nullable=False) #Type of test
    
    def __init__ (self, ID, Name ): #self is sed to access variables that belong to this class
        self.ID = ID
        self.Name  = Name 

#DrillID
#class subclass of the maindatabase 
class DrillsID (MeasurementsType):
    __tablename__ = 'DrillsID'
        
    # ID = Column(Integer, primary_key = True)
    # DrillName = Column(String(32), nullable=False)
    
    DescriptionData = Column(LargeBinary)
    Well = Column(LargeBinary)
    Measurement = Column(LargeBinary)
    E = Column (Float)
    N = Column (Float)
    Depth = Column(Float)

    def __init__ (self, ID, Name, DescriptionData, Well, Measurement, E, N, Depth):
        self.ID = ID
        self.Name = Name
        self.DescriptionData = DescriptionData
        self.Well = Well
        self.Measurement = Measurement
        self.E = E
        self.N = N
        self.Depth = Depth

#table to register the measurements
class MeasurementsID (base):
    __tablename__ = 'MeasurementsID'
    connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    
    MeasurementID = Column(Integer, primary_key = True)  
    DrillID = Column(Integer, nullable=False) #connects to well or drill
    Date = Column(Date)
    Observation = Column (String(256))

    def __init__ (self, MeasurementID, DrillID, Date, Observation):
        self.MeasurementID = MeasurementID
        self.DrillID = DrillID
        self.Date = Date
        self.Observation = Observation

#second table 
class WellsID (base):
    __tablename__ = 'WellsID'
    connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    
    WellID = Column(Integer, primary_key = True)
    WellName = Column(String(32), nullable=False)
    DrillID = Column(Integer) #drill that is connected to this well
    CaseHeight = Column(Float)
    Diameter = Column(String(32), nullable=False)
    FilterTop = Column (Float)
    FilterBase = Column (Float)
    Depth = Column (Float)
    
    def __init__ (self, TypeID, Name):
        self.WellID = WellID
        self.WellName = WellName
        self.DrillID = DrillID
        self.CaseHeight = CaseHeight
        self.Diameter = Diameter
        self.FilterTop = FilterTop
        self.FilterBase = FilterBase
        self.Depth = Depth






base.metadata.create_all(engine)
        

#retrieving Table as dataframe
def Access (table):
    Query = sqla.select([table]) 
    ResultProxy = connection.execute(Query)
    ResultSet = ResultProxy.fetchall()
    df = pd.DataFrame(ResultSet)
    return df


               
