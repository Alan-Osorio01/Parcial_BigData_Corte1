import pandas as pd
import holidays
import boto3
from datetime import date, timedelta

# CONFIGURACIÓN
BUCKET_NAME = "chinook-datalake-academy"
S3_PREFIX = "dim_date/"

LOCAL_PARQUET = "dim_date.parquet"

FECHA_INICIO = date(2009, 1, 1)
FECHA_FIN = date(2030, 12, 31)

# GENERAR DIM DATE
def generar_dim_date(fecha_inicio=date(2009, 1, 1), fecha_fin=date(2030, 12, 31)):
    registros = []

    festivos_colombia = {}
    for anio in range(fecha_inicio.year, fecha_fin.year + 1):
        festivos_colombia[anio] = holidays.Colombia(years=anio)

    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:

        registros.append({
            "DateKey": int(fecha_actual.strftime("%Y%m%d")),
            "FullDate": fecha_actual,
            "Year": fecha_actual.year,
            "Quarter": (fecha_actual.month - 1) // 3 + 1,
            "Month": fecha_actual.month,
            "Day": fecha_actual.day,
            "DayOfWeek": fecha_actual.strftime("%A"),
            "IsHoliday": fecha_actual in festivos_colombia[fecha_actual.year]
        })

        fecha_actual += timedelta(days=1)

    return pd.DataFrame(registros)

# GUARDAR PARQUET
def guardar_parquet(df, ruta):
    df.to_parquet(ruta, index=False)
    print(f"Parquet guardado en: {ruta}")

# SUBIR A S3
def subir_a_s3(ruta_local, bucket, prefijo):
    s3 = boto3.client("s3")
    nombre_archivo = ruta_local.split("/")[-1]
    s3_key = prefijo + nombre_archivo

    s3.upload_file(ruta_local, bucket, s3_key)
    print(f"Subido a: s3://{bucket}/{s3_key}")

# MAIN
if __name__ == "__main__":
    print("Generando DimDate...")

    df = generar_dim_date(FECHA_INICIO, FECHA_FIN)

    # 👇 Mostrar en terminal (sin usar CSV)
    print(df.head(10))   # primeras filas
    print("Total filas:", len(df))

    # Guardar parquet
    guardar_parquet(df, LOCAL_PARQUET)

    # Subir a S3
    subir_a_s3(LOCAL_PARQUET, BUCKET_NAME, S3_PREFIX)

    print("DimDate completado correctamente")