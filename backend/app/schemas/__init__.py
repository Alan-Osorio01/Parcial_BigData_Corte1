from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ArtistSchema(BaseModel):
    artist_id: int
    name: Optional[str]
    class Config:
        from_attributes = True

class GenreSchema(BaseModel):
    genre_id: int
    name: Optional[str]
    class Config:
        from_attributes = True

class TrackSchema(BaseModel):
    track_id: int
    name: str
    unit_price: Decimal
    album_id: Optional[int]
    genre_id: Optional[int]
    class Config:
        from_attributes = True

class TrackDetailSchema(BaseModel):
    track_id: int
    name: str
    unit_price: Decimal
    album: Optional[str] = None
    artist: Optional[str] = None
    genre: Optional[str] = None
    class Config:
        from_attributes = True

class CustomerSchema(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str
    class Config:
        from_attributes = True

class PurchaseRequest(BaseModel):
    customer_id: int
    track_ids: List[int]

class InvoiceSchema(BaseModel):
    invoice_id: int
    customer_id: int
    invoice_date: datetime
    total: Decimal
    class Config:
        from_attributes = True