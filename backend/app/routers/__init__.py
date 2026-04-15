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
from sqlalchemy import or_

def _format_tracks(tracks):
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

@router.get("/tracks", tags=["tracks"])
def get_tracks(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    tracks = db.query(Track).offset(offset).limit(limit).all()
    return _format_tracks(tracks)

@router.get("/tracks/search", tags=["tracks"])
def search_tracks(q: str, db: Session = Depends(get_db)):
    tracks = (
        db.query(Track)
        .join(Album, Track.album_id == Album.album_id)
        .join(Artist, Album.artist_id == Artist.artist_id)
        .join(Genre, Track.genre_id == Genre.genre_id)
        .filter(or_(
            Track.name.ilike(f"%{q}%"),
            Artist.name.ilike(f"%{q}%"),
            Genre.name.ilike(f"%{q}%")
        )).limit(100).all()
    )
    return _format_tracks(tracks)


# ─── CUSTOMERS ────────────────────────────────────────────────────────────────
from app.models import Customer

@router.get("/customers/me", tags=["customers"])
def my_customer(db: Session = Depends(get_db), current_user: User = Depends(auth_module.get_current_user)):
    from sqlalchemy import func
    customer = db.query(Customer).filter(Customer.email == current_user.email).first()
    if not customer:
        raw = current_user.email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
        parts = raw.split(' ', 1)
        next_id = (db.query(func.max(Customer.customer_id)).scalar() or 0) + 1
        customer = Customer(
            customer_id=next_id,
            first_name=parts[0],
            last_name=parts[1] if len(parts) > 1 else '',
            email=current_user.email
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
    return {
        "customer_id": customer.customer_id,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "email": customer.email
    }

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


# ─── INVOICES ─────────────────────────────────────────────────────────────────
@router.get("/invoices/me", tags=["invoices"])
def my_invoices(db: Session = Depends(get_db), current_user: User = Depends(auth_module.get_current_user)):
    customer = db.query(Customer).filter(Customer.email == current_user.email).first()
    if not customer:
        return {"customer": None, "invoices": []}
    result = []
    for inv in customer.invoices:
        tracks = [
            {"name": line.track.name, "price": float(line.unit_price)}
            for line in inv.lines if line.track
        ]
        result.append({
            "invoice_id": inv.invoice_id,
            "date": inv.invoice_date.isoformat(),
            "total": float(inv.total),
            "tracks": tracks
        })
    result.sort(key=lambda x: x["date"], reverse=True)
    return {"customer": f"{customer.first_name} {customer.last_name}", "invoices": result}


# ─── PURCHASE ─────────────────────────────────────────────────────────────────
from app.models import Invoice, InvoiceLine
from app.schemas import PurchaseRequest
from datetime import datetime
from decimal import Decimal

@router.post("/purchase", tags=["purchase"])
def purchase(data: PurchaseRequest, db: Session = Depends(get_db)):
    from sqlalchemy import func

    customer = db.query(Customer).filter(Customer.customer_id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    tracks = db.query(Track).filter(Track.track_id.in_(data.track_ids)).all()
    if not tracks:
        raise HTTPException(status_code=404, detail="Canciones no encontradas")

    total = sum(t.unit_price for t in tracks)

    next_invoice_id = (db.query(func.max(Invoice.invoice_id)).scalar() or 0) + 1
    invoice = Invoice(
        invoice_id=next_invoice_id,
        customer_id=data.customer_id,
        invoice_date=datetime.utcnow(),
        total=total
    )
    db.add(invoice)
    db.flush()

    next_line_id = (db.query(func.max(InvoiceLine.invoice_line_id)).scalar() or 0) + 1
    for i, track in enumerate(tracks):
        line = InvoiceLine(
            invoice_line_id=next_line_id + i,
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


# ─── GENRES ───────────────────────────────────────────────────────────────────
@router.get("/genres", tags=["admin"])
def get_genres(db: Session = Depends(get_db)):
    from app.models import Genre
    return [{"genre_id": g.genre_id, "name": g.name} for g in db.query(Genre).order_by(Genre.name).all()]


# ─── ADMIN — USUARIOS ─────────────────────────────────────────────────────────
@router.get("/admin/users", tags=["admin"])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(auth_module.require_admin)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "user_id": u.user_id,
            "email": u.email,
            "role": u.role,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]

@router.delete("/admin/users/{user_id}", tags=["admin"])
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_module.require_admin)):
    if user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta")
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(user)
    db.commit()
    return {"message": "Usuario eliminado"}


# ─── ADMIN — CANCIONES ────────────────────────────────────────────────────────
from app.schemas import AddTrackSchema

@router.post("/tracks", tags=["admin"])
def add_track(data: AddTrackSchema, db: Session = Depends(get_db), current_user: User = Depends(auth_module.require_admin)):
    from sqlalchemy import func
    from decimal import Decimal

    # Buscar o crear artista
    artist = db.query(Artist).filter(Artist.name.ilike(data.artist_name)).first()
    if not artist:
        next_artist_id = (db.query(func.max(Artist.artist_id)).scalar() or 0) + 1
        artist = Artist(artist_id=next_artist_id, name=data.artist_name)
        db.add(artist)
        db.flush()

    # Buscar o crear álbum "Singles" del artista
    album_title = f"Singles - {artist.name}"
    album = db.query(Album).filter(Album.artist_id == artist.artist_id, Album.title == album_title).first()
    if not album:
        next_album_id = (db.query(func.max(Album.album_id)).scalar() or 0) + 1
        album = Album(album_id=next_album_id, title=album_title, artist_id=artist.artist_id)
        db.add(album)
        db.flush()

    next_track_id = (db.query(func.max(Track.track_id)).scalar() or 0) + 1
    track = Track(
        track_id=next_track_id,
        name=data.name,
        album_id=album.album_id,
        genre_id=data.genre_id,
        unit_price=Decimal(str(data.unit_price))
    )
    db.add(track)
    db.commit()
    db.refresh(track)

    return {
        "track_id": track.track_id,
        "name": track.name,
        "artist": artist.name,
        "unit_price": float(track.unit_price),
        "message": "Canción agregada exitosamente"
    }
