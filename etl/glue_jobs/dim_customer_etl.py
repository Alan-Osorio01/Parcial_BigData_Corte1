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
from awsgluedq.transforms import EvaluateDataQuality

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Default ruleset used by all target nodes with data quality enabled
DEFAULT_DATA_QUALITY_RULESET = """
    Rules = [
        ColumnCount > 0
    ]
"""

# Script generated for node customer_source
customer_source_node1776805371815 = glueContext.create_dynamic_frame.from_options(
    connection_type = "postgresql",
    connection_options = {
        "useConnectionProperties": "true",
        "dbtable": "public.customer",
        "connectionName": "chinook-rds",
    },
    transformation_ctx = "customer_source_node1776805371815"
)

# Script generated for node Change Schema
ChangeSchema_node1776805427812 = ApplyMapping.apply(frame=customer_source_node1776805371815, mappings=[("customer_id", "int", "customer_id", "int"), ("first_name", "string", "first_name", "string"), ("last_name", "string", "last_name", "string"), ("company", "string", "company", "string"), ("city", "string", "city", "string"), ("state", "string", "state", "string"), ("country", "string", "country", "string"), ("email", "string", "email", "string")], transformation_ctx="ChangeSchema_node1776805427812")

# Script generated for node dim_customer_target
EvaluateDataQuality().process_rows(frame=ChangeSchema_node1776805427812, ruleset=DEFAULT_DATA_QUALITY_RULESET, publishing_options={"dataQualityEvaluationContext": "EvaluateDataQuality_node1776804912821", "enableDataQualityResultsPublishing": True}, additional_options={"dataQualityResultsPublishing.strategy": "BEST_EFFORT", "observations.scope": "ALL"})
dim_customer_target_node1776805782916 = glueContext.getSink(path="s3://chinook-datalake-academy/dim_customer/", connection_type="s3", updateBehavior="UPDATE_IN_DATABASE", partitionKeys=[], enableUpdateCatalog=True, transformation_ctx="dim_customer_target_node1776805782916")
dim_customer_target_node1776805782916.setCatalogInfo(catalogDatabase="chinook_dw",catalogTableName="dim_customer")
dim_customer_target_node1776805782916.setFormat("glueparquet", compression="snappy")
dim_customer_target_node1776805782916.writeFrame(ChangeSchema_node1776805427812)
job.commit()