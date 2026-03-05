from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import RegisterSchema, LoginSchema
import app.auth as auth_module

router = APIRouter()

# ─── REGISTRO PÚBLICO (siempre rol "usuario") ────────────────────────────────
@router.post("/auth/register", tags=["auth"])
def register(data: RegisterSchema, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    user = User(
        email=data.email,
        password=auth_module.hash_password(data.password),
        role="usuario"   # ← SIEMPRE usuario, nunca admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Usuario creado", "email": user.email, "role": user.role}


# ─── REGISTRO ADMIN (solo accesible con token de admin) ──────────────────────
@router.post("/auth/register/admin", tags=["auth"])
def register_admin(
    data: RegisterSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_module.require_admin)
):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    user = User(
        email=data.email,
        password=auth_module.hash_password(data.password),
        role=data.role   # admin puede asignar cualquier rol
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": f"Usuario '{data.role}' creado", "email": user.email, "role": user.role}


# ─── LOGIN ────────────────────────────────────────────────────────────────────
@router.post("/auth/login", tags=["auth"])
def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not auth_module.verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = auth_module.create_token({"sub": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "role": user.role}


# ─── ME (usuario autenticado) ─────────────────────────────────────────────────
@router.get("/auth/me", tags=["auth"])
def me(current_user: User = Depends(auth_module.get_current_user)):
    return {"email": current_user.email, "role": current_user.role}



# ─── TRACKS ───────────────────────────────────────────────────────────────────
from app.models import Track, Album, Artist, Genre
from app.schemas import TrackDetailSchema

@router.get("/tracks", tags=["tracks"])
def get_tracks(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    tracks = db.query(Track).offset(offset).limit(limit).all()
    result = []
    for t in tracks:
        album = t.album
        artist = album.artist if album else None
        genre = t.genre
        result.append({
            "track_id": t.track_id,
            "name": t.name,
            "unit_price": float(t.unit_price),
            "album": album.title if album else None,
            "artist": artist.name if artist else None,
            "genre": genre.name if genre else None,
        })
    return result


# ─── CUSTOMERS ────────────────────────────────────────────────────────────────
from app.models import Customer

@router.get("/customers", tags=["customers"])
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return [
        {
            "customer_id": c.customer_id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "email": c.email
        }
        for c in customers
    ]


# ─── PURCHASE ─────────────────────────────────────────────────────────────────
from app.models import Invoice, InvoiceLine
from app.schemas import PurchaseRequest
from datetime import datetime
from decimal import Decimal

@router.post("/purchase", tags=["purchase"])
def purchase(data: PurchaseRequest, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    tracks = db.query(Track).filter(Track.track_id.in_(data.track_ids)).all()
    if not tracks:
        raise HTTPException(status_code=404, detail="Canciones no encontradas")

    total = sum(t.unit_price for t in tracks)

    invoice = Invoice(
        customer_id=data.customer_id,
        invoice_date=datetime.utcnow(),
        total=total
    )
    db.add(invoice)
    db.flush()

    for track in tracks:
        line = InvoiceLine(
            invoice_id=invoice.invoice_id,
            track_id=track.track_id,
            unit_price=track.unit_price,
            quantity=1
        )
        db.add(line)

    db.commit()
    db.refresh(invoice)

    return {
        "invoice_id": invoice.invoice_id,
        "customer": f"{customer.first_name} {customer.last_name}",
        "tracks": [t.name for t in tracks],
        "total": float(total),
        "date": invoice.invoice_date.isoformat()
    }
