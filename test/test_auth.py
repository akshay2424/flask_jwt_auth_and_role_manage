from models import TheaterModel, SeatsModel
import json


def get_token(client):
    resp = client.post("/login", json={
        "username": "super",
        "password": "admin",
    })
    data = json.loads(resp.data)
    return data["access_token"]


def test_auth_admin(client):
    resp = client.post("/login", json={
        "username": "super",
        "password": "admin",
    })
    assert resp.status == '200 OK' and b'access_token' in resp.data


def test_auth_customer(client):
    resp = client.post("/login", json={
        "username": "test1",
        "password": "test1",
    })
    assert resp.status == '200 OK' and b'access_token' in resp.data


def test_get_theatres(client):
    data = client.get("/theaters", headers={
        "Authorization": "Bearer " + get_token(client)
    })
    assert json.loads(data.data) == TheaterModel.return_all()


def test_add_theatre(client):
    resp = client.post("/theaters", headers={
        "Authorization": "Bearer " + get_token(client)
    }, json={
        "t_name": "Test Demo",
        "address": "Test",
        "no_of_seats": 30
    })

    assert resp.status == '200 OK'


def test_get_seates(client):
    data = client.get("/seats", headers={
        "Authorization": "Bearer " + get_token(client)
    })
    assert json.loads(data.data) == SeatsModel.return_all()


def test_add_seates(client):
    data = client.post("/seats", headers={
        "Authorization": "Bearer " + get_token(client)
    }, json={
        "row": "Test Demo",
        "number": "Test",
        "theater_id": 1
    })
    assert data.status == '200 OK'
