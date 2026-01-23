from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, Text, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class PageView(Base):
    __tablename__ = "page_views"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    user_id = Column(String(100), index=True, nullable=True)
    page_url = Column(String(500), index=True)
    page_title = Column(String(200))
    referrer = Column(String(500), nullable=True)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    screen_width = Column(Integer, nullable=True)
    screen_height = Column(Integer, nullable=True)
    language = Column(String(10), nullable=True)
    duration = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    
    __table_args__ = (
        Index('idx_session_timestamp', 'session_id', 'timestamp'),
        Index('idx_url_timestamp', 'page_url', 'timestamp'),
    )

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    user_id = Column(String(100), index=True, nullable=True)
    event_type = Column(String(50), index=True)
    event_name = Column(String(100))
    properties = Column(Text, nullable=True)
    page_url = Column(String(500))
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.now, index=True)
    
    __table_args__ = (
        Index('idx_event_type_timestamp', 'event_type', 'timestamp'),
    )

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True)
    user_id = Column(String(100), index=True, nullable=True)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    page_views = Column(Integer, default=1)
    duration = Column(Float, default=0.0)
    referrer = Column(String(500), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    
    __table_args__ = (
        Index('idx_start_time', 'start_time'),
    )

class AggregatedStats(Base):
    __tablename__ = "aggregated_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    stat_type = Column(String(50), index=True)
    stat_date = Column(DateTime, index=True)
    page_url = Column(String(500), nullable=True, index=True)
    value = Column(Float, default=0.0)
    meta_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_stat_date_type', 'stat_date', 'stat_type'),
    )

def init_db():
    Base.metadata.create_all(bind=engine)
