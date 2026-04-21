from etl.python_jobs.dim_date_etl import generar_dim_date


def test_rango_fechas_correcto():
    # Verifica que el rango cubra suficientes días (2009–2030)
    df = generar_dim_date()
    assert len(df) >= 8000


def test_datekey_formato_yyyymmdd():
    df = generar_dim_date()
    sample = df.iloc[0]["DateKey"]
    assert len(str(sample)) == 8
    assert str(sample).isdigit()


def test_unicidad_datekey():
    # Verifica que no haya duplicados
    df = generar_dim_date()
    assert df["DateKey"].is_unique


def test_navidad_es_festivo():
    df = generar_dim_date()
    fila = df[df["DateKey"] == 20261225]
    assert not fila.empty
    assert fila["IsHoliday"].values[0] == True


def test_dia_semana_correcto():
    # Verifica día correcto
    df = generar_dim_date()
    fila = df[df["DateKey"] == 20260104]
    assert fila["DayOfWeek"].values[0] == "Sunday"


def test_quarter_correcto():
    # Verifica trimestre correcto
    df = generar_dim_date()
    fila = df[df["DateKey"] == 20260115]
    assert fila["Quarter"].values[0] == 1


def test_rango_mes():
    # Mes entre 1 y 12
    df = generar_dim_date()
    assert df["Month"].min() >= 1
    assert df["Month"].max() <= 12


def test_rango_dia():
    # Día entre 1 y 31
    df = generar_dim_date()
    assert df["Day"].min() >= 1
    assert df["Day"].max() <= 31


def test_sin_nulos():
    # No debe haber valores nulos
    df = generar_dim_date()
    assert df.isnull().sum().sum() == 0


def test_columnas_correctas():
    # Verifica columnas exactas
    df = generar_dim_date()
    columnas = {
        "DateKey",
        "FullDate",
        "Year",
        "Quarter",
        "Month",
        "Day",
        "DayOfWeek",
        "IsHoliday"
    }
    assert set(df.columns) == columnas