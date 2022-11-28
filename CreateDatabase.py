import sqlalchemy as sqla
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, String, Integer, Float, LargeBinary, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import pandas as pd

database_fn = 'Database.db'
path = 'D:\\Repos\\PirnaCaseStudy\\Database'
database_path = path + '\\' + database_fn
engine = create_engine("sqlite:///{}".format(database_fn), echo = True)
connection = engine.connect()
base = declarative_base()


class TestsType (base):
    __tablename__ = 'TestsType'
    #connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    ID = Column(Integer, primary_key = True)
    Name = Column(String(32), nullable=False) #Type of test
    ShortName = Column(String(32)) #Type of test
    Unit = Column(String(32)) #Type of test
    
    def __init__ (self, ID, Name, ShortName, Unit):
        self.ID = ID
        self.Name  = Name 
        self.ShortName = ShortName
        self.Unit = Unit

class Divers(base):
    __tablename__ = 'Divers'
    #connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    
    ID = Column(Integer, primary_key = True)
    Name = Column(String(32))
    Company = Column(String(32))
    IOT = Column(LargeBinary)
    Active = Column(LargeBinary)
    
    def __init__ (self, ID, Name, Company, IOT, Active):
        self.ID = ID
        self.Name = Name
        self.Company = Company
        self.IOT = IOT
        self.Active = Active
        
    
class Variables(base):
    __tablename__ = 'Variables'
    #connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    
    ID = Column(Integer, primary_key = True)
    Name = Column(String(32), nullable=False) #pH, Temperature, 
    
    '''
    The units have to be the same across all of the divers
    '''
    Description = Column(String(64), nullable=False)
    
    def __init__ (self, ID, Name, Description):
        self.ID = ID
        self.Name = Name
        self.Description = Description


class Points (base):
    __tablename__ = 'Points'
    #connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    
    ID = Column(Integer, primary_key = True)
    Name = Column(String(32), nullable=False)
    Type = Column(String(32), nullable=False)
    DescriptionData = Column(LargeBinary)
    MonitoringPoint = Column(LargeBinary)
    DrillingTest = Column(LargeBinary) #comes from measurements ID
    Depth = Column(Float)
    E = Column (Float)
    N = Column (Float)
    
    def __init__ (self, ID, Name, Type, DescriptionData, MonitoringPoint, DrillingTest, Depth, E, N):
        self.ID = ID
        self.Name = Name
        self.DescriptionData = DescriptionData
        self.MonitoringPoint = MonitoringPoint
        self.DrillingTest = DrillingTest
        self.Depth = Depth
        self.E = E
        self.N = N 

class DrillingTests (base):
    __tablename__ = 'DrillingTests'
    #connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    
    ID = Column(Integer, primary_key = True)  
    PointID = Column(Integer, ForeignKey("Points.ID")) #connects to Points 
    Depth = Column (Integer, nullable = False)
    TestTypeID = Column(Integer, ForeignKey("TestsType.ID")) #connects to TestType - Dad
    Value = Column (Float)    
        
    def __init__ (self, ID, PointID, Depth, TestTypeID, Value):
        self.ID = ID
        self.PointID = PointID
        self.Depth = Depth
        self.TestTypeID = TestTypeID
        self.Value = Value
        
# It is connected to Points also 
#coordinates can be retrieved based on this connection
class MonitoringPoints (base):
    __tablename__ = 'MonitoringPoints'
    #connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    
    ID = Column(Integer, primary_key = True)
    Name = Column(String(32), nullable=False)
    PointID = Column(Integer, ForeignKey('Points.ID')) #point that is connected to a measuring point
    Type = Column(String(32), nullable=False)
    ReferenceAltitude = Column(Float)
    TypeOfAltitude = Column(String(32))
    Diameter = Column(String(32), nullable=False)
    FilterTop = Column (Float)
    FilterBase = Column (Float)
    Depth = Column (Float)
    
    def __init__ (self, ID, Name, PointID, Type, ReferenceAltitude, TypeOfAltitude , Diameter, FilterTop, FilterBase, Depth):
        self.ID = ID
        self.Name = Name
        self.PointID = PointID
        self.Type = Type
        self.ReferenceAltitude = ReferenceAltitude
        self.TypeOfAltitude = TypeOfAltitude
        self.Diameter = Diameter
        self.FilterTop = FilterTop
        self.FilterBase = FilterBase
        self.Depth = Depth


# Insert here possible table for welltests

#relationship between well and diver    
#two foreign keys
class WellDiver(base):
    __tablename__ = 'WellDiver'
    #connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    
    ID = Column(Integer, primary_key = True)
    MonitoringPointID = Column(Integer, ForeignKey('MonitoringPoints.ID'))
    MonitoringPointName = Column(String(32))
    DiverID = Column(Integer, ForeignKey('Divers.ID'))
    DiverDepth = Column (Integer)
    
    def __init__ (self, ID, MonitoringPointID, MonitoringPointName, DiverID, DiverDepth):
        self.ID = ID
        self.MonitoringPointID = MonitoringPointID
        self.MonitoringPointName = MonitoringPointName
        self.DiverID = DiverID
        self.DiverDepth = DiverDepth

    
class PointsMeasurements(base):
    __tablename__ = 'PointsMeasurements'
    #connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    
    ID = Column(Integer, primary_key = True)
    
    '''
    Values from divers will be read but they have to be transferred to MonitoringPoints 
    before passing them into the database.
    
    The connection with the measuring point will be used to connect with the point and retrieve the coordinates
    '''
        
    MonitoringPointID = Column(Integer, ForeignKey('MonitoringPoints.ID'))
    Date = Column (Date)
    Hour = Column(Integer)
    Variable = Column (Integer, ForeignKey('Variables.ID'))
    Value = Column(Integer)
    
    def __init__ (self, ID, MonitoringPointID, Date, Hour, Variable, Value):
        self.ID = ID
        self.MonitoringPointID = MonitoringPointID
        self.Date = Date
        self.Hour = Hour
        self.Variable = Variable
        self.Value = Value

'''
create the database
'''
base.metadata.create_all(engine)


