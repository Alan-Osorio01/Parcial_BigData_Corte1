import pytest
from app.models import Track, Customer, Genre, Album, Artist
from decimal import Decimal

def create_test_data(db):
    artist = Artist(artist_id=1, name="AC/DC")
    db.add(artist)
    genre = Genre(genre_id=1, name="Rock")
    db.add(genre)
    album = Album(album_id=1, title="Back in Black", artist_id=1)
    db.add(album)
    track = Track(track_id=1, name="Thunderstruck", unit_price=Decimal("0.99"), album_id=1, genre_id=1)
    db.add(track)
    customer = Customer(customer_id=1, first_name="Alan", last_name="Osorio", email="alan@test.com")
    db.add(customer)
    db.commit()

# ── Endpoints Tracks ─────────────────────────────────
def test_get_tracks_empty(client):
    response = client.get("/api/tracks")
    assert response.status_code == 200
    assert response.json() == []

def test_get_tracks_with_data(client, db):
    create_test_data(db)
    response = client.get("/api/tracks")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_track_by_id_success(client, db):
    create_test_data(db)
    response = client.get("/api/tracks/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Thunderstruck"

def test_get_track_by_id_not_found(client):
    response = client.get("/api/tracks/999")
    assert response.status_code == 404

def test_search_tracks_found(client, db):
    create_test_data(db)
    response = client.get("/api/tracks/search?q=Thunder")
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_search_tracks_not_found(client, db):
    create_test_data(db)
    response = client.get("/api/tracks/search?q=xyzabc123")
    assert response.status_code == 404

# ── Endpoints Customers ──────────────────────────────
def test_get_customers(client, db):
    create_test_data(db)
    response = client.get("/api/customers")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_customer_by_id_success(client, db):
    create_test_data(db)
    response = client.get("/api/customers/1")
    assert response.status_code == 200
    assert response.json()["email"] == "alan@test.com"

def test_get_customer_not_found(client):
    response = client.get("/api/customers/999")
    assert response.status_code == 404

# ── Endpoint Compra ──────────────────────────────────
def test_purchase_success(client, db):
    create_test_data(db)
    response = client.post("/api/purchase", json={"customer_id": 1, "track_ids": [1]})
    assert response.status_code == 200
    assert response.json()["total"] == "0.99"
    assert response.json()["customer_id"] == 1

def test_purchase_customer_not_found(client, db):
    create_test_data(db)
    response = client.post("/api/purchase", json={"customer_id": 999, "track_ids": [1]})
    assert response.status_code == 404