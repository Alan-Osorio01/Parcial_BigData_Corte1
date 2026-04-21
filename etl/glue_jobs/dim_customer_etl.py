"""
DimCustomer ETL — AWS Glue Visual Job (exportado)
Fuente : RDS PostgreSQL tabla public.customer
Destino: s3://chinook-datalake-academy/dim_customer/
Modo   : Overwrite (siempre el estado actual)
Bookmark: ACTIVADO — solo procesa clientes nuevos en cada ejecución
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

# ── 1. SOURCE — Leer tabla customer desde RDS vía Glue Connection ───────────
customer_node = glueContext.create_dynamic_frame.from_options(
    connection_type="postgresql",
    connection_options={
        "useConnectionProperties": "true",
        "dbtable": "public.customer",
        "connectionName": "chinook-rds",  # nombre exacto de la Glue Connection
    },
    transformation_ctx="customer_node",  # necesario para el Job Bookmark
)

# ── 2. APPLYMAPPING — Renombrar y tipar columnas ────────────────────────────
mapped_node = ApplyMapping.apply(
    frame=customer_node,
    mappings=[
        ("customer_id", "int",    "CustomerKey", "int"),
        ("first_name",  "string", "FirstName",   "string"),
        ("last_name",   "string", "LastName",    "string"),
        ("company",     "string", "Company",     "string"),
        ("country",     "string", "Country",     "string"),
        ("city",        "string", "City",        "string"),
        ("state",       "string", "State",       "string"),
        ("email",       "string", "Email",       "string"),
        # Columnas que NO aparecen aquí son descartadas automáticamente:
        # address, postal_code, phone, fax, support_rep_id
    ],
    transformation_ctx="mapped_node",
)

# ── 3. TARGET — Escribir en S3 como Parquet (Snappy) ───────────────────────
glueContext.write_dynamic_frame.from_options(
    frame=mapped_node,
    connection_type="s3",
    format="glueparquet",
    connection_options={
        "path": "s3://chinook-datalake-academy/dim_customer/",
        "partitionKeys": [],        # sin particionamiento (tabla pequeña)
    },
    format_options={
        "compression": "snappy",
        "useGlueParquetWriter": True,
    },
    transformation_ctx="target_node",
)

# ── Commit del Job Bookmark ─────────────────────────────────────────────────
job.commit()