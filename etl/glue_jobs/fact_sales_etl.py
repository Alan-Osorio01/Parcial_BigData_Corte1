import sys
from awsglue.transforms import *
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
CONNECTION  = "chinook-rds"
GLUE_DB     = "chinook_dw"
BUCKET      = "chinook-datalake-academy"
TARGET_PATH = f"s3://{BUCKET}/fact_sales/"
# ─────────────────────────────────────────────────────────────────────────────

def read_jdbc(table: str) -> DynamicFrame:
    return glueContext.create_dynamic_frame.from_options(
        connection_type="jdbc",
        connection_options={
            "useConnectionProperties": "true",
            "dbtable": table,
            "connectionName": CONNECTION,
        },
        transformation_ctx=f"src_{table}",
    )


# ── 1. Leer tablas fuente ────────────────────────────────────────────────────
invoice_line_df = read_jdbc("invoice_line").toDF()
invoice_df      = read_jdbc("invoice").toDF()
customer_df     = read_jdbc("customer").toDF()
employee_df     = read_jdbc("employee").toDF()

# ── 2. Joins ─────────────────────────────────────────────────────────────────
# invoice_line → invoice
fact = invoice_line_df.join(
    invoice_df.select("invoice_id", "customer_id", "invoice_date"),
    on="invoice_id",
    how="inner",
)

# → customer (para obtener support_rep_id = EmployeeKey)
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

# ── 4. Selección y renombrado de columnas finales ────────────────────────────
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

# ── 5. Escribir a S3 particionado ────────────────────────────────────────────
fact_dyf = DynamicFrame.fromDF(fact, glueContext, "fact_sales_output")

sink = glueContext.getSink(
    path=TARGET_PATH,
    connection_type="s3",
    updateBehavior="UPDATE_IN_DATABASE",
    partitionKeys=["year", "month", "day"],
    compression="snappy",
    enableUpdateCatalog=True,
    transformation_ctx="sink_fact_sales",
)
sink.setCatalogInfo(catalogDatabase=GLUE_DB, catalogTableName="fact_sales")
sink.setFormat("glueparquet")
sink.writeFrame(fact_dyf)

job.commit()
