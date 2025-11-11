from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session
from ...config.env_loader import get_env_var
from contextvars import ContextVar
from urllib.parse import quote_plus

# Database URL construction
DB_URL = get_env_var("DB_URL")

engine = create_engine(
    DB_URL,
    pool_size=15,           # a bit higher base pool
    max_overflow=30,        # handle burst traffic
    pool_timeout=15,        # fail fast if pool exhausted
    pool_recycle=1800,      # 30 min recycling (less chance of stale)
    pool_pre_ping=True,     # 🔥 must enable this for cloud DBs
    connect_args={"connect_timeout": 10},  # abort quickly on bad network
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✅ Context variable for session
_db_context: ContextVar[Session] = ContextVar("db_session", default=None)

def set_db_session() -> Session:
    db = SessionLocal()
    _db_context.set(db)
    return db

def get_db_session() -> Session:
    db = _db_context.get()
    if db is None:
        raise RuntimeError("DB session not found in context")
    return db

def remove_db_session():
    db = _db_context.get()
    if db:
        db.close()
        _db_context.set(None)
