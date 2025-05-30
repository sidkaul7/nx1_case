from sqlalchemy import create_engine
from data.models import Base
 
engine = create_engine('sqlite:///data/filings.db')
Base.metadata.create_all(engine)
print('Database and tables created.') 