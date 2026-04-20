import pandas as pd
import holidays
from datetime import datetime
import boto3
import os

# ==========================
# CONFIGURACIÓN
# ==========================

START_DATE = "2009-01-01"
END_DATE = "2030-12-31"

# ⚠️ CAMBIAR cuando Alan tenga el bucket listo
S3_BUCKET = "chinook-datalake"
S3_KEY = "dim_date/dim_date.parquet"

# ==========================
# GENERAR DIM DATE
# ==========================

def generate_dim_date(start_date, end_date):
    print("Generando rango de fechas...")

    dates = pd.date_range(start=start_date, end=end_date)

    # Festivos Colombia
    co_holidays = holidays.Colombia()

    data = []

    for date in dates:
        year = date.year
        month = date.month
        day = date.day

        date_key = int(date.strftime("%Y%m%d"))

        # Quarter
        quarter = (month - 1) // 3 + 1

        # Día de la semana
        day_of_week = date.strftime("%A")

        # Festivo
        is_holiday = date in co_holidays

        data.append({
            "DateKey": date_key,
            "FullDate": date.date(),
            "Year": year,
            "Quarter": quarter,
            "Month": month,
            "Day": day,
            "DayOfWeek": day_of_week,
            "IsHoliday": is_holiday
        })

    df = pd.DataFrame(data)

    print(f"DimDate generada con {len(df)} registros")

    return df


# ==========================
# GUARDAR PARQUET LOCAL
# ==========================

def save_local(df, filename="dim_date.parquet"):
    print("Guardando archivo Parquet local...")
    df.to_parquet(filename, index=False)
    print(f"Archivo guardado: {filename}")
    return filename


# ==========================
# SUBIR A S3
# ==========================

def upload_to_s3(file_path, bucket, key):
    print("Subiendo a S3...")

    s3 = boto3.client("s3")

    try:
        s3.upload_file(file_path, bucket, key)
        print(f"Archivo subido a s3://{bucket}/{key}")
    except Exception as e:
        print("Error subiendo a S3:", e)


# ==========================
# MAIN
# ==========================

def main():
    df = generate_dim_date(START_DATE, END_DATE)

    file_path = save_local(df)

    # ⚠️ Solo funciona cuando tengas credenciales AWS activas
    if os.getenv("AWS_ACCESS_KEY_ID"):
        upload_to_s3(file_path, S3_BUCKET, S3_KEY)
    else:
        print("⚠️ No hay credenciales AWS, solo se guardó localmente.")


if __name__ == "__main__":
    main()