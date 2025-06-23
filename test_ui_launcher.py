import pytest
from ui_launcher import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Jupyter' in response.data
    assert b'Sandbox' in response.data

def test_launch_route_get_not_allowed(client):
    response = client.get('/launch')
    assert response.status_code == 405

def test_stop_route_get_not_allowed(client):
    response = client.get('/stop')
    assert response.status_code == 405
