from watson.utils.sqllite_handler import HexoLog


def test_database(dataset):
    # Gets the session from the fixture
    session = dataset

    # Do some basic checking
    assert len(session.query(HexoLog).all()) == 2

    # Retrieves John and Mary
