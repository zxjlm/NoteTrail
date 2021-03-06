import pytest

from watson.utils.sqllite_handler import HexoLog
from watson.utils.utils import generate_md5_from_text


@pytest.fixture(scope='function')
def dataset(setup_database):
    session = setup_database

    john = HexoLog(name='test1', hash=generate_md5_from_text('test1'))
    mary = HexoLog(name='test2', hash=generate_md5_from_text('test2'))

    session.add(john)
    session.add(mary)
    session.commit()

    yield session


def test_database(dataset):
    session = dataset

    assert len(session.query(HexoLog).all()) == 2
