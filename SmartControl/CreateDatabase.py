import os
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

database_fn = 'Database.db'
path = 'D:\\Repos\\PirnaCaseStudy\\Data'
database_path = path + '\\' + database_fn

os.chdir(path)
engine = create_engine("sqlite:///{}".format(database_fn), echo = True)
connection = engine.connect()
base = declarative_base()


class TestsType (base):
    __tablename__ = 'TestsType'
    
    ID = Column(Integer, primary_key = True)
    Name = Column(String(32), nullable=False) #Type of test
    ShortName = Column(String(16)) #Type of test
    Unit = Column(String(32)) #Type of test
    
    def __init__ (self, ID, Name, ShortName, Unit):
        self.ID = ID
        self.Name  = Name 
        self.ShortName = ShortName
        self.Unit = Unit

class Divers(base):
    __tablename__ = 'Divers'
     
    
    ID = Column(Integer, primary_key = True)
    LongID = Column(String(64))
    Project = Column(String(16))
    Name = Column(String(32))
    Company = Column(String(32))
    IOT = Column(Boolean)
    Active = Column(Boolean)
    Functioning = Column(Boolean)
    Variables = Column(String(128))
    Obs = Column(String(128))
    
    
    def __init__ (self, ID, LongID, Project, Name, Company, IOT, Active, Functioning, Variables, Obs):
        self.ID = ID
        self.LongID = LongID
        self.Project = Project
        self.Name = Name
        self.Company = Company
        self.IOT = IOT
        self.Active = Active
        self.Functioning = Functioning
        self.Variables = Variables
        self.Obs = Obs
        
    
class Variables(base):
    __tablename__ = 'Variables'
    
     
    
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
    
     
    
    ID = Column(Integer, primary_key = True)
    Name = Column(String(32), nullable=False)
    Type = Column(String(32), nullable=False)
    DescriptionData = Column(Boolean)
    MonitoringPoint = Column(Boolean)
    DrillingTest = Column(Boolean) #comes from measurements ID
    Depth = Column(Float)
    E = Column (Float)
    N = Column (Float)

    def __init__ (self, ID, Name, Type, DescriptionData, MonitoringPoint, DrillingTest, Depth, E, N):
        self.ID = ID
        self.Name = Name
        self.Type = Type
        self.DescriptionData = DescriptionData
        self.MonitoringPoint = MonitoringPoint
        self.DrillingTest = DrillingTest
        self.Depth = Depth
        self.E = E
        self.N = N 
        
class DrillingTests (base):
    __tablename__ = 'DrillingTests'
    
     
    
    ID = Column(Integer, primary_key = True)  
    PointID = Column(Integer, ForeignKey("Points.ID")) #connects to drill 
    Depth = Column (Float, nullable = False)
    TestTypeID = Column(Integer, ForeignKey("TestsType.ID")) #connects to TestType - Dad
    Value = Column (Float)    
        
    def __init__ (self, ID, PointID , Depth, TestTypeID, Value):
        self.ID = ID
        self.PointID  = PointID 
        self.Depth = Depth
        self.TestTypeID = TestTypeID
        self.Value = Value
        
# It is connected to Drills also 
# coordinates can be retrieved based on this connection
class MonitoringPoints (base):
    __tablename__ = 'MonitoringPoints'
    
    
    
    ID = Column(Integer, primary_key = True)
    Name = Column(String(32), nullable=False)
    PointID = Column(Integer, ForeignKey('Points.ID')) #Point that is connected to this measurement point
    Type = Column(String(16))
    ReferenceAltitude = Column(Float)
    TypeOfAltitude = Column(String(32))
    Diameter = Column(Float)
    FilterTop = Column (Float)
    FilterBase = Column (Float)
    Depth = Column (Float)
    
    def __init__ (self, ID, Name, PointID, Type, ReferenceAltitude, TypeOfAltitude, Diameter, FilterTop, FilterBase, Depth):
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
# Insert here possible hydrogeochemical data

        
#relationship between well and diver    
#two foreign keys
class WellDiver(base):
    __tablename__ = 'WellDiver'
    
    
     
    
    ID = Column(Integer, primary_key = True)
    MonitoringPointID = Column(Integer, ForeignKey('MonitoringPoints.ID'))
    MonitoringPointName = Column(String(32))
    DiverID = Column(Integer, ForeignKey('Divers.ID'))
    
    DiverDepth = Column (Float)
    
    def __init__ (self, ID, MonitoringPointID, MonitoringPointName, DiverID, DiverDepth):
        self.ID = ID
        self.MonitoringPointID = MonitoringPointID
        self.MonitoringPointName = MonitoringPointName
        self.DiverID = DiverID
        self.DiverDepth = DiverDepth

    
class PointsMeasurements (base):
    __tablename__ = 'PointsMeasurements'
    ID = Column(Integer, primary_key = True)
    
    ''' 
    this line of code can delete the database table. Do not run it

    ########################### connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))#####################################


    Values from divers will be read but they have to be transferred to wells 
    before passing them into the database.
    
    The connection with the well will be used to connect with the drill and retrieve the coordinates
    '''
        
    MonitoringPointID = Column(Integer, ForeignKey('MonitoringPoints.ID'))
    TimeStamp = Column (Integer)
    VariableID = Column (Integer, ForeignKey('Variables.ID'))
    Value = Column(Float)
    
    def __init__ (self, ID, MonitoringPointID, TimeStamp, VariableID, Value):
        self.ID = ID
        self.MonitoringPointID = MonitoringPointID
        self.TimeStamp = TimeStamp 
        self.VariableID = VariableID
        self.Value = Value



'''
create the database
'''
if __name__ == '__main__':
    base.metadata.create_all(engine)



