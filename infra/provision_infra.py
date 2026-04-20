import boto3
from botocore.exceptions import ClientError

# ── CONFIG ───────────────────────────────────────────────────────────────────
REGION          = "us-east-1"
BUCKET          = "chinook-datalake-academy"
VPC_ID          = "vpc-0f2744cffdd612162"
SUBNET_ID       = "subnet-0c7dc20fce18509a2"
RDS_SG_ID       = "sg-00e47686996fb4d28"
LAB_ROLE_ARN    = "arn:aws:iam::611318804612:role/LabRole"
RDS_ENDPOINT    = "chinook-db.cbi3bser5ehz.us-east-1.rds.amazonaws.com"
RDS_PORT        = 5432
DB_NAME         = "chinook"
DB_USER         = "postgres"
DB_PASSWORD     = "Parcial1"
GLUE_DB         = "chinook_dw"
GLUE_CONNECTION = "chinook-rds"
ATHENA_WG       = "chinook-wg"
GLUE_SG_NAME    = "sg-glue-chinook"

BUCKET_PREFIXES = [
    "scripts/", "dim_customer/", "dim_customer_history/",
    "dim_track/", "dim_employee/", "dim_employee_history/",
    "dim_date/", "fact_sales/", "athena-results/",
]
# ─────────────────────────────────────────────────────────────────────────────

s3     = boto3.client("s3",     region_name=REGION)
glue   = boto3.client("glue",   region_name=REGION)
athena = boto3.client("athena", region_name=REGION)
ec2    = boto3.client("ec2",    region_name=REGION)


def create_bucket():
    try:
        s3.head_bucket(Bucket=BUCKET)
        print(f"  [skip] Bucket {BUCKET} ya existe")
    except ClientError:
        s3.create_bucket(
            Bucket=BUCKET,
            CreateBucketConfiguration={"LocationConstraint": REGION},
        )
        print(f"  [ok]   Bucket {BUCKET} creado")
    for prefix in BUCKET_PREFIXES:
        s3.put_object(Bucket=BUCKET, Key=prefix)
    print(f"  [ok]   {len(BUCKET_PREFIXES)} carpetas verificadas")


def create_glue_sg():
    resp = ec2.describe_security_groups(
        Filters=[
            {"Name": "group-name", "Values": [GLUE_SG_NAME]},
            {"Name": "vpc-id",     "Values": [VPC_ID]},
        ]
    )
    if resp["SecurityGroups"]:
        sg_id = resp["SecurityGroups"][0]["GroupId"]
        print(f"  [skip] SG {GLUE_SG_NAME} ya existe: {sg_id}")
        return sg_id

    sg_id = ec2.create_security_group(
        GroupName=GLUE_SG_NAME,
        Description="Glue workers para Chinook ETL",
        VpcId=VPC_ID,
    )["GroupId"]
    print(f"  [ok]   SG creado: {sg_id}")

    # Self-reference All traffic — requerido por Glue para ejecutar jobs en VPC
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[{"IpProtocol": "-1", "UserIdGroupPairs": [{"GroupId": sg_id}]}],
    )
    print(f"  [ok]   Regla self-reference All traffic agregada a {sg_id}")

    # Permitir que Glue alcance el RDS en 5432
    try:
        ec2.authorize_security_group_ingress(
            GroupId=RDS_SG_ID,
            IpPermissions=[{
                "IpProtocol": "tcp",
                "FromPort": RDS_PORT,
                "ToPort": RDS_PORT,
                "UserIdGroupPairs": [{"GroupId": sg_id}],
            }],
        )
        print(f"  [ok]   Regla 5432 {sg_id} → {RDS_SG_ID} agregada")
    except ClientError as e:
        if "InvalidPermission.Duplicate" in str(e):
            print(f"  [skip] Regla 5432 ya existe en {RDS_SG_ID}")
        else:
            raise

    return sg_id


def create_glue_connection(sg_id):
    try:
        glue.get_connection(Name=GLUE_CONNECTION)
        print(f"  [skip] Conexión {GLUE_CONNECTION} ya existe")
        return
    except ClientError:
        pass

    glue.create_connection(
        ConnectionInput={
            "Name": GLUE_CONNECTION,
            "ConnectionType": "JDBC",
            "ConnectionProperties": {
                "JDBC_CONNECTION_URL": f"jdbc:postgresql://{RDS_ENDPOINT}:{RDS_PORT}/{DB_NAME}",
                "USERNAME": DB_USER,
                "PASSWORD": DB_PASSWORD,
                "JDBC_ENFORCE_SSL": "false",
            },
            "PhysicalConnectionRequirements": {
                "SubnetId": SUBNET_ID,
                "SecurityGroupIdList": [sg_id],
            },
        }
    )
    print(f"  [ok]   Conexión {GLUE_CONNECTION} creada")


def create_glue_database():
    try:
        glue.get_database(Name=GLUE_DB)
        print(f"  [skip] Glue DB {GLUE_DB} ya existe")
    except ClientError:
        glue.create_database(
            DatabaseInput={
                "Name": GLUE_DB,
                "Description": "Data Warehouse Chinook Analytics",
                "LocationUri": f"s3://{BUCKET}/",
            }
        )
        print(f"  [ok]   Glue DB {GLUE_DB} creada")


def create_athena_workgroup():
    try:
        athena.get_work_group(WorkGroup=ATHENA_WG)
        print(f"  [skip] Workgroup {ATHENA_WG} ya existe")
    except ClientError:
        athena.create_work_group(
            Name=ATHENA_WG,
            Configuration={
                "ResultConfiguration": {
                    "OutputLocation": f"s3://{BUCKET}/athena-results/"
                },
                "EnforceWorkGroupConfiguration": True,
                "PublishCloudWatchMetricsEnabled": False,
            },
            Description="Workgroup para Chinook Analytics",
        )
        print(f"  [ok]   Workgroup {ATHENA_WG} creado")


if __name__ == "__main__":
    print("\n=== provision_infra.py ===\n")
    print("1/5  S3 Bucket...")
    create_bucket()
    print("2/5  Security Group Glue...")
    sg_id = create_glue_sg()
    print("3/5  Glue Connection...")
    create_glue_connection(sg_id)
    print("4/5  Glue Database...")
    create_glue_database()
    print("5/5  Athena Workgroup...")
    create_athena_workgroup()
    print("\n✅  Infraestructura lista.\n")
