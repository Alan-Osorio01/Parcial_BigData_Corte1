"""
DimEmployee ETL — AWS Glue Visual Job (exportado)
Fuente : RDS PostgreSQL tabla public.employee
Destino: s3://chinook-datalake-academy/dim_employee/
Modo   : Overwrite (siempre el estado actual del empleado)
Bookmark: ACTIVADO — solo procesa empleados nuevos o modificados
Nota   : ReportsTo es auto-referencia (employee_id del jefe directo)
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# ── Inicialización ──────────────────────────────────────────────────────────
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc   = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job   = Job(glueContext)
job.init(args["JOB_NAME"], args)

# ── 1. SOURCE — Leer tabla employee desde RDS ───────────────────────────────
employee_node = glueContext.create_dynamic_frame.from_options(
    connection_type="postgresql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "public.employee",
        "connectionName": "chinook-rds",
    },
    transformation_ctx="employee_node",  # necesario para el Job Bookmark
)

# ── 2. APPLYMAPPING — Renombrar y tipar columnas ────────────────────────────
# Las columnas que NO se listan aquí se descartan automáticamente:
# address, city, state, country, postal_code, phone, fax, birth_date
mapped_node = ApplyMapping.apply(
    frame=employee_node,
    mappings=[
        ("employee_id", "int",    "EmployeeKey", "int"),
        ("first_name",  "string", "FirstName",   "string"),
        ("last_name",   "string", "LastName",    "string"),
        ("title",       "string", "Title",       "string"),
        ("reports_to",  "int",    "ReportsTo",   "int"),   # FK a sí misma
        ("hire_date",   "string", "HireDate",    "string"),
        ("email",       "string", "Email",       "string"),
    ],
    transformation_ctx="mapped_node",
)

# ── 3. TARGET — Escribir en S3 como Parquet (Snappy) ───────────────────────
glueContext.write_dynamic_frame.from_options(
    frame=mapped_node,
    connection_type="s3",
    format="glueparquet",
    connection_options={
        "path": "s3://chinook-datalake-academy/dim_employee/",
        "partitionKeys": [],        # sin particionamiento (tabla muy pequeña)
    },
    format_options={
        "compression": "snappy",
        "useGlueParquetWriter": True,
    },
    transformation_ctx="target_node",
)

# ── Commit del Job Bookmark ─────────────────────────────────────────────────
job.commit()