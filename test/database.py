# Third party imports
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Application imports
from watson.utils.sqllite_handler import HexoLog, Base
from watson.utils.utils import generate_md5_from_text


@pytest.fixture(scope='function')
def setup_database():

    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

# end setup_database()


@pytest.fixture(scope='function')
def dataset(setup_database):

    session = setup_database

    # Creates user
    john = HexoLog(name='test1', hash=generate_md5_from_text('test1'))
    mary = HexoLog(name='test2', hash=generate_md5_from_text('test2'))

    session.add(john)
    session.add(mary)
    session.commit()

    yield session

# end dataset_1

