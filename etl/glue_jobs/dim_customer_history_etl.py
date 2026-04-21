"""
DimCustomer History ETL — AWS Glue Visual Job (exportado)
Fuente : RDS PostgreSQL tabla public.customer
Destino: s3://chinook-datalake-academy/dim_customer_history/snapshot_date=YYYYMMDD/
Modo   : APPEND — nunca borra, acumula un snapshot completo por ejecución
Bookmark: DESACTIVADO — debe copiar TODOS los clientes en cada ejecución
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsgluedq.transforms import EvaluateDataQuality
from awsglue import DynamicFrame

def sparkSqlQuery(glueContext, query, mapping, transformation_ctx) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)
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
customer_source_node1776806820391 = glueContext.create_dynamic_frame.from_options(
    connection_type = "postgresql",
    connection_options = {
        "useConnectionProperties": "true",
        "dbtable": "public.customer",
        "connectionName": "chinook-rds",
    },
    transformation_ctx = "customer_source_node1776806820391"
)

# Script generated for node Change Schema
ChangeSchema_node1776806897516 = ApplyMapping.apply(frame=customer_source_node1776806820391, mappings=[("customer_id", "int", "customer_id", "int"), ("first_name", "string", "first_name", "string"), ("last_name", "string", "last_name", "string"), ("company", "string", "company", "string"), ("city", "string", "city", "string"), ("state", "string", "state", "string"), ("country", "string", "country", "string"), ("email", "string", "email", "string")], transformation_ctx="ChangeSchema_node1776806897516")

# Script generated for node SQL Query
SqlQuery0 = '''
SELECT *,
  CAST(date_format(current_date, 'yyyyMMdd') AS INT) AS snapshot_date
FROM myDataSource
'''
SQLQuery_node1776807121547 = sparkSqlQuery(glueContext, query = SqlQuery0, mapping = {"myDataSource":ChangeSchema_node1776806897516}, transformation_ctx = "SQLQuery_node1776807121547")

# Script generated for node dim_customer_history_target
EvaluateDataQuality().process_rows(frame=SQLQuery_node1776807121547, ruleset=DEFAULT_DATA_QUALITY_RULESET, publishing_options={"dataQualityEvaluationContext": "EvaluateDataQuality_node1776804912821", "enableDataQualityResultsPublishing": True}, additional_options={"dataQualityResultsPublishing.strategy": "BEST_EFFORT", "observations.scope": "ALL"})
dim_customer_history_target_node1776807180641 = glueContext.getSink(path="s3://chinook-datalake-academy/dim_customer_history/", connection_type="s3", updateBehavior="UPDATE_IN_DATABASE", partitionKeys=["snapshot_date"], enableUpdateCatalog=True, transformation_ctx="dim_customer_history_target_node1776807180641")
dim_customer_history_target_node1776807180641.setCatalogInfo(catalogDatabase="chinook_dw",catalogTableName="dim_customer_history")
dim_customer_history_target_node1776807180641.setFormat("glueparquet", compression="snappy")
dim_customer_history_target_node1776807180641.writeFrame(SQLQuery_node1776807121547)
job.commit()