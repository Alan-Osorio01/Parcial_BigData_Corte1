"""
DimEmployee History ETL — AWS Glue Visual Job (exportado)
Fuente : RDS PostgreSQL tabla public.employee
Destino: s3://chinook-datalake-academy/dim_employee_history/snapshot_date=YYYYMMDD/
Modo   : APPEND — nunca borra, acumula un snapshot completo por ejecución
Bookmark: DESACTIVADO — debe copiar TODOS los empleados en cada ejecución
Propósito: Preservar histórico de la jerarquía ReportsTo a lo largo del tiempo
"""

import sys
from datetime import datetime
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import lit

# ── Inicialización ──────────────────────────────────────────────────────────
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc   = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job   = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Fecha de hoy como entero yyyymmdd (ej: 20260421)
snapshot_date = int(datetime.today().strftime("%Y%m%d"))

# ── 1. SOURCE — Leer tabla employee desde RDS ───────────────────────────────
# SIN transformation_ctx para que NO use Job Bookmark (full copy siempre)
employee_node = glueContext.create_dynamic_frame.from_options(
    connection_type="postgresql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "public.employee",
        "connectionName": "chinook-rds",
    },
)

# ── 2. APPLYMAPPING — Renombrar y tipar columnas ────────────────────────────
# Las columnas no listadas se descartan automáticamente:
# address, city, state, country, postal_code, phone, fax, birth_date
mapped_node = ApplyMapping.apply(
    frame=employee_node,
    mappings=[
        ("employee_id", "int",    "EmployeeKey", "int"),
        ("first_name",  "string", "FirstName",   "string"),
        ("last_name",   "string", "LastName",    "string"),
        ("title",       "string", "Title",       "string"),
        ("reports_to",  "int",    "ReportsTo",   "int"),   # FK auto-referencia
        ("hire_date",   "string", "HireDate",    "string"),
        ("email",       "string", "Email",       "string"),
    ],
)

# ── 3. AGREGAR snapshot_date como columna ──────────────────────────────────
# Convertir a DataFrame Spark para agregar la columna, luego volver a DynamicFrame
df = mapped_node.toDF()
df = df.withColumn("snapshot_date", lit(snapshot_date))
snapshot_node = DynamicFrame.fromDF(df, glueContext, "snapshot_node")

# ── 4. TARGET — Escribir en S3 particionado por snapshot_date ──────────────
# Cada ejecución crea una nueva carpeta: snapshot_date=20260421/
# Las carpetas anteriores NO se tocan (modo append implícito por partición)
glueContext.write_dynamic_frame.from_options(
    frame=snapshot_node,
    connection_type="s3",
    format="glueparquet",
    connection_options={
        "path": "s3://chinook-datalake-academy/dim_employee_history/",
        "partitionKeys": ["snapshot_date"],  # crea carpeta snapshot_date=YYYYMMDD/
    },
    format_options={
        "compression": "snappy",
        "useGlueParquetWriter": True,
    },
)

# ── Commit (sin bookmark activo) ────────────────────────────────────────────
job.commit()