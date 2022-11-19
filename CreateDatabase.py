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
    Variable = Column(String(32)) #Type of test
    Unit = Column(String(32)) #Type of test
    
    def __init__ (self, ID, Name, Variable, Unit):
        self.ID = ID
        self.Name  = Name 
        self.Variable = Variable
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
        
    
class VariablesDivers(base):
    __tablename__ = 'VariablesDivers'
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


class Drills (base):
    __tablename__ = 'Drills'
    #connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    
    ID = Column(Integer, primary_key = True)
    Name = Column(String(32), nullable=False)
    DescriptionData = Column(LargeBinary)
    Well = Column(LargeBinary)
    DrillingTest = Column(LargeBinary) #comes from measurements ID
    Depth = Column(Float)
    E = Column (Float)
    N = Column (Float)
    
    #relationship
    # DrillTests = relationship("DrillingTests", back_populates ="Test") #Dad: one-to-many relationship

    def __init__ (self, ID, Name, DescriptionData, Well, DrillingTest, Depth, E, N):
        self.ID = ID
        self.Name = Name
        self.DescriptionData = DescriptionData
        self.Well = Well
        self.DrillingTest = DrillingTest
        self.Depth = Depth
        self.E = E
        self.N = N 

#table to register the drill measurements 
#there is a connection with Drills
# class DrillingTests (base):
#     __tablename__ = 'DrillingTests'
#     #connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    
#     DrillID = Column(Integer, ForeignKey("Drills.ID")) #connects to drill 
#     ID = Column(Integer, primary_key = True)  
#     TypeID = Column(Integer, ForeignKey("TestsType.ID")) #connects to TestType - Dad
#     Observation = Column (String(64))    
    
#     #relationship
#     # Test = relationship('Drills', back_populates  = 'DrillTests' ) # Child: one-to-many 
    
#     def __init__ (self, ID, DrillID, TypeID, Observation):
#         self.ID = ID
#         self.DrillID = DrillID
#         self.TypeID = TypeID
#         self.Observation = Observation   
        
class HydroTests (base):
    __tablename__ = 'HydroTests'
    #connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    
    ID = Column(Integer, primary_key = True)  
    DrillID = Column(Integer, ForeignKey("Drills.ID")) #connects to drill 
    Depth = Column (Integer, nullable = False)
    TestTypeID = Column(Integer, ForeignKey("TestsType.ID")) #connects to TestType - Dad
    Value = Column (Float)    
    
    #relationship
    # Test = relationship('Drills', back_populates  = 'DrillTests' ) # Child: one-to-many 
    
    def __init__ (self, ID, DrillID, Depth, TestTypeID, Value):
        self.ID = ID
        self.DrillID = DrillID
        self.Depth = Depth
        self.TestTypeID = TestTypeID
        self.Value = Value
        
# It is connected to Drills also 
#coordinates can be retrieved based on this connection
class Wells (base):
    __tablename__ = 'Wells'
    #connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    
    ID = Column(Integer, primary_key = True)
    Name = Column(String(32), nullable=False)
    DrillID = Column(Integer, ForeignKey('Drills.ID')) #drill that is connected to this well
    CaseHeight = Column(Float)
    Diameter = Column(String(32), nullable=False)
    FilterTop = Column (Float)
    FilterBase = Column (Float)
    Depth = Column (Float)
    
    def __init__ (self, ID, Name, DrillID, CaseHeight, Diameter, FilterTop, FilterBase, Depth):
        self.ID = ID
        self.Name = Name
        self.DrillID = DrillID
        self.CaseHeight = CaseHeight
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
    WellID = Column(Integer, ForeignKey('Wells.ID'))
    DiverID = Column(String(32), ForeignKey('Divers.ID'))
    DiverDepth = Column (Integer)
    
    def __init__ (self, ID, WellID, DiverID, DiverDepth):
        self.ID = ID
        self.WellID = WellID
        self.DiverID = DiverID
        self.DiverDepth = DiverDepth

    
class DiversMeasurements(base):
    __tablename__ = 'DiversMeasurements'
    #connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    
    ID = Column(Integer, primary_key = True)
    
    '''
    Values from divers will be read but they have to be transferred to wells 
    before passing them into the database.
    
    The connection with the well will be used to connect with the drill and retrieve the coordinates
    '''
        
    WellID = Column(Integer, ForeignKey('Wells.ID'))
    Date = Column (Date)
    Hour = Column(Integer)
    Variable = Column (Integer, ForeignKey('VariablesDivers.ID'))
    Value = Column(Integer)
    
    def __init__ (self, ID, WellID, Date, Hour, Variable, Value):
        self.ID = ID
        self.WellID = WellID
        self.Date = Date
        self.Hour = Hour
        self.Variable = Variable
        self.Value = Value

#Table to know what each diver is monitoring
class DiverReads(base):
    __tablename__ = 'DiverReads'
    #connection.execute('DROP TABLE IF EXISTS {}'.format(__tablename__))
    
    ID = Column(Integer, primary_key = True)
    VariablesDiversID = Column(Integer, ForeignKey('VariablesDivers.ID'))
    DiverID = Column (Integer, ForeignKey('Divers.ID'))
    
    def __init__ (self, ID, VariablesDiversID, DiverID):
        self.ID = ID
        self.VariablesDiversID = VariablesDiversID
        self.DiverID = DiverID


'''
create the database
'''
base.metadata.create_all(engine)



#retrieving Table as dataframe
def Access_df (table):
    Query = sqla.select([table]) 
    ResultProxy = connection.execute(Query)
    ResultSet = ResultProxy.fetchall()
    df = pd.DataFrame(ResultSet)
    return df

