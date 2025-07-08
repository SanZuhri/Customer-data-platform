# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# FORMAT: postgresql://<user>:<password>@<host>:<port>/<dbname>
DATABASE_URL = "postgresql+psycopg2://alfamart_user:alfamart123@localhost:5432/alfamart_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
