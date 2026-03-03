import pytest
from app.services import (
    get_all_tracks, get_track_by_id,
    get_customer_by_id, get_all_customers,
    search_tracks, purchase_tracks
)
from app.models import Track, Customer, Genre, Album, Artist
from app.schemas import PurchaseRequest
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

# ── Tests de Tracks ───────────────────────────────────
def test_get_all_tracks_empty(db):
    tracks = get_all_tracks(db)
    assert tracks == []

def test_get_all_tracks_with_data(db):
    create_test_data(db)
    tracks = get_all_tracks(db)
    assert len(tracks) == 1
    assert tracks[0].name == "Thunderstruck"

def test_get_track_by_id_exists(db):
    create_test_data(db)
    track = get_track_by_id(db, 1)
    assert track is not None
    assert track.name == "Thunderstruck"
    assert track.unit_price == Decimal("0.99")

def test_get_track_by_id_not_exists(db):
    track = get_track_by_id(db, 999)
    assert track is None

def test_search_tracks_by_name(db):
    create_test_data(db)
    results = search_tracks(db, "Thunder")
    assert len(results) == 1
    assert results[0].name == "Thunderstruck"

def test_search_tracks_by_artist(db):
    create_test_data(db)
    results = search_tracks(db, "AC/DC")
    assert len(results) == 1

def test_search_tracks_no_results(db):
    create_test_data(db)
    results = search_tracks(db, "xyzabc123")
    assert results == []

# ── Tests de Customers ───────────────────────────────
def test_get_all_customers(db):
    create_test_data(db)
    customers = get_all_customers(db)
    assert len(customers) == 1
    assert customers[0].email == "alan@test.com"

def test_get_customer_by_id_exists(db):
    create_test_data(db)
    customer = get_customer_by_id(db, 1)
    assert customer is not None
    assert customer.first_name == "Alan"

def test_get_customer_by_id_not_exists(db):
    customer = get_customer_by_id(db, 999)
    assert customer is None

# ── Tests de Compra ──────────────────────────────────
def test_purchase_tracks_success(db):
    create_test_data(db)
    purchase = PurchaseRequest(customer_id=1, track_ids=[1])
    invoice = purchase_tracks(db, purchase)
    assert invoice is not None
    assert invoice.total == Decimal("0.99")
    assert invoice.customer_id == 1

def test_purchase_tracks_customer_not_found(db):
    create_test_data(db)
    purchase = PurchaseRequest(customer_id=999, track_ids=[1])
    result = purchase_tracks(db, purchase)
    assert result is None