
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from contextlib import contextmanager
from app import log, config

# Create database engine
engine = create_engine(
    config.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in config.database_url else {},
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=30
)

if "sqlite" in config.database_url:
    log.info(f"Using database sqlite: {config.database_url}")
else:
    log.info(f"Using database mysql: {config.mysql_host}:{config.mysql_port}/{config.mysql_db}")

# Database session management
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Declare model base class
Base = declarative_base()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def SessionManager():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        # if we fail somehow rollback the connection
        log.error(f"We somehow failed in a DB operation and auto-rollbacking... {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


# Initialize database
def init_db():
    """Initialize database (create table structure)"""
    try:
        Base.metadata.create_all(bind=engine)
    except sqlalchemy.exc.OperationalError:
        # sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (1049, "Unknown database 'at_better'")
        log.error("May be the database 'at_better' is not created in mysql, please create it first.")
        exit(1)