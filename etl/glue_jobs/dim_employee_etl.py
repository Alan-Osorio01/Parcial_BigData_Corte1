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

# Script generated for node employee_source
employee_source_node1776810860143 = glueContext.create_dynamic_frame.from_options(
    connection_type = "postgresql",
    connection_options = {
        "useConnectionProperties": "true",
        "dbtable": "public.employee",
        "connectionName": "chinook-rds",
    },
    transformation_ctx = "employee_source_node1776810860143"
)

# Script generated for node Change Schema
ChangeSchema_node1776810895557 = ApplyMapping.apply(frame=employee_source_node1776810860143, mappings=[("employee_id", "int", "EmployeeKey", "int"), ("last_name", "string", "LastName", "string"), ("first_name", "string", "FirstName", "string"), ("title", "string", "Title", "string"), ("reports_to", "int", "ReportsTo", "int"), ("hire_date", "timestamp", "HireDate", "timestamp"), ("email", "string", "Email", "string")], transformation_ctx="ChangeSchema_node1776810895557")

# Script generated for node dim_employee_target
EvaluateDataQuality().process_rows(frame=ChangeSchema_node1776810895557, ruleset=DEFAULT_DATA_QUALITY_RULESET, publishing_options={"dataQualityEvaluationContext": "EvaluateDataQuality_node1776810737330", "enableDataQualityResultsPublishing": True}, additional_options={"dataQualityResultsPublishing.strategy": "BEST_EFFORT", "observations.scope": "ALL"})
dim_employee_target_node1776811144844 = glueContext.getSink(path="s3://chinook-datalake-academy/dim_employee/", connection_type="s3", updateBehavior="UPDATE_IN_DATABASE", partitionKeys=[], enableUpdateCatalog=True, transformation_ctx="dim_employee_target_node1776811144844")
dim_employee_target_node1776811144844.setCatalogInfo(catalogDatabase="chinook_dw",catalogTableName="dim_employee")
dim_employee_target_node1776811144844.setFormat("glueparquet", compression="snappy")
dim_employee_target_node1776811144844.writeFrame(ChangeSchema_node1776810895557)
job.commit()