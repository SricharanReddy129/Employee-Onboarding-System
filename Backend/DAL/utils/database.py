from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ...config.env_loader import get_env_var
 
# Example: mysql+mysqlclient://username:password@host:port/dbname
DATABASE_URL = get_env_var("DB_URL")
 
engine = create_engine(DATABASE_URL, echo=True)  # echo=True for SQL logging
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()