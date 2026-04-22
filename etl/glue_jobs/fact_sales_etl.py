import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.context import SparkContext
from pyspark.sql import functions as F

args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc          = SparkContext()
glueContext = GlueContext(sc)
spark       = glueContext.spark_session
job         = Job(glueContext)
job.init(args["JOB_NAME"], args)

# ── CONFIG ───────────────────────────────────────────────────────────────────
JDBC_URL    = "jdbc:postgresql://chinook-db.cbi3bser5ehz.us-east-1.rds.amazonaws.com:5432/chinook"
JDBC_PROPS  = {
    "user":   "postgres",
    "password": "Parcial1",
    "driver": "org.postgresql.Driver",
}
GLUE_DB     = "chinook_dw"
BUCKET      = "chinook-datalake-academy"
TARGET_PATH = f"s3://{BUCKET}/fact_sales/"
# ─────────────────────────────────────────────────────────────────────────────

def read_table(table: str):
    return spark.read.jdbc(url=JDBC_URL, table=table, properties=JDBC_PROPS)


# ── 1. Leer tablas fuente (PySpark nativo, sin Glue connection catalog) ──────
invoice_line_df = read_table("invoice_line")
invoice_df      = read_table("invoice")
customer_df     = read_table("customer")

# ── 2. Joins ─────────────────────────────────────────────────────────────────
fact = invoice_line_df.join(
    invoice_df.select("invoice_id", "customer_id", "invoice_date"),
    on="invoice_id",
    how="inner",
)

fact = fact.join(
    customer_df.select("customer_id", "support_rep_id"),
    on="customer_id",
    how="left",
)

# ── 3. Columnas derivadas ────────────────────────────────────────────────────
fact = (
    fact
    .withColumn(
        "InvoiceDateKey",
        (
            F.year("invoice_date")  * 10000 +
            F.month("invoice_date") * 100   +
            F.dayofmonth("invoice_date")
        ).cast("int"),
    )
    .withColumn("TotalAmount", (F.col("unit_price") * F.col("quantity")).cast("decimal(10,2)"))
    .withColumn("year",  F.year("invoice_date").cast("int"))
    .withColumn("month", F.month("invoice_date").cast("int"))
    .withColumn("day",   F.dayofmonth("invoice_date").cast("int"))
)

# ── 4. Columnas finales ──────────────────────────────────────────────────────
fact = fact.select(
    F.col("customer_id").alias("CustomerKey"),
    F.col("track_id").alias("TrackKey"),
    F.col("InvoiceDateKey"),
    F.col("support_rep_id").alias("EmployeeKey"),
    F.col("quantity").alias("Quantity"),
    F.col("unit_price").alias("UnitPrice"),
    F.col("TotalAmount"),
    F.col("year"),
    F.col("month"),
    F.col("day"),
)

# ── 5. Escribir a S3 particionado en modo OVERWRITE ──────────────────────────
# Sin Glue Bookmarks (spark.read.jdbc no los soporta), sobrescribimos todo
# en cada ejecución para evitar duplicados.
spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")

(
    fact.write
        .mode("overwrite")
        .partitionBy("year", "month", "day")
        .option("compression", "snappy")
        .parquet(TARGET_PATH)
)

job.commit()
