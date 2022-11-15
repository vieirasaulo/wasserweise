import CreateDatabase as db
from sqlalchemy.orm import sessionmaker
import sqlalchemy as sql
import pandas as pd

Session = sessionmaker(bind = db.engine)
session = Session()

# for s in session.query(db.DrillType).all():
#     print(s.TypeID, s.Name)


database_fn = 'D:\\Repos\\PirnaCaseStudy\\Database\\Database.db'
engine = sql.create_engine("sqlite:///{}".format(database_fn), echo = True)
connection = engine.connect()


# for w, d in session.query(db.Wells, db.Drills).filter(db.Drills.ID == db.Wells.DrillID).all():
#     print ("wid: {} WName: {} DID: {} {} DNmame: {}".format(w.ID, w.Name, w.DrillID, d.ID, d.Name))


query = sql.select([db.DrillingTests, db.Drills]) 


ResultProxy = connection.execute(query)

binary_columns = ['DescriptionData', 'Well', 'DrillingTest']

ResultSet = ResultProxy.fetchall()
df = pd.DataFrame(ResultSet)

# S = session.query(Wells, Drills).filter(Drills.ID == Wells.DrillID).all()
# for w, d in S:
#     


# for col in binary_columns:
#     df[col] = pd.Series([list(b)[1] for b in df[col]])


# x = session.query(DiversMeasurements)

# x = session.query(DiversMeasurements).join(Wells).join(
#     Drills
#     ).filter(DiversMeasurements.Variable == 0
#               ).filter(DiversMeasurements.Date == pd.to_datetime('2015-01-30'
#                                                                 ).date()).all()
    


#Query Hydro data



# sqlalchemy.delete().where(db.DrillType.TypeID < 40)
# session.commit()



# for i in session.query(Wells).join(Drills).all():
#     print (i.ID)