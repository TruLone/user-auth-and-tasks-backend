from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()