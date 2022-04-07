import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from watson.utils.sqllite_handler import Base


@pytest.fixture(scope='function')
def setup_database():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

# end setup_database()
