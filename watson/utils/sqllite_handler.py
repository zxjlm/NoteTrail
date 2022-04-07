import datetime

from sqlalchemy import Column, create_engine
from sqlalchemy import Integer
from sqlalchemy import String, DateTime
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()
engine = create_engine("sqlite://", echo=True, future=True)
sql_session = Session(engine)


class HexoLog(Base):
    __tablename__ = 'hexo_log'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    hash = Column(String(32), nullable=False)

    create_at = Column(DateTime, nullable=False, default=datetime.datetime.now)
    update_at = Column(DateTime, nullable=False, default=datetime.datetime.now)


# with Session(engine) as session:
#     session.add_all([spongebob, sandy, patrick])
#     session.commit()
