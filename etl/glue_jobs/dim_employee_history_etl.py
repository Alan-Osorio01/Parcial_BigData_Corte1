"""
DimEmployee History ETL — AWS Glue Visual Job (exportado)
Fuente : RDS PostgreSQL tabla public.employee
Destino: s3://chinook-datalake-academy/dim_employee_history/snapshot_date=YYYYMMDD/
Modo   : APPEND — nunca borra, acumula un snapshot completo por ejecución
Bookmark: DESACTIVADO — debe copiar TODOS los empleados en cada ejecución
Propósito: Preservar histórico de la jerarquía ReportsTo a lo largo del tiempo
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

# Script generated for node employee_source
employee_source_node1776811567455 = glueContext.create_dynamic_frame.from_options(
    connection_type = "postgresql",
    connection_options = {
        "useConnectionProperties": "true",
        "dbtable": "public.employee",
        "connectionName": "chinook-rds",
    },
    transformation_ctx = "employee_source_node1776811567455"
)

# Script generated for node Change Schema
ChangeSchema_node1776811606783 = ApplyMapping.apply(frame=employee_source_node1776811567455, mappings=[("employee_id", "int", "EmployeeKey", "int"), ("last_name", "string", "LastName", "string"), ("first_name", "string", "FirstName", "string"), ("title", "string", "Title", "string"), ("reports_to", "int", "ReportsTo", "int"), ("hire_date", "timestamp", "HireDate", "timestamp"), ("email", "string", "Email", "string")], transformation_ctx="ChangeSchema_node1776811606783")

# Script generated for node SQL Query
SqlQuery0 = '''
SELECT *,
  CAST(date_format(current_date, 'yyyyMMdd') AS INT) AS snapshot_date
FROM myDataSource
'''
SQLQuery_node1776811789941 = sparkSqlQuery(glueContext, query = SqlQuery0, mapping = {"myDataSource":ChangeSchema_node1776811606783}, transformation_ctx = "SQLQuery_node1776811789941")

# Script generated for node dim_employee_history_target
EvaluateDataQuality().process_rows(frame=SQLQuery_node1776811789941, ruleset=DEFAULT_DATA_QUALITY_RULESET, publishing_options={"dataQualityEvaluationContext": "EvaluateDataQuality_node1776810737330", "enableDataQualityResultsPublishing": True}, additional_options={"dataQualityResultsPublishing.strategy": "BEST_EFFORT", "observations.scope": "ALL"})
dim_employee_history_target_node1776811835510 = glueContext.getSink(path="s3://chinook-datalake-academy/dim_employee_history/", connection_type="s3", updateBehavior="UPDATE_IN_DATABASE", partitionKeys=["snapshot_date"], enableUpdateCatalog=True, transformation_ctx="dim_employee_history_target_node1776811835510")
dim_employee_history_target_node1776811835510.setCatalogInfo(catalogDatabase="chinook_dw",catalogTableName="dim_employee_history")
dim_employee_history_target_node1776811835510.setFormat("glueparquet", compression="snappy")
dim_employee_history_target_node1776811835510.writeFrame(SQLQuery_node1776811789941)
job.commit()