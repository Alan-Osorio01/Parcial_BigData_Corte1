from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Track, Artist, Album, Genre, Customer, Invoice, InvoiceLine
from app.schemas import PurchaseRequest
from datetime import datetime
from decimal import Decimal

def search_tracks(db: Session, query: str):
    return (
        db.query(Track)
        .join(Album, Track.album_id == Album.album_id)
        .join(Artist, Album.artist_id == Artist.artist_id)
        .join(Genre, Track.genre_id == Genre.genre_id)
        .filter(
            or_(
                Track.name.ilike(f"%{query}%"),
                Artist.name.ilike(f"%{query}%"),
                Genre.name.ilike(f"%{query}%")
            )
        ).all()
    )

def get_all_tracks(db: Session, skip: int = 0, limit: int = 50):
    return db.query(Track).offset(skip).limit(limit).all()

def get_track_by_id(db: Session, track_id: int):
    return db.query(Track).filter(Track.track_id == track_id).first()

def get_customer_by_id(db: Session, customer_id: int):
    return db.query(Customer).filter(Customer.customer_id == customer_id).first()

def get_all_customers(db: Session):
    return db.query(Customer).all()

def purchase_tracks(db: Session, purchase: PurchaseRequest):
    customer = get_customer_by_id(db, purchase.customer_id)
    if not customer:
        return None

    total = Decimal("0.00")
    invoice = Invoice(
        customer_id=purchase.customer_id,
        invoice_date=datetime.now(),
        total=Decimal("0.00")
    )
    db.add(invoice)
    db.flush()

    for track_id in purchase.track_ids:
        track = get_track_by_id(db, track_id)
        if track:
            line = InvoiceLine(
                invoice_id=invoice.invoice_id,
                track_id=track_id,
                unit_price=track.unit_price,
                quantity=1
            )
            db.add(line)
            total += track.unit_price

    invoice.total = total
    db.commit()
    db.refresh(invoice)
    return invoice