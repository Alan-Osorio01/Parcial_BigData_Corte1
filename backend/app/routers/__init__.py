from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import services, schemas
from typing import List

router = APIRouter()

# ── Tracks ──────────────────────────────────────────
@router.get("/tracks", response_model=List[schemas.TrackSchema])
def get_tracks(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return services.get_all_tracks(db, skip, limit)

@router.get("/tracks/search", response_model=List[schemas.TrackSchema])
def search_tracks(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    results = services.search_tracks(db, q)
    if not results:
        raise HTTPException(status_code=404, detail="No se encontraron resultados")
    return results

@router.get("/tracks/{track_id}", response_model=schemas.TrackSchema)
def get_track(track_id: int, db: Session = Depends(get_db)):
    track = services.get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Canción no encontrada")
    return track

# ── Customers ────────────────────────────────────────
@router.get("/customers", response_model=List[schemas.CustomerSchema])
def get_customers(db: Session = Depends(get_db)):
    return services.get_all_customers(db)

@router.get("/customers/{customer_id}", response_model=schemas.CustomerSchema)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = services.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return customer

# ── Compras ──────────────────────────────────────────
@router.post("/purchase", response_model=schemas.InvoiceSchema)
def purchase(purchase: schemas.PurchaseRequest, db: Session = Depends(get_db)):
    invoice = services.purchase_tracks(db, purchase)
    if not invoice:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return invoice