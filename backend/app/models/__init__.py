from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Artist(Base):
    __tablename__ = "artist"
    artist_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120))
    albums = relationship("Album", back_populates="artist")

class Album(Base):
    __tablename__ = "album"
    album_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(160))
    artist_id = Column(Integer, ForeignKey("artist.artist_id"))
    artist = relationship("Artist", back_populates="albums")
    tracks = relationship("Track", back_populates="album")

class Genre(Base):
    __tablename__ = "genre"
    genre_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120))

class Track(Base):
    __tablename__ = "track"
    track_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    album_id = Column(Integer, ForeignKey("album.album_id"))
    genre_id = Column(Integer, ForeignKey("genre.genre_id"))
    unit_price = Column(Numeric(10, 2))
    album = relationship("Album", back_populates="tracks")
    genre = relationship("Genre")

class Customer(Base):
    __tablename__ = "customer"
    customer_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(40))
    last_name = Column(String(20))
    email = Column(String(60))
    invoices = relationship("Invoice", back_populates="customer")

class Invoice(Base):
    __tablename__ = "invoice"
    invoice_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"))
    invoice_date = Column(DateTime)
    total = Column(Numeric(10, 2))
    customer = relationship("Customer", back_populates="invoices")
    lines = relationship("InvoiceLine", back_populates="invoice")

class InvoiceLine(Base):
    __tablename__ = "invoice_line"
    invoice_line_id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoice.invoice_id"))
    track_id = Column(Integer, ForeignKey("track.track_id"))
    unit_price = Column(Numeric(10, 2))
    quantity = Column(Integer)
    invoice = relationship("Invoice", back_populates="lines")
    track = relationship("Track")
# ── AUTENTICACIÓN ─────────────────────────────────────
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

class User(Base):
    __tablename__ = "users"
    user_id    = Column(Integer, primary_key=True, index=True)
    email      = Column(String(100), unique=True, nullable=False)
    password   = Column(String(255), nullable=False)
    role       = Column(String(20), default="usuario")
    created_at = Column(DateTime, default=datetime.utcnow)
