"""
Tests unitarios de la lógica de transformación de FactSales.
Prueban los cálculos puros sin depender de Spark ni AWS.
"""
from datetime import date


def invoice_date_key(d: date) -> int:
    """Convierte una fecha en la clave yyyymmdd (lógica equivalente a fact_sales_etl)."""
    return d.year * 10000 + d.month * 100 + d.day


def total_amount(unit_price: float, quantity: int) -> float:
    return round(unit_price * quantity, 2)


# ── InvoiceDateKey ───────────────────────────────────────────────────────────

def test_invoice_date_key_formato_yyyymmdd():
    assert invoice_date_key(date(2026, 4, 21)) == 20260421


def test_invoice_date_key_primer_dia_anio():
    assert invoice_date_key(date(2025, 1, 1)) == 20250101


def test_invoice_date_key_ultimo_dia_anio():
    assert invoice_date_key(date(2025, 12, 31)) == 20251231


def test_invoice_date_key_longitud():
    assert len(str(invoice_date_key(date(2024, 5, 3)))) == 8


# ── TotalAmount ──────────────────────────────────────────────────────────────

def test_total_amount_unitario():
    assert total_amount(0.99, 1) == 0.99


def test_total_amount_multiples_cantidades():
    assert total_amount(0.99, 4) == 3.96


def test_total_amount_precio_alto():
    assert total_amount(1.99, 10) == 19.90


def test_total_amount_sin_overflow_decimal():
    # Valores típicos de Chinook con redondeo de 2 decimales
    assert total_amount(0.99, 3) == 2.97


# ── Particionamiento ─────────────────────────────────────────────────────────

def test_extraer_particiones_year_month_day():
    d = date(2026, 4, 21)
    assert d.year == 2026
    assert d.month == 4
    assert d.day == 21
