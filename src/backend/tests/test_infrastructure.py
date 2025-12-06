"""
Simple test to verify test infrastructure works
"""


def test_infrastructure_works():
    """Verify pytest is set up correctly"""
    assert True


def test_fixtures_available(test_engine, session, client):
    """Verify all fixtures are available and work"""
    assert test_engine is not None
    assert session is not None
    assert client is not None
