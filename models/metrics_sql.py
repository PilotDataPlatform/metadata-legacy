from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, TIMESTAMP

Base = declarative_base()


class SystemMetrics(Base):
    """
    PostgreSQL system metrics table
    """
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True)
    active_user = Column(Integer)
    project = Column(Integer)
    storage = Column(Integer)
    vm = Column(Integer)
    cores = Column(Integer)
    ram = Column(Integer)
    date = Column(TIMESTAMP)
