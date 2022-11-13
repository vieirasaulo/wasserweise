import CreateDatabase as db
from sqlalchemy.orm import sessionmaker
import sqlalchemy as sql
import pandas as pd

# Session = sessionmaker(bind = db.engine)
# session = Session()

# for s in session.query(db.DrillType).all():
#     print(s.TypeID, s.Name)


database_fn = 'D:\\Repos\\PirnaCaseStudy\\Database\\Test1.db'
engine = sql.create_engine("sqlite:///{}".format(database_fn), echo = True)
connection = engine.connect()


query = sql.select([db.DrillType]) 

ResultProxy = connection.execute(query)


ResultSet = ResultProxy.fetchall()
df = pd.DataFrame(ResultSet)
# print(ResultSet)



# sqlalchemy.delete().where(db.DrillType.TypeID < 40)
# session.commit()